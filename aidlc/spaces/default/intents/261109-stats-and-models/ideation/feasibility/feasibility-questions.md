# Câu hỏi — Khả thi và ràng buộc

## Q1. [Tech] Phần mới phải gắn vào những đâu

Câu này chốt phạm vi tích hợp để đánh giá khả thi, không hỏi lại kiến trúc.

A. Chỉ thêm lệnh CLI mới, không đụng pipeline hiện có
B. Thêm lệnh CLI và gắn kết quả vào dashboard hiện có
C. Thêm lệnh CLI, dashboard, và thêm bước vào chuỗi `run --stage all`
D. Not yet defined
X. Other (please specify)

[Answer]: B

## Q2. [Tech] Máy chạy có cài thêm được thư viện từ internet không

Phần thống kê và mô hình cần thêm gói; nếu máy không ra được PyPI thì phải tính cách khác.

A. Có, cài trực tiếp từ PyPI bình thường
B. Có, nhưng phải qua mirror hoặc proxy nội bộ
C. Không, chỉ dùng được những gì đã cài
D. Not yet defined
X. Other (please specify)

[Answer]: A

## Q3. [Tech] Thời gian chạy chấp nhận được cho cả phần kiểm định và huấn luyện mô hình

A. Dưới 1 phút
B. Từ 1 đến 5 phút
C. Từ 5 đến 15 phút
D. Không giới hạn, miễn chạy đúng
X. Other (please specify)

[Answer]: D

## Q4. [Data] Dùng giai đoạn nào để huấn luyện mô hình

Dữ liệu 2016 chỉ có 329 đơn, nên dùng hay bỏ là một quyết định có ảnh hưởng tới mô hình.

A. Toàn bộ 2016-2018 như dữ liệu hiện có
B. Chỉ từ 2017 trở đi, bỏ 2016 vì quá ít đơn
C. Chỉ 2018, coi là giai đoạn gần nhất
D. Not yet defined
X. Other (please specify)

[Answer]: A

## Q5. [Tech] Cách chia dữ liệu huấn luyện và kiểm tra

A. Chia theo thời gian: huấn luyện trên giai đoạn sớm, kiểm tra trên giai đoạn muộn
B. Chia ngẫu nhiên theo tỉ lệ 80/20
C. Chia theo thời gian, và báo cáo thêm kết quả chia ngẫu nhiên để so sánh
D. Not yet defined
X. Other (please specify)

[Answer]: A

## Q6. [Product] Mốc thời gian của đợt này

A. Trong vòng 1 tuần
B. Từ 1 đến 2 tuần
C. Từ 2 đến 4 tuần
D. Chưa có mốc
X. Other (please specify)

[Answer]: A

## Q7. [Product] Có trở ngại nào bên ngoài mã nguồn không

A. Không có
B. Có, thời gian bị chia sẻ với môn khác hoặc kỳ thi
C. Có, máy hoặc môi trường có thể đổi giữa đợt
D. Not applicable
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- Q1: phần mới gồm một lệnh CLI mới và phần hiển thị trên dashboard hiện có
- Q2: máy cài thêm được thư viện trực tiếp từ PyPI
- Q3: không giới hạn thời gian chạy, miễn đúng
- Q4: huấn luyện trên toàn bộ dữ liệu 2016-2018
- Q5: chia theo thời gian, huấn luyện giai đoạn sớm và kiểm tra giai đoạn muộn
- Q6: mốc trong vòng 1 tuần
- Q7: không có trở ngại bên ngoài mã nguồn

- Looks correct
- Request changes

[Answer]: Looks correct

