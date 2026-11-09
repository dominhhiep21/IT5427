# Functional Design — u1-thin-slice

Lát cắt mỏng: một thực thể `don_hang` → một truy vấn viết lại → một thẻ trên tab "Tích hợp".

## Q1. [Kỹ thuật] Truy vấn của lát cắt cần những trường nào của `don_hang`?

Đây là tập trường tối thiểu của thực thể; các trường khác để đơn vị sau thêm.

- A. Mã đơn, ngày đặt, trạng thái đơn
- B. Mã đơn, ngày đặt, trạng thái đơn, mã khách
- C. Mã đơn, ngày đặt, trạng thái đơn, mã khách, bang giao
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Q2. [Kỹ thuật] Truy vấn đếm đơn ở trạng thái nào?

Con số trên thẻ phụ thuộc vào lựa chọn này.

- A. Chỉ đơn `delivered` (khớp định nghĩa KPI hiện có)
- B. Tất cả trạng thái, tách riêng từng trạng thái
- C. `delivered` và `shipped`
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q3. [Sản phẩm] Thẻ trên tab hiển thị gì?

- A. Một con số tổng và số đơn theo từng tháng trong 12 tháng gần nhất
- B. Chỉ một con số tổng
- C. Chỉ bảng theo tháng, không có tổng
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Trường tối thiểu của `don_hang`: mã đơn, ngày đặt, trạng thái đơn, mã khách, bang giao.
- Truy vấn đếm đơn ở **tất cả** trạng thái, tách riêng từng trạng thái (không lọc ngầm).
- Thẻ hiển thị một con số tổng và số đơn theo từng tháng trong 12 tháng gần nhất.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
