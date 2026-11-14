# SLO Report

Nguồn: `../observability-setup/slo-config.md`, `../observability-setup/dashboards.md`, `../observability-setup/alarms.md`, `../deployment-execution/deployment-log.md`, `../performance-validation/test-results.md`, `../incident-response/incident-plan.md`.

## Không có SLO để báo cáo tuân thủ, và đó là kết luận chứ không phải thiếu sót

`slo-config.md` của `observability-setup/` đã chốt: không có SLO vì không có **mẫu số**. Một tiến trình chạy theo lệnh 3,5 giây rồi kết thúc không có "99,9% trong 30 ngày" để đo — không có request, không có thời gian phục vụ, không có error budget.

Báo cáo này vì vậy không thể là "SLO đạt 99,95%, budget còn 78%". Nó là báo cáo **mốc nghiệm thu so với thực đo**, và mọi con số dưới đây đến từ `performance-validation/test-results.md`.

## Mốc nghiệm thu so với thực đo

| Mốc | Ngưỡng | Thực đo | Dư địa |
|---|---|---|---|
| Tầng `stats` (toàn tiến trình) | < 300 s | **3,49–3,70 s** | 81× |
| Tầng `stats` (chỉ tính toán) | < 300 s | **2,33 s** (lần chạy cuối) | 129× |
| Một phép kiểm định | < 60 s | **78,6–244,8 ms** | ≥ 245× |
| Huấn luyện mô hình | < 900 s | **1,56 s** | 577× |
| Đỉnh bộ nhớ của tầng | < 2.048 MB | **8,45 MB** | 242× |
| Tab kết quả dựng | < 1 s | **0,92–1,16 ms** | ≥ 860× |
| Độ phủ test | ≥ 80% | **92,45%** | +12,45 điểm |
| Hồi quy KPI | 5 KPI baseline không đổi | khớp cả năm sau khi dựng lại toàn bộ | — |

## Mục duy nhất không đạt, và nó không phải mốc vận hành

| Mục | Mốc | Thực đo | Trạng thái |
|---|---|---|---|
| AUC mô hình | ≥ 0,70 (FR2.3) | **0,5133** | **không đạt**, ghi bằng `auc_below_target = true`, hiện trên tab |

Đây là **mục tiêu chất lượng mô hình**, không phải SLO vận hành: nó không đo hệ thống chạy có đúng không mà đo mô hình dự báo có tốt không. Trộn hai loại này vào cùng một báo cáo là cách để một con số đỏ làm lu mờ một hệ thống xanh — và ngược lại.

## Không có error budget, và điều đó nói gì

Error budget chỉ có nghĩa khi có cam kết dịch vụ để tiêu. Ở đây cam kết duy nhất là **"năm KPI baseline không đổi"**, và nó là nhị phân: hoặc khớp, hoặc pipeline dừng. Không có vùng đệm nào để "tiêu dần".

Hệ quả thực tế: không có chính sách "đóng băng tính năng khi budget cạn", vì không có budget. Cái thay thế là `KpiReconciler` — nó không cho phép trôi, nên không cần một cơ chế quản lý trôi.

## Sức khoẻ sau khi dựng lại toàn bộ

Lần chạy dùng làm bằng chứng: xoá-trạng-thái-tương-đương bằng cách chạy lại `run --stage all` (**28,86 s**, sáu tầng đều `success`) rồi `run --stage stats` (**2,33 s**, `success=True`). Sau đó đọc lại báo cáo:

| Trường | Giá trị | So với trước khi dựng lại |
|---|---|---|
| `version` | 2 | không đổi |
| `stats.late_rate.rate` | 0,0811 | không đổi |
| `model.auc` | 0,5133 | không đổi |
| `model.threshold` | 0,4 | không đổi |
| `train_n + test_n` | 64.322 + 32.156 | không đổi |

Đó là định nghĩa vận hành của "không trôi": dựng lại từ `dataset/` cho ra đúng cùng con số.

## Điều kiện để báo cáo này trở thành SLO thật

Nếu đợt cải thiện đặc trưng biến mô hình thành một API có người gọi từ ngoài (mức B — dự đoán tương tác), lúc đó mới có lưu lượng, có độ trễ theo phân vị, có tỉ lệ lỗi. Báo cáo này phải được **viết lại từ đầu** kèm cửa sổ đo và mẫu số — không phải đổi nhãn "mốc nghiệm thu" thành "SLO".
