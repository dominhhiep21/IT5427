# Competitive Analysis — Công cụ và cách tiếp cận đang cạnh tranh

Phạm vi so sánh lấy từ `../intent-capture/intent-statement.md`: đợt này bổ sung kiểm định thống kê và mô hình dự báo cho dự án Olist. [Q1] Đây là bài tập môn học, không có thị trường thương mại, nên phần so sánh chỉ gồm các công cụ mã nguồn mở đang dùng và các cách làm phổ biến khác. [Q1]

## Các lựa chọn đang tồn tại

| Lựa chọn | Điểm mạnh | Điểm yếu | Quan hệ với đợt này |
|---|---|---|---|
| Bộ thư viện hiện có của dự án (`pandas`, `duckdb`, `dash`, `plotly`) | Đã cài, đã ghim phiên bản, pipeline và dashboard đang chạy trên đó | Không có kiểm định thống kê, không có mô hình | Nền để gắn phần mới vào [Q1] |
| `scipy` / `statsmodels` | Có sẵn kiểm định, khoảng tin cậy, phân rã chuỗi thời gian | Thêm phụ thuộc mới, cần ghim phiên bản | Được chọn cho phần thống kê [Q3] |
| `scikit-learn` | Chuẩn cho phân loại, có chia dữ liệu, đo AUC, hiệu chỉnh ngưỡng | Thêm phụ thuộc mới; mô hình cần dữ liệu đặc trưng dựng riêng | Được chọn cho mô hình dự báo [Q4] |
| Nền tảng BI thương mại (Power BI, Tableau, Metabase) | Kéo thả nhanh, nhiều loại biểu đồ | Không chạy trong pipeline Python, khó tái lập bằng mã, có phí hoặc cần dịch vụ ngoài | Không chọn [Q1] |
| Sổ tay phân tích công khai trên Kaggle | Có sẵn ví dụ về bộ dữ liệu Olist | Không có kiểm định, không đóng gói thành pipeline, khó kiểm chứng số liệu | Chỉ tham khảo cách đặt câu hỏi, không sao chép mã [Q1] |

## Mức tối thiểu mà người xem mặc định mong có

Bốn thứ sau được xác nhận là mức tối thiểu, không phải điểm khác biệt: KPI doanh thu, số đơn và giá trị đơn trung bình; bộ lọc theo thời gian, vùng, danh mục và trạng thái; biểu đồ xu hướng theo thời gian; và khả năng đọc lại số liệu đã tính. [Q2] Dashboard hiện có đã đáp ứng cả bốn, nên phần mới phải giữ nguyên chúng thay vì thay thế. [Q2]

## Khoảng trống mà đợt này lấp

- Chưa có suy luận thống kê: chỉ có trung bình, tổng và phần trăm. [Q3]
- Chưa có mô hình dự báo nào trong mã nguồn. [Q4]
- Chưa có chỗ đọc lại kết quả phân tích ngoài màn hình dashboard. [Q2]
