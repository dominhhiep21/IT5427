# Competitive Analysis

Nguồn: `../intent-capture/intent-statement.md`, `../../../261109-stats-and-models/operation/feedback-optimization/feedback-loop.md`, `src/analytics/model.py`, `requirements.txt`.

## Đối thủ của mô hình này không phải một sản phẩm — mà là các baseline

Dự án không có thị trường bên ngoài: không có khách hàng trả tiền, không có đối thủ thương mại, không có bản giá nào để so [intent-statement]. Nhưng "cạnh tranh" vẫn có nghĩa rất cụ thể ở đây: một mô hình chỉ đáng giữ nếu nó **thắng các cách làm rẻ hơn nó**. Đó là những gì bảng dưới so.

| # | Cách làm | Chi phí | AUC đã đo | Trạng thái |
|---|---|---|---|---|
| C1 | Không mô hình hóa: dùng tỉ lệ trễ trung bình 8,11% cho mọi đơn | 0 | 0,5 (tương đương đoán ngẫu nhiên) | baseline thô nhất, không cần mã |
| C2 | Một đặc trưng `customer_state` | vài dòng | **0,5333** | đã đo ở đợt trước, trên đơn, khung lúc đặt hàng |
| C3 | 11 đặc trưng + hồi quy logistic (hiện tại) | mô-đun đầy đủ | **0,5133** | đang chạy; **thua C2** |
| C4 | Đặc trưng mới, khung bàn giao, đơn vị dòng hàng | chưa biết | **chưa đo** | đợt này |

Ba dòng đầu là số đo thật lấy từ record của đợt trước [feedback-loop]. Dòng C4 là giả thuyết của đợt này và **chưa có bằng chứng** — nó chỉ đáng làm nếu vượt được C2 sau khi C2 được đo lại trong cùng khung [intent-statement].

## Điều bảng này nói, và điều nó không nói

Nó nói: **đối thủ thật của C4 là C2, không phải C3.** Đánh bại C3 là việc dễ và vô nghĩa — C3 đã tệ hơn C2. Một mô hình mới mà chỉ nhích lên 0,55 vẫn có thể thua C2 đo lại.

Nó **không** nói C4 sẽ thắng. Không có phép đo nào cho C4, và bảng này không được phép giả vờ có.

## Vì sao không có "đối thủ bên ngoài" để phân tích

Không có sản phẩm nào giải cùng bài toán trên cùng dữ liệu này, và không có nguồn trích dẫn nào trong workspace để khẳng định về thị trường dự đoán trễ giao hàng [intent-statement]. Một bảng so sánh với "các giải pháp trên thị trường" sẽ là bịa — ideation guardrail cấm đúng điều đó.

## Hệ quả cho đợt này

- Mốc so sánh bắt buộc là **C2 đo lại**, không phải con số 0,5333 trong bảng [intent-statement].
- C4 phải thắng C2 **và** vượt mốc 0,70; nếu chỉ đạt một trong hai thì kết luận là "chưa đủ", không phải "đã tốt hơn trước".
- Nếu C4 **không** thắng C2 dù đã thử hết đặc trưng, người làm chốt: được **một lần thử cuối** bằng mô hình cây trước khi kết luận, và kết luận đó — "hướng dự đoán này không cứu được bằng đặc trưng" — **được công bố**, không bị coi là thất bại cần che [intent-statement].
- Kết luận chỉ đúng cho giai đoạn 2016–2018; mọi con số phải đi kèm giới hạn đó [intent-statement].
