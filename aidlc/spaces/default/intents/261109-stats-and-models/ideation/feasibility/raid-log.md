# RAID Log — Risks, Assumptions, Issues, Dependencies

Bối cảnh: `../intent-capture/intent-statement.md`, `../market-research/build-vs-buy.md`, và `constraint-register.md`.

## Risks

| Mã | Rủi ro | Khả năng | Tác động | Cách giảm | Nguồn |
|---|---|---|---|---|---|
| R-01 | Mô hình dùng đặc trưng chỉ có sau khi đơn hoàn tất, gây rò rỉ và kết quả đẹp giả tạo | Trung bình | Cao | Chỉ dùng đặc trưng biết trước thời điểm giao; rà danh sách cột trước khi huấn luyện | [Q5] |
| R-02 | Lớp trễ chỉ khoảng 8%, mô hình dự đoán "không trễ" cho mọi đơn vẫn đạt độ chính xác cao | Cao | Trung bình | Báo cáo AUC, precision, recall; không dùng accuracy làm chỉ số chính | [Q5] |
| R-03 | Mốc 1 tuần không đủ cho phạm vi đã chốt | Trung bình | Cao | Giữ phạm vi: bốn nhóm kiểm định và một mô hình; không mở rộng thêm | [Q6] |
| R-04 | Chia theo thời gian làm tập kiểm tra lệch mùa vụ so với tập huấn luyện | Trung bình | Trung bình | Ghi rõ trong báo cáo; so sánh với chia ngẫu nhiên như tài liệu tham khảo, không thay kết quả chính | [Q5] |

## Assumptions

| Mã | Giả định | Nếu sai thì sao | Nguồn |
|---|---|---|---|
| A-01 | Nhãn "giao trễ" trong dữ liệu là đáng tin để huấn luyện | Phải định nghĩa lại nhãn và làm lại phần mô hình | [Q5] |
| A-02 | Hai thư viện mới cài được bằng một lần `pip install` | Phải tìm phương án khác, có thể tự viết công thức | [Q2] |
| A-03 | Người dùng dashboard là nhóm 2-5 người dùng chung máy | Nếu đông hơn, phần đọc kết quả phải tính tới truy cập đồng thời | [Q7] |

## Issues

| Mã | Vấn đề | Trạng thái | Nguồn |
|---|---|---|---|
| I-01 | Chưa có vấn đề nào phát sinh ở thời điểm lập kế hoạch | Mở, theo dõi | [Q1] |

## Dependencies

| Mã | Phụ thuộc | Loại | Ảnh hưởng | Nguồn |
|---|---|---|---|---|
| D-01 | `scipy` hoặc `statsmodels` cho phần kiểm định | Thư viện ngoài | Phải ghim phiên bản trước khi viết mã | [Q2] |
| D-02 | `scikit-learn` cho phần mô hình | Thư viện ngoài | Phải ghim phiên bản trước khi viết mã | [Q2] |
| D-03 | Bảng mart và view DuckDB đã dựng bởi tầng `integrate` | Nội bộ | Kiểm định và mô hình chỉ chạy sau khi pipeline hoàn tất | [Q1] |
| D-04 | Dashboard hiện có còn giữ cấu trúc tab và vùng kết quả | Nội bộ | Phần hiển thị mới phải theo cấu trúc đó | [Q1] |
