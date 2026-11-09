# Build vs Buy — Nâng cấp tích hợp dữ liệu Olist

Bối cảnh lấy từ `ideation/intent-capture/intent-statement.md`: bốn nhóm chủ đề tích hợp dữ liệu cần thể hiện trên hệ Olist hiện có, phục vụ giảng viên/hội đồng chấm.

## Quyết định

- **Tự xây phần lõi, chỉ dùng thư viện cho phần phụ** (Q2 = B).
- **Chỉ dùng công cụ/thư viện mã nguồn mở, miễn phí** (Q4 = A).
- **Nhóm thương mại chỉ xuất hiện để so sánh, không dùng trong sản phẩm** (Q1 = C, Q4 = A).

## Phân rã theo bốn nhóm chủ đề

| Nhóm | Tự xây | Dùng thư viện có sẵn | Lý do |
|---|---|---|---|
| Đồng nhất lược đồ / lược đồ trung gian | Khai báo lược đồ trung gian và ánh xạ từ nguồn Olist + IBGE | Không (dbt/Trino bị loại vì che mất lý thuyết) | Đây là phần lý thuyết trung tâm cần thể hiện |
| Ghép bản ghi / nhận dạng thực thể | Blocking, tính độ tương đồng, chọn ngưỡng, báo cáo cặp khớp | Có thể dùng thư viện so khớp chuỗi mã nguồn mở cho bước tính điểm | Thuật toán phải tự viết; phần so khớp ký tự là chi tiết kỹ thuật |
| Xử lý / viết lại truy vấn | Viết lại truy vấn từ lược đồ trung gian xuống truy vấn nguồn, hiển thị kế hoạch | Không dùng Trino | Cần thấy được quá trình viết lại, không chỉ kết quả |
| Chọn nguồn dữ liệu | Luật chọn nguồn dựa trên khả năng truy cập và chi phí ước tính | Không dùng Airbyte/Fivetran | Nguồn chỉ có Olist và cache IBGE; cần mô phỏng tình huống chọn |

## Vì sao không mua/không dùng công cụ đóng gói

- Mục tiêu là *chứng minh hiểu lý thuyết*; công cụ đóng gói che thuật toán nên làm mất chính phần cần chấm.
- Ràng buộc miễn phí loại nhóm thương mại khỏi triển khai.
- Quy mô dữ liệu nhỏ, một máy: đầu tư hạ tầng phân tán không mang lại giá trị.

## Đánh đổi đã chấp nhận

- Tốn thời gian hơn so với cắm công cụ có sẵn, đổi lại bài nộp thể hiện được từng bước của lý thuyết.
- Phần tự xây sẽ kém đầy đủ hơn sản phẩm thương mại (ví dụ tối ưu truy vấn chỉ ở mức minh hoạ); phạm vi được giới hạn trong biên giới của `intent-statement.md`.
- Thư viện phụ trợ phải là mã nguồn mở và nhỏ, để không kéo theo hạ tầng ngoài phạm vi.

## Tiêu chí kiểm chứng quyết định này

- Mỗi nhóm chủ đề có ít nhất một đoạn thuật toán tự viết và một kiểm thử tương ứng.
- Không có phụ thuộc mới nào là công cụ thương mại.
- Toàn bộ test hiện có vẫn xanh sau khi thêm phần mới (ràng buộc không hồi quy ở `intent-statement.md`).
