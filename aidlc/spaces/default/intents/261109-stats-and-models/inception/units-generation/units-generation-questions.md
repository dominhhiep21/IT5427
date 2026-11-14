# Câu hỏi — Chia đơn vị công việc

Mỗi đơn vị công việc sẽ được thi công trọn vẹn theo thứ tự đã chốt (không có lát cắt mỏng), nên số đơn vị quyết định số vòng thi công.

## Q1. [Product] Chia thành bao nhiêu đơn vị

A. Ba đơn vị: thống kê, mô hình, hiển thị
B. Hai đơn vị: phần tính toán (thống kê + mô hình) và phần hiển thị
C. Năm đơn vị: thống kê, mô hình, ghi/đọc báo cáo, tầng pipeline, hiển thị
X. Other (please specify)

[Answer]: A

## Q2. [Tech] Đơn vị "thống kê" gồm những gì

A. Mô-đun kiểm định, thành phần ghi/đọc báo cáo, và tầng `stats` — đủ để chạy end-to-end
B. Chỉ mô-đun kiểm định; ghi/đọc báo cáo nằm ở đơn vị riêng
C. Chỉ mô-đun kiểm định; ghi/đọc báo cáo gộp vào đơn vị hiển thị
X. Other (please specify)

[Answer]: A

## Q3. [Product] Thứ tự thi công

A. Thống kê → mô hình → hiển thị, đúng thứ tự đã chốt
B. Thống kê → hiển thị → mô hình, để thấy giao diện sớm
C. Mô hình → thống kê → hiển thị
X. Other (please specify)

[Answer]: A

## Q4. [Tech] Có đơn vị riêng cho hạ tầng (CI, cấu hình, README) không

A. Không; gộp vào đơn vị đầu tiên
B. Có, một đơn vị thứ tư
C. Không; để cuối cùng, làm cùng đơn vị hiển thị
X. Other (please specify)

[Answer]: A

## Q5. [Product] Điều kiện xong của mỗi đơn vị

A. Có test end-to-end riêng xanh trên dữ liệu thật, cộng chuỗi xác nhận bốn bước
B. Chỉ cần test đơn vị xanh
C. Test end-to-end cho đơn vị đầu, các đơn vị sau chỉ test đơn vị
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- Q1: ba đơn vị — thống kê, mô hình, hiển thị
- Q2: đơn vị thống kê gồm mô-đun kiểm định, thành phần ghi/đọc báo cáo, và tầng `stats`
- Q3: thứ tự thống kê → mô hình → hiển thị
- Q4: không có đơn vị hạ tầng riêng; gộp vào đơn vị đầu tiên
- Q5: điều kiện xong là có test end-to-end riêng xanh trên dữ liệu thật, cộng chuỗi xác nhận bốn bước

- Looks correct
- Request changes

[Answer]: Looks correct

