# Interaction Spec — Tab kết quả

## Trạng thái

Mỗi màn hình xử lý đủ năm trạng thái. [Q3]

| Trạng thái | Điều kiện | Hiển thị |
|---|---|---|
| Đang tải | Đang đọc tệp báo cáo | Dải tóm tắt thay bằng khung xương; hai khối hiện dòng "đang đọc báo cáo" |
| Rỗng | Không có tệp báo cáo | Câu "Chưa có báo cáo phân tích" + câu lệnh cần chạy dạng `code` |
| Lỗi | Tệp có nhưng thiếu trường hoặc sai định dạng | Câu "Không đọc được báo cáo phân tích" + đường dẫn tệp |
| Đầy đủ | Có cả hai khối | Toàn bộ nội dung như trong `mockups.md` |
| Một phần | Thiếu khối thống kê hoặc khối mô hình | Khối có hiện bình thường; khối thiếu hiện "chưa có" thay cho số liệu |

## Bộ lọc ngưỡng

- Vị trí: hàng trên của khối mô hình. [Q2]
- Giá trị: từ 0,10 đến 0,90, bước 0,05.
- Mặc định: ngưỡng đã chọn trong báo cáo.
- Thay đổi ngưỡng chỉ vẽ lại khối mô hình từ dữ liệu đã có; không đọc lại tệp.
- Bàn phím: chọn được bằng phím mũi tên; giá trị hiện tại đọc được bằng trình đọc màn hình.

## Phản hồi

- Không có thông báo nổi (toast); mọi phản hồi nằm tại chỗ trong khối.
- Khi chuyển tab rồi quay lại, tab đọc lại tệp báo cáo và giữ ngưỡng đã chọn trong phiên.

## Không có trong đợt này

- Không có nút chạy lại phân tích từ giao diện. [Q2]
- Không có sửa số liệu, không có xuất tệp từ tab.
