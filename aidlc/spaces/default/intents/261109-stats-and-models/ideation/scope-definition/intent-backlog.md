# Intent Backlog — Các đơn vị công việc dự kiến

Danh sách dưới đây là các đơn vị công việc ở mức thô, chưa phải kế hoạch thi công chi tiết. Thứ tự theo `scope-document.md`: kiểm định trước, mô hình sau, hiển thị cuối. [Q3]

| Mã | Đơn vị | Giá trị | Công sức | Ưu tiên | Phụ thuộc | Nguồn |
|---|---|---|---|---|---|---|
| B-01 | Khung kiểm định + khoảng tin cậy và so sánh hai tỉ lệ | Cao | Thấp | Must | Dữ liệu mart đã có | [Q2] |
| B-02 | Tương quan giữa hai biến số kèm khoảng tin cậy | Cao | Thấp | Must | B-01 (dùng chung khung) | [Q2] |
| B-03 | Lệnh CLI chạy kiểm định và ghi báo cáo JSON | Cao | Thấp | Must | B-01, B-02 | [Q1] |
| B-04 | Mô hình phân loại đơn trễ, chia theo thời gian, báo cáo AUC và precision/recall | Cao | Cao | Must | B-03 (đọc dữ liệu cùng đường) | [Q2] |
| B-05 | Tab mới trên dashboard đọc báo cáo và hiển thị | Trung bình | Trung bình | Must | B-03, B-04 | [Q6] |
| B-06 | So sánh nhóm hoặc kiểm định phân phối | Trung bình | Trung bình | Should | B-01 | [Q2] |
| B-07 | Phân rã mùa vụ của chuỗi doanh thu tháng | Trung bình | Trung bình | Should | B-01 | [Q2] |

## Ghi chú ưu tiên

- Bốn đơn vị Must đầu tiên tạo ra kết quả thấy được sớm, đúng hướng ưu tiên đã chọn. [Q4]
- B-06 và B-07 là phần nên có; nếu hết thời gian thì cắt trước, không cắt B-01 đến B-05. [Q1]
- Không có đơn vị nào bị ràng buộc bởi mốc thời gian riêng. [Q5]

## Rủi ro gắn với backlog

- B-04 mang rủi ro rò rỉ đặc trưng và mất cân bằng lớp đã ghi trong `../feasibility/raid-log.md` (R-01, R-02).
- B-05 phụ thuộc hình dạng báo cáo do B-03 chốt; đổi định dạng báo cáo sau khi làm B-05 sẽ phải sửa cả hai nơi. [Q6]
