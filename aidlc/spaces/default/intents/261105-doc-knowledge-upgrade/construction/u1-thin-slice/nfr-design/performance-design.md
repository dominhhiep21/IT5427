# Performance Design — u1-thin-slice

Nguồn: `nfr-requirements/` (`performance-requirements.md`, `security-requirements.md`, `scalability-requirements.md`, `reliability-requirements.md`, `observability-requirements.md`, `tech-stack-decisions.md`), `functional-design/functional-spec.md`, `contract-design/contract-summary.md` (C4, C8, C9).

Đơn vị: `u1-thin-slice` (Bolt 1). Phạm vi hiệu năng: một pipeline nạp `don_hang` từ CSV, một truy vấn đếm đơn theo tháng trên DuckDB in-memory, một **vùng số liệu** `don-theo-thang` trong tab "Tích hợp".

## 1. Ngân sách độ trễ

Bốn ngưỡng của `performance-requirements.md` được chia thành ngân sách từng bước, để khi test đỏ thì biết đỏ ở đâu chứ không chỉ biết tổng vượt.

| Mã | Ngưỡng | Ngân sách từng bước | Dự phòng |
|---|---|---|---|
| NFR1.3 | nạp 99.441 đơn < 5 giây | mở tệp + `read_csv` với `usecols` **4 cột của bảng đơn** ≈ 0,7 giây; đọc tiêu đề bảng khách để kiểm `bang_giao` ≈ 0,02 giây; dựng 99.441 dataclass ≈ 1,2 giây; kiểm mã đơn duy nhất ≈ 0,2 giây; kiểm ngày và trạng thái ≈ 0,4 giây | ≈ 2,5 giây |
| NFR1.2 | truy vấn < 2 giây | đăng ký DataFrame vào DuckDB ≈ 0,02 giây; quét 99.441 dòng, nhóm theo tháng × trạng thái ≈ 0,05 giây; dựng danh sách `rows` ≈ 0,03 giây | ≈ 1,9 giây |
| NFR1.1 | dựng lại vùng số liệu < 2 giây (dữ liệu đã trong bộ nhớ) | lấy kết quả đã có từ biến cấp tiến trình ≈ 0,01 giây; chọn 12 tháng gần nhất ≈ 0,01 giây; dựng cây Dash ≈ 0,15 giây | ≈ 1,8 giây |
| NFR1.4 | test hiệu năng chạy trong bộ nhanh, ngưỡng cứng 2 giây | đo riêng phần thực thi truy vấn, không tính nạp | — |

**Ngân sách theo từng lần bấm, không theo lần mở tab.** Mở tab không chạy truy vấn (Workflow 3), nên không có ngân sách cho việc mở. Lần bấm **"Chạy truy vấn" đầu tiên** gồm nạp ≤ 5 giây cộng truy vấn ≤ 2 giây, tức **7 giây**; mọi lần bấm sau chỉ còn truy vấn trên dữ liệu đã nạp, ngân sách **2 giây**.

Con số từng bước là **ngân sách thiết kế**, chưa phải số đo. Số đo thật do NFR1.4 ghi lại ở lần chạy đầu và được ghi vào `memory.md` của bước sinh mã nếu lệch quá 50% ngân sách.

## 2. Quyết định thiết kế

### ADR-U1-P1 — Nạp một lần cho cả tiến trình, dùng lại trong mọi phiên

Nạp CSV là bước đắt nhất (khoảng 2,5 giây theo ngân sách trên). Nếu mỗi lần bấm lại đọc lại tệp, ngân sách 2 giây của các lần sau vỡ ngay.

**Quyết định:** nạp đúng một lần cho **mỗi tiến trình dashboard**, giữ `LoadResult` trong một biến cấp mô-đun của gói `src/integration/` (khoá theo đường dẫn tệp + thời điểm sửa tệp). Mọi phiên trình duyệt trong cùng tiến trình dùng chung bản đã nạp đó. Kết quả truy vấn thành công gần nhất cũng giữ ở biến cấp mô-đun (không dùng `dcc.Store`), để lần chạy sau lỗi vẫn hiện được "kết quả lần trước". Không có cache trên đĩa, không có TTL, không có cache phân tán (`scalability-requirements.md` — một người dùng).

**Hệ quả:** lần bấm "Chạy truy vấn" đầu tiên trong tiến trình chịu cả 5 giây nạp và 2 giây truy vấn (đúng ghi chú NFR1.3); các lần bấm sau chỉ còn ngân sách truy vấn, kể cả khi mở thêm một cửa sổ trình duyệt. Khoá theo thời điểm sửa tệp để nếu tệp nguồn được thay ngoài ý muốn thì lần bấm sau nạp lại thay vì phục vụ dữ liệu cũ.

### ADR-U1-P2 — Chỉ đọc 4 cột của bảng đơn; trường `bang_giao` chỉ kiểm tiêu đề

Thực thể `don_hang` của lát cắt có năm trường, nhưng danh sách cột đọc suy ra từ cờ `loaded` trong tệp lược đồ, và chỉ áp cho **bảng khoá** của thực thể:

| Trường trung gian | Bảng nguồn | Cột nguồn | Đọc dữ liệu? |
|---|---|---|---|
| `ma_don` | `olist_orders_dataset` | `order_id` | Có |
| `ngay_dat` | `olist_orders_dataset` | `order_purchase_timestamp` | Có |
| `trang_thai` | `olist_orders_dataset` | `order_status` | Có |
| `ma_khach` | `olist_orders_dataset` | `customer_id` | Có |
| `bang_giao` | `olist_customers_dataset` | `customer_state` | **Không** — bảng khác bảng khoá; chỉ kiểm cột có thật (functional-spec Workflow 1 bước 2), và `load.py` ghi sự kiện `integration.load.skipped` |

**Quyết định:** `usecols` = các trường có `loaded: true` **thuộc bảng khoá** của thực thể (hiện là các cột của `olist_orders_dataset`; tệp lược đồ hiện có thêm hai trường ngày giao nên danh sách là sáu cột, không phải bốn — người viết mã lấy từ lược đồ, không chép tay). Với bảng ngoài bảng khoá, chỉ đọc **tiêu đề** (`nrows=0`) và kiểm cột nằm trong đó.

**Hệ quả:** danh sách cột đọc không còn suy ra từ "năm trường" mà từ cờ `loaded` trong tệp lược đồ (`logical-components.md` §2, L4) — một nguồn sự thật duy nhất. Phép kiểm "danh sách `usecols` khớp các trường có `loaded: true`" nằm ở `reliability-design.md` §5 bảng kiểm chứng; lệch là test đỏ, không phải lỗi lúc chạy.

### ADR-U1-P3 — Truy vấn chạy trên DuckDB in-memory

**Quyết định:** đăng ký DataFrame `don_hang` vào một kết nối `duckdb.connect()` không có đường dẫn, chạy SQL nguồn do bước viết lại sinh ra, đóng kết nối ngay sau khi lấy kết quả (`tech-stack-decisions.md` TS-U1-2).

**Hệ quả:** không phụ thuộc `warehouse/olist.duckdb` nên lát cắt chạy được trên máy chưa `integrate`; không có trạng thái sống giữa hai lần chạy. Đổi lại, mỗi lần chạy truy vấn phải đăng ký lại DataFrame — chấp nhận được vì đó là 0,02 giây.

### ADR-U1-P4 — Không tối ưu trước

Các kỹ thuật trong `nfr-design-guide.md` (cache tầng, kết nối pool, xử lý bất đồng bộ, phân trang) đều nhắm hệ nhiều người dùng hoặc dữ liệu lớn hơn nhiều lần. Với 99.441 dòng, một người dùng, một máy, mỗi kỹ thuật đó thêm mã và thêm chỗ hỏng mà không mua được gì.

**Quyết định:** không thêm cache tầng, không thêm kết nối pool, không chạy truy vấn ở luồng nền. Điều kiện xem lại được ghi ở `scalability-design.md` §3.

## 3. Cách đo

- Mỗi lần nạp và mỗi lần chạy truy vấn trả kèm `elapsed_ms` đo bằng `time.perf_counter()` quanh đúng phần việc, không quanh cả hàm bao gồm dựng giao diện.
- Thẻ hiện `elapsed_ms` của truy vấn cạnh số dòng, để người dùng thấy ngưỡng 2 giây đang được tôn trọng hay không (`observability-requirements.md` OB-U1-1).
- NFR1.4 là một test trong bộ nhanh: dựng DataFrame tổng hợp 99.441 dòng một lần, đo riêng lần thực thi truy vấn, khẳng định `< 2000 ms`. Test không đo thời gian đọc tệp, nên không đỏ ngẫu nhiên vì đĩa.

```python
started = time.perf_counter()
rows = connection.execute(source_sql).fetchall()
elapsed_ms = int((time.perf_counter() - started) * 1000)
if elapsed_ms > 2000:
    logger.warning("integration.query.slow", plan_id=plan_id, elapsed_ms=elapsed_ms)
```

## 4. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Máy đích là máy 8 GB đang dùng, ổ đĩa cục bộ, không có tải nền đáng kể | Giả định — lấy từ `scalability-requirements.md` |
| A2 | `read_csv` với 4 cột của bảng đơn mất dưới 1 giây trên máy này | Giả định — đo ở lần chạy đầu của NFR1.4, ghi lại nếu sai |
| Q1 | Ngưỡng 2 giây của thẻ có tính cả lần dựng biểu đồ đầu tiên của Plotly không? | Không chặn: ngân sách dựng thẻ 0,15 giây đã bao gồm chi phí đó; nếu đo thực tế vượt, tách ngân sách chứ không nâng ngưỡng |
