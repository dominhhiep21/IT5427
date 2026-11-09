# Intent Backlog — Nâng cấp tích hợp dữ liệu Olist

Proto-Units cho giai đoạn Inception và Construction. Bối cảnh: `scope-document.md`, `intent-statement.md`, `feasibility-assessment.md`.

Ưu tiên theo MoSCoW; kích thước tương đối S/M/L. Tất cả hạng mục Must đều thuộc bốn nhóm chủ đề đã chốt hoặc bảo vệ không hồi quy.

| ID | Năng lực | MoSCoW | Phụ thuộc | Cỡ | Ghi chú |
|---|---|---|---|---|---|
| PB-01 | Lược đồ trung gian khai báo + ánh xạ từ 9 CSV và cache IBGE | Must | — | L | Nền cho mọi nhóm; làm sâu |
| PB-02 | Mô tả nguồn dữ liệu (khả năng truy cập, chi phí ước tính) | Must | PB-01 | S | Đầu vào cho chọn nguồn |
| PB-03 | Luật chọn nguồn dữ liệu cho một truy vấn | Must | PB-01, PB-02 | S | Một kịch bản trên hai nguồn hiện có |
| PB-04 | Viết lại truy vấn từ lược đồ trung gian xuống SQL nguồn | Must | PB-01, PB-02 | L | Làm sâu; giới hạn ở tập truy vấn mẫu |
| PB-05 | Ghép bản ghi: blocking, điểm tương đồng, ngưỡng, báo cáo cặp khớp | Must | PB-01 | M | Một kịch bản; dùng thư viện so khớp chuỗi nếu cần |
| PB-06 | Lớp ngữ nghĩa: định nghĩa KPI dùng chung cho dashboard và truy vấn | Should | PB-01 | M | Ngăn lệch số giữa các màn hình |
| PB-07 | Tab "Tích hợp" hiển thị ánh xạ, cặp khớp, kế hoạch viết lại | Must | PB-01..PB-05 | M | Một tab gộp bốn nhóm |
| PB-08 | Bộ test bảo vệ hành vi hiện có (KPI, ba tab) | Must | — | S | Chạy trước khi sửa để có mốc so sánh |
| PB-09 | Làm mới ba tab hiện có (bố cục, biểu đồ, bộ lọc) | Should | PB-08 | S | Làm cuối |
| PB-10 | Tài liệu: danh mục ánh xạ + kịch bản demo trước hội đồng | Should | PB-01..PB-07 | S | Phục vụ phần trình bày |

## Không làm trong lần này (Won't)

| Hạng mục | Lý do |
|---|---|
| ML dự báo giao trễ | Ngoài bốn nhóm chủ đề, không cần cho mục tiêu thể hiện lý thuyết |
| Thêm nguồn dữ liệu mới | Biên giới ở `intent-statement.md` |
| Đăng nhập, phân quyền, nhiều người dùng | Không có yêu cầu bảo mật |
| Dùng công cụ thương mại | Ràng buộc BC-01 |
| Tối ưu truy vấn tổng quát | Rủi ro R-02, vượt phạm vi |

## Đường găng

`PB-01 → PB-02 → PB-04 → PB-07`

Lược đồ trung gian là điểm nghẽn duy nhất: mọi nhóm khác chờ nó. Nếu chậm ở PB-01, toàn bộ tiến độ chậm theo; nên dành thời gian đầu cho PB-01 thay vì làm song song.

## Ghi chú cắt phạm vi khi hết thời gian

- Cắt trước: PB-09, PB-10, PB-06.
- Không cắt: PB-01, PB-04, PB-08 — đây là phần thể hiện lý thuyết và bảo vệ không hồi quy.
- PB-05 và PB-03 có thể giữ ở mức một kịch bản duy nhất, không mở rộng.
