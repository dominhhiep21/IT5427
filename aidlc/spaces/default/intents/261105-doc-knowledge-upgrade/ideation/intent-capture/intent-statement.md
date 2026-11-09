# Intent Statement — Nâng cấp tích hợp dữ liệu và giao diện Olist

## Problem Statement

- Hệ thống hiện tại đã có pipeline và dashboard chạy được, nhưng phần tích hợp dữ liệu chưa có lớp lược đồ trung gian / ánh xạ / truy vấn thống nhất để thể hiện đúng lý thuyết tích hợp dữ liệu. [desc] [Q1]
- Người xem chưa thấy được các khái niệm tích hợp dữ liệu trong sản phẩm — hiện chỉ thấy dashboard báo cáo. [Q1]
- Lần nâng cấp này giải quyết cả hai: lớp tích hợp đúng lý thuyết và giao diện thể hiện được nó. [Q1]

## Target Customer

- Người dùng chính của giao diện sau nâng cấp là giảng viên/hội đồng chấm đồ án — cần thấy bằng chứng áp dụng lý thuyết. [Q4]
- Sản phẩm phục vụ việc áp dụng các kiến thức trong `doc/` vào hệ thống hiện có. [desc]

## Success Metrics

- Demo được các nhóm chủ đề tích hợp dữ liệu trên dữ liệu Olist thật, có số liệu đối chiếu. [Q5] [Q9]
- Dashboard trả lời câu hỏi nghiệp vụ nhanh hơn hiện tại (ít thao tác hơn, thêm bộ lọc/tương tác). [Q5]
- Không hồi quy: KPI baseline giữ nguyên và toàn bộ test hiện có vẫn xanh. [Q5]

## Initiative Trigger

- Yêu cầu của môn học/đồ án (`doc/Projects.pdf`) — cần bản thể hiện đủ nội dung lý thuyết. [Q6]
- Đồng thời hệ đã chạy ổn, muốn nâng chất lượng để thể hiện phần tích hợp dữ liệu đã học. [Q6]

## Initial Scope Signal

- Workflow-selected scope: `feature`. [scope]
- Nhóm chủ đề của lần nâng cấp: cả bốn nhóm — đồng nhất lược đồ & lược đồ trung gian, ghép bản ghi/nhận dạng thực thể, xử lý & viết lại truy vấn, chọn nguồn dữ liệu. [Q2] [Q9]
- Giao diện: vừa thêm màn hình cho các năng lực tích hợp, vừa nâng chất lượng giao diện hiện có. [Q3]
- Biên giới phiên bản đầu: không thêm nguồn dữ liệu ngoài Olist + cache IBGE hiện có. [Q8]

## Assumptions & Open Questions

- [assumption] Kênh giao tiếp và nhịp báo cáo với giảng viên/hội đồng chưa được xác định. [Q4]
