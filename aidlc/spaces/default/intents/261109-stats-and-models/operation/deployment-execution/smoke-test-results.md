# Smoke Test Results

Nguồn: `deployment-log.md`, `../../construction/ci-pipeline/quality-gates.md`, `../../construction/build-and-test/test-results.md`.

## Kiểm tra khói sau triển khai

Ở dự án này "kiểm tra khói" không phải gọi một endpoint — không có endpoint. Nó là **hai cổng chạy trong bước 2** cộng **một lần xem bằng mắt ở bước 4**.

| # | Kiểm | Ngưỡng | Kết quả |
|---|---|---|---|
| S1 | `QualityGate` (21 check cấu trúc) | mọi check xanh | xanh |
| S2 | `QualityGate` chế độ `full` (9 check số dòng + 10 dị thường allowlist) | mọi check xanh | xanh |
| S3 | `KpiReconciler` (5 KPI, dung sai riêng) | doanh thu 15.419.773,75; 96.478 đơn; AOV 159,83; 7.826 trễ; 8,11% | khớp cả năm |
| S4 | Báo cáo đọc lại được | `read_report` trả `day-du` | `day-du`, hai khối |
| S5 | Tab hiện đúng | 5 tab, ba khối, dải tóm tắt, không tràn ngang ở 1280px | đạt |
| S6 | Số học trong khối mô hình | `train_n + test_n = 96.478`; `flagged + not_flagged = total` | khớp |

## Ba con số dùng làm chốt

| Số | Giá trị | Nguồn |
|---|---|---|
| Tỉ lệ trễ | 8,11% (7.826 / 96.478) | `late_rate` trong báo cáo |
| Cỡ mẫu mô hình | 64.322 + 32.156 | `split` trong khối mô hình |
| AUC | 0,5133 — **dưới mốc 0,70** | `counts.auc_below_target = true`, tab hiện "không đạt mốc 0,70" |

## Điều kiểm tra khói **không** nói

Nó không nói mô hình tốt. Nó chỉ nói hệ thống chạy đúng và các con số khớp nhau. Một mô hình có AUC 0,51 vẫn qua S1–S6, và đó là hành vi đúng: chất lượng mô hình là mục tiêu riêng, không phải điều kiện của kiểm tra khói.

## Kết luận

Sáu mục đều đạt. Không có hồi quy so với baseline, và không có ngưỡng nào bị nới để đạt.
