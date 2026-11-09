# Cross-Unit Traceability — Olist integration upgrade

Sáu đơn vị Construction, hợp đồng giữa chúng, và bằng chứng kiểm chứng.

## 1. Đơn vị và mã nguồn

| Đơn vị | Gói mã | Tệp test chính | Trạng thái cổng |
|---|---|---|---|
| u1-thin-slice | `src/integration/{card,load,models,query,schema}.py` | `tests/unit/test_integration_{card,load,model,query,schema,correctness}.py` | duyệt (skeleton + unit) |
| u2-mediated-schema | `src/integration/schema.py`, `config/mediated-schema.yaml` | `tests/unit/test_integration_schema.py` | duyệt |
| u3-query-rewriter | `src/integration/rewrite.py`, `src/common/kpis.py` | `tests/unit/test_integration_rewrite.py`, `test_common_kpis.py` | duyệt |
| u4-record-linkage | `src/linkage/{index,models,result,score}.py` | `tests/unit/test_linkage_*.py` | duyệt |
| u5-source-selector | `src/integration/selector.py`, `config/integration-sources.yaml` | `tests/unit/test_integration_selector.py` | duyệt |
| u6-integration-ui | `src/integration/tab.py`, `src/dashboard/app.py`, `config/integration-tab.yaml` | `tests/unit/test_integration_tab.py`, `test_dashboard_smoke.py` | duyệt |

## 2. Hợp đồng và nơi tiêu thụ

| Hợp đồng | Nhà cung cấp → người dùng | Bằng chứng tiêu thụ thật |
|---|---|---|
| C1 | U2 → U3 | `load_schema` trả `MediatedSchemaView` có `elapsed_ms` + `partial`; `rewrite` kiểm bảng/cột theo lược đồ |
| C2 | U2 → U5, U3 | `MediatedFieldCatalogue` — danh mục `entity.field`; U5 đối chiếu mọi mã trường với danh mục |
| C3 | U5 → U3 | `_checked_selection` dùng `selected_sources[0].tables`: nguồn thắng phải khai đủ bảng mẫu truy vấn đọc, thiếu → `SchemaError` (khoá bằng 2 test) |
| C4 | U3 → U6 | `QueryRunResult` mang `elapsed_ms`, `row_count`, `rewrite_plan`, `kpi_comparison`; tab hiển thị |
| C5 | U4 → U6 | `data/integration/linkage-<customer\|seller>.json`; `tab.py` đọc qua `load_linkage_result`, thiếu tệp là trạng thái rỗng, tệp hỏng là lỗi |
| C6 | U2 → U6 | `load_schema` trong màn hình lược đồ; `partial` hiển thị thành "một phần" |
| C7 | U5 → U6 | `SourceCatalogue` gồm hồ sơ, quyết định, `query_fields`, `pending_query_id`; bảng nguồn hiển thị lý do bằng chữ |
| C8 | U1 → U2 | `config/mediated-schema.yaml`: ba thực thể, danh sách bản ghi có `source_column`/`data_type`/`loaded`; U2 đọc và kiểm |
| C9 | U1 → U6 | `config/integration-tab.yaml`: bốn `card_ids` + `result_region_ids: [don-theo-thang]`; U6 dựng **mọi** vùng trong danh sách |

## 3. Yêu cầu → đơn vị → bằng chứng

| Nhóm yêu cầu | Đơn vị | Bằng chứng |
|---|---|---|
| FR1.x (lược đồ trung gian) | U1, U2 | `test_integration_schema.py`, `test_u2_end_to_end.py` |
| FR2.x (viết lại truy vấn, sai lệch 0) | U3 | `test_integration_rewrite.py` (KPI + dung sai), `test_u3_end_to_end.py` |
| FR3.x (ghép bản ghi) | U4 | `test_linkage_*.py`, `test_u4_end_to_end.py` |
| FR4.x (chọn nguồn) | U5 | `test_integration_selector.py` |
| FR5.x (tab Tích hợp) | U1, U6 | `test_integration_tab.py`, `test_dashboard_smoke.py` |
| NFR1 (hiệu năng) | U1, U3, U6 | test hiệu năng ngưỡng cứng 2 giây; số đo thật ở `test-results.md` |
| NFR2/NFR3 (phủ, lint) | toàn bộ | `--cov-fail-under=80` (90,69%), `ruff` sạch |
| NFR4 (tiếp cận) | U6 | rà tay + token CSS; chưa có test tự động (ghi ở `test-results.md` §6) |
| NFR5 (bảo đảm dữ liệu) | U1, U4, U5, U6 | pipeline 6/6 tầng + `KpiReconciler` xanh; cổng đối chiếu độc lập của lát cắt |
| NFR6 (local, UTF-8) | toàn bộ | rà mã: không `urllib`/`requests`/`socket`; mọi lệnh chạy `-X utf8` |

## 4. Thay đổi xuyên đơn vị trong đợt này

| Thay đổi | Vì sao | Đơn vị bị ảnh hưởng |
|---|---|---|
| C9 thêm `result_region_ids` | Người làm yêu cầu số liệu lát cắt hiện trên tab | U1 (khai), U6 (dựng), U3 (cộng thêm vùng sau) |
| C8 chốt hình dạng bản ghi | Hợp đồng cũ `fields: list[str]` không đủ cho U2 | U1 (bàn giao), U2 (đọc), U3 (dùng) |
| C3 được tiêu thụ thật | Trước đó chọn nguồn khác vẫn ra cùng SQL | U3 (kiểm), U5 (khai `tables`) |
| Ánh xạ truy vấn→trường có test khoá | Ba bản sao không có kiểm bằng nhau | U3, U5 |

## 5. Điểm nối chưa có test tự động

- **C9 → nhiều vùng**: cơ chế duyệt `result_region_ids` có test cho *một* vùng và cho *id lạ*; chưa có test với hai vùng cùng lúc vì hiện chỉ có một vùng thật.
- **C5 ↔ U4**: tab đọc tệp kết quả ghép, nhưng không có test nào chạy U4 rồi đưa tệp thật vào tab; test dùng payload dựng tay.
