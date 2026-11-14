# Intent Statement — Kiểm định thống kê và mô hình dự báo

## Problem Statement

Dự án Olist hiện dừng ở mức mô tả: KPI, biểu đồ và bảng tổng hợp, chưa có suy luận thống kê và chưa có mô hình dự báo. [desc] Đề bài yêu cầu "statistical calculations should be included" và khuyến khích dùng mô hình ML/AI để tìm thông tin ẩn trong dữ liệu, nên hai phần này đang là khoảng trống so với yêu cầu. [desc]

## Target Customer

Người làm dự án là người trực tiếp chạy pipeline và viết báo cáo; kết quả của đợt này là căn cứ để trả lời yêu cầu định lượng của đề bài. [desc]

## Success Metrics

- Bốn nhóm kiểm định thống kê chạy được trên dữ liệu thật và ghi thành một báo cáo đọc lại được. [Q2]
- Mô hình phân loại đơn hàng có nguy cơ giao trễ đạt AUC tối thiểu 0,70, kèm precision và recall ở ngưỡng cảnh báo. [Q3][Q6]
- Kết quả đến được cả hai nơi: lệnh CLI ghi báo cáo JSON, dashboard đọc lại để hiển thị. [Q5]
- Thư viện mới dùng cho mô hình được ghim phiên bản trong `requirements.txt`. [Q4]

## Initiative Trigger

Đề bài môn học nêu yêu cầu bắt buộc về tính toán thống kê và khuyến khích mô hình ML/AI; dự án chưa có cả hai. [desc]

## Initial Scope Signal

- Workflow-selected scope: `feature` [scope]
- Trong phạm vi: làm cả hai phần, kiểm định thống kê trước rồi tới mô hình dự báo. [Q1]
- Trong phạm vi: cả bốn nhóm kiểm định — khoảng tin cậy và so sánh hai tỉ lệ, tương quan kèm khoảng tin cậy, so sánh nhóm hoặc kiểm định phân phối, phân rã mùa vụ của chuỗi doanh thu. [Q2]
- Trong phạm vi: mô hình phân loại đơn hàng có nguy cơ giao trễ. [Q3]
- Trong phạm vi: dùng `scikit-learn`, ghim phiên bản và ghi lý do trong `requirements.txt`. [Q4]
- Ngoài phạm vi: không sửa dữ liệu gốc trong `dataset/`. [Q7]

## Assumptions & Open Questions

None.
