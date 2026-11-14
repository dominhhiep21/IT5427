# Câu hỏi — Feedback & Optimization

Không có câu hỏi nào để hỏi bạn.

## Vì sao

Stage này thường hỏi bốn câu: SLO có đạt không, có cơ hội cắt chi phí nào, có trôi cấu hình không, hành vi người dùng gợi ý tính năng gì. Câu đầu không có mẫu số (đã chốt ở `slo-config.md`), câu hai và ba đã có câu trả lời đo được, còn câu bốn cần người dùng thật — dự án có một người dùng, là người làm.

## Consolidated Summary Confirmation

- Stage này không có câu hỏi, nên không có câu trả lời để tóm tắt.
- **SLO**: không có SLO để báo cáo tuân thủ, và đó là kết luận. Báo cáo thay bằng 8 mốc nghiệm thu so với thực đo — tất cả dư ít nhất 80 lần. Mục duy nhất không đạt là AUC 0,5133 so với mốc 0,70, và nó là mục tiêu chất lượng mô hình chứ không phải mốc vận hành.
- **Chi phí**: hoá đơn đám mây bằng 0, nên chi phí thật là đĩa ~260 MB, CI ~5,7 phút mỗi lần push (80% nằm ở bộ test phủ), và ~1,9 phút người làm mỗi chuỗi xác nhận. Bốn đề xuất tối ưu đã cân nhắc và **cả bốn bị từ chối**, mỗi cái kèm giá phải trả.
- **Trôi**: bảy phép đối chiếu, **hai chỗ trôi thật**. `README.md` chỉ dẫn lệnh định dạng hẹp hơn `ci.yml` (34 mục), và `docs/runbook.md` không có bước nào cho tầng `stats` — chỗ thứ hai đã bị nêu đúng ở `R-07` của U3 rồi bỏ lại `Unresolved`.
- **Vòng phản hồi**: phát hiện quan trọng nhất là mô hình 11 đặc trưng (AUC 0,5133) **tệ hơn** baseline một đặc trưng `customer_state` (0,5333). Đợt sau phải đánh bại baseline đó, không chỉ đạt 0,70.
- Bảy việc cho đợt sau (B1–B7) và năm việc **không** nên làm, mỗi việc kèm điều kiện nghiệm thu.
- Một câu hỏi sản phẩm để lại Ideation có chủ đích: khung dự đoán "lúc đặt hàng" có phải khung đúng, hay nên chuyển sang "lúc bàn giao cho đơn vị vận chuyển".

- Looks correct
- Request changes

[Answer]: Looks correct
