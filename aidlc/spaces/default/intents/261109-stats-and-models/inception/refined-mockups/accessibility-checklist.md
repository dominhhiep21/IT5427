# Accessibility Checklist — Tab kết quả

Mức áp dụng: WCAG 2.1 AA, ngang các tab hiện có. [Q5]

## Cấu trúc

- [ ] Trang có đúng một `h1`; ba khối là `h2` theo thứ tự (A)(B)(C), không nhảy cấp.
- [ ] Vùng chính là `main`; thanh tab là `nav` có nhãn "Các tab báo cáo".
- [ ] Mỗi bảng có `caption` hoặc `aria-label` mô tả nội dung.
- [ ] Thứ tự tab (focus) đi theo thứ tự đọc: tab → dải tóm tắt → bảng thống kê → bộ lọc ngưỡng → bảng mô hình.

## Bàn phím

- [ ] Tab tới được mọi phần tử tương tác: nút tab, bộ chọn ngưỡng.
- [ ] Bộ chọn ngưỡng dùng được phím mũi tên, không cần chuột.
- [ ] Không có bẫy focus; thoát khỏi mọi vùng bằng Tab/Shift+Tab.

## Màu và tương phản

- [ ] Chữ thường đạt tương phản tối thiểu 4,5:1; chữ lớn 3:1.
- [ ] Trạng thái không chỉ dựa vào màu: mỗi trạng thái có biểu tượng và câu chữ.
- [ ] Số liệu trong bảng dùng chữ số đều bề rộng; số âm và số dương không phân biệt chỉ bằng màu.

## Trình đọc màn hình

- [ ] Khối trạng thái dùng `role="status"`; khối lỗi dùng `role="alert"`.
- [ ] Dải tóm tắt có nhãn cho từng ô, không chỉ con số trần.
- [ ] Bộ chọn ngưỡng có `aria-label` nêu đơn vị và khoảng giá trị.
- [ ] Bảng đọc được theo hàng và cột nhờ `th` đúng vị trí.

## Kiểm chứng

- [ ] Kiểm bằng trình duyệt thật: mở tab, đi hết bằng bàn phím, đọc bằng trình đọc màn hình.
- [ ] Không có lỗi console ở mức `error`.
- [ ] Kích thước chữ không nhỏ hơn 12px ở phần ghi chú.
