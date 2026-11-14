# Câu hỏi — Hợp đồng giữa các đơn vị

## Q1. [Tech] Cơ chế hợp đồng giữa U1, U2, U3

A. Dùng chung một mô-đun Python định nghĩa kiểu dữ liệu; các đơn vị import kiểu đó
B. Giao tiếp qua REST nội bộ
C. Chỉ ràng buộc bằng tệp JSON và hàm đọc, không có kiểu dùng chung
X. Other (please specify)

[Answer]: A

## Q2. [Tech] Ai sở hữu đặc tả báo cáo

A. U1 sở hữu toàn bộ đặc tả, kể cả khối mô hình
B. U1 sở hữu khung và khối thống kê; U2 sở hữu đặc tả khối mô hình
C. U3 sở hữu vì là bên đọc
X. Other (please specify)

[Answer]: B

## Q3. [Tech] Chính sách phiên bản của tệp báo cáo

A. Có trường `version`; đổi cấu trúc thì tăng số, tab từ chối bản không khớp
B. Không đặt phiên bản, chỉ ghi thời điểm sinh
C. Ghi cả `version` và thời điểm sinh, nhưng tab chỉ cảnh báo khi lệch
X. Other (please specify)

[Answer]: A

## Q4. [Product] Khi báo cáo thiếu một khối

A. Hàm đọc trả trạng thái "một phần" kèm khối thiếu; tab hiện phần có và ghi rõ phần thiếu
B. Coi là lỗi, không hiện gì
C. Bỏ qua im lặng
X. Other (please specify)

[Answer]: A

## Q5. [Tech] Chính sách lỗi, thời gian chờ, thử lại ở biên

A. Không áp dụng: các đơn vị gọi hàm trong cùng tiến trình, không có mạng
B. Có thử lại khi đọc tệp thất bại, tối đa 2 lần
C. Khác — mô tả
X. Other (please specify)

[Answer]: A

## Q6. [Tech] Cách ghi danh sách kiểm định bị bỏ qua trong khối thống kê

Bối cảnh: câu trả lời Q4 buộc mỗi kiểm định không chạy được phải hiện ra kèm lý do, nhưng hợp đồng C1 hiện không có chỗ nào chứa. Đây là điểm làm Functional Design của U1 bị chặn.

A. Thêm trường `skipped` vào `StatsBlock`, là danh sách các cặp `{test, reason}`
B. `skipped` là dict, khoá theo tên kiểm định, giá trị là lý do
C. Một trường `notes` dạng văn bản tự do liệt kê các kiểm định bị bỏ qua
X. Other (please specify)

[Answer]: A

## Q7. [Tech] Chỗ ghi số đơn bị loại khi so sánh bang

Bối cảnh: so sánh hai tỉ lệ chỉ dùng bang có tối thiểu 100 đơn đã giao; các bang bị loại và số đơn của chúng hiện không được ghi lại, nên US1.1 thiếu dữ kiện để kiểm.

A. Mỗi `ComparisonResult` mang thêm trường `excluded` là tổng số đơn của các bang bị loại
B. `StatsBlock` có thêm trường `excluded_states`, danh sách `{state, delivered_orders}` của các bang bị loại
C. Chỉ ghi trong `skipped` của Q6, không thêm trường riêng
X. Other (please specify)

[Answer]: A

## Q8. [Tech] Tab đọc bản báo cáo phiên bản cũ sau khi tăng phiên bản

Bối cảnh: đổi cấu trúc buộc tăng `REPORT_VERSION` từ 1 lên 2 theo chính sách thay đổi của hợp đồng. Cần chốt tab xử lý tệp phiên bản 1 còn sót lại thế nào.

A. Tab chỉ chấp nhận phiên bản 2; bản 1 trả trạng thái `loi` kèm thông điệp "chạy lại tầng stats"
B. Tab đọc được cả 1 và 2 trong giai đoạn chuyển tiếp, bản 1 hiện thiếu các trường mới
C. Không cần xử lý: xoá tệp cũ khi triển khai
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- Q1: dùng chung một mô-đun Python định nghĩa kiểu dữ liệu; các đơn vị import kiểu đó
- Q2: U1 sở hữu khung và khối thống kê; U2 sở hữu đặc tả khối mô hình
- Q3: có trường `version`; đổi cấu trúc thì tăng số, tab từ chối bản không khớp
- Q4: hàm đọc trả trạng thái "một phần" kèm khối thiếu; tab hiện phần có và ghi rõ phần thiếu
- Q5: không áp dụng chính sách lỗi mạng; các đơn vị gọi hàm trong cùng tiến trình
- Q6: `StatsBlock` có thêm trường `skipped`, là danh sách các cặp `{test, reason}` ghi mọi kiểm định không chạy được
- Q7: mỗi `ComparisonResult` mang thêm trường `excluded` là tổng số đơn đã giao của các bang bị loại
- Q8: tab chỉ chấp nhận phiên bản 2; tệp phiên bản 1 trả trạng thái `loi` kèm thông điệp chạy lại tầng `stats`

- Looks correct
- Request changes

[Answer]: Looks correct

