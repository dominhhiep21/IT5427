# Scope Document — Kiểm định thống kê và mô hình dự báo

Phạm vi dưới đây chốt từ `../intent-capture/intent-statement.md`, `../feasibility/feasibility-assessment.md` và `../feasibility/constraint-register.md`. Kế hoạch đang chạy là `feature`. [Q1]

## 1. Phạm vi tối thiểu còn giá trị

Cả bốn nhóm kiểm định thống kê và một mô hình dự báo. [Q1] Nếu thời gian thiếu, phần dễ thấy kết quả được làm trước, nhưng mức "xong" vẫn tính theo mốc này. [Q4]

## 2. Trong phạm vi

| Mã | Hạng mục | Mức | Nguồn |
|---|---|---|---|
| S-01 | Khoảng tin cậy cho một tỉ lệ và so sánh hai tỉ lệ | Bắt buộc | [Q2] |
| S-02 | Tương quan giữa hai biến số kèm khoảng tin cậy | Bắt buộc | [Q2] |
| S-03 | Mô hình phân loại đơn hàng có nguy cơ giao trễ | Bắt buộc | [Q2] |
| S-04 | So sánh nhóm hoặc kiểm định phân phối | Nên có | [Q2] |
| S-05 | Phân rã mùa vụ của chuỗi doanh thu theo tháng | Nên có | [Q2] |
| S-06 | Lệnh CLI chạy kiểm định và ghi báo cáo JSON | Bắt buộc | [Q1] |
| S-07 | Một tab mới trên dashboard để hiện kết quả | Bắt buộc | [Q6] |

## 3. Ngoài phạm vi

- Không làm real-time hay streaming. [Q7]
- Không sửa dữ liệu gốc trong `dataset/`. [Q7]

Các mục không được chọn ở câu hỏi phạm vi không tự động trở thành loại trừ: deep learning, API công khai và giao diện mới ngoài phần hiển thị kết quả vẫn chưa có quyết định, nên chưa được ghi là ngoài phạm vi. [Q7]

## 4. Thứ tự thi công

1. Kiểm định thống kê trước, vì cho kết quả thấy được sớm nhất. [Q3][Q4]
2. Mô hình dự báo sau, vì cần dựng đặc trưng và kiểm rò rỉ. [Q3]
3. Hiển thị trên dashboard cuối cùng, sau khi báo cáo đã có hình dạng ổn định. [Q3]

Không hạng mục nào bị buộc phải xong trước vì mốc thời gian riêng. [Q5]

## 5. Điều kiện coi là xong

- Bốn nhóm kiểm định chạy trên dữ liệu thật và ghi được báo cáo. [Q2]
- Mô hình đạt AUC tối thiểu 0,70 với cách chia theo thời gian, có precision và recall ở ngưỡng cảnh báo. [Q2]
- Kết quả đọc được từ CLI và từ tab mới trên dashboard. [Q6]
- Không hồi quy: các kiểm tra chất lượng và KPI hiện có vẫn xanh. [Q1]
