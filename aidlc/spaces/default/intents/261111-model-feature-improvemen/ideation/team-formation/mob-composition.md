# Mob Composition

Nguồn: `team-assessment.md`, `skill-matrix.md`, `../scope-definition/intent-backlog.md`, `../../../261109-stats-and-models/operation/incident-response/escalation-matrix.md`.

## "Mob" ở đây là một người cộng với các vai agent

Mob programming cần từ hai người trở lên. Ở đây có một. Cách trung thực để viết mục này là nói rõ vai nào do người làm đảm nhận, vai nào do agent AI đảm nhận, và vai nào **không tồn tại** — thay vì gán ba vai cho một người rồi gọi đó là mob.

| Vai | Ai đảm nhận | Làm gì trong đợt này |
|---|---|---|
| **Driver** | người làm | viết mã, chạy lệnh, quyết định ở mỗi cổng |
| **Navigator** | agent kiến trúc sư / agent sản phẩm trong phiên | soát artifact, tìm mâu thuẫn, kiểm bằng mã thật thay vì đọc chữ |
| **Researcher** | người làm + agent | tra repo, tra tài liệu thư viện, đo số thật trên dữ liệu |
| **Reviewer độc lập** | **không có** | đây là vai duy nhất thật sự trống |
| **Người phê duyệt thứ hai** | **không có** | Q7 = A: người làm tự duyệt |

## Ba Bolt, ba nhịp

| Bolt | Đơn vị | Kết quả kiểm được khi xong | Điểm dừng cho người |
|---|---|---|---|
| **B1** | U1 | baseline `customer_state` trong khung mới, đo trên dữ liệu thật | xem con số rồi mới quyết định đi tiếp |
| **B2** | U2 | AUC của hai mô hình trên cùng đặc trưng, mô hình thắng đã lưu | xem AUC rồi quyết định giữ hay hạ mốc 0,70 |
| **B3** | U3 | giao diện dự đoán chạy từ mô hình đã lưu; mốc sàn 0,55 trong CI | xem bằng mắt ở 1280px |

Việc chia ba Bolt không phải để cho đẹp: ở 5–10 giờ/tuần, mỗi Bolt là khoảng một đến ba tuần, và mỗi Bolt kết thúc bằng **một con số bạn đọc được** — không phải một báo cáo tiến độ.

## Nhịp làm việc

| Việc | Khi nào |
|---|---|
| Chạy bộ nhanh trước khi commit | cuối mỗi phiên |
| Chuỗi bốn bước đầy đủ | cuối mỗi Bolt, không phải mỗi phiên |
| Cập nhật record | ngay khi một quyết định được chốt, không để cuối |
| Soát lại phạm vi | đầu mỗi Bolt, đối chiếu `scope-document.md` |

## Leo thang khi có sự cố

Không có ai để leo thang. Ba nguồn có thể nhờ, giới hạn của chúng đã ghi ở `escalation-matrix.md` của đợt trước: agent AI trong phiên (không biết trạng thái máy), CI (không biết môi trường cục bộ), tài liệu trong repo (không tự cập nhật).

## Điều mục này không hứa

Nó không hứa rằng agent AI thay được người soát thứ hai. Một agent đọc artifact không bắt được lỗi mà chỉ một người chạy thử mới thấy — nhưng nó **đã** bắt được lỗi thật ở đợt trước (bảy điểm ở Intent Capture, trong đó có một điểm nghiêm trọng), nên nó là thứ tốt nhất hiện có, không phải thứ tương đương.
