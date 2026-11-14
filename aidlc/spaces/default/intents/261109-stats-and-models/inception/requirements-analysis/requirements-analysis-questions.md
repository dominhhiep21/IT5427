# Câu hỏi — Yêu cầu chức năng và phi chức năng

## Q1. [Data] Mức ý nghĩa và độ tin cậy cho các kiểm định

A. Mức ý nghĩa 0,05 và khoảng tin cậy 95%
B. Mức ý nghĩa 0,01 và khoảng tin cậy 99%
C. Không đặt, báo cáo giá trị p để người đọc tự diễn giải
X. Other (please specify)

[Answer]: A

## Q2. [Tech] Báo cáo kết quả gồm mấy tệp

A. Một tệp JSON chứa cả phần thống kê và phần mô hình
B. Hai tệp riêng: một cho thống kê, một cho mô hình
C. Ba tệp: thống kê, mô hình, và chỉ số đánh giá
X. Other (please specify)

[Answer]: A

## Q3. [Data] Ngưỡng cảnh báo của mô hình đơn trễ

A. Chọn từ đường cong precision/recall và báo cáo cả hai ở ngưỡng đã chọn
B. Cố định 0,5
C. Không đặt ngưỡng, chỉ báo cáo AUC
X. Other (please specify)

[Answer]: A

## Q4. [Tech] Giới hạn thời gian chạy

A. Kiểm định dưới 1 phút, huấn luyện mô hình dưới 5 phút
B. Kiểm định dưới 5 phút, huấn luyện dưới 15 phút
C. Không đặt giới hạn
X. Other (please specify)

[Answer]: B

## Q5. [Tech] Độ phủ test cho mô-đun mới

A. Giữ ngưỡng chung 80% cho toàn `src/`
B. Đặt 90% riêng cho mô-đun thống kê và mô hình
C. Không đặt riêng
X. Other (please specify)

[Answer]: A

## Q6. [Product] Cách xử lý khi báo cáo thiếu hoặc hỏng

A. Thiếu báo cáo thì hiện trạng thái rỗng kèm câu lệnh; báo cáo hỏng thì hiện trạng thái lỗi
B. Tự chạy lại phân tích khi mở tab
C. Ẩn mục đó, không báo gì
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- Q1: mức ý nghĩa 0,05 và khoảng tin cậy 95%
- Q2: một tệp JSON chứa cả phần thống kê và phần mô hình
- Q3: chọn ngưỡng cảnh báo từ đường cong precision/recall và báo cáo cả hai
- Q4: kiểm định dưới 5 phút, huấn luyện mô hình dưới 15 phút
- Q5: giữ ngưỡng phủ chung 80% cho toàn `src/`
- Q6: thiếu báo cáo thì hiện trạng thái rỗng kèm câu lệnh; báo cáo hỏng thì hiện trạng thái lỗi

- Looks correct
- Request changes

[Answer]: Looks correct

