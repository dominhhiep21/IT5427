# Decision Log — Ideation

Nguồn: câu trả lời trong `../intent-capture/`, `../market-research/`, `../feasibility/`, `../scope-definition/`, `../team-formation/`, `../rough-mockups/` và artifact tương ứng.

## Quyết định về vấn đề và mục tiêu

| Mã | Quyết định | Nguồn |
|---|---|---|
| **D-01** | Đợt này sửa mô hình bằng **đặc trưng và khung dự đoán**, không bằng cách hạ mốc hay đổi thước đo | `intent-statement` (Q1 = D) |
| **D-02** | Đối tượng là **người học / nhóm làm đồ án**, không phải một nhóm người dùng vận hành | Q2 = D |
| **D-03** | Tiêu chí chất lượng: AUC **≥ 0,70** và **> baseline đo lại**; mốc 0,70 là mục tiêu hiện tại, hạ mốc là lựa chọn **chưa chốt** (Q15 = D) | Q3, Q15, Q18 |
| **D-04** | Nếu không đạt 0,70, người làm quyết định **ngay ở Build and Test** và ghi vào record (Q19 = A) | Q19 |
| **D-05** | Thêm **mốc sàn 0,55 trong CI**, phải xem lại sau khi đo baseline (Q20 = B) | Q20 |

## Quyết định về khung và dữ liệu

| Mã | Quyết định | Nguồn |
|---|---|---|
| **D-06** | Khung dự đoán: **lúc bàn giao cho đơn vị vận chuyển** (Q4 = B) | Q4 |
| **D-07** | Đơn vị dự đoán: **mỗi dòng hàng** (Q5 = A, Q11 = A) | Q5, Q11 |
| **D-08** | Danh sách cấm giữ hiệu lực; **nới đúng hai cột mốc** (`order_approved_at`, `order_delivered_carrier_date`), chỉ ở dạng **số ngày** (Q6 = A, Q17 = C) | Q6, Q17 |
| **D-09** | Chia tập theo **`order_id`**, mốc **2018-04-01** trên **ngày đặt hàng** (Q4 = A ở feasibility) | feasibility Q4 |
| **D-10** | Chỉ chấm AUC trên đơn **đã có carrier date**; lọc 2 dòng thiếu và ghi rõ số bị lọc (Q3 = A) | feasibility Q3 |
| **D-11** | **Nới mart** thay vì đọc cleaned: thêm cột, **không đổi số dòng** (Q1 = A) | feasibility Q1 |
| **D-12** | **Đo lại baseline** là bước đầu tiên của đợt (Q21 = A) | Q21 |

## Quyết định về mô hình và kỹ thuật

| Mã | Quyết định | Nguồn |
|---|---|---|
| **D-13** | Chạy **cả** logistic và `HistGradientBoosting` trên cùng đặc trưng (Q2 = C ở market research) | market-research Q2 |
| **D-14** | **`D-13` bị đảo một phần**: mô hình **triển khai là logistic**, vì cần hệ số để hiện mức đóng góp; cây vẫn chạy nhưng chỉ để **báo cáo**, và con số của nó phải có trong record (Q3 = B, Q4 = A ở rough mockups) | rough-mockups Q3, Q4 |
| **D-15** | **Lưu mô hình** vào `data/models/` + JSON mô tả đặc trưng và phiên bản thư viện (Q2 = A ở feasibility) | feasibility Q2 |
| **D-16** | Không thêm phụ thuộc nào; không SHAP; đóng góp tính từ hệ số logistic | `constraint-register` TC-01 |

## Quyết định về giao diện

| Mã | Quyết định | Nguồn |
|---|---|---|
| **D-17** | Khối dự đoán là **mục thứ tư** trong tab có sẵn, `H3`, không thêm tab (Q1 = A) | rough-mockups Q1 |
| **D-18** | **Sáu trường + một ô ngày** (bảy ô); phần còn lại mặc định và hiện rõ (Q2 = A) | rough-mockups Q2 |
| **D-19** | Kết quả: xác suất · so ngưỡng · quyết định · **ba đóng góp log-odds** (Q3 = B) | rough-mockups Q3 |
| **D-20** | Không thêm token màu; phân biệt kết quả bằng chữ; một vùng `aria-live` duy nhất | `wireframes` |

## Quyết định về phạm vi và đội

| Mã | Quyết định | Nguồn |
|---|---|---|
| **D-21** | Biên phạm vi: không thuật toán ngoài `scikit-learn`, không API, không đụng tab khác (Q1 = A ở scope) | scope Q1 |
| **D-22** | **Không cắt gì** — cả ba đơn vị đều Bắt buộc (Q2 = C) | scope Q2 |
| **D-23** | Không có mốc thời gian cứng (Q3 = A) | scope Q3 |
| **D-24** | **Ba Bolt**, một đơn vị mỗi Bolt (Q2 = A ở team-formation) | team Q2 |
| **D-25** | Nguồn lực **5–10 giờ/tuần** (Q1 = B) | team Q1 |

## Quyết định ở cổng này

| Mã | Quyết định | Nguồn |
|---|---|---|
| **D-26** | Xác nhận mục tiêu và phạm vi, giữ nguyên (Q1 = A) | approval Q1 |
| **D-27** | Chấp nhận **R-01** (AUC có thể không đạt 0,70) và **R-08** (chia tập theo ngày đặt trong khi dự đoán lúc bàn giao) (Q2 = A) | approval Q2 |
| **D-28** | Cam kết **5–10 giờ/tuần, ba Bolt** cho Construction (Q3 = A) | approval Q3 |

## Điều log này cho thấy

Ba quyết định bị **đảo trong cùng một đợt** — và cả ba đều được ghi lại chứ không bị viết đè: D-13 → D-14 (thuật toán), D-03 (mốc 0,70 từ "không hạ" về "chưa chốt"), và biên phạm vi ở D-21 (trước đó là "không loại trừ gì"). Một log không ghi các lần đảo là một log chỉ kể chuyện êm.
