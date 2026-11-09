# RAID Log — Nâng cấp tích hợp dữ liệu Olist

Bối cảnh từ `intent-statement.md`, `build-vs-buy.md` và các câu trả lời Feasibility.

## Risks

| ID | Rủi ro | Khả năng | Tác động | Ứng phó |
|---|---|---|---|---|
| R-01 | Quỹ thời gian 1–2 tuần không đủ cho bốn nhóm chủ đề cộng giao diện | Cao | Cao | Giới hạn mỗi nhóm ở một kịch bản tối thiểu; cắt nhóm viết lại truy vấn xuống một truy vấn mẫu nếu cần |
| R-02 | Phần viết lại truy vấn phình thành trình tối ưu tổng quát | Trung bình | Cao | Chốt tập truy vấn mẫu ngay từ thiết kế; không nhận thêm yêu cầu ngoài tập đó |
| R-03 | Thêm thư viện phụ kéo theo phụ thuộc lớn hoặc không tương thích Python 3.13 | Trung bình | Trung bình | Chỉ chọn thư viện nhỏ, thuần Python; kiểm tra trên môi trường ảo trước khi thêm |
| R-04 | Sửa vào pipeline hiện có làm hỏng KPI baseline | Trung bình | Cao | Chạy bộ test hiện có trước khi sửa; thêm test cho phần mới; so sánh KPI trước/sau |
| R-05 | Không có mốc nộp khiến tiến độ trượt âm thầm | Trung bình | Trung bình | Tự đặt mốc kiểm tra theo từng nhóm chủ đề thay vì theo ngày |

## Assumptions

| ID | Giả định | Cơ sở | Cần xác nhận khi nào |
|---|---|---|---|
| A-01 | Bốn nhóm chủ đề dùng chung một lược đồ trung gian, nên làm một lần rồi tái sử dụng | Thiết kế tự nhiên của mediation | Ở bước Domain Design |
| A-02 | Dữ liệu Olist đủ để minh hoạ ghép bản ghi mà không cần sinh thêm dữ liệu giả | Có `customer_unique_id` và nhiều trường mô tả | Khi làm nhóm ghép bản ghi |
| A-03 | Chỉ hai nguồn (Olist + cache IBGE) là đủ để minh hoạ chọn nguồn dữ liệu | Biên giới ở `intent-statement.md` | Khi làm nhóm chọn nguồn |

## Issues

| ID | Vấn đề | Trạng thái | Ghi chú |
|---|---|---|---|
| I-01 | Không có vấn đề đang mở tại thời điểm lập log | Mở | Cập nhật khi phát sinh |

## Dependencies

| ID | Phụ thuộc | Loại | Ảnh hưởng |
|---|---|---|---|
| D-01 | Lược đồ trung gian và ánh xạ phải có trước phần viết lại truy vấn | Nội bộ | Quyết định thứ tự làm ở giai đoạn Construction |
| D-02 | Cùng phải có trước phần chọn nguồn dữ liệu | Nội bộ | Chọn nguồn dựa trên mô tả nguồn trong lược đồ trung gian |
| D-03 | Dashboard phụ thuộc vào lớp truy vấn mới | Nội bộ | Màn hình tích hợp chỉ làm sau khi có dữ liệu trả về |
| D-04 | Cache IBGE cục bộ trong `dataset/external/ibge/` | Dữ liệu | Không phụ thuộc mạng; chỉ làm mới khi có kết nối |
