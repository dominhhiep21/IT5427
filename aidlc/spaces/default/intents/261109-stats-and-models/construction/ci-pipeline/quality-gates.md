# Quality Gates

Nguồn: `ci-config.md`, `../build-and-test/test-results.md`, `../build-and-test/performance-test-instructions.md`, `aidlc/spaces/default/memory/project.md` (`## Testing Posture`).

## Cổng đang chặn merge

| # | Cổng | Ngưỡng | Có canh bằng test không |
|---|---|---|---|
| G1 | `ruff check .` | không lỗi | — (bản thân là cổng) |
| G2 | `ruff format --check` | mọi tệp trong danh sách sạch | `test_ci_config.py` canh danh sách khớp tệp thật |
| G3 | `--stage all` | `QualityGate` và `KpiReconciler` xanh | `test_u1_stats_end_to_end.py` |
| G4 | `--stage stats` | chạy được, báo cáo `day-du` | `test_u2_model_end_to_end.py` |
| G5 | Bộ nhanh | 525 passed | — |
| G6 | Phủ toàn bộ | **≥ 80%**, đo trên nhanh **và** `slow` | `--cov-fail-under=80` |
| G7 | Smoke cấu hình | nạp được `config/integration-sources.yaml` | — |

## Cổng **không** chặn merge, và vì sao

| Mục | Vì sao không phải cổng |
|---|---|
| AUC ≥ 0,70 | Đây là **mục tiêu chất lượng**, không phải điều kiện đúng/sai. Model hiện 0,5133 vẫn cho ra báo cáo hợp lệ, và tab ghi rõ "không đạt". Đặt làm cổng sẽ làm CI đỏ thường trực cho tới khi có đợt cải thiện — cổng đỏ thường trực là cổng bị bỏ qua |
| Thời gian chạy (NFR1.1, NFR5.5) | Máy CI khác máy phát triển; một cổng thời gian đỏ vì lý do không liên quan tới thay đổi |
| Bố cục 1280px | Không có trình duyệt trong CI; kiểm bằng mắt ở bước 4 chuỗi xác nhận |

## Vì sao phủ 80% đo trên toàn bộ bộ test

Bảy mô-đun `src/` chỉ có phần phủ đến từ bộ `slow`. Đo riêng bộ nhanh sẽ cho một con số thấp hơn thực tế và khuyến khích viết test nhanh vô nghĩa để bù. Ngưỡng không được hạ, và không được tách sang bộ nhanh.

## Điều kiện dừng khi đỏ

Dừng ngay ở bước đỏ đầu tiên trong chuỗi xác nhận cục bộ, không chạy tiếp để "xem còn gì nữa". Một lần chạy đỏ ở bước 2 làm mọi kết quả sau đó vô nghĩa, vì chúng đo trên dữ liệu chưa dựng đúng.
