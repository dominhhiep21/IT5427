# Unit ↔ Story Map — Nâng cấp tích hợp dữ liệu Olist

Mỗi dòng là một câu chuyện và các đơn vị thực hiện nó. Đơn vị được nêu chỉ khi nó thực hiện một phần câu chuyện đó.

| Story | Units | Ghi chú |
|---|---|---|
| US1.1 | U1; U2; U6 | U1 dựng đường tối thiểu, U2 đủ ba thực thể, U6 hiển thị danh sách và bảng |
| US1.2 | U2; U6 | U2 sinh dạng ánh xạ `GAV`, U6 hiển thị nhãn và tên thực thể |
| US1.3 | U2 | Kiểm tra cột nguồn là việc của bộ nạp, không có bề mặt giao diện |
| US2.1 | U1; U3; U6 | U1 một truy vấn mẫu, U3 ba truy vấn, U6 chọn và chạy |
| US2.2 | U3; U6 | Kế hoạch viết lại và SQL nguồn |
| US2.3 | U3 | Đối chiếu KPI là logic, không có bề mặt riêng |
| US3.1 | U4; U6 | Số liệu tóm tắt và bảng đối tượng |
| US3.2 | U4; U6 | U4 sinh cặp và quyết định, U6 hiển thị bảng cặp với điểm 2 chữ số |
| US3.3 | U4; U6 | U4 ghi cặp bị bỏ qua, U6 hiển thị dòng "Bỏ qua" |
| US4.1 | U5; U6 | Hồ sơ nguồn và bảng nguồn |
| US4.2 | U5; U6 | Luật đề xuất nguồn; U6 hiển thị nút và cập nhật bảng |
| US5.1 | U6 | Tab và bốn thẻ |
| US5.2 | U6 | Điều hướng vào/ra màn hình chi tiết |
| US5.3 | U6 | Bốn trạng thái hiển thị |
| US6.1 | U1; U2; U3; U4; U5; U6 | Không hồi quy là điều kiện đóng của mọi đơn vị |
| US6.2 | U3; U6 | Định nghĩa KPI dùng chung; U6 đọc cùng định nghĩa đó để hiển thị |
| NFR1 | U3; U6 | U3 giữ truy vấn chạy trong ngân sách (đo thời gian), U6 giữ tương tác dưới 2 giây |

## Kiểm tra phủ

- Mọi câu chuyện `US1.1`–`US6.2` đều có ít nhất một đơn vị.
- Mọi đơn vị đều có ít nhất một dòng: U1 (US1.1, US2.1, US6.1), U2 (US1.1–US1.3, US6.1), U3 (US2.1–US2.3, US6.1, US6.2), U4 (US3.1–US3.3, US6.1), U5 (US4.1, US4.2, US6.1), U6 (US1.1, US1.2, US2.1, US2.2, US3.1–US3.3, US4.1, US4.2, US5.1–US5.3, US6.1, US6.2).
- Không câu chuyện nào phủ bởi đơn vị không tồn tại.

## Cross-cutting

- US6.1 (không hồi quy) trải trên cả sáu đơn vị: mỗi đơn vị phải giữ bộ test hiện có xanh và cập nhật test hình dạng dashboard khi chạm giao diện.

## Thứ tự trong từng đơn vị

1. **U1**: khai báo lược đồ tối thiểu → viết lại một truy vấn → một thẻ trên tab → chạy lệnh xác nhận.
2. **U2**: bộ nạp lược đồ → kiểm tra cột nguồn → thực thể thứ hai và thứ ba.
3. **U3**: truy vấn mẫu thứ hai và thứ ba → kế hoạch viết lại từng bước → đối chiếu KPI.
4. **U4**: khoá chặn → tính điểm → ngưỡng và quyết định → cặp bị bỏ qua → tỉ lệ đúng.
5. **U5**: hồ sơ nguồn → luật xếp hạng → lý do chọn/loại.
6. **U6**: khung tab → màn hình tổng quan → bốn màn hình chi tiết → bốn trạng thái → kiểm tiếp cận.
