# Escalation Matrix — intent `261111-model-feature-improvemen`

## 1. Ma trận (một người, nên ma trận ngắn)

| Mức | Ai xử lý | Trong bao lâu | Kênh |
|---|---|---|---|
| P1 | người làm (chủ repo) | ngay, dừng việc khác | không có kênh tự động — tự phát hiện qua cổng đỏ |
| P2 | người làm | trong ngày | |
| P3 | người làm | trước lần hợp nhất kế tiếp | |
| P4 | người làm | khi có dịp | ghi vào ghi chú, không mở việc riêng |

## 2. Điều ma trận này **không** có, và vì sao

| Không có | Vì sao |
|---|---|
| On-call rotation | một người; "on-call" là chính mình |
| Kênh thông báo (Slack/PagerDuty/email) | không có người nhận thứ hai, không có dịch vụ nền |
| Người phê duyệt thứ hai | `team.md`: không review chéo, CI là cổng duy nhất |
| Thời gian phản hồi theo SLA | không có người dùng ngoài; SLA sẽ là lời hứa rỗng |

## 3. Khi nào ma trận này phải đổi

Khi có **người thứ hai** hoặc **môi trường chạy tự động**. Lúc đó mới cần: kênh thông báo, người trực, SLA theo mức, và một người phê duyệt cho thay đổi baseline.

## 4. Liên hệ

Không ghi thông tin liên hệ cá nhân vào artifact được commit. Chủ repo tự biết đường liên hệ của mình.
