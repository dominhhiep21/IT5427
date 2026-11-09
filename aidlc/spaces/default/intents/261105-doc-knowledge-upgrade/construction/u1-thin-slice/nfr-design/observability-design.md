# Observability Design — u1-thin-slice

Nguồn: `nfr-requirements/` (`observability-requirements.md` — gồm cả NFR4, `reliability-requirements.md`, `performance-requirements.md`, `security-requirements.md`, `scalability-requirements.md`, `tech-stack-decisions.md`), `functional-design/functional-spec.md` (bảng trạng thái của thẻ), `contract-design/contract-summary.md` (C4, C9).

Đơn vị: `u1-thin-slice`. Hệ chạy local một người dùng nên không có metric tập trung, không có tracing, không có alerting (`observability-requirements.md`, ghi chú). Phần còn lại — và là phần có giá trị — gồm: nhật ký JSONL đúng chỗ (Q2 = A), định nghĩa chỉ số đo được, và cách thẻ truyền đạt trạng thái cho người dùng (NFR4).

## 1. Quyết định thiết kế

### ADR-U1-O1 — Nhật ký của tab mới ghi nối vào tệp nhật ký của lần chạy gần nhất

Đây là quyết định đã chốt ở Q2 = A: không tạo tệp nhật ký riêng cho dashboard.

**Quyết định:** khi dashboard khởi động, nó chọn tệp `logs/<run_id>.jsonl` có thời điểm sửa mới nhất; mọi sự kiện phát sinh từ tab "Tích hợp" được ghi nối vào tệp đó với `stage="integration"`. Nếu `logs/` chưa có tệp nào (chưa chạy pipeline lần nào), dashboard tạo `logs/integration-<run_id>.jsonl` của riêng nó và ghi sự kiện `integration.log.no_pipeline_run` một lần.

Hai trường định danh mang hai nghĩa khác nhau, và điều này được ghi rõ để không ai đọc nhầm:

| Trường | Nghĩa | Nguồn |
|---|---|---|
| `run_id` (trong bản ghi) | Phiên dashboard đang chạy | OB-U1-1 — "run_id của phiên dashboard" |
| Tên tệp | Lần chạy pipeline gần nhất | Q2 = A — "ghi chung tệp nhật ký của lần chạy gần nhất" |

**Hệ quả:** một tệp nhật ký chứa cả sự kiện pipeline (`stage` là `ingest`, `clean`, …) và sự kiện dashboard (`stage="integration"`), nên khi điều tra một con số lệch chỉ cần mở một tệp. Đánh đổi đã biết: hai tiến trình cùng ghi nối vào một tệp (dashboard và một lần chạy pipeline khác). Trên Windows, ghi nối một dòng ngắn bằng `open("a")` là một lời gọi ghi duy nhất nên hiếm khi chen dòng, nhưng **không được bảo đảm**; §5 ghi cách xử lý và điều kiện xem lại.

**Điều không làm:** không thêm gói ghi nhật ký mới, không dựng dịch vụ thu thập log, không xoay vòng tệp nhật ký tự động — `logs/` bị `.gitignore` và mỗi lần chạy pipeline đã sinh một tệp mới.

### ADR-U1-O2 — Cùng một bộ trường cho mọi sự kiện

Mọi bản ghi dùng lại `src/common/logging.py` với năm trường bắt buộc đã có (`timestamp`, `level`, `run_id`, `stage`, `event`) và các trường riêng của sự kiện. Không có định dạng thứ hai.

**Hệ quả:** phân tích bằng `jq`/pandas trên cùng một lược đồ; thêm sự kiện mới chỉ là thêm một dòng trong danh mục §2.

### ADR-U1-O3 — Chỉ số đo là kết quả trả về, không phải phép đo nền

**Quyết định:** `elapsed_ms` và `row_count` đi cùng kết quả truy vấn (C4) và được thẻ hiển thị; không có bộ thu thập số liệu chạy nền.

**Hệ quả:** người dùng thấy ngay ngưỡng 2 giây có bị vượt hay không; không cần thêm hạ tầng. Đổi lại, không có lịch sử độ trễ ngoài nhật ký — chấp nhận được vì NFR1.4 đã là một test có ngưỡng cứng.

### ADR-U1-O4 — SLO của đơn vị này được khẳng định bằng test, không bằng bảng theo dõi

Hệ không có nơi nào tổng hợp số liệu liên tục, nên một "SLO 99,9% trong 30 ngày" sẽ là con số không ai đo. Thay vào đó, ba chỉ số dưới đây được định nghĩa rõ và được khẳng định bằng test chạy trên dữ liệu thật:

| SLI | Định nghĩa | SLO cho đơn vị này | Khẳng định bởi |
|---|---|---|---|
| Tỉ lệ nạp thành công | số lần nạp không lỗi / số lần nạp | 100% trên dữ liệu nguồn hiện có | `tests/integration/`, test end-to-end của đơn vị |
| Độ trễ truy vấn | `elapsed_ms` của truy vấn đếm đơn | 100% dưới 2.000 ms | NFR1.4 trong bộ nhanh |
| Độ đúng của kết quả | số dòng và tổng đơn khớp phép đếm độc lập trên cùng tệp | khớp tuyệt đối (lệch 0) | Test đối chiếu với `pandas` đếm trực tiếp |
| Tỉ lệ dựng thẻ thành công | số lần dựng thẻ không rơi vào nhánh lỗi / số lần mở tab | 100% khi dữ liệu đã nạp | Test gọi thẳng hàm dựng thẻ |

Ghi rõ giới hạn: đây là **SLO của một lần chạy xác nhận**, không phải cam kết vận hành liên tục. Đơn vị không có môi trường production nên không có error budget để tiêu.

## 2. Danh mục sự kiện

Tên sự kiện dùng dấu chấm, tiền tố `integration.`, để lọc được bằng một tiền tố duy nhất.

| Sự kiện | Mức | Trường kèm theo | Khi nào | Để trả lời câu hỏi |
|---|---|---|---|---|
| `integration.load.started` | INFO | `file`, `entity`, `attempt` | trước mỗi lần đọc | Đang nạp tệp nào, lần thử thứ mấy |
| `integration.load.retried` | WARNING | `file`, `attempt`, `error_code` | sau lần đọc lỗi đầu tiên | Lỗi đọc có phải tạm thời không |
| `integration.load.completed` | INFO | `entity`, `rows_in`, `rows_loaded`, `rows_dropped`, `drop_reasons`, `elapsed_ms` | nạp xong | Mất bao nhiêu bản ghi và vì sao (OB-U1-3) |
| `integration.load.failed` | ERROR | `file`, `error_code`, `field`, `column` | sau lần thử cuối | Trường/cột nào sai (OB-U1-2) |
| `integration.query.started` | INFO | `plan_id`, `template_id`, `source_sql` | trước khi chạy SQL | Câu truy vấn nào, kế hoạch nào, SQL nguồn để đối chiếu |
| `integration.query.completed` | INFO | `plan_id`, `row_count`, `elapsed_ms` | chạy xong | Truy vấn mất bao lâu, trả bao nhiêu dòng (OB-U1-1) |
| `integration.query.slow` | WARNING | `plan_id`, `elapsed_ms` | khi vượt 2.000 ms | Ngưỡng NFR1.2 có bị vượt |
| `integration.query.failed` | ERROR | `plan_id`, `error_code`, `message` | SQL lỗi | Lỗi gì; kết quả cũ có được giữ không |
| `integration.card.render_failed` | ERROR | `reason` | hàm dựng thẻ bắt được lỗi | Thẻ hỏng vì đâu (OB-U1-4) |
| `integration.log.no_pipeline_run` | WARNING | `log_path` | chưa có nhật ký pipeline | Vì sao sự kiện nằm ở tệp riêng |
| `integration.logs.pruned` | INFO | `kept`, `deleted` | cuối lần chạy pipeline, sau sự kiện `summary` | Đã giữ bao nhiêu tệp nhật ký, xoá bao nhiêu (Q3 = B) |
| `integration.logs.prune_failed` | WARNING | `reason` | khi không dọn được | Vì sao không dọn; lần chạy vẫn tiếp tục |

`drop_reasons` là dict đếm theo lý do (`trung_ma_don`, `ngay_dat_rong`, `trang_thai_ngoai_mien`) — chỉ đếm, không chứa giá trị bản ghi (`security-design.md` §4).

Bảng trên là **nguồn sự thật duy nhất** cho lược đồ nhật ký của đơn vị này — **mười hai** sự kiện `integration.*` (mười sự kiện gốc, cộng hai sự kiện dọn nhật ký do Q3 = B thêm ở bước sinh mã). `security-design.md` §4 thêm ba giới hạn trên nó (không ghi giá trị bản ghi; `source_sql` chỉ ở sự kiện `integration.query.started`; `error_code` là tập giá trị đóng gồm `file_not_found`, `permission_denied`, `decode_error`, `column_missing`, `identifier_invalid`, `sql_error`, `result_unreadable`, và giá trị lạ được ghi thành `unknown`). Tập đóng đó được khai **một lần** trong `src/common/logging.py` (`ERROR_CODES`, `normalise_error_code`).

## 3. Truy vết giữa các tầng

Một lần chạy truy vấn có thể truy ngược qua bốn mã, đều có mặt trong bản ghi hoặc trong kết quả trả về:

```
run_id (phiên dashboard) → plan_id (kế hoạch viết lại) → template_id (truy vấn mẫu) → NFR1.2 (ngưỡng)
```

`plan_id` sinh một lần cho mỗi lần chạy và được trả trong `QueryRunResult` (C4), nên thẻ hiển thị được nó nếu người dùng cần đối chiếu với nhật ký. Không có `trace_id` phân tán vì không có tiến trình thứ hai.

## 4. Vùng số liệu và khả năng tiếp cận (NFR4)

Vùng số liệu phải vừa truyền đạt trạng thái vừa dùng được bằng bàn phím. Bốn yêu cầu NFR4 được thực thi như sau:

| Mã | Cách thực thi trong thiết kế vùng |
|---|---|
| NFR4.1 | Mọi phần tử tương tác của vùng (nút "Chạy truy vấn", nút "Thử lại") là thành phần Dash lõi có thể nhận tiêu điểm (`html.Button`); không có `div` bấm được bằng chuột mà không nhận Tab |
| NFR4.2 | Viền tiêu điểm dùng token `focus` của `refined-mockups/design-system-mapping.md` (tương phản ≥ 3:1); không đặt `outline: none` ở bất kỳ đâu |
| NFR4.3 | Chữ thường tương phản ≥ 4,5:1 với nền; số liệu lớn ≥ 3:1. Cặp màu lấy từ bảng token, không tự pha |
| NFR4.4 | Mỗi trạng thái có **chữ + biểu tượng**, không chỉ màu: "Chưa chạy" và "Rỗng" (biểu tượng thông tin), "Đang tải" (biểu tượng vòng quay), "Đầy đủ" (dấu kiểm), "Một phần" (biểu tượng cảnh báo), "Lỗi" (biểu tượng lỗi) |

Sáu trạng thái của vùng (chưa chạy, đang tải, rỗng, đầy đủ, một phần, lỗi — `functional-spec.md`) là sáu đường mã riêng, mỗi đường có nhãn chữ riêng. Đây cũng là điều kiện của RL-U1-3 (rỗng khác 0) và BR1.8.

## 5. Vận hành nhật ký

- Mỗi bản ghi là một dòng JSON độc lập; một dòng hỏng không làm hỏng phần còn lại của tệp.
- Ghi bằng một lời gọi `write` trên tệp mở ở chế độ nối; không giữ tệp mở lâu, không đệm trong bộ nhớ.
- Không xoay vòng, không nén: mỗi lần chạy pipeline sinh tệp mới, tệp cũ nằm trong `logs/` (bị `.gitignore`).
- **Rủi ro đã biết:** hai tiến trình ghi nối cùng một tệp có thể chen dòng. Vì mỗi dòng dưới 500 byte và ghi bằng một lời gọi, khả năng chen là thấp; nếu quan sát thấy dòng hỏng, cách xử lý là bỏ dòng đó khi phân tích, **không** thêm khoá tệp vào đường nóng của dashboard. Điều kiện xem lại: nếu cần phân tích nhật ký tự động, tách tệp riêng cho dashboard và ghi lại quyết định.

## 6. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | `logs/` luôn tồn tại sau lần chạy pipeline đầu tiên | Giả định — có nhánh dự phòng tạo tệp riêng khi chưa có |
| A2 | Không ai đọc nhật ký bằng công cụ yêu cầu một dòng JSON hoàn chỉnh tuyệt đối | Đánh đổi đã ghi ở §5 |
| Q1 | Có cần ghi sự kiện khi người dùng **mở** tab (không chỉ khi thẻ dựng) để đo NFR1.1 ngoài test? | Không chặn — hiện không ghi, vì NFR1.1 được đo bằng test và hiển thị `elapsed_ms` của truy vấn đã đủ cho người dùng. Nếu muốn đo thật, thêm `integration.tab.opened` với `elapsed_ms` |
| Q2 | Nhãn "kết quả lần trước" có cần kèm giờ chính xác đến giây không? | Không chặn — thiết kế chọn có (giờ:phút:giây), vì người dùng cần biết số liệu cũ bao lâu |
