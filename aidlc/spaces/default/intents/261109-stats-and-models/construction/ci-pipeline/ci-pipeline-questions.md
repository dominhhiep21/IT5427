# Câu hỏi — CI Pipeline

Không có câu hỏi nào cho stage này, và đây là lý do thay vì để tệp trống.

## Vì sao không có câu hỏi

Cấu hình CI của dự án đã tồn tại từ trước và đã được chốt ở ba nơi:

- `## Way of Working` trong `project.md` — nhánh của đợt phải có mặt trong **cả hai** danh sách trigger, làm cùng lúc với việc tạo nhánh.
- `## Deployment` trong `project.md` — chuỗi xác nhận bốn bước, không có bước deploy.
- `## Testing Posture` trong `team.md` — cổng phủ 80% đo trên toàn bộ bộ test, không hạ ngưỡng.

Đợt này chỉ **thêm** vào cấu hình đã có: nhánh, tầng `stats`, tệp mới trong danh sách định dạng, và ghim `scikit-learn`. Không có lựa chọn kiến trúc nào mở ra.

## Ba thứ đáng lẽ là câu hỏi, nhưng đã có câu trả lời trong record

| Đáng lẽ hỏi | Đã chốt ở đâu |
|---|---|
| Có thêm bước deploy không? | Không — `## Deployment` nói rõ chưa có môi trường |
| Có ma trận đa hệ điều hành không? | Không — dự án chạy Windows, đường dẫn có tiếng Việt |
| Có cổng thời gian không? | Không — `performance-design.md` của U3 và NFR1.1 của U1 đều ghi rõ mốc thời gian là mục tiêu nghiệm thu, không phải cổng CI |

Nếu bạn muốn thêm bất kỳ mục nào ở trên, đó là thay đổi phạm vi và tôi sẽ ghi vào record trước khi làm.
