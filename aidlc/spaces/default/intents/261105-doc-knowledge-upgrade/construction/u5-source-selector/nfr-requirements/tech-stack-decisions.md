# Tech Stack Decisions — u5-source-selector

Nguồn: `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`, `requirements.txt`, `functional-design/functional-spec.md`, `functional-design/rules.md`, `functional-design/entities.md`, `inception/requirements-analysis/requirements.md` (NFR1–NFR6, ràng buộc C1–C6), `inception/contract-design/contract-summary.md` (C2, C3, C7).

## 1. Đã chốt ở cấp dự án

| Hạng mục | Lựa chọn | Ghi chú |
|---|---|---|
| Ngôn ngữ | Python 3.13 | Có sẵn |
| Đọc cấu hình | `PyYAML 6.0.2` qua `yaml.safe_load` | Đã ghim, đang dùng trong `src/config.py` và `src/integration/schema.py` |
| Danh mục trường đầu vào | `MediatedFieldCatalogue` của U2 (C2) | Đọc qua `src/integration/models.py` |
| Kiểu dữ liệu hợp đồng | `dataclass(frozen=True)` trong `src/integration/models.py` | Cùng chỗ với C1/C2/C6 |
| Kiểu lỗi | `PipelineError` và các lớp con trong `src/common/exceptions.py` | `NoSourceAvailableError` là lớp con mới |
| Kiểm thử | pytest 9.1.1 + pytest-cov 7.1.0 | Có sẵn |

## 2. Quyết định riêng cho đơn vị này

| Mã | Quyết định | Lý do |
|---|---|---|
| TS-U5-1 | Đặt logic chọn nguồn trong **`src/integration/selector.py`** (tệp mới), kiểu dữ liệu trong `src/integration/models.py` | Cùng gói `src/integration/` đang chứa `schema.py`, `load.py`, `query.py`, `card.py`; U5 là thành phần thứ tư của cùng component `SourceSelector`, không tạo gói mới |
| TS-U5-2 | Bộ hồ sơ nguồn và ánh xạ truy vấn → trường cần nằm trong **`config/integration-sources.yaml`** | Quyết định Q6 = A: cấu hình tĩnh. Cùng thư mục với `config/mediated-schema.yaml` (C8), nên người sửa chỉ nhìn một chỗ |
| TS-U5-3 | Đọc cấu hình bằng `yaml.safe_load` | Không dựng đối tượng tuỳ ý; cùng mẫu với `src/config.py` và `src/integration/schema.py` |
| TS-U5-4 | **Không suy `tables` hay `is_simulated`** từ tên nguồn hay từ `covered_fields`; cả hai khai tường minh | R-01/R-06 của vòng review thiết kế: C2 không mang ánh xạ thực thể → bảng, nên mọi phép suy đều phải bịa. Khai tường minh là cách duy nhất kiểm được |
| TS-U5-5 | Không thêm gói nào | `yaml`, `pathlib`, `dataclasses` đều đã có; ràng buộc dự án chỉ cho thêm thư viện nhỏ đã ghim |
| TS-U5-6 | Xếp hạng bằng **khoá sắp xếp tường minh** `(cost_level, latency_ms, source_name)`, không dựa vào thứ tự dict | BR5.4: kết quả phải tất định, không phụ thuộc thứ tự khai báo (SR-U5-12) |
| TS-U5-7 | Thêm `NoSourceAvailableError` vào `src/common/exceptions.py`, là lớp con của `PipelineError` | C3/C7 khai lỗi này; phải có lớp thật để U3 và U6 bắt. Cùng mẫu với `QueryExecutionError` |
| TS-U5-8 | Danh mục nguồn là **đối tượng bất biến**: `tuple` cho danh sách, dataclass `frozen=True`. Cập nhật danh mục = **dựng danh mục mới** bằng `dataclasses.replace`, không sửa tại chỗ | Cùng quy ước U2 (TS-U2-8); C7 được U6 đọc lại, nên không được sửa tại chỗ |
| TS-U5-9 | Hàm công khai nhận `logger` tuỳ chọn, mặc định `NullLogger` | Cùng mẫu `query.py`/`load.py`/`card.py`; không tạo mẫu ghi log thứ hai |
| TS-U5-10 | Không đọc CSV nguồn, không đọc `data/` | U5 chỉ cần tệp cấu hình và C2; đọc dữ liệu ô là việc của U3/U4 (SR-U5-9) |
| TS-U5-11 | Hàm đề xuất nguồn trả **`SourceSelection`** (C3), mang thêm trường `catalogue` là bản C7 đã cập nhật. Nhánh không nguồn nào đủ trường ném `NoSourceAvailableError` mang thuộc tính `catalogue` cùng bản C7 đó | W2/W3 đều ghi `choices` và xoá `partial_reason`/`pending_query_id`. Danh mục bất biến (TS-U5-8) nên hàm dựng bản mới; C3 và C7 đều được cộng thêm trường ngày 2026-11-08 trong `contract-summary.md`, đúng change policy "chỉ thêm trường". U6 nhận bản C7 mới qua `SourceSelection.catalogue`, không qua một kênh thứ hai |
| TS-U5-12 | Kiểm tên bảng bằng `SOURCE_TABLES` của `src/integration/schema.py` | SR-U5-14: `SOURCE_TABLES` là tập chín tên tệp đã bỏ `.csv`, đúng dạng tên trong `tables`; `TABLE_SPECS` khoá bằng tên logic nên không dùng trực tiếp được. Không cần C1 |
| TS-U5-13 | **Điểm ghép nối C7**: U6 dựng danh mục một lần khi khởi động màn hình — gọi `build_field_catalogue` của U2 (C2) rồi `load_source_catalogue(path, C2)` của U5 — và giữ `SourceCatalogue` trả về; mỗi lần bấm "Đề xuất nguồn" thì truyền chính danh mục đó vào `select_source` và đọc bản mới ở `SourceSelection.catalogue` | C2 khai U5 là consumer, còn U6 nhận C6 (không có `fields_by_entity`). Vì vậy U6 phải lấy C2 **trực tiếp từ U2** — đúng chiều hợp đồng. Ghi rõ để bước sinh mã không dựng đường thứ hai |
| TS-U5-14 | **Kiểm kiểu tường minh cho tám khoá của hồ sơ**: `has_data`, `is_simulated` phải là `bool` thật (không nhận chuỗi `"false"`); `cost_level`, `latency_ms` phải là `int` và không phải `bool`; `covered_fields`, `tables` phải là danh sách chuỗi; `source_name`, `label` phải là chuỗi | YAML trả về kiểu tuỳ theo chữ người viết: `has_data: "false"` là chuỗi truthy và sẽ lọt vị từ ứng viên; `latency_ms: "800"` làm `TypeError` ném ra ngoài ba lớp lỗi mà U6/U3 được dặn bắt (ADR-U5-S7) |
| TS-U5-15 | **Phạm vi tệp của đơn vị** (để NFR3.1 có nghĩa): `src/integration/selector.py` (mới), `src/integration/models.py`, `src/common/exceptions.py`, `src/config.py`, `config.yaml`, `config/integration-sources.yaml` (mới), `tests/unit/test_integration_selector.py` (mới) | Danh sách này là phạm vi `ruff check` + `ruff format --check` của đơn vị; các tệp không có trong danh sách không bị format lây (quy ước team.md) |

## 3. Chỉ tiêu kỹ thuật

```yaml
nfr_requirements:
  - id: NFR1.1
  - id: NFR2.1
  - id: NFR2.2
  - id: NFR3.1
  - id: NFR5.1
  - id: NFR5.2
  - id: NFR6.1
  - id: NFR6.2
```


Đơn vị kiểu `library` không sinh `performance-requirements.md`, `scalability-requirements.md`, `reliability-requirements.md` hay `observability-requirements.md`; các chỉ tiêu đo được của đơn vị vì vậy được chốt ở đây và mang mã `NFRx.y` đúng chuẩn.

| Mã | Chỉ tiêu | Ngưỡng | Đo bằng | Nguồn |
|---|---|---|---|---|
| NFR1.1 | Thời gian nạp bộ hồ sơ và trả kết quả chọn nguồn cho một truy vấn | ≤ 2 giây — giữ ngưỡng chung của NFR1, không đặt ngưỡng chặt hơn | Đo bằng `time.perf_counter()` **trong test**, bọc quanh hai hàm công khai (nạp hồ sơ và đề xuất nguồn), khẳng định mỗi lần `<= 2000` ms trên fixture. Không thêm trường đo vào C3/C7: hợp đồng không có `elapsed_ms`, và đợt này không mở rộng hợp đồng chỉ để đo | NFR1 |
| NFR2.1 | Độ phủ dòng toàn dự án | ≥ 80% | `pytest --cov=src --cov-fail-under=80` trên toàn bộ bộ test | NFR2 |
| NFR2.2 | Mỗi mô-đun mới có test riêng | 1 tệp test cho `src/integration/selector.py` | Rà `tests/unit/` | NFR2 |
| NFR3.1 | Lint và định dạng | 0 vi phạm | `ruff check` + `ruff format --check` trên phạm vi đã chốt | NFR3 |
| NFR5.1 | Không làm đổi hành vi pipeline và số liệu | `KpiReconciler` xanh; 5 KPI lệch 0 | `python -X utf8 -m src.pipeline run --stage all` sau khi thêm đơn vị; `KpiReconciler` so 5 chỉ số với giá trị tham chiếu đã ghi, không so tệp thô (Parquet/JSONL đổi `run_id` và thời điểm mỗi lần chạy) | NFR5 |
| NFR5.2 | 11 view phải tồn tại; số dòng 9 bảng mart không đổi | `len(views) == 11` và số dòng 9 bảng mart khớp baseline | `tests/integration/test_u2_end_to_end.py` — **lưu ý phạm vi**: test này khẳng định 11 view *tồn tại* và số dòng **9 bảng mart**; hai bảng `agg_sales_daily` và `agg_delivery_daily` **chưa có baseline số dòng** trên dữ liệu thật, nên chúng không được bảo vệ bởi chỉ tiêu này | NFR5 |
| NFR6.1 | Chạy local, không mạng | 0 lời gọi mạng | Rà `src/integration/selector.py`: không `urllib`, `requests`, `socket` | NFR6 |
| NFR6.2 | Chạy UTF-8 | Mọi lệnh Python dùng `-X utf8` | `docs/runbook.md`; lệnh chạy của đơn vị | NFR6 |

**Ghi rõ về NFR4 (tiếp cận):** không áp dụng cho đơn vị này vì nó không hiển thị gì; yêu cầu WCAG 2.1 AA thuộc `u6-integration-ui`. Bảng traceability ghi `N/A` kèm lý do này.

## 4. Việc cần làm ở bước sinh mã

- Thêm `NoSourceAvailableError` vào `src/common/exceptions.py` (TS-U5-7).
- Thêm `SourceProfile`, `SourceChoice`, `SourceCatalogue`, `SourceSelection` vào `src/integration/models.py` (TS-U5-8), cạnh C1/C2/C6 đang có.
- Thêm trường `integration_sources_path` vào `AppConfig` trong `src/config.py` và khoá tương ứng trong `config.yaml`, theo đúng mẫu `mediated_schema_path` đang có (R-07). Không rải hằng đường dẫn trong `selector.py`.
- Tạo `src/integration/selector.py` (TS-U5-1) với hai hàm công khai có chữ ký đã chốt:
  - `load_source_catalogue(path: Path, field_catalogue: MediatedFieldCatalogue, pending_query_id: str | None = None, logger=None) -> SourceCatalogue` (W1). Người gọi là U6 khi khởi động màn hình: lấy C2 từ `build_field_catalogue` của U2 rồi truyền vào (TS-U5-13). `pending_query_id` vắng mặt thì lấy truy vấn đầu tiên **theo thứ tự khai báo** trong ánh xạ — tất định, không phụ thuộc dict.
  - `select_source(catalogue: SourceCatalogue, query_id: str, logger=None) -> SourceSelection` (W2) — trả payload C3, gồm trường `catalogue` là bản C7 đã cập nhật (TS-U5-11). Nhánh W3 ném `NoSourceAvailableError` mang thuộc tính `catalogue` cùng bản C7 đó.
- Tạo `config/integration-sources.yaml` (TS-U5-2) với đúng ba nguồn và ba ánh xạ truy vấn của `functional-spec.md` W2.
- Viết `tests/unit/test_integration_selector.py`: nạp hồ sơ; tập tên nguồn kín; mã trường lạ; tên bảng ngoài `TABLE_SPECS`; hồ sơ thiếu khoá và `cost_level` ngoài 1..5; xếp hạng; loại nguồn mô phỏng; sáu nhánh lý do; nhánh "một phần"; nhánh không nguồn nào đủ trường; tính tất định khi đảo thứ tự khai báo; đo NFR1.1 bằng `time.perf_counter`.
- Sửa đồng thời **bốn** chỗ mô tả phép kiểm tên bảng để cả bộ tài liệu nói `SOURCE_TABLES`: `functional-design/rules.md` BR5.3, `functional-design/entities.md` (ràng buộc của `SourceProfile`), `functional-design/functional-spec.md` W1 bước 4, và `nfr-requirements/security-requirements.md` §2/§4.
- Kiểm phạm vi ruff và `--cov-fail-under=80` theo lệnh xác nhận đã chốt của dự án.
