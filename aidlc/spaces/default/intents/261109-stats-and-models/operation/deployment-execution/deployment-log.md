# Deployment Log

Nguồn: `../deployment-pipeline/{cd-config.md,deployment-strategy.md}`, `../environment-provisioning/{environment-inventory.md,validation-report.md}`, `../../construction/build-and-test/test-results.md`.

## Lần triển khai được ghi lại

Không có bước "deploy" từ xa. "Triển khai" ở dự án này là chạy chuỗi bốn bước trên máy người làm sau khi mã và dữ liệu đã sẵn sàng. Dưới đây là lần chạy dùng làm bằng chứng nghiệm thu.

| Bước | Lệnh | Kết quả | Thời điểm |
|---|---|---|---|
| 0 | Đóng dashboard | không còn tiến trình giữ khoá `warehouse/olist.duckdb` | trước khi chạy |
| 1 | `pytest -m "not slow"` | **525 passed**, 12 deselected, 18,62 s | 2026-11-11 |
| 2 | `run --stage all` | success; `QualityGate` + `KpiReconciler` xanh | 2026-11-11 |
| 3 | `run --stage stats` | success; báo cáo `day-du`, hai khối đầy đủ | 2026-11-11 |
| 4 | mở dashboard, xem tab kết quả | 5 tab; ba khối; dải tóm tắt `8,11% · 96.478 · 0 · 0,5133` kèm "không đạt mốc 0,70"; không tràn ngang ở 1280px | 2026-11-11 |

Bộ đầy đủ kèm cổng phủ, chạy trong cùng đợt: **537 passed**, phủ **92,45%**, 281,85 s.

## Phiên bản triển khai

| Mục | Giá trị |
|---|---|
| Nhánh | `feature/analysis-and-models` |
| Phiên bản | commit hash của nhánh (chưa commit tại thời điểm ghi) |
| Mốc CHANGELOG | `v0.4.0` |
| Artefact | không có — mã nguồn là artefact |

## Trạng thái

**Đã triển khai và đã xác nhận bằng mắt.** Không có môi trường thứ hai để thăng cấp, nên không có bước tiếp theo nào để chờ.

## Điều không xảy ra, và vì sao

- Không có cửa sổ triển khai: không có ai khác dùng hệ thống.
- Không có thông báo cho người dùng: người dùng là người triển khai.
- Không có chuyển lưu lượng: một tiến trình duy nhất.
