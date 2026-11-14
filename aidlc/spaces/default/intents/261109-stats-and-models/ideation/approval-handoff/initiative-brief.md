# Initiative Brief — Kiểm định thống kê và mô hình dự báo

Bản tóm tắt một trang cho giai đoạn Ideation. Nguồn: `../intent-capture/intent-statement.md`, `../market-research/`, `../feasibility/`, `../scope-definition/`, `../rough-mockups/`.

## 1. Ý định và bài toán

Dự án Olist hiện dừng ở mô tả: KPI, biểu đồ, bảng. Đề bài yêu cầu tính toán thống kê và khuyến khích mô hình ML/AI, nên đợt này bổ sung hai phần đó. [Q1]

## 2. Căn cứ từ nghiên cứu

Không có thị trường thương mại để so sánh; các lựa chọn là công cụ mã nguồn mở đang dùng. Chọn `scipy`/`statsmodels` cho kiểm định và `scikit-learn` cho mô hình, giữ nguyên Dash và cách ghi báo cáo JSON. [Q4][Q5]

## 3. Khả thi và rủi ro

Khả thi: dữ liệu đã có trong DuckDB, hai thư viện cài được, thời gian chạy không giới hạn. Bốn rủi ro đã ghi nhận và chấp nhận: rò rỉ đặc trưng, mất cân bằng lớp, mốc 1 tuần, lệch mùa vụ khi chia theo thời gian. [Q2]

## 4. Ranh giới phạm vi

- Trong phạm vi: bốn nhóm kiểm định, một mô hình phân loại đơn trễ, lệnh CLI ghi báo cáo, một tab mới trên dashboard. [Q6]
- Ngoài phạm vi: không real-time hay streaming; không sửa `dataset/`. [Q7]
- Phạm vi tối thiểu còn giá trị: cả bốn nhóm kiểm định và một mô hình. [Q1]

## 5. Hình dung sản phẩm

Một tab mới có dải tóm tắt, rồi bảng kiểm định, rồi khối mô hình; có trạng thái rỗng và trạng thái lỗi. Chi tiết ở `../rough-mockups/wireframes.md`. [Q4]

## 6. Kế hoạch nhân sự

Một người làm, không có nhóm hay mob. Bước Team Formation được bỏ qua vì không áp dụng. [Q6]

## 7. Khuyến nghị

Đi tiếp sang Inception. Điều kiện: giữ phạm vi đã chốt, không thêm hạng mục ngoài bốn nhóm kiểm định và một mô hình. [Q7]
