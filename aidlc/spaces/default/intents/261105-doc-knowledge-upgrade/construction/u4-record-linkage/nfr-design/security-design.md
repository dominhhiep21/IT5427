# Security Design — u4-record-linkage

Nguồn: `nfr-requirements/security-requirements.md` (SR-U4-1..8), `nfr-requirements/tech-stack-decisions.md` (TS-U4-1..7, NFR1.1–NFR6.1), `functional-design/functional-spec.md`, `inception/contract-design/contract-summary.md` (C5).

Đơn vị: `u4-record-linkage`. Bề mặt tấn công bằng không (không cổng, không đầu vào người dùng), nhưng đầu ra là **một artefact gần định danh** — cặp mã khách kèm cờ "cùng một người". Thiết kế dưới đây nói đúng điều đó.

## 1. Mô hình mối đe doạ

| Tài sản | Mối đe doạ | Khả năng | Tác động | Kiểm soát |
|---|---|---|---|---|
| Tệp `linkage-<entity>.json` | Người khác trên máy đọc được và biết hai `customer_id` là cùng một người | Trung bình — tệp nằm trong `data/`, không mã hoá | Tiết lộ quan hệ giữa hai mã khách của một bộ dữ liệu công khai | Đây là **mục đích** của đơn vị (SR-U4-8); giảm thiểu bằng cách không kèm khoá mốc và không kèm giá trị bản ghi |
| Nhật ký `logs/*.jsonl` | Ghi kèm mã khách hoặc tên thành phố | Thấp nếu danh mục sự kiện được giữ | Rò rỉ dữ liệu gần định danh vào tệp dễ bị đọc hơn | Danh mục sự kiện ở `security-requirements.md` §3 chỉ có số đếm và tên đối tượng |
| `dataset/` | Bị ghi đè | Thấp | Mất dữ liệu gốc | Chỉ `pd.read_csv`; không có đường ghi (SR-U4-7) |
| Mã nguồn | Đầu vào người dùng dựng thành ngưỡng/đường dẫn | Không — không có giao diện | — | Ngưỡng, trọng số, trần cặp là hằng số (SR-U4-3) |

## 2. Quyết định thiết kế

### ADR-U4-S1 — Tệp kết quả chỉ mang `customer_id`, không mang `customer_unique_id`

**Quyết định:** khoá mốc chỉ tồn tại trong bộ nhớ, dùng để tính `is_correct` và `correct_rate`; tệp chỉ chứa `customer_id`, điểm, các tỉ lệ bằng chứng và **cờ boolean** `is_correct`.

**Hệ quả:** người đọc tệp biết "hai mã này cùng một người" nhưng **không** biết nhóm người thật gồm những ai, và không thể nối hai nhóm với nhau. Test bắt buộc: đọc tệp kết quả, khẳng định không chuỗi nào trùng một `customer_unique_id` đã biết trong fixture.

### ADR-U4-S2 — Nhật ký là nơi dễ rò rỉ nhất, nên danh mục sự kiện đóng

**Quyết định:** ba sự kiện `integration.linkage.*` chỉ mang `target_entity`, số đếm, `elapsed_ms`, cờ cắt và `error_code`; mọi trường khác bị cấm. `error_code` chuẩn hoá qua `normalise_error_code` sẵn có.

**Hệ quả:** khi cần chẩn đoán một cặp cụ thể, phải chạy lại ở môi trường phát triển với log tạm — không thêm trường vào nhật ký thường.

### ADR-U4-S3 — `is_correct` là tiết lộ có chủ đích, và mức tiết lộ phải nói đúng

**Quyết định:** giữ `is_correct` vì C5 yêu cầu và vì AC3.2.3 cần cỡ mẫu. Nói đúng mức tiết lộ: mỗi cặp "Ghép" mang nhãn `is_correct`, nên **gom các cặp `true` bằng union-find là dựng lại được chính các nhóm người thật**. Việc bỏ `customer_unique_id` khỏi tệp chỉ giấu *tên* của nhóm, không giấu *phân hoạch*. Đây là giới hạn thật của hợp đồng C5, không phải điều có thể vá bằng cách đặt tên trường khác.

**Hệ quả:** biện pháp duy nhất còn lại là kiểm soát nơi tệp tồn tại (chỉ trên máy local, `data/` bị `.gitignore`). Nếu C5 đổi được, phương án giảm tiết lộ là bỏ `is_correct` khỏi tệp và chỉ giữ `correct_rate` + cỡ mẫu — khi đó AC3.2.3 vẫn đọc được con số tổng hợp mà không có nhãn từng cặp. Ghi thành câu hỏi mở ở §5, không tự đổi hợp đồng.

**Hệ quả:** nếu đợt sau mở dữ liệu cho người ngoài xem, đây là chỗ phải xem lại trước — ghi ở §4.

### ADR-U4-S4 — Không có xác thực và không cần

**Quyết định:** không thêm đăng nhập, token hay khoá cho đơn vị chạy trong pipeline.

**Hệ quả:** bảo vệ duy nhất là quyền truy cập thư mục của hệ điều hành; chấp nhận, vì đơn vị không phục vụ mạng.

## 3. Kiểm chứng

| Kiểm chứng | Cách làm |
|---|---|
| Không có khoá mốc trong tệp | Test đọc `data/integration/linkage-customer.json` (fixture) và khẳng định không chuỗi nào bằng `customer_unique_id` đã biết |
| Nhật ký không có giá trị bản ghi | Test chạy một lần với fixture, đọc tệp log, khẳng định không sự kiện nào chứa `customer_id`, mã bưu chính hoặc tên thành phố |
| Không ghi vào `dataset/` | `git status dataset/` trống sau lần chạy thử |
| `error_code` thuộc tập đóng | Test khẳng định mọi `error_code` ghi ra nằm trong `ERROR_CODES` hoặc bằng `unknown` |
| Không có lời gọi mạng | Rà mã: `src/linkage/` không import `urllib`, `http`, `requests`, `socket` |

## 4. Rủi ro đã biết

- Tệp cặp + địa chỉ gần đúng thu hẹp một người tới một khu vực. Chấp nhận: Olist công khai đã ẩn danh, tệp không rời máy.
- `payment_similarity` cho phép suy ra hành vi mua. Chấp nhận cùng lý do.
- `is_correct` là tiết lộ có chủ đích (ADR-U4-S3).
- Nếu tệp bị chép ra ngoài máy, không có cơ chế nào thu hồi — không có mã hoá vì không có bí mật để quản lý.
