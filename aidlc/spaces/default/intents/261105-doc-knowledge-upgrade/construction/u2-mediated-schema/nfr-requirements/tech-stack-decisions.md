# Tech Stack Decisions — u2-mediated-schema

Nguồn: `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`, `requirements.txt`,
`functional-design/functional-spec.md`, `functional-design/rules.md`, `inception/requirements-analysis/
requirements.md` (NFR1–NFR6, ràng buộc C1–C7), `inception/contract-design/contract-summary.md` (C1, C2, C6, C8).

## 1. Đã chốt ở cấp dự án

| Hạng mục | Lựa chọn | Ghi chú |
|---|---|---|
| Ngôn ngữ | Python 3.13 | Có sẵn |
| Đọc YAML | `PyYAML 6.0.2` qua `yaml.safe_load` | Đã ghim, đang dùng trong `src/config.py` và `src/integration/schema.py` |
| Danh sách bảng nguồn | `TABLE_SPECS` của `src/ingest/schemas.py` | Một nguồn sự thật duy nhất (functional-spec, "Nguồn vào") |
| Lỗi theo tầng | `SchemaError`, `ConfigurationError` trong `src/common/exceptions.py` | Đã có; CLI bắt ở biên |
| Kiểm thử | pytest 9.1.1 + pytest-cov 7.1.0 | Có sẵn |

## 2. Quyết định riêng cho đơn vị này

| Mã | Quyết định | Lý do |
|---|---|---|
| TS-U2-1 | **Mở rộng `src/integration/schema.py` đang có**, không tạo gói mới | Tệp này đã nạp lược đồ **ba thực thể** do U1 bàn giao (C8: `don_hang` 7 trường, `mat_hang` 5, `san_pham` 2, mọi trường `loaded: true`) và đã có `load_schema`, `MediatedSchema`, `EntityMapping`, `FieldMapping`, `checked_identifier`. Sửa tại chỗ giữ nguyên các test đang xanh (`test_load_schema_rejects_a_missing_file`) và tránh hai bộ nạp song song |
| TS-U2-2 | Tra `TableSpec` theo **`file_name`**, không theo khoá nội bộ của `TABLE_SPECS` | BR2.2: người sửa tệp YAML viết tên tệp nguồn (`olist_orders_dataset`), không phải khoá nội bộ. `SOURCE_TABLES` hiện đã dựng từ `spec.file_name` — giữ nguyên cách đó |
| TS-U2-3 | Kiểm tiêu đề nguồn bằng `csv.reader` **chỉ đọc dòng đầu**; không `pd.read_csv`, không `read().splitlines()` | SR-U2-6: không đưa giá trị ô vào bộ nhớ. `csv` là thư viện chuẩn nên không thêm gói; đọc với `encoding="utf-8-sig"`, `newline=""` |
| TS-U2-4 | `partial` là **kênh dữ liệu**, không phải ngoại lệ | BR2.1: thiếu một thực thể vẫn trả view, kèm danh sách thực thể thiếu và lý do. Kiểu mang `partial: tuple[...]`, rỗng khi đủ ba thực thể |
| TS-U2-5 | `MediatedSchemaView` (C1) và `MediatedFieldCatalogue` (C2) là **dataclass trong `src/integration/models.py`**, hàm dựng nằm trong `schema.py` | Giữ đúng quy ước U1: `models.py` chứa kiểu dữ liệu hợp đồng, `schema.py` chứa logic nạp/kiểm. U3, U5, U6 chỉ import kiểu từ `models.py`. `MediatedSchemaView` mang thêm `elapsed_ms` và `partial` để bên gọi đo và hiển thị trạng thái "một phần" mà không cần hợp đồng phụ (SR-U2-11) |
| TS-U2-6 | Không thêm gói nào | Ràng buộc dự án: chỉ thêm thư viện nhỏ, mã nguồn mở, ghim trong `requirements.txt`. Mọi thứ đơn vị này cần (`yaml`, `csv`, `re`, `pathlib`, `dataclasses`) đều đã có |
| TS-U2-7 | Cờ `loaded` **mặc định `True` khi vắng mặt**, nhưng vẫn phải là `true|false` khi có mặt | functional-spec Workflow 1 bước 2 nói rõ mặc định; mã hiện tại đòi `bool` bắt buộc. Sửa cho khớp đặc tả, giữ nguyên việc từ chối giá trị không phải boolean |
| TS-U2-8 | Thứ tự trường giữ bằng `tuple`, không `dict`, khi trả ra | BR2.6: danh mục trường và bảng hiển thị phải ổn định giữa các lần chạy; `tuple` giữ thứ tự tệp khai báo và không thể sửa tại chỗ |
| TS-U2-9 | Thiếu tệp CSV nguồn → `ConfigurationError`; sai cấu trúc khai báo → `SchemaError` | Quyết định Q3 = A. Giữ ranh giới đã có: thiếu tệp là lỗi môi trường/cấu hình, nội dung sai là lỗi lược đồ |
| TS-U2-10 | Bộ nạp **không tự phát** sự kiện; nhận `logger` mặc định `NullLogger`, đúng mẫu đang dùng ở `query.py`/`load.py`/`card.py` | Quyết định Q2 = A. Giữ nguyên quy ước gói hiện có (tham số `logger`, mặc định không ghi), nên không phải sửa ba tệp kia và cũng không tạo một mẫu ghi log thứ hai. Tiêu chí kiểm chỉ áp cho hai tệp U2 sở hữu: `src/integration/schema.py`, `src/integration/models.py` |

## 3. Chỉ tiêu kỹ thuật

Đơn vị kiểu `library` không sinh `performance-requirements.md`, `scalability-requirements.md`,
`reliability-requirements.md` hay `observability-requirements.md`; các chỉ tiêu đo được của đơn vị vì vậy
được chốt ở đây và mang mã `NFRx.y` đúng chuẩn.

| Mã | Chỉ tiêu | Ngưỡng | Đo bằng | Nguồn |
|---|---|---|---|---|
| NFR1.1 | Thời gian một lần nạp + kiểm lược đồ đầy đủ (đọc YAML + tiêu đề các tệp nguồn của ba thực thể) | ≤ 2 giây — **giữ ngưỡng chung của NFR1, không đặt ngưỡng chặt hơn** (Q1 = A) | `view.elapsed_ms` do chính bộ nạp đo và trả về (SR-U2-11); test dùng fixture lược đồ + CSV nhỏ, khẳng định `elapsed_ms <= 2000`; sự kiện `integration.schema.loaded` chỉ là kênh quan sát tuỳ chọn, không phải cách đo | NFR1, Q1 = A |
| NFR2.1 | Độ phủ dòng toàn dự án | ≥ 80% | `pytest --cov=src --cov-fail-under=80` trên toàn bộ bộ test | NFR2, luật dự án |
| NFR2.2 | Mỗi mô-đun mới có test riêng | 1 tệp test cho mỗi tệp nguồn mới, kể cả tệp "chỉ nối dây" | Rà danh sách `src/integration/` và `tests/unit/` | NFR2 |
| NFR3.1 | Lint và định dạng | 0 vi phạm | `ruff check` + `ruff format --check` trên phạm vi đã chốt | NFR3 |
| NFR5.1 | `quality full` và `KpiReconciler` xanh sau thay đổi | 0 vi phạm; 5 KPI lệch 0 | `python -X utf8 -m src.pipeline run --stage all` sau khi thêm đơn vị | NFR5, luật dự án |
| NFR5.2 | Số dòng 11 view và 5 KPI baseline không đổi | Khớp chính xác | `KpiReconciler` + test tích hợp hiện có | NFR5 |
| NFR6.1 | Chạy local, không mạng | 0 lời gọi mạng | Rà mã `src/integration/`: không `urllib`, không `requests`, không `socket` | NFR6 |

**Ghi rõ về NFR4 (tiếp cận):** không áp dụng cho đơn vị này vì nó không hiển thị gì; yêu cầu WCAG 2.1 AA
thuộc `u6-integration-ui`. Bảng traceability ghi `N/A` kèm lý do này.

## 4. Việc cần làm ở bước sinh mã

- Mở rộng `src/integration/schema.py` (TS-U2-1): thêm kiểm tiêu đề nguồn (TS-U2-3), kênh `partial`
  (TS-U2-4), mặc định `loaded = True` (TS-U2-7), đo `elapsed_ms`, tham số `logger` mặc định `NullLogger`
  (TS-U2-10), và hàm dựng `MediatedSchemaView` / `MediatedFieldCatalogue`.
- Thêm `MediatedSchemaView` (kèm `elapsed_ms`, `partial`), `MediatedFieldCatalogue`, kiểu `PartialEntity`
  vào `src/integration/models.py` (TS-U2-5), cạnh các hợp đồng U1 đang có.
- Tách nhánh lỗi cho đúng TS-U2-9 và SR-U2-10; giữ nguyên câu lỗi nêu `field_name` + `source_column`
  (BR2.8); ánh xạ `error_code` theo bảng ở `security-requirements.md` §3 (phần lớn lỗi khai báo sẽ là
  `unknown` — chấp nhận, không thêm mã trong đợt này).
- Cập nhật **cùng một thay đổi** với C1/C2/C6 trong `inception/contract-design/contract-summary.md`
  (đã cộng thêm ngày 2026-11-07): hai kiểu lỗi, `elapsed_ms`, `partial` — luật "cập nhật mọi nơi khai
  cùng một sự thật" của dự án.
- Không thêm lời gọi vào `src/pipeline/stages.py` và không chạm `micro_batch`: đơn vị là thư viện, bên gọi
  quyết định khi nào nạp và có truyền `logger` hay không (khác U4, vốn phải chạy một lần trong pipeline).
- Không sửa `src/integration/query.py`, `load.py`, `card.py`: chúng đã có mẫu `logger` riêng và không
  thuộc phạm vi đơn vị này.
- Một tệp test cho mỗi tệp chạm tới (NFR2.2); không sửa test hình dạng dashboard — hình dạng đích là **4 tab, 8 callback, 4 thẻ + 1 vùng**; U6 sở hữu test hình dạng.
