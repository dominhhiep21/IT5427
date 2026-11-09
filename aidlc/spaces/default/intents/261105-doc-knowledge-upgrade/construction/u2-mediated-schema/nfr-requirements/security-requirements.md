# Security Requirements — u2-mediated-schema

Nguồn: `functional-design/functional-spec.md` (Workflow 1–4, A1–A2, Q1–Q2), `functional-design/rules.md`
(BR2.1–BR2.9), `inception/requirements-analysis/requirements.md` (NFR4, NFR5, NFR6; ràng buộc C1–C7;
OS5 loại đăng nhập/phân quyền khỏi phạm vi), `inception/contract-design/contract-summary.md` (C1, C2, C6,
C8), và `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md` (PyYAML 6.0.2).

Đơn vị này là **thư viện thuần trong tiến trình**: không mở cổng, không xác thực, không nhận dữ liệu
người dùng từ giao diện. Nhưng nó không "không có gì để bảo vệ": nó là chỗ **duy nhất** biến chữ trong
một tệp YAML do người sửa tay thành tên bảng, tên cột và tên trường mà U3 sẽ dùng để dựng SQL. Vì vậy
kiểm tra đầu vào ở đây chính là kiểm soát an toàn của đơn vị, và phần dưới nói đúng điều đó.

Hai kiểu lỗi của đơn vị (`SchemaError` cho nội dung khai báo sai, `ConfigurationError` cho tệp thiếu)
nay là một phần của hợp đồng dùng chung: C1, C2 và C6 trong
`inception/contract-design/contract-summary.md` đã được cập nhật **cộng thêm** ngày 2026-11-07, cùng
`elapsed_ms` và `partial` trong giá trị trả về (SR-U2-11). Nhờ vậy consumer không phải đoán, và quyết
định Q3 = A không còn nằm ngoài hợp đồng.

## 1. Yêu cầu dẫn xuất

| Mã | Yêu cầu | Cách đáp ứng | Đo bằng |
|---|---|---|---|
| SR-U2-1 | Không có xác thực, không mở cổng mạng | Thư viện chỉ chạy trong tiến trình pipeline/dashboard; không bind cổng, không phục vụ HTTP | Rà mã: không `socket`, không `http`, không `run_server` trong `src/integration/` |
| SR-U2-2 | Không thêm bí mật, không đọc biến môi trường | Không API key, không token; đường dẫn tệp lấy từ `AppConfig`, không từ lời gọi bên ngoài | Rà `os.environ` trong mã mới: không có |
| SR-U2-3 | **Chỉ định danh nằm trong tập cho phép mới được đi tiếp** | BR2.3: mỗi tên khớp `^[a-z][a-z0-9_]*$`, ≤ 64 ký tự; tên bảng/cột phải có trong `TABLE_SPECS` và tiêu đề thật của tệp nguồn (BR2.2). Đây là hàng rào chống việc một tệp YAML bị sửa xấu đưa ký tự lạ vào SQL mà U3 dựng | Test: mỗi mẫu tên sai (`"Orders";DROP`, `don hang`, `A_B`, tên 65 ký tự, cột không có trong tiêu đề) đều ném `SchemaError` |
| SR-U2-4 | Không "làm sạch" ngầm, không tự sửa | BR2.8: câu lỗi nêu `field_name` và `source_column`; không nhánh nào tự đổi cột, tự bỏ qua trường sai hay tự hạ kiểu về `string` (BR2.5) | Rà mã: không `strip`/`lower`/`replace` trên tên trường, bảng, cột |
| SR-U2-5 | Đọc YAML bằng `yaml.safe_load`, không bao giờ `yaml.load` trần | `functional-spec.md` Workflow 1 bước 1 đã chốt `yaml.safe_load`; `safe_load` không dựng đối tượng tuỳ ý nên một tệp YAML độc hại không chạy được mã | Grep `src/integration/`: chỉ `safe_load`; không `Loader`, không `FullLoader` |
| SR-U2-6 | Chỉ đọc **tiêu đề** tệp nguồn, không đọc dữ liệu | Workflow 1 bước 4 chỉ mở tiêu đề; nhờ vậy giá trị thật (mã khách, địa chỉ, số tiền) không vào bộ nhớ của đơn vị và không thể lọt vào thông điệp lỗi | Rà mã: không `read_csv` đầy đủ, không `read()` toàn tệp; test khẳng định chỉ đọc dòng đầu |
| SR-U2-7 | Bộ nạp **không tự phát** sự kiện nào; chỉ phát khi bên gọi truyền logger | Q2 = A: `load_schema` nhận `logger: Logger | None = None`, mặc định `NullLogger` — đúng mẫu đang dùng ở `src/integration/query.py`, `load.py`, `card.py`. Không truyền logger thì không có một dòng log nào; có truyền thì đơn vị phát đúng ba sự kiện ở §3 | Rà **đúng hai tệp U2 sở hữu** (`src/integration/schema.py`, `src/integration/models.py`): không có lời gọi ghi log nào ngoài nhánh `logger is not None`; test gọi `load_schema` không truyền logger và khẳng định logger rỗng |
| SR-U2-8 | `dataset/` chỉ đọc | Chỉ mở tệp CSV ở chế độ đọc; không ghi vào `dataset/` | `git status dataset/` trống sau khi chạy pipeline |
| SR-U2-9 | Không thêm gói phụ thuộc | Chỉ `PyYAML 6.0.2` (đã ghim) + thư viện chuẩn (`dataclasses`, `pathlib`, `re`, `csv`) | `requirements.txt` không đổi (`tech-stack-decisions.md` TS-U2-6) |
| SR-U2-10 | Thiếu tệp là lỗi nêu rõ, không đoán | Tệp lược đồ thiếu → `ConfigurationError`; bảng nguồn thiếu CSV → `ConfigurationError` (Q3 = A). `SchemaError` giữ **mọi** sai về nội dung khai báo — BR2.2 (cột nguồn không có thật), BR2.3 (định danh sai), BR2.4 (`schema_kind` khác `GAV`), BR2.5 (`data_type` ngoài tập kín), BR2.6 (trùng `field_name`) — đúng như `src/integration/schema.py` đang ném | Test cho từng nhánh; thông điệp nêu đường dẫn tệp thiếu hoặc tên trường và tên cột |
| SR-U2-11 | Bên gọi phải kiểm chứng được thời lượng và trạng thái "một phần" mà **không** cần thêm hợp đồng riêng | **C1 và C6** mang `elapsed_ms` + `partial`; **C2 thì không** — payload C2 chỉ có `fields_by_entity` (danh mục trường, không có thời lượng hay kênh một phần), và `MediatedFieldCatalogue` trong mã đúng như vậy. Nhờ C1/C6, NFR1.1 đo được ngay trên giá trị trả về, và consumer (U3, U5, U6) biết phải bắt hai kiểu lỗi | `view.elapsed_ms` là số nguyên dương; test khẳng định `elapsed_ms <= 2000` trên bộ dữ liệu mẫu; rà `contract-summary.md` C1/C6 có `elapsed_ms` + `partial` và cả hai kiểu lỗi |

## 2. Mối đe doạ đã cân nhắc

| Mối đe doạ | Đánh giá | Kiểm soát |
|---|---|---|
| Tệp YAML bị sửa để chèn mã khi nạp | Có thật với `yaml.load`; **không** với `safe_load` | SR-U2-5 |
| Tên bảng/cột bị sửa để chèn vào SQL của U3 | Có thật — đây là đường đi thật của dữ liệu | SR-U2-3 (tập kín + tiêu đề thật), SR-U2-4 (từ chối, không sửa) |
| Đơn vị đọc dữ liệu khách hàng rồi để lộ qua lỗi | Thấp — chỉ đọc tiêu đề | SR-U2-6 |
| Đơn vị phát sự kiện kèm giá trị trường hoặc nội dung YAML | Thấp — chỉ xảy ra khi bên gọi truyền logger | SR-U2-7 + §3 (hai vế cấm/cho phép) |
| Tấn công chuỗi cung ứng | Thấp — 8 gói đã ghim, không thêm gói | SR-U2-9 |
| Người trên cùng máy đọc/sửa tệp lược đồ | Chấp nhận được — máy local, tệp trong repo, thay đổi đi qua git | Không có kiểm soát thêm; ghi ở §4 |
| Đường dẫn tệp do giao diện truyền vào (path traversal) | Không có bề mặt: không tham số đường dẫn tự do từ UI | SR-U2-2 |

## 3. Nhật ký (do chính đơn vị phát, chỉ khi được truyền logger)

Đơn vị kiểu `library` không có `observability-design.md` riêng. Theo Q2 = A, bộ nạp **không tự phát** gì:
`load_schema` nhận `logger` và mặc định là `NullLogger`, nên khi bên gọi không truyền thì không có dòng
log nào (SR-U2-7). Khi có logger, đơn vị phát đúng ba sự kiện dưới đây, cùng khuôn
`logs/<run_id>.jsonl` với `timestamp`, `level`, `run_id`, `stage`, `event`.

**Người phát là đơn vị này, không phải bên gọi.** Đơn vị không thêm lời gọi vào `src/pipeline/stages.py`
(§4 của `tech-stack-decisions.md`); muốn có sự kiện thì bên gọi truyền logger của lần chạy, giống
`query.py`/`load.py` đang làm. Nhờ vậy không có nghĩa vụ nào rơi ra ngoài phạm vi đơn vị, và NFR1.1
**không** phụ thuộc vào việc có ai ghi log: nó đo trên `view.elapsed_ms` (SR-U2-11).

| Sự kiện | Mức | Trường | Khi nào |
|---|---|---|---|
| `integration.schema.loaded` | INFO | `entity_count`, `field_count`, `partial_entities`, `elapsed_ms` | sau khi nạp và kiểm thành công (kể cả khi có `partial`) |
| `integration.schema.partial` | WARNING | `missing_entities`, `reason` | khi view trả kênh `partial` (BR2.1) |
| `integration.schema.failed` | ERROR | `error_code`, `message` | khi ném `SchemaError` hoặc `ConfigurationError` |

Ánh xạ `error_code` (tập đóng `ERROR_CODES` trong `src/common/logging.py`, qua `normalise_error_code`):

| Nhánh lỗi | `error_code` | Ghi chú |
|---|---|---|
| Tệp lược đồ hoặc tệp CSV nguồn không có mặt | `file_not_found` | `ConfigurationError` |
| Tệp không đọc được: `UnicodeDecodeError`, YAML hỏng, `OSError` | `decode_error` (`permission_denied` khi là lỗi quyền) | `SchemaError` |
| Định danh sai hình dạng, bảng không có trong `TABLE_SPECS` (BR2.3) | `identifier_invalid` | `SchemaError` |
| Cột nguồn không có trong tiêu đề thật của tệp (BR2.2) | `column_missing` | `SchemaError` |
| `schema_kind` sai, trùng `field_name`, `data_type` ngoài tập kín, sai cấu trúc | `unknown` | Chấp nhận: `ERROR_CODES` không có mã riêng, và đợt này không thêm mã. Nếu sau cần chẩn đoán tốt hơn thì thêm mã vào `ERROR_CODES` trong cùng thay đổi với bộ nạp |

Hai vế rõ ràng cho nội dung được phép ghi:

- **Cấm:** giá trị ô của tệp dữ liệu (kể cả trong thông điệp), nội dung thô của tệp YAML, và mọi đường
  dẫn tuyệt đối nằm ngoài repo.
- **Được phép:** tên thực thể, tên trường, tên bảng, tên cột, số đếm, `elapsed_ms`, và thông điệp lỗi có
  cấu trúc mà BR2.8 buộc phải nêu `field_name` + `source_column`. Tên cột ở đây là tên trong tiêu đề
  CSV — công khai trong `dataset/` và `src/ingest/schemas.py`, không phải giá trị dữ liệu.


## 4. Rủi ro đã biết

- **Không có đăng nhập và không có phân quyền** (OS5 ngoài phạm vi). Ai chạy được lệnh Python trên máy
  này đều đọc được lược đồ và dữ liệu; đó là thiết kế đã chốt, không phải thiếu sót của đơn vị này.
- **Tệp lược đồ do người sửa tay** (A1). Vì vậy phần lớn "sự cố" ở đây là sửa sai tệp, không phải tấn
  công; cách xử lý là từ chối kèm tên trường và tên cột (SR-U2-4), không tự sửa hộ.
- **Thông điệp lỗi nêu tên bảng và tên cột của nguồn** — cần thiết để sửa được tệp, và không tiết lộ gì
  ngoài tên cột vốn đã công khai trong `dataset/` và `src/ingest/schemas.py`.
- **Lược đồ là đầu vào của SQL**: nếu đợt sau cho phép nạp lược đồ từ nguồn ngoài (hiện C5 cấm), SR-U2-3
  phải được xem lại trước, vì tập kín hiện tại giả định tệp nằm trong repo và đi qua git.
- **NFR4 (tiếp cận) không áp dụng cho đơn vị này** vì nó không hiển thị gì; yêu cầu WCAG 2.1 AA thuộc
  `u6-integration-ui`. Bảng traceability ghi `N/A` kèm lý do này.
- **NFR5 (đúng đắn dữ liệu) áp dụng gián tiếp**: đơn vị không sinh số liệu, nhưng lược đồ sai sẽ làm U3
  đọc sai trường. Vì vậy kiểm cột nguồn (BR2.2) là kiểm soát dữ liệu, không chỉ kiểm soát an toàn.
