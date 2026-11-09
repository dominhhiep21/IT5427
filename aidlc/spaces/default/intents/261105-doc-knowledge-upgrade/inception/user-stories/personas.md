# Personas — Nâng cấp tích hợp dữ liệu Olist

Hai persona, đúng phạm vi đã chốt: người chấm là người dùng chính của giao diện mới, người vận hành là người chạy và kiểm tra hệ thống.

## P1 — Người chấm (giảng viên/hội đồng)

| Trường | Nội dung |
|---|---|
| Vai trò | Giảng viên hoặc thành viên hội đồng chấm đồ án |
| Mục tiêu | Thấy bằng chứng hệ thống thật sự áp dụng bốn nhóm lý thuyết tích hợp dữ liệu; đối chiếu được với bài giảng |
| Nỗi đau | Dashboard hiện chỉ cho thấy báo cáo cuối, không cho thấy quá trình tích hợp; không phân biệt được "làm đúng lý thuyết" với "ghép dữ liệu bằng tay" |
| Bối cảnh dùng | Mở dashboard trên laptop hoặc máy chiếu, xem trong vài phút mỗi phần |
| Mức quen kỹ thuật | Trung bình — đọc được thuật ngữ lý thuyết (GAV, blocking, query rewriting) nhưng không đọc mã |
| Tần suất | Một lần, ở buổi bảo vệ |

## P2 — Người vận hành (chủ dự án)

| Trường | Nội dung |
|---|---|
| Vai trò | Người xây và chạy hệ thống; cũng là người quyết định phạm vi |
| Mục tiêu | Chạy lại được toàn bộ hệ thống bằng một lệnh, kiểm tra kết quả tích hợp đúng, và biết ngay khi có hồi quy |
| Nỗi đau | Cùng một sự thật dữ liệu đang khai ở nhiều nơi; sửa một chỗ dễ làm lệch KPI mà không biết |
| Bối cảnh dùng | Terminal và trình duyệt localhost, làm việc theo từng đơn vị công việc |
| Mức quen kỹ thuật | Cao — đọc và sửa mã, chạy test, đọc log |
| Tần suất | Hằng ngày trong đợt nâng cấp |

## Quan hệ và thứ tự ưu tiên

- **P1 là người dùng chính của tab "Tích hợp"**: mọi câu chuyện giao diện viết cho P1.
- **P2 là người dùng chính của công cụ kiểm tra**: các câu chuyện về chạy lại, đối chiếu, và không hồi quy viết cho P2.
- Khi hai persona xung đột (ví dụ P2 muốn nhiều chi tiết kỹ thuật, P1 muốn gọn), ưu tiên P1 ở phần hiển thị mặc định và để chi tiết kỹ thuật ở lớp thứ hai.
