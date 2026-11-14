# Unit ↔ Story Map

| Story | Units | Ghi chú |
|---|---|---|
| US1.1 | U1 | Chạy kiểm định và đọc kết quả |
| US2.1 | U2 | Huấn luyện mô hình và đọc chỉ số |
| US3.1 | U1 | Tệp báo cáo dùng chung do U1 dựng; khối mô hình thêm ở U2 |
| US4.1 | U3 | Tab kết quả đọc báo cáo của U1 và U2 |
| US5.1 | U1 | Chuỗi xác nhận, CI, cấu hình, README |

## Kiểm tra phủ

- Mọi story thuộc đúng một đơn vị.
- Không đơn vị nào không có story: U1 có ba, U2 có một, U3 có một.
- Thứ tự đơn vị tôn trọng phụ thuộc story: US2.1 cần US3.1 xong, US4.1 cần US2.1 xong.
