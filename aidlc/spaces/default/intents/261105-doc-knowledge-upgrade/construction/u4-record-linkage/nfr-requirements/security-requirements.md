# Security Requirements — u4-record-linkage

Nguồn: `functional-design/functional-spec.md`, `functional-design/rules.md` (BR4.1–BR4.10), `inception/requirements-analysis/requirements.md` (NFR5, NFR6), `inception/contract-design/contract-summary.md` (C5).

Không có dữ liệu cá nhân thật và không có yêu cầu quy định (đã chốt ở Feasibility), nhưng đơn vị này **sinh ra một artefact gần định danh**: cặp `customer_id` kèm điểm và cờ đúng. Phần dưới nói đúng điều đó thay vì nói "không có gì để bảo vệ".

## 1. Yêu cầu dẫn xuất

| Mã | Yêu cầu | Cách đáp ứng | Đo bằng |
|---|---|---|---|
| SR-U4-1 | Không có xác thực, không mở cổng mạng | Đơn vị chỉ chạy trong tiến trình pipeline; không bind cổng, không phục vụ HTTP | Grep mã: không `socket`, không `http`, không `run_server` |
| SR-U4-2 | Không thêm bí mật, không đọc biến môi trường | Không API key, không token; nguồn là CSV cục bộ | Rà `os.environ` trong mã mới: không có |
| SR-U4-3 | Không có đầu vào người dùng dựng thành truy vấn hay đường dẫn | Ngưỡng, trọng số, độ dài khoá chặn, trần cặp là hằng số trong mã; đường dẫn lấy từ `AppConfig` | Rà chữ ký hàm: không tham số tự do từ giao diện |
| SR-U4-4 | Kết quả chỉ nằm trong `data/integration/` | Ghi qua `AtomicWriter.write_json`; `data/` đã bị `.gitignore`; không gửi lên mạng | Đường dẫn ghi là hằng số từ `AppConfig` |
| SR-U4-5 | Nhật ký không chứa giá trị bản ghi, trừ `message` của sự kiện lỗi | Sự kiện chỉ mang số đếm, tên đối tượng, `elapsed_ms`, cờ cắt — **không** ghi `customer_id`, `customer_unique_id`, tên thành phố, mã bưu chính. **Ngoại lệ đã biết:** `integration.linkage.failed` ghi `message=str(exc)[:200]`, và một số thông điệp lỗi có nhúng mã bản ghi (`src/linkage/models.py`), nên mã khách có thể lọt vào log của sự kiện lỗi | Rà danh mục sự kiện ở §3; nếu cần chặt hơn, che `record_a`/`record_b` trước khi ghi `message` |
| SR-U4-6 | `customer_unique_id` không xuất hiện ở bất kỳ đầu ra nào | Mỗi cặp trong tệp ghi đúng mười một khoá: `pair_id`, `target_entity`, `record_a`, `record_b`, `score`, `geo_ratio`, `order_ratio`, `payment_similarity`, `zip_prefix`, `decision`, `is_correct`. `record_a`/`record_b` **là** `customer_id` (hoặc `seller_id`) — không có khoá mốc nào. `is_correct` kiểu `bool` hoặc `None`: `None` với người bán, `False` khi thiếu khoá mốc. Khoá mốc chỉ dùng trong bộ nhớ để tính `is_correct` và `correct_rate` | Test đọc tệp kết quả, khẳng định không chuỗi nào bằng một `customer_unique_id` đã biết và không có khoá lạ ngoài danh sách trên |
| SR-U4-7 | Đọc nguồn ở chế độ chỉ đọc | Chỉ `read_csv` trên `dataset/`; không `to_csv`, không ghi vào `dataset/` | `git status dataset/` trống sau khi chạy |
| SR-U4-8 | `is_correct` là một tiết lộ có chủ đích, phải được khai | C5 yêu cầu trường này; `true` nói thẳng hai `customer_id` là cùng một người. Đây là **mục đích** của đơn vị, không phải sơ suất — nhưng nó phải nằm trong rủi ro đã biết (§3), không được mô tả là "không tiết lộ gì" | Rà tài liệu: §3 nêu rõ |

## 2. Mối đe doạ đã cân nhắc

| Mối đe doạ | Đánh giá | Kiểm soát |
|---|---|---|
| Tệp kết quả bị người khác trên cùng máy đọc | Chấp nhận được — máy local, dữ liệu Olist công khai | SR-U4-4 |
| Tệp kết quả tiết lộ hai mã khách là cùng một người | **Đúng, và là mục đích của đơn vị** | SR-U4-8: khai minh bạch; không thêm cột khoá mốc (SR-U4-6) |
| Đầu độc dữ liệu nguồn để làm sai kết quả ghép | Thấp — `dataset/` chỉ đọc | Kiểm cột nguồn trước khi dùng (`SchemaError`), kiểm sau khi ghi |
| Tấn công chuỗi cung ứng | Thấp — chỉ thư viện chuẩn + pandas đã ghim | Không thêm gói (`tech-stack-decisions.md` TS-U4-7) |
| Ghép sai làm sai số liệu chất lượng | Có thật; đây là lý do đổi hướng ngày 2026-11-06 | `correct_rate` kèm cỡ mẫu (BR4.8); không tuyên bố tỉ lệ trước khi đo |

## 3. Nhật ký (danh mục sự kiện của đơn vị này)

Đơn vị không có `observability-design.md` riêng (stage đó không chạy cho đơn vị kiểu `library`), nên danh mục sự kiện được chốt ở đây và là nguồn sự thật cho bước sinh mã.

| Sự kiện | Mức | Trường | Khi nào |
|---|---|---|---|
| `integration.linkage.started` | INFO | `target_entity` | trước khi chặn |
| `integration.linkage.completed` | INFO | `target_entity`, `pairs_scored`, `pairs_matched`, `pairs_review`, `pairs_skipped`, `pairs_truncated`, `elapsed_ms` | sau khi ghi tệp và kiểm xong |
| `integration.linkage.failed` | ERROR | `target_entity`, `error_code`, `message` | đối tượng đó lỗi; đối tượng kia vẫn chạy |

`error_code` dùng tập đóng đã có trong `src/common/logging.py` (`ERROR_CODES`, `normalise_error_code`); giá trị lạ thành `unknown`. Không trường nào trong bảng trên mang giá trị bản ghi (SR-U4-5).

## 4. Rủi ro đã biết

- `zip_prefix` (5 chữ số) là dữ liệu gần định danh ở Brazil, và tệp cặp thu hẹp một người tới một khu vực nhỏ. Chấp nhận: Olist là bộ công khai đã ẩn danh, tệp không rời máy. (Không có tên thành phố trong tệp — chỉ có tiền tố mã bưu chính.)
- `payment_similarity` và `score` cho phép suy ra hành vi mua của một `customer_id`. Cùng lý do trên; nếu đợt sau mở dữ liệu cho người khác xem, đây là chỗ phải xem lại trước.
- `is_correct` tiết lộ quan hệ "cùng một người" (SR-U4-8). Đây là chủ đích; điều không được phép là tiết lộ thêm khoá mốc.

## 5. Ghi chú sau khi C8/C9 đổi (2026-11-09)

Hai hợp đồng của U1 vừa đổi: **C8** chốt hình dạng tệp lược đồ (danh sách bản ghi, có `source_column`/`data_type`/`loaded`) và **C9** thêm `result_region_ids` cho vùng kết quả trong tab. Đơn vị này **không bị ảnh hưởng**:

- U4 không đọc tệp lược đồ và không dựng giao diện; nó chỉ đọc `dataset/` và ghi `data/integration/linkage-<customer|seller>.json` theo C5.
- C5 không đổi. Mọi yêu cầu trong tài liệu này vẫn áp nguyên.
- Kiểm lại: `sensor-traceability` vẫn PASS; không mã nào của U4 trỏ tới C8/C9.

