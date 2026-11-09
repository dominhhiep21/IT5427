# Reliability Design — u1-thin-slice

Nguồn: `nfr-requirements/` (`reliability-requirements.md`, `performance-requirements.md`, `security-requirements.md`, `scalability-requirements.md`, `observability-requirements.md`, `tech-stack-decisions.md`), `functional-design/functional-spec.md` (Workflow 1–3, bảng trạng thái của thẻ), `contract-design/contract-summary.md` (C4, C8, C9).

Đơn vị: `u1-thin-slice`. Mọi mẫu chịu lỗi trong `nfr-design-guide.md` đều giả định có lời gọi mạng hoặc dịch vụ ngoài; đơn vị này **không có** cả hai, nên phần lớn các mẫu đó bị loại một cách có lý do, và cái còn lại là cách xử lý lỗi đọc tệp, lỗi truy vấn, và cách giữ cho một thẻ hỏng không kéo cả dashboard xuống.

## 1. Mẫu chịu lỗi: dùng gì và loại gì

| Mẫu | Áp dụng? | Lý do |
|---|---|---|
| Retry với chờ tăng dần | **Có, một lần** | Tệp cục bộ có thể bị khoá tạm thời khi phần mềm khác đang quét đĩa. Một lần thử lại bắt được đúng trường hợp đó mà không kéo dài thời gian chờ của trường hợp lỗi vĩnh viễn (quyết định Q1 = A) |
| Circuit breaker | Không | Không có lời gọi ra ngoài; ngắt mạch một tệp cục bộ là vô nghĩa |
| Bulkhead (luồng riêng theo phụ thuộc) | Không | Một tiến trình, một người dùng (`scalability-design.md`) |
| Timeout | Không đặt cứng | Truy vấn cố định trên 99.441 dòng, chạy dưới 0,1 giây; một timeout cứng chỉ tạo thêm một đường thất bại giả. Thay bằng cảnh báo chậm (§3) |
| Rate limiter | Không | Không có lưu lượng từ ngoài |
| Fallback | **Có** | Kết quả truy vấn lần trước được giữ và ghi rõ "kết quả lần trước" (RL-U1-5) |
| Health check đầu-cuối | **Có, dạng lệnh** | `pytest -m "not slow"` → `python -m src.pipeline run --stage all` → mở dashboard (`team.md`), không phải endpoint HTTP |

## 2. Quyết định thiết kế

### ADR-U1-R1 — Thử lại một lần cho bước đọc, không thử lại cho bước kiểm lược đồ

**Quyết định:**

- Lần đọc thứ nhất lỗi (`OSError`, `PermissionError`, `UnicodeDecodeError`) → chờ 100 ms, thử lại **một** lần.
- Lần thứ hai lỗi → ném `SchemaError` nêu tên tệp và lý do, dừng nạp.
- Lỗi **kiểm lược đồ** (thiếu cột, thừa cột, tên cột không hợp lệ) → ném ngay, **không** thử lại: cùng một tệp, cùng một tiêu đề, thử lại chỉ lặp lại đúng lỗi đó.

**Hệ quả:** người dùng thấy lỗi trong khoảng 100 ms cộng thời gian đọc một lần, không phải chờ ba lần đọc. Trạng thái lỗi của thẻ nêu việc gì hỏng và có nút thử lại (Workflow 3, nhánh lỗi) — nút đó là lần thử mới của người dùng, không phải vòng lặp của mã.

```python
for attempt in (1, 2):
    try:
        frame = pd.read_csv(path, usecols=columns, dtype=str)
        break
    except (OSError, UnicodeDecodeError) as exc:
        if attempt == 2:
            raise SchemaError(f"không đọc được {path.name}: {exc}") from exc
        logger.warning("integration.load.retried", file=path.name, attempt=attempt)
        time.sleep(0.1)
```

**Điều không làm:** không thử lại ở tầng giao diện bằng cách gọi lại callback nhiều lần — mỗi lần gọi lại là một lần đọc 99.441 dòng, và người dùng không biết vì sao thẻ nhấp nháy.

### ADR-U1-R2 — Lỗi truy vấn không xoá kết quả đang xem

**Quyết định:** kết quả truy vấn thành công gần nhất được giữ trong **biến cấp tiến trình** của gói `src/integration/` (cùng chỗ với bộ nhớ đệm nạp ở ADR-U1-P1), không dùng `dcc.Store`. Lý do: vùng có **một** `Output` riêng, và trạng thái "kết quả lần trước" phải sống qua nhiều lần bấm; `dcc.Store` sẽ thêm một `Output` thứ hai cho cùng callback mà không mua được gì trong một tiến trình, một người dùng. Khi lần chạy mới lỗi, vùng **không** bị thay bằng trạng thái rỗng; nó giữ số liệu cũ, gắn nhãn "kết quả lần trước" kèm thời điểm và câu lỗi, và vẫn có nút thử lại.

**Hệ quả:** người dùng không mất số liệu vì một lần lỗi thoáng qua (RL-U1-5). Đánh đổi: có thể đang xem số liệu cũ mà tưởng là mới — vì vậy nhãn "kết quả lần trước" là **bắt buộc**, và test phải khẳng định nhãn này xuất hiện đúng lúc.

### ADR-U1-R3 — Cô lập lỗi ở mức thẻ

Ba mức hỏng và bán kính ảnh hưởng:

| Mức hỏng | Ảnh hưởng | Cách cô lập |
|---|---|---|
| Không nạp được dữ liệu | Chỉ thẻ "Đơn theo tháng" của tab mới | Thẻ hiện trạng thái lỗi; ba tab cũ vẫn dùng `warehouse/` và không bị ảnh hưởng vì chúng không đi qua đường nạp của đơn vị này |
| Truy vấn lỗi | Chỉ thẻ đang xem | Giữ kết quả cũ (ADR-U1-R2) |
| Một hàm dựng vùng ném lỗi không lường trước | Cả callback của vùng (các output khác trong cùng callback) | Callback của vùng là callback **riêng**, không gộp vào hai callback của ba tab báo cáo; lỗi được bắt ngay trong hàm dựng vùng và trả về cây trạng thái lỗi thay vì để Dash nhận exception |

Ghi chú cho bước sinh mã: callback của vùng **phải riêng**, không gộp vào hai callback của ba tab báo cáo, nếu không một lỗi ở vùng sẽ làm đỏ cả bốn tab. Vì vậy số callback trong test hình dạng dashboard tăng từ 7 lên **8** (NFR5.3).

### ADR-U1-R4 — Không có sao lưu, có thủ tục dựng lại

**Quyết định:** không có bản sao dữ liệu, không có failover. `dataset/` là nguồn bất biến, chỉ đọc; `data/`, `warehouse/`, `logs/` là sản phẩm sinh ra và bị `.gitignore`.

**Hệ quả:** "khôi phục" = xoá thư mục sinh ra và chạy lại pipeline (`team.md`, mục Deployment). Đơn vị này càng an toàn hơn vì nó **không ghi** vào `data/` hay `warehouse/`: hỏng đơn vị này không để lại dữ liệu nửa vời.

### ADR-U1-R5 — Chuỗi kích hoạt cố định: bấm "Chạy truy vấn" → nạp (nếu chưa có) → chạy truy vấn → dựng vùng

Vùng không tự chạy khi dashboard khởi động hay khi mở tab (trạng thái đầu là **chưa chạy**), và không phụ thuộc pipeline đã chạy trước đó hay chưa: `warehouse/` không nằm trên đường của đơn vị này (`logical-components.md` vùng hỏng D4).

Chuỗi kích hoạt, đúng thứ tự, khi người dùng bấm nút "Chạy truy vấn" của vùng `don-theo-thang`:

1. Đọc cache cấp tiến trình (`performance-design.md` ADR-U1-P1). Chưa có → nạp `don_hang`; có rồi → dùng lại.
2. Nạp lỗi → **dừng ở bước 2**, vùng hiện trạng thái **Lỗi** kèm câu nêu việc gì hỏng và nút thử lại.
3. Chạy truy vấn đếm đơn theo tháng trên bản đã nạp.
4. Truy vấn lỗi → vùng hiện **Lỗi** (hoặc "kết quả lần trước" nếu đã có kết quả — ADR-U1-R2).
5. Truy vấn xong nhưng chưa có dòng nào → trạng thái **Rỗng**, khác hoàn toàn với "0 đơn".
6. Có dòng → trạng thái **Đầy đủ** hoặc **Một phần** (theo độ đầy đủ 12 tháng), dựng thẻ.

Trạng thái **Rỗng** vì vậy có nghĩa là "truy vấn chạy được nhưng không có bản ghi nào trong dữ liệu nguồn", kèm một nút **Chạy truy vấn** — không phải lời hướng dẫn "chạy pipeline" (bản nháp trước sai ở chỗ này, vì tab mới không cần pipeline).

Hành vi nút thử lại:

| Lỗi đang hiện | Nút làm gì |
|---|---|
| Lỗi nạp (bước 2) | Nạp lại **rồi** chạy truy vấn |
| Lỗi truy vấn (bước 4) | Chỉ chạy lại truy vấn trên bản đã nạp |
| Rỗng | Chạy lại truy vấn (dữ liệu nguồn có thể vừa được thay) |

Nút là một `html.Button` nhận Tab, nhãn chữ cố định "Thử lại" / "Chạy truy vấn" (NFR4.1, NFR4.4).

## 3. Bảng tình huống hỏng

| Tình huống | Phát hiện | Hành vi | Phục hồi |
|---|---|---|---|
| Thiếu tệp CSV nguồn | `FileNotFoundError` ở lần đọc | Thử lại 1 lần, rồi `SchemaError` nêu tên tệp | Nút thử lại; kiểm `dataset/` |
| Tệp bị khoá bởi chương trình khác | `PermissionError` | Thử lại 1 lần sau 100 ms | Thường tự khỏi; nếu không, đóng chương trình đang giữ tệp |
| Thiếu cột nguồn | So tiêu đề CSV với ánh xạ trong lược đồ | `SchemaError` nêu **tên trường** và **tên cột** (functional-spec Workflow 1, lỗi) | Sửa ánh xạ hoặc tệp nguồn; không tự sửa |
| Tên cột/bảng không hợp lệ | `checked_identifier` (`security-design.md` ADR-U1-S2) | `SchemaError` trước khi mở DuckDB | Sửa tệp lược đồ |
| Bản ghi trùng mã đơn | Kiểm duy nhất sau khi dựng bản ghi | Loại bản ghi sau, đếm và ghi lý do; lô vẫn nạp tiếp (BR1.1, RL-U1-2) | Không cần — đã xử lý |
| Ngày đặt rỗng hoặc trạng thái ngoài tám giá trị | Kiểm miền giá trị | Loại, đếm, ghi lý do (BR1.2) | Không cần |
| Truy vấn không có điều kiện trạng thái | Kiểm kế hoạch viết lại (BR1.4) | Từ chối chạy, nêu lý do; không chạy SQL | Sửa mẫu truy vấn |
| SQL nguồn lỗi | DuckDB ném lỗi | `QueryExecutionError` nêu truy vấn và lỗi; giữ kết quả cũ (ADR-U1-R2) | Nút thử lại |
| Truy vấn chậm bất thường | `elapsed_ms` > 2000 | Vẫn trả kết quả, ghi `integration.query.slow` mức WARNING | Xem lại dữ liệu và truy vấn; không tự nâng ngưỡng |
| Không có dòng kết quả | `rows` rỗng sau khi chạy truy vấn | Trạng thái **rỗng** kèm nút "Chạy truy vấn", **không** hiện số 0 (BR1.7, RL-U1-3, ADR-U1-R5) | Bấm "Chạy truy vấn" |
| Chưa bấm "Chạy truy vấn" lần nào | Cache nạp trống, chưa có `QueryRunResult` | Vùng hiện trạng thái **Chưa chạy** kèm nút "Chạy truy vấn" (ADR-U1-R5) | Bấm "Chạy truy vấn" |
| Thiếu một phần tháng/trạng thái | Kiểm độ đầy đủ của 12 tháng | Nhãn "một phần" + nêu phần thiếu (BR1.8) | Không cần |

## 4. Bảo vệ các bảo đảm dữ liệu hiện có

NFR5.1–5.3 là ràng buộc cứng của đợt. Đơn vị này giữ được chúng vì:

- **Không ghi** vào `data/marts/`, `warehouse/`, `dataset/`: không có đường nào để 5 KPI lệch hay số dòng 11 view đổi (NFR5.1, NFR5.2).
- **Có** chạm hình dạng dashboard: thêm một tab, bốn `card_ids` theo C9, một vùng kết quả `don-theo-thang` và một callback riêng cho vùng. Vì vậy NFR5.3 buộc cập nhật **trong cùng thay đổi**: `tests/unit/test_dashboard_smoke.py` (4 tab, 8 callback, 4 thẻ + vùng) và `tests/integration/test_u3_end_to_end.py`. Đây là điều kiện của bước sinh mã, không phải việc của đơn vị sau.

### 4.1 Ngưỡng phủ, test riêng cho từng mô-đun, và lint

Ba yêu cầu chất lượng mã của đơn vị (`tech-stack-decisions.md` NFR2.1, NFR2.2, NFR3.1) được thực thi bằng đúng ba cổng, không thêm cơ chế mới:

| Mã | Cách giữ |
|---|---|
| NFR2.1 — phủ dòng ≥ 80% cho `src/` | Lệnh xác nhận đã ghi trong state của đơn vị: `.venv/Scripts/python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80`. Ngưỡng nằm trong lệnh, nên không ai hạ được ngầm; đơn vị này chỉ **thêm test**, không sửa lệnh |
| NFR2.2 — mỗi mô-đun mới có test riêng | Mỗi tệp mới trong `src/integration/` có một tệp `tests/unit/test_<tên>.py` tương ứng, kể cả tệp chỉ nối dây; đây là điều kiện của bước sinh mã |
| NFR3.1 — `ruff check` và `ruff format --check` sạch | Ghim `ruff` vào `requirements.txt` kèm lý do (TS-U1-3) và thêm cấu hình ở gốc repo; hai lệnh chạy cạnh bộ test nhanh trước khi coi là xong |

Ghi chú: test của đơn vị này **không** được phép nới ngưỡng phủ hay bỏ qua cổng để lấy xanh — nếu phần mới làm tụt phủ, viết thêm test chứ không hạ `--cov-fail-under`.

## 5. Kiểm chứng chịu lỗi

| Kiểm chứng | Cách làm |
|---|---|
| Thử lại đúng một lần | Test tiêm lỗi đọc ở lần 1, thành công ở lần 2 → nạp xong, có sự kiện `integration.load.retried` |
| Lỗi vĩnh viễn | Test tiêm lỗi cả hai lần → `SchemaError`, thông điệp nêu tên tệp, và **đúng hai** lần thử |
| Không thử lại lỗi lược đồ | Test thiếu cột → `SchemaError` ngay, không có sự kiện `retried` |
| Giữ kết quả cũ | Test: chạy thành công, rồi tiêm lỗi truy vấn → nhãn "kết quả lần trước" xuất hiện, số liệu cũ còn nguyên |
| Rỗng khác 0 | Test: kết quả rỗng → chuỗi trạng thái rỗng, **không** chứa "0" như một con số tổng |
| Lỗi thẻ không lan | Test: hàm dựng thẻ ném lỗi → callback trả cây trạng thái lỗi, không ném ra ngoài |
| `usecols` khớp lược đồ | Test: dựng danh sách cột đọc từ tệp lược đồ (chỉ trường có `loaded: true` **thuộc bảng khoá**) và khẳng định nó bằng đúng danh sách đó; thêm/bớt trường trong lược đồ mà quên đổi `usecols` là test đỏ |
| Trường chỉ kiểm, không đọc | Test: `bang_giao` được kiểm tiêu đề `customer_state` nhưng không xuất hiện trong dữ liệu đã nạp (không có giá trị nào của nó trong `LoadResult`) |
| Mã lỗi đóng | Test: mọi `error_code` ghi ra nhật ký thuộc tập bảy giá trị đã khai; giá trị lạ bị thay bằng `unknown` |

## 6. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Chờ 100 ms là đủ để một khoá tệp tạm thời trên Windows nhả ra | Giả định — nếu thực tế khoá lâu hơn, người dùng vẫn có nút thử lại; không tăng số lần thử |
| A2 | Không có tiến trình nào khác ghi vào `logs/` cùng lúc | Giả định — xem `observability-design.md` §5 về việc ghi nối vào tệp nhật ký gần nhất |

Không còn câu hỏi mở: hành vi nút thử lại đã chốt ở ADR-U1-R5, và chuỗi kích hoạt cũng vậy.
