# Đánh giá User Stories

## Phân tích yêu cầu

- **Yêu cầu gốc**: Xây dựng pipeline tích hợp, làm sạch và phân tích dữ liệu Olist, kèm dashboard Plotly Dash.
- **Tác động tới người dùng**: Trực tiếp — dashboard có người dùng cuối; pipeline tạo dữ liệu cho báo cáo.
- **Mức độ phức tạp**: Trung bình đến phức tạp — nhiều grain dữ liệu, nhiều bẫy chất lượng, nhiều loại KPI.
- **Các bên liên quan**: Chuyên viên phân tích dữ liệu, giảng viên/người đánh giá đồ án, kỹ sư dữ liệu, (tùy chọn) quản lý kinh doanh.

## Tiêu chí đánh giá được đáp ứng

- [x] **High Priority — New User Features**: Dashboard là tính năng người dùng trực tiếp.
- [x] **High Priority — Multi-Persona System**: Người xem báo cáo, người vận hành pipeline và người đánh giá có nhu cầu khác nhau.
- [x] **High Priority — Complex Business Logic**: Doanh thu, giao trễ, mua lặp lại có nhiều quy tắc và grain.
- [x] **Medium Priority — Data Changes**: KPI và báo cáo chịu ảnh hưởng trực tiếp từ cách làm sạch/tích hợp.
- [x] **Medium Priority — Testing**: Cần tiêu chí chấp nhận rõ để kiểm thử dashboard và KPI.

## Quyết định

**Execute User Stories**: Có.

**Lý do**: Dashboard có người dùng thật và các KPI dễ bị hiểu sai nếu không mô tả theo góc nhìn người dùng. User stories giúp chuyển 11 yêu cầu chức năng thành lát cắt có giá trị, đồng thời tạo tiêu chí kiểm thử thống nhất cho pipeline và giao diện.

## Kết quả kỳ vọng

- Persona rõ ràng cho người xem báo cáo, người vận hành và người đánh giá.
- Story có tiêu chí chấp nhận kiểm thử được, gắn với KPI baseline.
- Bao phủ cả luồng dữ liệu (data engineer) lẫn luồng khám phá (analyst), tránh chỉ mô tả giao diện.
- Truy vết từ yêu cầu → story → kiểm thử.
