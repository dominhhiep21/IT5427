# Câu hỏi — Ghi nhận & đóng khung ý định

## Sources

- [desc] Initial description: "bổ sung kiểm định thống kê và mô hình dự báo cho dự án Olist, đáp ứng yêu cầu đề bài về statistical calculations và ML/AI"
- [scope] Workflow-selected scope: `feature`.

## Q1. [Product] Trọng tâm của đợt này

Đề bài ghi "statistical calculations should be included" và "the use of machine learning/AI models is encouraged". Hai phần này có thể làm lệch nhau về công sức, nên cần chốt thứ tự.

A. Chỉ làm kiểm định thống kê, mô hình dự báo để đợt sau
B. Chỉ làm mô hình dự báo, kiểm định thống kê để sau
C. Làm cả hai, thống kê trước rồi tới mô hình
D. Làm cả hai, song song ngay từ đầu
E. Not yet defined
X. Other (please specify)

[Answer]: C

## Q2. [Product] Những kiểm định thống kê nào cần có (chọn tất cả nếu muốn)

Không phải kiểm định nào cũng đáng làm; mỗi loại cần một loại dữ liệu và một cách diễn giải riêng.

A. Khoảng tin cậy cho một tỉ lệ (ví dụ tỉ lệ giao trễ) và so sánh hai tỉ lệ giữa hai bang
B. Tương quan giữa hai biến số kèm khoảng tin cậy (ví dụ giá hàng và phí vận chuyển)
C. So sánh nhóm hoặc kiểm định phân phối (chi-square, t-test)
D. Phân rã mùa vụ của chuỗi doanh thu theo tháng
E. Làm cả bốn mục trên
X. Other (please specify)

[Answer]: E

## Q3. [Product] Mô hình dự báo nào cần xây

Dữ liệu hiện có nhãn cho bài toán đơn trễ, có chuỗi doanh thu theo tháng, và có mã khách để phân khúc.

A. Phân loại đơn hàng có nguy cơ giao trễ (nhãn sẵn: 7.826 đơn trễ trên 96.478 đơn đã giao)
B. Dự báo doanh thu theo tháng (chuỗi thời gian)
C. Phân khúc khách hàng bằng RFM và gom cụm
D. Làm cả A và B
E. Làm cả ba
X. Other (please specify)

[Answer]: A

## Q4. [Tech] Dùng thư viện nào cho phần mô hình

Quy ước dự án bắt ghim mọi phụ thuộc mới vào `requirements.txt` và ghi lý do, nên lựa chọn này ảnh hưởng tới cả đợt.

A. `scikit-learn`, ghim phiên bản và ghi lý do vào `requirements.txt`
B. Chỉ dùng `numpy` và `pandas` đã có, tự viết thuật toán
C. `scikit-learn` cho mô hình và `statsmodels` cho chuỗi thời gian
D. Not yet defined
X. Other (please specify)

[Answer]: A

## Q5. [Product] Kết quả phân tích và dự báo được dùng ở đâu

A. Một lệnh CLI mới, ghi báo cáo JSON vào `data/reports/`
B. Thêm vào dashboard hiện có (tab mới hoặc mục mới)
C. Cả hai: CLI ghi báo cáo, dashboard đọc lại để hiển thị
D. Not yet defined
X. Other (please specify)

[Answer]: C

## Q6. [Quality] Ngưỡng đánh giá mô hình

Một mô hình không có ngưỡng thì không nói được là đạt hay không đạt. Câu này chỉ áp dụng nếu có mô hình phân loại.

A. AUC tối thiểu 0,70 và báo cáo precision/recall ở ngưỡng cảnh báo
B. Chỉ báo cáo chỉ số, không đặt ngưỡng đạt
C. AUC tối thiểu 0,80
D. Chỉ áp dụng cho dự báo chuỗi thời gian, dùng MAE và MAPE
E. Not yet defined
X. Other (please specify)

[Answer]: A

## Q7. [Product] Ranh giới: đợt này không làm gì (chọn tất cả nếu muốn)

Kế hoạch đã chọn là `feature`. Câu này chỉ hỏi phạm vi sản phẩm của đợt, không hỏi lại kế hoạch.

A. Không dùng deep learning
B. Không làm real-time hay streaming thật
C. Không thêm API công khai hay xác thực người dùng
D. Không sửa dữ liệu gốc trong `dataset/`
E. Tất cả các mục trên
X. Other (please specify)

[Answer]: D

## Consolidated Summary Confirmation

- Q1: làm cả hai, kiểm định thống kê trước rồi tới mô hình dự báo
- Q2: làm cả bốn nhóm kiểm định (khoảng tin cậy và so sánh hai tỉ lệ, tương quan, so sánh nhóm/phân phối, phân rã mùa vụ)
- Q3: mô hình phân loại đơn hàng có nguy cơ giao trễ
- Q4: dùng `scikit-learn`, ghim phiên bản và ghi lý do vào `requirements.txt`
- Q5: kết quả dùng ở cả hai nơi — lệnh CLI ghi báo cáo JSON và dashboard đọc lại để hiển thị
- Q6: AUC tối thiểu 0,70, kèm precision/recall ở ngưỡng cảnh báo
- Q7: ranh giới đợt này chỉ loại trừ việc sửa dữ liệu gốc trong `dataset/`

- Looks correct
- Request changes

[Answer]: Looks correct

