# Code Summary — u5-source-selector

## Gia cố C1/C7 (2026-11-09)

- **C7 sửa dữ liệu sai**: hồ sơ `partner_simulated` khai phủ `don_hang.bang_giao` nhưng `tables` chỉ có `olist_orders_dataset`; cột đó nằm ở `olist_customers_dataset`, nay đã thêm bảng này vào hồ sơ.
- **Khoá drift C1**: thêm `test_the_shipped_config_and_the_rewriter_agree_on_query_fields` — đọc `config/integration-sources.yaml` thật và khẳng định `query_fields` bằng đúng `TEMPLATE_MEDIATED_FIELDS` của U3, đồng thời `QUERY_IDS == TEMPLATE_IDS`. Trước đây ánh xạ tồn tại ba bản không có kiểm bằng nhau.
- **Khoá C7 ↔ bảng**: thêm `test_every_covered_field_belongs_to_a_table_its_profile_declares` — mỗi trường trong `covered_fields` phải có bảng nguồn nằm trong `tables` của chính hồ sơ.

Vì sao là test chứ không phải kiểm lúc nạp: bộ test dựng cấu hình rút gọn có chủ đích, nên phép kiểm bằng nhau đặt trong `load_source_catalogue` sẽ đỏ oan; đặt ở test tích hợp thì vẫn khoá được drift của cấu hình thật.


Nguồn: kế hoạch đã duyệt `code-generation-plan.md`, hướng dẫn test `unit-test-instructions.md`, và các lần chạy lệnh ghi trong tài liệu này.

## 1. Đã dựng gì

| Lớp | Tệp | Nội dung |
|---|---|---|
| Mô hình dữ liệu | `src/integration/models.py` | Thêm `SourceProfile` (tám trường), `SourceChoice` (`reason` bắt buộc), `SourceCatalogue` (`sources`, `choices`, `query_fields`, `partial_reason`, `pending_query_id`), `SourceSelection` (`catalogue` bắt buộc) — cả bốn `frozen=True`, danh sách là `tuple` |
| Truy cập dữ liệu (L1/L2) | `src/integration/selector.py` | `yaml.safe_load`; kiểm kiểu từng khoá; tập tên nguồn đóng; đúng một nguồn mô phỏng; `covered_fields` và ánh xạ truy vấn đối chiếu C2; `tables` đối chiếu `SOURCE_TABLES`; dựng câu `coverage` |
| Logic nghiệp vụ (L3) | `src/integration/selector.py` | Vị từ ứng viên (loại nguồn mô phỏng và nguồn không có dữ liệu); xếp hạng `(cost_level, latency_ms, source_name)`; sáu nhánh lý do loại; `NoSourceAvailableError` mang `missing_fields` + `catalogue`; `SourceSelection` mang `catalogue` mới và xoá `partial_reason`/`pending_query_id` |
| Nhật ký (L5) | `src/integration/selector.py` | Bốn sự kiện `integration.sources.loaded/partial/selected/failed`; mặc định `NullLogger` |
| Lỗi | `src/common/exceptions.py` | `NoSourceAvailableError(PipelineError)` mang `missing_fields`, `catalogue` |
| Cấu hình | `src/config.py`, `config.yaml`, `config/integration-sources.yaml` | `integration_sources_path` theo mẫu `mediated_schema_path`; tệp cấu hình ba nguồn + ba ánh xạ truy vấn |
| Test | `tests/unit/test_integration_selector.py` | 26 hàm test (48 ca thu thập) |
| CI | `.github/workflows/ci.yml` | Thêm tệp test vào `ruff format --check`; thêm bước đo phủ toàn bộ và bước smoke nạp cấu hình thật |

## 2. Kết quả kiểm chứng

| Cổng | Lệnh | Kết quả |
|---|---|---|
| Test của đơn vị + phủ mô-đun | `pytest tests/unit/test_integration_selector.py --cov=src.integration.selector --cov-fail-under=90` | **48 passed**, `selector.py` **99,50%** |
| Bộ nhanh toàn repo | `pytest -m "not slow"` | **268 passed, 7 deselected** — không hồi quy |
| Lint | `ruff check` trên năm tệp | sạch |
| Định dạng | `ruff format --check` trên năm tệp | sạch |
| Smoke trên tệp cấu hình thật | `load_source_catalogue(config/integration-sources.yaml, C2)` | in `3 3` — ba nguồn, ba truy vấn |

## 3. Quyết định chính

| Quyết định | Vì sao |
|---|---|
| `select_source` trả `SourceSelection` mang `catalogue`, nhánh lỗi mang `catalogue` và `missing_fields` | ADR-U5-S4: danh mục bất biến, bản mới đi kèm kết quả; không có kênh thứ hai |
| Inheritance: `selector.py` import `SOURCE_TABLES` từ `schema.py` | ADR-U5-S2; `schema.py` không import `selector.py` nên không có vòng |
| Giữ guard `SchemaError` khi nguồn thắng là mô phỏng | ADR-U5-S3; guard là bất biến phòng thủ, không chạm tới trong luồng bình thường nên còn **1 câu lệnh không phủ** (99,50%) |
| `rejected_sources` giữ thứ tự khai báo | ADR-U5-S6 chỉ đòi **kết quả chọn** tất định; thứ tự trình bày theo tệp cấu hình; test đảo thứ tự khẳng định kết quả chọn không đổi |

## 4. Chỉ tiêu đo được

| Mã | Ngưỡng | Đo được | Kết luận |
|---|---|---|---|
| NFR1.1 | ≤ 2 giây | `time.perf_counter` trong test, `<= 2000` ms | đạt |
| NFR2.2 | test riêng cho mô-đun mới | 26 hàm / 48 ca; `selector.py` 99,50% | đạt |
| NFR3.1 | 0 vi phạm | `ruff check` + `ruff format --check` sạch | đạt |
| NFR6.1 | không mạng | không import thư viện mạng | đạt |
| NFR2.1 / NFR5.1 / NFR5.2 | 80%, KPI, view | đo trên toàn bộ bộ test ở Build and Test | chưa kết luận ở bước này |

## 5. Điểm lệch kế hoạch

| # | Lệch | Ghi chú |
|---|---|---|
| 1 | `ruff format` cũng gộp bốn khối nhiều dòng có sẵn trong `src/config.py` | `team.md` cho phép dọn mã cũ theo từng tệp khi sửa tới; không đổi logic |
| 2 | 26 hàm test nhưng 48 ca | Kế hoạch chốt 20–26 **hàm**; các nhánh lỗi dùng `parametrize` |
| 3 | Hai phép kiểm thêm không có dòng riêng ở bảng §1.1 (danh sách mã trường của truy vấn phải là list chuỗi khác rỗng; `pending_query_id` phải có trong ánh xạ) | Đúng thứ tự ADR-U5-S1 để không lộ thành `NoSourceAvailableError`; đều có ca test |
| 4 | `rejected_sources` giữ thứ tự khai báo | Xem §3 |

## 6. Việc chưa làm

- **AC4.1.1** (bảng nguồn có năm cột) do `u6-integration-ui` hiển thị; `traceability.json` đánh `N/A`.
- **NFR2.1, NFR5.1, NFR5.2** đo ở Build and Test (bộ `slow`, `--stage all`, `KpiReconciler`).
- Bước 17–18 của kế hoạch do người điều phối hoàn tất: `code-summary.md` (tệp này), `source-manifest.json`, `traceability.json`.
