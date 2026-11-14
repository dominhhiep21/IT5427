# Decisions — Kiểm định thống kê và mô hình dự báo

## ADR-01 — Tách thống kê và mô hình thành hai mô-đun

**Context.** Hai phần có nhịp thay đổi khác nhau: phần kiểm định ổn định sau khi chốt công thức, phần mô hình còn thử nghiệm đặc trưng và ngưỡng.

**Decision.** Hai mô-đun riêng trong `src/analytics`: `stats.py` và `model.py`.

**Consequences.** Thay đổi ở mô hình không chạm phần kiểm định; test tách theo mô-đun; cần một kiểu báo cáo chung để ghép hai phần.

**Alternatives rejected.** Một mô-đun chung (dễ lệch nhịp thay đổi); một gói mới (không cần thiết vì cùng miền phân tích).

## ADR-02 — Đọc dữ liệu qua `AnalyticsService` hiện có

**Context.** Phần mới cần mart và view DuckDB; đã có lớp truy vấn với tham số hoá và bộ lọc.

**Decision.** Dùng `AnalyticsService` thay vì mở kết nối riêng.

**Consequences.** Không lặp định nghĩa doanh thu; mọi truy vấn mới phải đi qua lớp này; nếu cần truy vấn đặc thù thì thêm hàm vào service, không viết SQL rời.

**Alternatives rejected.** Truy vấn trực tiếp trong mô-đun mới (dễ lặp định nghĩa KPI); lớp đọc riêng (thêm một lớp nữa cho cùng việc).

## ADR-03 — Một thành phần ghi báo cáo dùng chung

**Context.** Hai phần cùng sinh kết quả cần ghi vào một tệp.

**Decision.** `report-writer` nhận kết quả từ cả hai phần và ghi một tệp JSON qua `AtomicWriter`.

**Consequences.** Một chỗ duy nhất quyết định hình dạng tệp; hai phần không biết đường dẫn tệp; ghi tệp vẫn an toàn khi tiến trình dừng.

**Alternatives rejected.** Mỗi phần tự ghi (hai tệp, dễ lệch); tầng pipeline ghi (pipeline phải biết hình dạng báo cáo).

## ADR-04 — Đọc báo cáo qua hàm dùng chung có kiểm cấu trúc

**Context.** Tab chỉ đọc; nếu đọc rời trong callback thì mỗi lần sửa định dạng phải sửa nhiều nơi.

**Decision.** `report-reader` trong cùng mô-đun, kiểm trường bắt buộc và trả lỗi có kiểu.

**Consequences.** Tab chỉ việc hiển thị; trạng thái lỗi có nguồn rõ; đọc thiếu trường thì báo lỗi thay vì hiện số rỗng.

**Alternatives rejected.** Đọc trực tiếp trong callback (lặp mã, khó test).

## ADR-05 — Một kiểu dữ liệu chung cho toàn bộ báo cáo

**Context.** Hai phần trả kết quả khác nhau nhưng cùng ghi một tệp.

**Decision.** Một dataclass báo cáo gồm hai khối con, mỗi khối có kiểu riêng.

**Consequences.** Chỗ ghép kiểu rõ ràng; tab đọc một kiểu duy nhất; thêm khối mới là thay đổi có chủ đích ở kiểu.

**Alternatives rejected.** Dict tự do (không kiểm được); hai kiểu rời rạc (người đọc phải tự ghép).
