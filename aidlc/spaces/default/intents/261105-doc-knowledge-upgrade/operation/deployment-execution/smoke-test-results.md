# Smoke Test Results — local release 2026-11-09

## 1. Kiểm tra khói máy kiểm được

| Kiểm tra | Cách kiểm | Kết quả |
|---|---|---|
| Pipeline dựng được toàn bộ dữ liệu | `python -X utf8 -m src.pipeline run --stage all` | `success=True`, 6/6 tầng |
| Cổng chất lượng dữ liệu | `QualityGate` chế độ `full` trong pipeline | xanh |
| Cổng KPI | `KpiReconciler` 5 chỉ số | xanh, lệch 0 |
| Tệp kết quả ghép đọc được | `integration.linkage.completed` + tệp `data/integration/linkage-*.json` | sinh tệp, `elapsed_ms` 3,98 s |
| App dựng được với cấu hình thật | `create_app(load_config())` trong `test_dashboard_smoke.py` | 4 tab, 8 callback, 4 thẻ + 1 vùng |
| Vùng số liệu có mặt trong layout | test `test_integration_tab_holds_the_thin_slice_region` | có, trạng thái "Chưa chạy" |
| Số trên vùng khớp phép tính độc lập | `tests/unit/test_integration_correctness.py` | 0 sai lệch |

## 2. Kiểm tra khói phải làm bằng mắt

| Kiểm tra | Trạng thái |
|---|---|
| Mở `http://127.0.0.1:8050`, tab "Tích hợp" hiện bốn thẻ + vùng `don-theo-thang` | **chưa chạy trong phiên này** |
| Bấm "Chạy truy vấn", vùng hiện tổng số đơn và bảng theo tháng/trạng thái | **chưa chạy** |
| Bảng nguồn, bảng lược đồ, màn hình chi tiết hiển thị đúng tiếng Việt có dấu | **chưa chạy** |

Ba mục trên không thể tự động hoá trong đợt này; chúng là điều kiện còn lại trước khi coi lần phát hành là hoàn tất.

## 3. Dấu hiệu phải quay lui (nếu gặp khi kiểm mắt)

| Dấu hiệu | Hành động |
|---|---|
| Vùng báo `Lỗi` kèm "Không đọc được dữ liệu nguồn" | kiểm `dataset/` còn nguyên; chạy lại pipeline |
| Vùng báo `Lỗi` kèm "Không chạy được truy vấn" | đọc `logs/*.jsonl` mục `integration.query.failed` |
| Tab không mở, dashboard trắng | kiểm `logs/` có lỗi `integration.tab.*`, chạy lại `pytest tests/unit/test_dashboard_smoke.py` |
| Số hiện ra nhưng khác lần trước | **không** quay lui mù: chạy `pytest tests/unit/test_integration_correctness.py -m slow` để đối chiếu độc lập |
