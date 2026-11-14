# Câu hỏi — Scope Definition

## Q1. Danh sách "Ngoài phạm vi" của đợt này

Q9 ở Intent Capture trả lời "không loại trừ gì", nên đợt này hiện **không có** biên nào để giữ. Không có biên thì mọi mở rộng về sau đều không bị nhận ra là thay đổi phạm vi.

- A. Chốt biên tối thiểu: **không thêm thuật toán ngoài `scikit-learn`**, **không làm API dự đoán**, **không đụng tab nào ngoài "Kết quả phân tích"**
- B. Chỉ loại API dự đoán; thuật toán và các tab khác để mở
- C. Giữ nguyên "không loại trừ gì" như Q9
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Nếu không đủ thời gian, phần nào được cắt trước

Ba phần của đợt phụ thuộc nhau: nới mart → đặc trưng + mô hình → giao diện dự đoán.

- A. Cắt giao diện trước: chỉ làm đến mô hình và báo cáo, giao diện dự đoán để đợt sau
- B. Cắt theo kết quả: nếu AUC < 0,70 thì dừng sau phần mô hình, không làm giao diện
- C. Không cắt gì; làm đủ ba phần bất kể kết quả
- X. Khác (vui lòng nêu rõ)

[Answer]: C

## Q3. Có mốc thời gian cứng nào không

- A. Không có mốc cứng
- B. Có (nêu mốc ở phần trả lời)
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Ba câu đã trả lời. Bản tóm tắt để bạn xác nhận:

- **Biên phạm vi** [Q1 = A]: **không thêm thuật toán ngoài `scikit-learn`**, **không làm API dự đoán**, **không đụng tab nào ngoài "Kết quả phân tích"**.
- **Đường cắt khi thiếu thời gian** [Q2 = C]: **không cắt gì** — làm đủ ba phần bất kể kết quả. Đánh đổi đã ghi: không có đường cắt thoả thuận trước, nên nếu phải cắt thì đó là thay đổi phạm vi có khai báo.
- **Mốc thời gian** [Q3 = A]: không có mốc cứng.
- **Ba đơn vị, cả ba đều Bắt buộc**: U1 nới mart + đo baseline → U2 đặc trưng + hai mô hình + lưu → U3 giao diện + mốc sàn CI.
- **Tám điều kiện "xong"** đã liệt kê trong `scope-document.md`, gồm cả điều kiện có thể không đạt (AUC ≥ 0,70) và cách xử lý khi không đạt.
- **Danh sách "Ngoài phạm vi"** bảy dòng — thứ mà đợt trước không có, và là điểm R-05 đã nêu.

- Looks correct
- Request changes

[Answer]: Looks correct
