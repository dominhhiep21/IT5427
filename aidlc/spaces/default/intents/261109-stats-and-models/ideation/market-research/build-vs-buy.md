# Build vs Buy — Quyết định cho từng phần

Bối cảnh lấy từ `../intent-capture/intent-statement.md`: bốn nhóm kiểm định thống kê, một mô hình phân loại đơn trễ, và kết quả phải đến được cả CLI lẫn dashboard. [Q3][Q4] Người dùng là nhóm nhỏ 2-5 người dùng chung một máy. [Q5]

| Phần | Tự viết | Dùng thư viện | Quyết định | Lý do |
|---|---|---|---|---|
| Kiểm định thống kê | Công thức Wilson, kiểm định z, tương quan, phân rã mùa vụ | `scipy`, `statsmodels` | Dùng thư viện [Q3] | Đã có sẵn và được kiểm chứng; tự viết dễ sai ở p-value và khoảng tin cậy |
| Mô hình phân loại đơn trễ | Hồi quy logistic viết tay | `scikit-learn` | Dùng thư viện [Q4] | Chuẩn cho chia dữ liệu, đo AUC, hiệu chỉnh ngưỡng; ít mã phải bảo trì |
| Dashboard | Giữ nguyên Dash hiện có | Nền tảng BI thương mại | Giữ Dash [Q1] | Bốn mức tối thiểu đã đạt; đổi nền tảng là thay thế, không phải bổ sung [Q2] |
| Lưu trữ kết quả | Ghi JSON bằng mã | Dịch vụ cơ sở dữ liệu | Ghi JSON [Q2] | Nhóm nhỏ dùng chung máy; cần đọc lại và tái lập, không cần máy chủ |

## Phụ thuộc phát sinh

- `scipy` hoặc `statsmodels` cho phần thống kê; ghim phiên bản vì đây là phụ thuộc mới. [Q3]
- `scikit-learn` cho phần mô hình; ghim phiên bản cùng lý do. [Q4]
- Không thêm dịch vụ ngoài, không thêm cơ sở dữ liệu mạng. [Q1]

## Điều kiện đổi quyết định

Nếu sau này dữ liệu tăng lên mức cần cụm tính toán, hoặc xuất hiện yêu cầu nhiều người dùng đồng thời qua mạng, hai quyết định "giữ Dash" và "ghi JSON" sẽ phải xem lại; phần kiểm định và mô hình thì không đổi. [Q5]
