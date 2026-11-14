# Scope Document — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `../intent-capture/intent-statement.md`, `../feasibility/feasibility-assessment.md`, `../feasibility/constraint-register.md`, `../feasibility/raid-log.md`.

## Mục tiêu của đợt

Cứu mô hình dự đoán đơn giao trễ khỏi trạng thái "thua một baseline một cột": AUC 0,5133 hiện tại thấp hơn 0,5333 của một đặc trưng `customer_state` duy nhất [intent-statement]. Đợt này không thêm tab, không thêm tầng, không đổi kiến trúc — nó đổi **khung dự đoán, đơn vị dự đoán và đặc trưng**, rồi chứng minh kết quả bằng số.

## Trong phạm vi

| Mã | Hạng mục | Mức | Vì sao bắt buộc |
|---|---|---|---|
| **U1** | **Nới mart + đo baseline trong khung mới** — thêm 2 cột mốc vào `v_fact_orders`, thêm `seller_state` vào `v_fact_order_items`; dựng truy vấn quần thể grain dòng hàng; đo AUC của baseline `customer_state` trong đúng khung/đơn vị | **Bắt buộc** | không có mốc so thì mọi con số sau đều vô nghĩa [feasibility-assessment] |
| **U2** | **Đặc trưng mới + mô hình + lưu mô hình** — dựng đặc trưng từ khung bàn giao; huấn luyện **hồi quy logistic** (mô hình triển khai, vì cần hệ số để giải thích) và chạy thêm `HistGradientBoosting` **để báo cáo** đánh đổi; lưu mô hình logistic vào `data/models/` kèm JSON mô tả | **Bắt buộc** | đây là phần trả lời câu hỏi của cả đợt [intent-statement]. Ghi chú: chọn "chọn theo AUC" đã bị thay bằng "logistic triển khai, cây để báo cáo" ở Rough Mockups (Q4 = A) |
| **U3** | **Giao diện dự đoán + mốc sàn CI** — vùng nhập liệu trên tab "Kết quả phân tích" đưa ra điểm nguy cơ từ mô hình đã lưu; thêm mốc sàn 0,55 vào CI, xem lại sau khi có baseline đo lại | **Bắt buộc** | tiêu chí chất lượng thứ hai của đợt, và cổng chặn thoái hoá [intent-statement] |

Cả ba đều **Bắt buộc** — không có hạng mục "Nên có" nào. Đây là hệ quả trực tiếp của quyết định "không cắt gì", xem mục *Rủi ro phạm vi* bên dưới.

## Ngoài phạm vi

Chốt ở stage này để lần sau có mốc so:

| Điều **không** làm | Vì sao |
|---|---|
| Thêm bất kỳ thuật toán nào ngoài `scikit-learn` đã ghim (`xgboost`, `lightgbm`, `catboost`, mạng nơ-ron) | vi phạm ràng buộc không thêm phụ thuộc; và `HistGradientBoosting` đã đủ để trả lời câu hỏi "thuật toán có phải nút thắt không" [constraint-register] |
| API dự đoán (endpoint gọi từ ngoài) | giao diện dự đoán đặt trong tiến trình dashboard; thêm API là thêm bề mặt vận hành không ai yêu cầu |
| Đụng vào bốn tab còn lại của dashboard | chúng đang có test canh hình dạng; đổi là churn không đổi giá trị |
| Sửa `dataset/` hay chỉnh tay tệp trung gian | dữ liệu gốc bất biến [constraint-register] |
| Đổi 5 KPI baseline, số dòng 9 bảng nguồn, 11 bảng mart, 11 view | hợp đồng cứng [constraint-register] |
| Tối ưu CI (bỏ bước test nhanh, cache marts) | đã cân nhắc và từ chối ở đợt trước; ba trong bốn đề xuất đổi một chốt đúng lấy vài giây |
| Dựng SLO, dashboard giám sát, tracing | không có lưu lượng để đo; lý do cấu trúc đã ghi ở đợt trước |

Danh sách này **không** phải điều bạn đã nói "không" — nó là điều đợt này tự đặt biên để phát hiện trôi phạm vi. Nếu sau này cần vượt một dòng trong bảng, đó là một thay đổi phạm vi có ghi lại, không phải một quyết định lẻ trong lúc code.

## Thứ tự thi công

Phụ thuộc dữ liệu, không phải mức hấp dẫn của giao diện:

```
U1 (nới mart + baseline) → U2 (đặc trưng + mô hình + lưu) → U3 (giao diện + mốc sàn)
```

Lý do: U2 không có mốc so nếu U1 chưa đo baseline; U3 không có mô hình để nạp nếu U2 chưa lưu. Làm ngược thứ tự sẽ phải đoán một trong hai.

## Tiêu chí "xong" của đợt

| # | Điều kiện | Kiểm bằng |
|---|---|---|
| 1 | Baseline `customer_state` trong khung/đơn vị mới **được đo và ghi vào record** | số trong record, tái lập được |
| 2 | AUC của **mô hình logistic triển khai** ≥ 0,70 và **> baseline đo lại** | báo cáo `day-du` |
| 3 | Bốn con số của phần mô hình khớp số học: cỡ mẫu, số dòng trễ, ngưỡng, precision/recall | test trên dữ liệu thật |
| 4 | Giao diện đưa ra **cùng một điểm** cho cùng đầu vào qua các lần chạy và sau khi khởi động lại | phép kiểm lặp lại |
| 5 | Mốc sàn 0,55 có trong CI và **đã được xem lại** sau khi có baseline đo lại | `ci.yml` + ghi chú trong record |
| 6 | 5 KPI baseline, 9 bảng nguồn, 11 bảng mart, 11 view **không đổi số dòng** | `KpiReconciler`, `StarSchemaValidator` |
| 7 | Độ phủ ≥ 80% trên toàn bộ bộ test; `ruff` sạch | CI |
| 8 | Chạy hết chuỗi bốn bước và mở dashboard xem bằng mắt | lần chạy thật |

Điều kiện 2 có thể **không đạt** — và đó không phải lý do để bỏ đợt này. Khi không đạt, kết luận đúng là câu đã chốt ở `intent-statement`: người làm quyết định tại Build and Test, và quyết định đó ghi vào record.

## Rủi ro phạm vi

**Không có hạng mục nào để cắt.** Chọn "làm đủ ba phần bất kể kết quả" nghĩa là nếu thời gian cạn, không có đường cắt đã thoả thuận trước — người làm sẽ phải cắt tuỳ lúc, và đó đúng là cách phạm vi trôi mà không ai ghi lại.

Đổi lại, quyết định này tránh một cái bẫy khác: cắt giao diện khi AUC thấp sẽ biến "mô hình chưa đủ tốt" thành "không giao được gì", trong khi hai tiêu chí chất lượng đã được chốt là **độc lập**.

Nếu cần một đường cắt về sau, nó phải được khai thành thay đổi phạm vi — không được tự quyết trong lúc code.
