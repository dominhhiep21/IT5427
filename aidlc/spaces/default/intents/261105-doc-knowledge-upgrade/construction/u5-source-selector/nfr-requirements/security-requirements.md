# Security Requirements — u5-source-selector

Nguồn: `functional-design/functional-spec.md` (W1–W4, máy trạng thái), `functional-design/rules.md` (BR5.1–BR5.11), `functional-design/entities.md` (bề mặt lỗi), `inception/requirements-analysis/requirements.md` (NFR2, NFR3, NFR6; ràng buộc C1–C6; OS5 loại đăng nhập/phân quyền), `inception/contract-design/contract-summary.md` (C2, C3, C7), và `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`.

Đơn vị này là **thư viện thuần trong tiến trình**: không mở cổng, không xác thực, không nhận dữ liệu người dùng từ giao diện. Nhưng nó không "không có gì để bảo vệ": nó là chỗ **duy nhất** biến chữ trong một tệp cấu hình do người sửa tay thành tên nguồn, tên bảng và mã trường — rồi trả những dữ kiện đó cho U3 (để dựng SQL) và U6 (để hiển thị). Ba rủi ro thật của đơn vị là: một tên nguồn lạ đi lọt, một mã trường không có thật đi vào kết quả chọn nguồn, và một nguồn mô phỏng bị coi là nguồn thật.

## 1. Yêu cầu dẫn xuất

| Mã | Yêu cầu | Cách đáp ứng | Đo bằng |
|---|---|---|---|
| SR-U5-1 | Không có xác thực, không mở cổng mạng | Thư viện chỉ chạy trong tiến trình pipeline/dashboard; không bind cổng, không phục vụ HTTP | Rà mã `src/integration/selector.py`: không `socket`, không `http`, không `run_server` |
| SR-U5-2 | Không thêm bí mật, không đọc biến môi trường | Không API key, không token; đường dẫn tệp cấu hình lấy từ `AppConfig`/hằng của gói, không từ lời gọi bên ngoài | Rà `os.environ` trong mã mới: không có |
| SR-U5-3 | **Nguồn mô phỏng không được phát sinh lệnh gọi mạng** | BR5.7: `has_data` và `latency_ms` là dữ kiện khai báo, không phải kết quả gọi thử; mã không import thư viện mạng | Grep `src/integration/selector.py`: không `urllib`, `requests`, `socket`, `httpx` |
| SR-U5-4 | **Tên nguồn nằm trong tập kín ba giá trị** | BR5.2: chỉ `olist_csv`, `ibge_cache`, `partner_simulated`; tên lạ ném `SchemaError`, không bị bỏ qua | Test: tên nguồn thứ tư → `SchemaError` nêu tên |
| SR-U5-5 | **Mã trường phải có thật trong C2** | BR5.3: mọi mã trong `covered_fields` và trong ánh xạ truy vấn → trường phải có trong `MediatedFieldCatalogue`; mã lạ ném `SchemaError` | Test: mã `don_hang.khong_ton_tai` → `SchemaError` nêu mã và nguồn |
| SR-U5-6 | **Nguồn mô phỏng không bao giờ được trả như nguồn thật** | BR5.11: `selected_sources` không bao giờ chứa nguồn `is_simulated = true`; vi phạm là `SchemaError` | Test: đặt `partner_simulated` rẻ nhất và đủ trường → vẫn bị loại, `rejected_sources` có lý do "nguồn mô phỏng" |
| SR-U5-7 | Lý do chọn/loại không chở dữ liệu nhạy cảm | BR5.5/BR5.8: `reason` chỉ chứa tên nguồn, mã trường và câu diễn giải; không chứa giá trị ô của CSV, không chứa mã khách/người bán | Rà mẫu lý do trong test: chỉ có tên nguồn và mã trường |
| SR-U5-8 | Không chèn HTML/markup vào chuỗi trả cho giao diện | `coverage` và `reason` là chữ thuần; U6 chịu trách nhiệm escape khi render | Test: chuỗi dựng ra không chứa `<`, `>`; rà `selector.py` không dựng thẻ HTML |
| SR-U5-9 | `dataset/` chỉ đọc, và đơn vị không đọc dữ liệu ô nào | W1 chỉ đọc tệp cấu hình và C2; không mở CSV nguồn | Rà mã: không `read_csv`, không `open` trên `dataset/` |
| SR-U5-10 | Không thêm gói phụ thuộc | Chỉ `PyYAML 6.0.2` (đã ghim) + thư viện chuẩn (`dataclasses`, `pathlib`) | `requirements.txt` không đổi (`tech-stack-decisions.md` TS-U5-5) |
| SR-U5-11 | Thiếu tệp hoặc cấu hình sai là lỗi nêu rõ, không đoán | Ánh xạ lỗi duy nhất ở bảng §1.1; không nhánh nào tự sửa hay tự bỏ qua | Test cho từng nhánh trong bảng §1.1 |
| SR-U5-12 | Kết quả chọn nguồn phải tất định giữa các lần chạy | BR5.4: xếp hạng theo chi phí → độ trễ → tên nguồn, không phụ thuộc thứ tự khai báo hay thứ tự dict | Test: đảo thứ tự khai báo trong tệp cấu hình, kết quả chọn không đổi |
| SR-U5-13 | Đọc YAML bằng `yaml.safe_load`, không bao giờ `yaml.load` trần | Cùng mẫu `src/config.py` và `src/integration/schema.py`; `safe_load` không dựng đối tượng tuỳ ý nên một tệp cấu hình bị sửa xấu không chạy được mã | Grep `src/integration/selector.py`: chỉ `safe_load`; không `Loader`, không `full_load` |
| SR-U5-15 | **Kiểm kiểu từng khoá hồ sơ trước khi dùng** | `has_data`/`is_simulated` phải là `bool` thật, `cost_level` phải là `int` trong 1..5 (không phải `bool`), `latency_ms` phải là `int >= 0`, `covered_fields`/`tables` phải là danh sách chuỗi; sai kiểu hoặc ngoài miền → `ConfigurationError` nêu khoá | Test: `has_data: "false"`, `latency_ms: "800"`, `latency_ms: -1` đều ném `ConfigurationError`, không lọt vào vị từ ứng viên và không gây `TypeError` |
| SR-U5-16 | Mọi lỗi mang `error_code` thuộc tập đóng `ERROR_CODES` | Ánh xạ ở §1.2; không thêm mã mới trong đợt này | Rà mã: mọi lần ghi log lỗi đi qua `normalise_error_code`; test khẳng định mã của từng nhánh |
| SR-U5-14 | **Tên bảng trong `tables` phải thuộc danh sách bảng nguồn của dự án** | So từng phần tử với `SOURCE_TABLES` của `src/integration/schema.py` — tập chín **tên tệp đã bỏ `.csv`** (`olist_orders_dataset`, …), đúng dạng tên đi trong `tables`. Không so với khoá logic của `TABLE_SPECS` (`orders`, `customers`, …) vì hai dạng tên khác nhau. Đây là kiểm **tên**, không phải kiểm quan hệ trường ↔ bảng — quan hệ đó cần C1 và không thuộc U5 (`entities.md`) | Test: `tables: [olist_khong_ton_tai]` → `SchemaError` nêu tên bảng; `tables: [olist_orders_dataset]` → qua |

### §1.1 Ánh xạ lỗi duy nhất

| Nhánh | Lỗi | Thông điệp |
|---|---|---|
| Tệp cấu hình không có mặt | `ConfigurationError` | nêu **nhãn tương đối cố định** `config/integration-sources.yaml` (không tính từ `Path.cwd()`; nhãn này là hằng của gói, nên kết quả không phụ thuộc máy chạy) |
| Khoá hồ sơ sai kiểu (SR-U5-15) | `ConfigurationError` | nêu tên nguồn, tên khoá và kiểu mong đợi |
| Hồ sơ nguồn thiếu khoá bắt buộc, hoặc `cost_level` ngoài 1..5, hoặc `tables` rỗng mà `covered_fields` khác rỗng | `ConfigurationError` | nêu tên nguồn và tên khoá sai |
| `source_name` ngoài tập ba tên, `source_name` trùng | `SchemaError` | nêu tên nguồn |
| Hồ sơ có số nguồn mô phỏng khác 1 (không đúng "đúng một nguồn mô phỏng") | `SchemaError` | nêu danh sách nguồn mô phỏng đếm được |
| Mã trường không có trong C2 | `SchemaError` | nêu mã trường và tên nguồn |
| Ánh xạ truy vấn thiếu hoặc thừa `query_id` so với đúng ba truy vấn mẫu của FR2.1 | `SchemaError` | nêu các `query_id` thừa/thiếu |
| Tên bảng trong `tables` không thuộc `SOURCE_TABLES` | `SchemaError` | nêu tên bảng và tên nguồn |
| C2 ném `SchemaError` hoặc `ConfigurationError` | lan truyền nguyên vẹn | thêm ngữ cảnh "khi dựng bảng nguồn" |
| Không nguồn nào đủ trường | `NoSourceAvailableError`, mang **hai** thuộc tính: `missing_fields` (hợp các trường không nguồn nào phủ) và `catalogue` (bản C7 đã cập nhật) | nêu `missing_fields` và nguồn gần nhất thiếu gì |

### §1.2 Ánh xạ `error_code` (tập đóng `ERROR_CODES` của `src/common/logging.py`)

| Nhánh | `error_code` |
|---|---|
| Tệp cấu hình không có mặt | `file_not_found` |
| Hồ sơ sai kiểu, `cost_level` ngoài 1..5, `tables` rỗng mà có trường | `unknown` (không thêm mã mới trong đợt này) |
| `source_name` lạ/trùng, mã trường lạ, tên bảng lạ, ánh xạ truy vấn sai, số nguồn mô phỏng khác 1 | `identifier_invalid` |
| Lỗi của C2 lan truyền | giữ nguyên `error_code` của C2 |
| Không nguồn nào đủ trường | `unknown` (không phải lỗi cấu hình; U6 hiển thị `missing_fields`) |

## 1.3 Chỉ tiêu NFR mà các yêu cầu trên bảo vệ

Bảng này chỉ liệt kê **những chỉ tiêu thật sự có yêu cầu bảo vệ**. Chỉ tiêu không có dòng ở đây thì **không** được SR nào bảo vệ — chúng dựa vào lệnh chạy tay và CI, không phải vào mã của đơn vị; nói khác đi là che giấu chỗ trống.

| Mã | Chỉ tiêu | Yêu cầu bảo vệ |
|---|---|---|
| NFR1.1 | ≤ 2 giây cho một lần nạp và một lần đề xuất nguồn | SR-U5-1, SR-U5-12 |
| NFR5.1 | Pipeline xanh, 5 KPI lệch 0 | SR-U5-6, SR-U5-9 |
| NFR5.2 | 11 view tồn tại và số dòng 9 bảng mart không đổi | SR-U5-9 |
| NFR6.1 | Không lời gọi mạng | SR-U5-3 |
| NFR6.2 | Chạy UTF-8 | SR-U5-10, SR-U5-13 |

**Không có SR bảo vệ, và không nên giả vờ là có:** NFR2.1 (phủ ≥ 80%), NFR2.2 (test riêng mỗi mô-đun), NFR3.1 (ruff sạch). Ba chỉ tiêu này là cổng vận hành — chạy tay trước khi phát hành, hoặc trong CI — chứ không phải hành vi mà một yêu cầu bảo mật nào đó cưỡng chế.

## 1.4 Không áp dụng cho đơn vị này

- **Mã hoá dữ liệu khi lưu và khi truyền**: đơn vị không lưu và không truyền gì ra ngoài tiến trình; dữ liệu nguồn nằm trong `dataset/` và đã có chủ sở hữu khác.
- **Tuân thủ dữ liệu cá nhân (PII)**: đơn vị không đọc giá trị ô nào (SR-U5-9), nên không có dữ liệu cá nhân nào đi qua nó; mã khách/người bán không xuất hiện trong bất kỳ chuỗi nào nó sinh ra (SR-U5-7).

## 2. Mối đe doạ đã cân nhắc

| Mối đe doạ | Đánh giá | Kiểm soát |
|---|---|---|
| Tên nguồn hoặc tên bảng lạ bị chèn vào SQL mà U3 dựng | Có thật — `tables` đi thẳng vào C3 | Tên nguồn tập kín (SR-U5-4) và **tên bảng đối chiếu `SOURCE_TABLES`** (SR-U5-14): một bảng lạ không ra khỏi U5. Đây là kiểm soát thật ở phía U5, không phải câu chuyển trách nhiệm |
| Tệp cấu hình bị sửa để dựng đối tượng tuỳ ý khi nạp | Có thật với `yaml.load`; **không** với `safe_load` | SR-U5-13 |
| Mã trường không có thật làm U3 đọc sai trường | Có thật | SR-U5-5: đối chiếu C2 |
| Nguồn mô phỏng được trả như nguồn thật, kết quả không khớp `src/analytics` | Có thật — đây là lý do BR5.11 tồn tại | SR-U5-6 |
| Lý do loại để lộ dữ liệu khách hàng | Thấp — đơn vị không đọc dữ liệu ô nào | SR-U5-7, SR-U5-9 |
| Nguồn mô phỏng âm thầm gọi mạng khi nạp | Thấp — không có mã mạng | SR-U5-3 |
| Tấn công chuỗi cung ứng | Thấp — 8 gói đã ghim, không thêm gói | SR-U5-10 |
| Người trên cùng máy sửa tệp cấu hình để đổi chi phí/độ trễ | Chấp nhận được — máy local, tệp trong repo, thay đổi đi qua git | Không có kiểm soát thêm; ghi ở §4 |
| Đường dẫn tệp do giao diện truyền vào (path traversal) | Không có bề mặt: U5 không nhận đường dẫn từ UI | SR-U5-2 |

## 3. Nhật ký

Đơn vị kiểu `library` không có `observability-design.md` riêng. Theo quy ước gói đang dùng (`query.py`, `load.py`, `card.py`), mọi hàm của U5 nhận `logger` tuỳ chọn với mặc định `NullLogger`; không truyền logger thì không có dòng log nào. Khi có logger, U5 phát đúng bốn sự kiện:

| Sự kiện | Mức | Trường | Khi nào |
|---|---|---|---|
| `integration.sources.loaded` | INFO | `source_count`, `query_count`, `simulated_count` | sau khi nạp và kiểm bộ hồ sơ thành công |
| `integration.sources.partial` | WARNING | `pending_query_id`, `partial_reason` | khi danh mục trả nhánh "một phần" (BR5.9) |
| `integration.sources.selected` | INFO | `query_id`, `source_name`, `rejected_count` | sau mỗi lần đề xuất nguồn |
| `integration.sources.failed` | ERROR | `error_code`, `message` | khi ném `SchemaError`, `ConfigurationError` hoặc `NoSourceAvailableError` |

Chỉ ghi tên nguồn, mã truy vấn, mã trường, số đếm và thông điệp lỗi có cấu trúc. Không ghi giá trị ô dữ liệu, không ghi nội dung thô của tệp cấu hình, không ghi đường dẫn tuyệt đối ngoài repo.

## 4. Rủi ro đã biết

- **Không có đăng nhập và không có phân quyền** (OS5 ngoài phạm vi). Ai chạy được lệnh Python trên máy này đều đọc và sửa được tệp cấu hình; đó là thiết kế đã chốt.
- **`tables` được kiểm tên nhưng không kiểm quan hệ với trường**: SR-U5-14 đối chiếu từng tên bảng với `SOURCE_TABLES` (chín bảng nguồn của dự án), nên một tên bảng lạ không đi qua được. Việc đối chiếu "trường này thuộc bảng nào" cần C1, mà C1 không nằm trong hợp đồng của U5, nên phần đó vẫn là trách nhiệm của U3 khi dựng SQL.
- **Chi phí và độ trễ là ước tính khai báo**, không đo thật. Chúng phục vụ minh hoạ luật chọn nguồn; con số thật của nguồn Olist chỉ có ở U3 khi chạy truy vấn.
- **NFR4 (tiếp cận) không áp dụng cho đơn vị này** vì nó không hiển thị gì; yêu cầu WCAG 2.1 AA thuộc `u6-integration-ui`.
