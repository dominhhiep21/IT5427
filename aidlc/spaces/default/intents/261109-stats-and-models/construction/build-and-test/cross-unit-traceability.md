# Cross-Unit Traceability

Nguồn: ba tệp `traceability.json` của Code Generation, `../../../inception/units-generation/unit-of-work.md`, `../../../inception/requirements-analysis/requirements.md`, `../../../inception/contract-design/contract-summary.md`.

## Yêu cầu → đơn vị

| Yêu cầu | Đơn vị | Bằng chứng |
|---|---|---|
| FR1.1–FR1.5 (năm phép kiểm định) | u1-statistics | `src/analytics/statistics.py`, `tests/unit/test_analytics_statistics.py` |
| FR3.1, FR3.2 (một tệp báo cáo, ghi nguyên tử) | u1-statistics | `src/analytics/report.py`, `tests/unit/test_analytics_report.py` |
| FR2.1–FR2.4 (đặc trưng, chia tập, ngưỡng, cách chọn) | u2-model | `src/analytics/model.py`, `tests/unit/test_analytics_model.py` |
| FR4.1–FR4.3 (tab đọc theo thứ tự, trạng thái rỗng, token sẵn có) | u3-display | `src/dashboard/analysis_tab.py`, `tests/unit/test_dashboard_analysis_tab.py` |
| FR5.1 (tầng `stats` trong `run --stage`) | u1-statistics | `src/pipeline/stages.py`, `src/pipeline/cli.py`, `tests/unit/test_pipeline_stages.py` |
| FR5.2, FR5.3 (nhánh CI, README/CHANGELOG) | u1-statistics + Code Generation | `ci.yml`, `README.md`, `CHANGELOG.md`, `tests/unit/test_ci_config.py` |
| NFR1 (thời gian) | cả ba | đo trong test `slow` của từng đơn vị |
| NFR2 (phủ 80%) | cả ba | cổng phủ trong CI |
| NFR3 (không hồi quy) | u1-statistics | `KpiReconciler`, `StarSchemaValidator` trong `--stage all` |
| NFR4 (chất lượng mã) | cả ba | `ruff` + danh sách định dạng trong `ci.yml` |
| NFR5 (tiếp cận) | u3-display | `BR3.8`, `tests/unit/test_analysis_tab_contrast.py` |

## Hợp đồng dùng chung

| Hợp đồng | Bên cung cấp | Bên dùng | Kiểm ở đâu |
|---|---|---|---|
| C1 (kiểu báo cáo + hàm ghi), phiên bản 2 | U1 | U2 | `tests/unit/test_analytics_report.py`, `test_analytics_model.py` |
| C2 (hàm đọc, bốn trạng thái) | U1 | U3 | `tests/unit/test_analytics_report.py` (sáu mẫu), `test_dashboard_analysis_tab.py` (năm token) |
| C3 (khối mô hình, bảy trường) | U2 | U3 | `test_dashboard_analysis_tab.py` (thẻ AUC kèm dấu) |

## Chuỗi chạy đã kiểm

`--stage all` → `--stage stats` → tab đọc báo cáo. Test `slow` của cả ba đơn vị chạy trên dữ liệu thật và khẳng định lại các con số baseline, nên một đứt gãy ở bất kỳ mắt nào đều đỏ.

## Khoảng trống

Không có yêu cầu nào không có đơn vị nhận. Không có mã nào không truy được về một yêu cầu, trừ phần hạ tầng dev (`.venv`, script CI) — vốn không phải sản phẩm.
