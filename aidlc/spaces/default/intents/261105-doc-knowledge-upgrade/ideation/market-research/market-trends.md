# Market Trends — Nâng cấp tích hợp dữ liệu Olist

Bối cảnh lấy từ `ideation/intent-capture/intent-statement.md`. Người dùng chính là giảng viên/hội đồng chấm, nên tiêu chí chọn xu hướng là "thể hiện được xu hướng nào có ích cho việc học và cho sản phẩm", không phải chạy theo thị trường.

> Ghi chú bằng chứng: các xu hướng dưới đây là kiến thức chung, chưa kiểm chứng lại bằng khảo sát trong phiên này. Chúng được ghi ở mức định hướng, không nêu số liệu thị trường.

## Xu hướng được đưa vào phạm vi

### Semantic layer / lớp ngữ nghĩa dùng chung (Q3 = A)

- Định nghĩa metric một lần, nhiều công cụ cùng đọc: dashboard, CLI, truy vấn SQL đều dùng chung một định nghĩa thay vì mỗi nơi tự tính.
- Trong hệ hiện tại, KPI được tính trong `src/analytics` và hiển thị ở `src/dashboard`; nếu mỗi nơi tự tính lại, số liệu dễ lệch nhau.
- Hướng áp dụng cho lần nâng cấp: đưa định nghĩa KPI và chiều phân tích thành một lớp ngữ nghĩa khai báo, để lớp truy vấn trung gian và dashboard cùng dùng.
- Liên hệ lý thuyết: lược đồ trung gian trong `doc/` chính là một dạng lớp ngữ nghĩa; đây là cầu nối tự nhiên giữa bài giảng và sản phẩm.

## Xu hướng ghi nhận nhưng không làm trong lần này

| Xu hướng | Vì sao ghi nhận | Vì sao chưa làm |
|---|---|---|
| Lakehouse và xử lý tại chỗ | Hệ đã dùng Parquet + DuckDB, đúng hướng | Đã có sẵn; không cần thêm hạ tầng để thể hiện lý thuyết tích hợp |
| Data contracts và lineage | Hữu ích cho truy vết nguồn gốc dữ liệu | Không nằm trong bốn nhóm chủ đề đã chốt (Q3 chỉ chọn semantic layer) |
| Nền tảng dữ liệu tự phục vụ | Liên quan tới trải nghiệm người xem | Vượt phạm vi một đồ án một máy, không có người dùng thật ngoài hội đồng |

## Kỳ vọng tối thiểu so với điểm khác biệt

- **Tối thiểu (table stakes)**: số liệu KPI đúng và nhất quán giữa các màn hình; lọc theo thời gian, danh mục, bang hoạt động ổn định.
- **Khác biệt**: nhìn thấy được *cách* dữ liệu được tích hợp — ánh xạ lược đồ, cặp bản ghi được ghép và lý do, kế hoạch truy vấn sau khi viết lại. Đây là thứ công cụ đóng gói sẵn không cho thấy.

## Kết luận cho các bước sau

- Chỉ semantic layer được đưa vào phạm vi; các xu hướng còn lại giữ ở mức ghi nhận.
- Yêu cầu chức năng ở bước Requirements Analysis nên bám vào hai ý: nhất quán số liệu (semantic layer) và minh bạch quá trình tích hợp.
