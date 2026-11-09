# Code Summary — u2-mediated-schema

## Xác nhận C8 sau khi hợp đồng đổi (2026-11-09)

Rà mã theo C8 (danh sách bản ghi, ba thực thể, `don_hang` 7 trường, mọi trường `loaded: true`):

- `src/integration/schema.py` khai `ENTITY_KEYS`/`FIELD_KEYS` gồm `source_column`, `data_type`, `loaded`; `_parse_entity`/`_parse_field` đòi mỗi phần tử là bản ghi và `_reject_unknown_keys` chặn khoá lạ. Không còn nhánh nào đọc `fields` như danh sách chuỗi.
- `config/mediated-schema.yaml` có ba thực thể (7/5/2 trường), tất cả `loaded: true` — khớp C8.
- Hệ quả đã ghi nhận (Minor, chưa sửa): `bang_giao` khai `loaded: true` nhưng `load_don_hang` chỉ đọc bảng khoá `olist_orders_dataset`, nên giá trị trường này luôn `None`; cần một quyết định riêng (nạp thêm bảng customers, hoặc hạ cờ) — ghi ở `memory.md` cấp stage.


Nguồn: kế hoạch đã duyệt `code-generation-plan.md`, hướng dẫn test `unit-test-instructions.md`, và các lần chạy
lệnh ghi trong tài liệu này.

## 1. Đã dựng gì

| Lớp | Tệp | Nội dung |
|---|---|---|
| Mô hình dữ liệu | `src/integration/models.py` | Thêm `PartialEntity` (`name`, `reason`), `MediatedSchemaView` (`schema_kind`, `entities`, `mappings`, `elapsed_ms`, `partial`, và `entity(name)` để bên dùng U1 không phải đổi), `MediatedFieldCatalogue` (`fields_by_entity`) — cả ba `frozen=True`; danh sách trường là `tuple`, không `dict` (TS-U2-8) |
| Truy cập dữ liệu (L3) | `src/integration/schema.py` | `_source_path`, `_source_header` (chỉ đọc **dòng đầu** bằng `csv.reader`, `utf-8-sig`, `newline=""`), `_read_headers` (mỗi tiêu đề đọc đúng một lần cho cả lượt nạp) |
| Logic nghiệp vụ (L1/L2/L4) | `src/integration/schema.py` | `_parse_schema` (L1: `safe_load`, `schema_kind = GAV`, cấu trúc, định danh, trùng tên thực thể/trường, `data_type` tập kín, `loaded` mặc định `True`), `_check_columns` (L3, BR2.2/BR2.8), `_partial_entities` (BR2.1), `load_schema` trả `MediatedSchemaView`, `build_field_catalogue` (BR2.7) |
| Nhật ký (L5) | `src/integration/schema.py` | `_failed` gắn `error_code` đóng vào ngoại lệ; `load_schema` phát `integration.schema.loaded` (INFO), `integration.schema.partial` (WARNING), `integration.schema.failed` (ERROR) qua `logger` do bên gọi truyền; mặc định `NullLogger` |
| Khai báo (C8) | `config/mediated-schema.yaml` | Khai đủ ba thực thể `don_hang`, `mat_hang`, `san_pham` (don_hang giữ nguyên; hai thực thể còn lại **chỉ cộng thêm** theo BR2.9) |
| Test | `tests/unit/test_integration_schema.py` | 41 hàm test (44 mục, 1 hàm tham số hoá 4 mục); fixture tự dựng trong `tmp_path`: một YAML ba thực thể + bốn CSV nhỏ có **dòng dữ liệu sai kiểu** để chứng minh chỉ đọc tiêu đề; một test đọc chính `config/mediated-schema.yaml` đang phát hành |
| CI | `.github/workflows/ci.yml` | `tests/unit/test_integration_schema.py` nằm trong danh sách `ruff format --check` (G2); xem §5 mục 8 về phạm vi thay đổi của tệp |

## 2. Quyết định chính

| Quyết định | Vì sao |
|---|---|
| `load_schema(path, csv_dir=None, logger=None)` — `csv_dir` là **tuỳ chọn** | R1 của kế hoạch: `src/integration/load.py` (dòng 176) và `card.py` (dòng 310) gọi `load_schema(path)` một tham số, và 12 test U1 dựng lược đồ trong `tmp_path`; đổi chữ ký thành bắt buộc sẽ làm đỏ cả bộ nhanh. Vắng `csv_dir` thì lấy `AppConfig.raw_csv_dir` |
| `csv_dir` mặc định lấy **một lần** qua `load_config()`, cache trong `_CSV_DIR` | Tránh đọc `config.yaml` lại mỗi lần nạp; `load_config()` có tác dụng phụ tạo thư mục đầu ra (đã là hành vi có chủ đích của repo), và trên máy này mọi thư mục đều có sẵn nên không tạo gì mới |
| Thứ tự cố định của ADR-U2-S1 | `_parse_schema` (định danh, không mở tệp CSV) chạy **trước** `_read_headers`; `_default_csv_dir()` cũng nằm sau bước kiểm định danh, để tệp YAML xấu không điều khiển được đường dẫn đọc |
| Giữ `MediatedSchema` làm kết quả phân tích, `MediatedSchemaView` là payload C1 | `MediatedSchema` không bị xoá (không phá API cũ); view là hình chiếu cộng thêm `elapsed_ms` + `partial` đúng TS-U2-5 |
| `elapsed_ms = max(1, round(...))` | SR-U2-11 đòi **số nguyên dương**; trên fixture một lượt nạp có thể tròn 0 ms, nên chặn dưới 1 ms. Con số này không phải phép đo hiệu năng thật (R2) |
| Kiểm **tên thực thể trùng** (ngoài danh sách bước 9) | `entities.md` khai `name` là `unique: true`, và `mappings` có khoá theo tên thực thể — trùng tên sẽ làm mất một thực thể trong im lặng |
| `error_code` gắn vào ngoại lệ (`_failed`) thay vì đổi kiểu lỗi | C1/C2/C6 cam kết đúng `SchemaError` + `ConfigurationError`; gắn thuộc tính là cách giữ nguyên hợp đồng mà vẫn có mã đóng cho nhật ký |

## 3. Kết quả kiểm chứng

| Cổng | Lệnh | Kết quả |
|---|---|---|
| Test của đơn vị | `.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_schema.py` | **44 passed** (41 hàm test) |
| Bộ nhanh toàn repo (bước 11) | `.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow"` | **220 passed, 7 deselected** — không hồi quy |
| Lint | `ruff check src/integration tests/unit/test_integration_schema.py` | sạch |
| Định dạng | `ruff format --check src/integration tests/unit/test_integration_schema.py` | sạch |
| Ngưỡng phủ toàn dự án | `pytest -m "not slow" --cov=src --cov-fail-under=80` | **81,73%** — đạt ngưỡng 80% |
| Phủ riêng hai tệp của đơn vị (toàn bộ bộ nhanh) | `pytest -m "not slow" --cov=src.integration.schema --cov=src.integration.models` | `schema.py` **96%**, `models.py` **99%** |
| Chạy thật trên dữ liệu gốc | `load_schema(Path('config/mediated-schema.yaml'))` (không truyền `csv_dir`) | `GAV ['don_hang', 'mat_hang', 'san_pham'] None 9` — đủ ba thực thể, `partial` **rỗng**, đọc tiêu đề thật trong `dataset/`; `elapsed_ms` = 9 ms ở lần chạy này |

**Đầu ra đỏ đã ghi (TDD):**

| Lớp | Bước | Đầu ra đỏ |
|---|---|---|
| Mô hình dữ liệu | 3 | `ImportError: cannot import name 'MediatedFieldCatalogue' from 'src.integration.models'` (1 error khi collect) |
| Truy cập dữ liệu (L3) | 6 | **5 failed, 7 passed** — cả 5 hỏng với `TypeError: load_schema() got an unexpected keyword argument 'csv_dir'` |
| Logic nghiệp vụ (L1/L2/L4) | 9 | `ImportError: cannot import name 'build_field_catalogue' from 'src.integration.schema'` (1 error khi collect) |

**Dòng còn chưa phủ trong `schema.py` (8 dòng, toàn bộ bộ nhanh):** 56 và 75–78 là nhánh `raise` của
`EntityMapping.field` / `MediatedSchema.entity`; 138 là nhánh `PermissionError` (không dựng được lỗi quyền
một cách tin cậy trên Windows); 232 và 250 là hai nhánh "phần tử không phải ánh xạ". Tất cả là nhánh lỗi
biên, không phải đường đi nghiệp vụ.

## 4. Chỉ tiêu đo được

| Mã | Ngưỡng | Đo được | Kết luận |
|---|---|---|---|
| NFR1.1 | ≤ 2 giây | fixture: `elapsed_ms` là `int`, `0 < elapsed_ms <= 2000`; chạy thật trên `config/mediated-schema.yaml` + `dataset/`: **9 ms** | đạt — nhưng xem ghi chú R2 dưới |
| NFR2.1 | ≥ 80% | toàn dự án **81,73%** trên bộ nhanh; `schema.py` 96%, `models.py` 99% | đạt |
| NFR2.2 | mỗi mô-đun mới có test riêng | `tests/unit/test_integration_schema.py` phủ `schema.py` và phần `models.py` của đơn vị | đạt |
| NFR3.1 | 0 vi phạm | `ruff check` + `ruff format --check` sạch | đạt |
| NFR6.1 | không mạng | không import `urllib`/`requests`/`socket`; chỉ `yaml`, `csv`, `re`, `time`, `pathlib`, `dataclasses` | đạt |
| NFR5.1/NFR5.2 | không hồi quy | bộ nhanh 220 passed; đơn vị không ghi vào mart/view, không thêm lời gọi pipeline | đạt ở mức test; xác nhận dữ liệu thuộc Build and Test |

**Ghi chú R2 (không tuyên bố quá):** test NFR1.1 trên fixture chứng minh **cơ chế đo tồn tại và có cận trên**,
không chứng minh hiệu năng thật. Con số 4 ms ở trên là lần chạy thật đầu tiên trên `dataset/` (chỉ đọc tiêu
đề bốn tệp), ghi lại để tham chiếu — chưa phải phép đo có kiểm soát.

## 5. Điểm lệch kế hoạch

| # | Lệch | Ghi chú |
|---|---|---|
| 1 | `csv_dir` là tham số **tuỳ chọn** (`load_schema(path, csv_dir=None, logger=None)`) thay vì bắt buộc | R1 của kế hoạch đã lường trước; nếu bắt buộc, `load.py`, `card.py` và 12 test U1 sẽ đỏ |
| 2 | Thêm kiểm **trùng tên thực thể** | `entities.md` khai `unique: true`; thiếu kiểm này thì `mappings` mất một thực thể trong im lặng |
| 3 | Hàm dựng danh mục đặt tên `build_field_catalogue` | Kế hoạch chỉ nói "hàm dựng catalogue từ view", không đặt tên |
| 4 | 41 hàm test (44 mục) thay vì 22–26 | Phủ thêm các nhánh L1 (trùng tên thực thể/trường, trùng `source_tables`, khoá lạ, thiếu `source_tables`, tệp lược đồ không đọc được), ánh xạ `error_code` (`column_missing`, `decode_error`), đường mặc định `csv_dir` từ `AppConfig`, thứ tự ADR-U2-S1 và một test đọc chính tệp cấu hình đang phát hành |
| 5 | `load_schema` **trả `MediatedSchemaView`** thay cho `MediatedSchema` | Đúng TS-U2-5/C1; `.entity(name)` được giữ trên view nên `load.py`, `card.py` và các test U1 không phải sửa |
| 6 | Docstring trong `schema.py` và của ba kiểu mới trong `models.py` viết bằng **tiếng Việt** | Quy tắc ngôn ngữ hội thoại của đơn vị này (`Conversation language: Vietnamese`). Docstring cũ của U1 trong `schema.py` cũng được dịch để tệp không trộn hai ngôn ngữ; chỉ đổi chú thích, không đổi mã hay chữ ký |
| 7 | `partial` dùng `PartialInfo(missing, reason)` thay cho `tuple[PartialEntity, ...]` | `entities.md` khai đúng hình dạng `{ missing, reason }`; mã được đổi cho khớp tài liệu, không phải tài liệu đổi cho khớp mã (sửa theo phát hiện R-07 của vòng review 1). `PartialEntity` không còn tồn tại |
| 8 | `config/mediated-schema.yaml` được sửa trong đơn vị này dù không nằm trong `Touches` của kế hoạch | Đây là mục tiêu chính của U2 (`unit-of-work.md` §U2 "khai báo đủ ba thực thể"); kế hoạch bỏ sót tệp. Thay đổi **chỉ cộng thêm** hai thực thể `mat_hang`, `san_pham`, giữ nguyên `don_hang` (BR2.9), và có test đọc chính tệp này (sửa theo phát hiện R-01) |
| 9 | Phạm vi thay đổi `.github/workflows/ci.yml` không kiểm chứng được bằng git | Cả thư mục `.github/` chưa được git theo dõi nên không có mốc so sánh. Tệp đã tồn tại trong cây làm việc với các bước CI và danh sách format của các đơn vị khác; thay đổi của riêng U2 là thêm `tests/unit/test_integration_schema.py` vào dòng `ruff format --check` (bước 12 của kế hoạch). Không có thay đổi nào khác được thực hiện ở tệp này (ghi theo phát hiện R-08) |

## 6. Việc chưa làm — cần chốt ở bước sau

**BR2.1 đã đạt trên tệp đang phát hành:** `config/mediated-schema.yaml` khai đủ `don_hang`, `mat_hang`,
`san_pham`, và lần chạy thật cho `partial` rỗng (mục §3). Những việc còn lại **không** thuộc đơn vị này:

- **FR1.3 và FR1.4** (hiển thị danh sách thực thể, bảng ánh xạ, nhãn `GAV` trên màn hình) — chuyển sang
  `u6-integration-ui`; `traceability.json` đánh `Deferred`. Đơn vị này không render gì.
- **NFR5.2** (số dòng 11 view và 5 KPI baseline) — xác nhận ở Build and Test sau khi chạy `--stage all`.
- **Khóa mức người bán** cho U4 — nằm ngoài lược đồ ba thực thể này (`FR1.5`).

## 7. Test viết nhưng chưa chạy

- 7 test `slow` (end-to-end + data-quality baseline của toàn dự án) **không** chạy ở bước này — thuộc
  Build and Test và lần xác nhận trước phát hành, đúng như `unit-test-instructions.md`.
- Lệnh xác nhận đầy đủ của đơn vị (`pytest -m "not slow"` → `python -m src.pipeline run --stage all` → mở
  dashboard) mới chạy được **bước 1**; hai bước sau thuộc Build and Test.

## 8. Vòng sửa sau review 1 (R-01 … R-08)

| Phát hiện | Đã làm |
|---|---|
| R-01 (Critical) — `config/mediated-schema.yaml` thiếu `mat_hang`, `san_pham`; `traceability.json` ghi `OK` sai | Thêm hai thực thể (chỉ cộng thêm, giữ `don_hang`); thêm `test_released_schema_declares_the_three_entities` đọc chính tệp đang phát hành và khẳng định đủ ba thực thể + `partial is None`; cập nhật `traceability.json` (BR2.1, FR1.1, BR2.9), `code-summary.md`, `source-manifest.json` |
| R-02 (Major) — FR1.3/FR1.4 là yêu cầu hiển thị nhưng bị ghi `OK` | Đổi cả hai sang `Deferred`, target `u6-integration-ui` |
| R-03 (Major) — test "chỉ đọc tiêu đề" không đếm được số dòng đọc | Thêm `LineCountingHandle` bọc `Path.open` (monkeypatch) và khẳng định mỗi tệp CSV được đọc đúng **một** dòng; giữ fixture dòng dữ liệu sai kiểu |
| R-04 (Minor) — test "NullLogger mặc định" thực ra kiểm logger được gọi | Giữ test cũ, thêm `test_load_schema_without_a_logger_writes_nothing`: gọi không truyền logger, khẳng định không stdout/stderr, không bản ghi `caplog`, không tệp log phát sinh |
| R-05 (Minor) — thiếu ca ghim thứ tự ADR-U2-S1 | Thêm `test_load_schema_checks_identifiers_before_opening_source_files` (định danh sai **và** CSV nguồn thiếu → `SchemaError`, không phải `ConfigurationError`) |
| R-06 (Minor) — bỏ qua khoá lạ, nhận `source_tables` trùng | Thêm `_reject_unknown_keys` và `_unique_source_tables` trong `schema.py`, kèm ba test (`unknown_entity_key`, `unknown_field_key`, `duplicate_source_tables`) |
| R-07 (Minor) — `partial` lệch `entities.md` | Mã dùng `PartialInfo(missing, reason)` đúng hình dạng tài liệu; bỏ `PartialEntity`; ghi điểm lệch ở §5 mục 7 |
| R-08 (Minor) — không kiểm chứng được phạm vi sửa `ci.yml` | Ghi rõ ở §5 mục 9: `.github/` chưa được git theo dõi nên không có mốc so sánh; thay đổi của U2 chỉ là thêm một đường dẫn test vào dòng `ruff format --check` |
