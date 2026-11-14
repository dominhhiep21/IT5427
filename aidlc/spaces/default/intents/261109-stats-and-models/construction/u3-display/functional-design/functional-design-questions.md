# Câu hỏi — Thiết kế chức năng cho u3-display

## Q1. [Product] Bộ chọn ngưỡng trên tab

Bối cảnh: `unit-of-work.md` giao U3 một "bộ chọn ngưỡng", nhưng hợp đồng C3 chỉ mang **một** ngưỡng đã chọn sẵn trong khối mô hình, kèm precision/recall tại đúng ngưỡng đó. Không có bảng theo từng nấc để chọn lại.

A. Không có bộ chọn: tab chỉ hiện ngưỡng đã báo cáo, kèm precision/recall — đổi lại phải sửa `unit-of-work.md`
B. Có bộ chọn nhưng chỉ hiện lại giá trị đã báo cáo, không tính toán gì
C. Thêm bảng nhiều nấc ngưỡng vào khối mô hình rồi mới có bộ chọn thật — phải tăng `REPORT_VERSION`
X. Other (please specify)

[Answer]: A

## Q2. [Design] Dải tóm tắt gồm những gì

Bối cảnh: US4.1 chỉ nói "thấy dải tóm tắt trước, rồi mục thống kê, rồi mục mô hình". Chưa chốt dải tóm tắt chứa thẻ nào.

A. Bốn thẻ: tỉ lệ trễ, doanh thu delivered, số đơn delivered, AUC kèm dấu đạt/không đạt
B. Ba thẻ: tỉ lệ trễ, AUC, và số kiểm định đã bỏ qua
C. Sáu thẻ: đủ năm KPI baseline cộng AUC
X. Other (please specify)

[Answer]: A

## Q3. [Product] Khi báo cáo thiếu khối mô hình

Bối cảnh: hàm đọc trả `mot-phan` với `missing = ("model",)`. Tab cần một hành vi, và nó khác với `rong` (chưa có tệp) và `loi` (tệp hỏng).

A. Hiện đầy đủ mục thống kê, và ở chỗ mục mô hình ghi rõ "chưa chạy bước mô hình" kèm lệnh cần chạy
B. Hiện một dải cảnh báo trên cùng, phần mô hình để trống hoàn toàn
C. Coi như lỗi, không hiện gì
X. Other (please specify)

[Answer]: A
