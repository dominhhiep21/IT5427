# Personas

## P1 — Chuyên viên phân tích dữ liệu

**Hồ sơ**: 28-35 tuổi, làm phân tích vận hành/kinh doanh cho sàn thương mại điện tử hoặc đơn vị bán lẻ. Thành thạo Excel, biết SQL cơ bản và Python ở mức đọc/sửa script; không muốn vận hành hạ tầng.

**Mục tiêu**
- Trả lời nhanh câu hỏi: doanh thu tháng này bao nhiêu, danh mục nào tăng/giảm, khu vực nào đóng góp nhiều nhất.
- So sánh hiệu quả giữa danh mục, bang/vùng và người bán.
- Xuất số liệu để đưa vào báo cáo quản trị.
- Tin được con số trên dashboard mà không phải mở CSV kiểm tra lại.

**Nỗi đau**
- Dữ liệu nằm rải rác trong 9 tệp, khóa và grain khác nhau.
- Từng bị sai số do join geolocation hoặc cộng trùng payment/review.
- Không rõ doanh thu đang tính theo `payment_value` hay `price + freight_value`.
- Dashboard chậm hoặc nhãn tiếng Anh, khó dùng trong báo cáo tiếng Việt.

**Hành vi điển hình**
- Mở dashboard vào đầu tuần, lọc 30 ngày gần nhất, xem KPI và biểu đồ danh mục.
- So sánh hai kỳ, sau đó lọc theo bang để tìm nguyên nhân.
- Xuất bảng top sản phẩm/seller để gửi quản lý.

**Nhu cầu với hệ thống**
- KPI có định nghĩa rõ ràng, hiển thị tiếng Việt, tiền BRL, ngày dd/mm/yyyy.
- Bộ lọc thời gian, bang/vùng, danh mục, trạng thái đơn.
- Phản hồi ≤ 3 giây; có trạng thái “không có dữ liệu” thay vì lỗi trắng.
- Số liệu phải tái lập được từ CSV gốc.

**Tiêu chí thành công**
- Tìm được insight doanh thu/danh mục trong ≤ 5 phút.
- Không phát hiện chênh lệch giữa dashboard và truy vấn đối soát.
- Không cần hỗ trợ kỹ thuật để thao tác dashboard.

**Không thuộc nhu cầu của P1**
- Cài đặt DuckDB/Spark, quản lý cron, đọc log kỹ thuật.

---

## P2 — Giảng viên / người đánh giá

**Hồ sơ**: 35-50 tuổi, giảng dạy hoặc đánh giá đồ án tích hợp và xử lý dữ liệu lớn. Quen các khái niệm schema alignment, record linkage, source selection, 3V, star schema, dashboard.

**Mục tiêu**
- Kiểm chứng pipeline thực sự tích hợp, làm sạch và phân tích dữ liệu, không chỉ vẽ biểu đồ.
- Chạy lại được từ CSV gốc trên máy khác.
- Thấy bằng chứng xử lý các bẫy dữ liệu: geolocation trùng, `customer_id` theo đơn, payment/review nhiều dòng, danh mục thiếu.
- Đánh giá mức độ đáp ứng 3V và chất lượng dashboard.

**Nỗi đau**
- Đồ án demo được trên máy tác giả nhưng không chạy lại được.
- Số liệu không giải thích được nguồn gốc hoặc định nghĩa.
- Không có test, log, tài liệu cài đặt.
- Dùng thư viện/hạ tầng không khai báo, thiếu hướng dẫn.

**Hành vi điển hình**
- Đọc README, kiểm tra phiên bản Python và dependency.
- Chạy một lệnh pipeline, xem log số dòng vào/ra.
- Chạy test, xóa thư mục output và chạy lại để kiểm tra tái lập.
- Mở dashboard, thử bộ lọc và đối chiếu một KPI với dữ liệu gốc.

**Nhu cầu với hệ thống**
- Một lệnh chạy toàn bộ pipeline; hỗ trợ chạy từng stage.
- README, data dictionary, mô tả nguồn IBGE và giấy phép.
- Test tự động cho cleaning/integration và kiểm tra chất lượng dữ liệu.
- Log có run_id, số dòng, thời gian, lỗi rõ ràng.
- Không phụ thuộc cloud, Kafka hay dịch vụ trả phí.

**Tiêu chí thành công**
- Chạy lại toàn bộ trong ≤ 15 phút sau khi cài dependency.
- Test pass; số dòng/KPI khớp baseline trong tài liệu.
- Giải thích được mọi quyết định làm sạch quan trọng.

**Không thuộc nhu cầu của P2**
- Tùy biến giao diện theo thương hiệu hoặc phân quyền người dùng.
