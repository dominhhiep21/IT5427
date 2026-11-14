# Câu hỏi — Deployment Pipeline

Không có câu hỏi nào, và đây là lý do.

## Vì sao không có gì để hỏi

Dự án **không có môi trường triển khai**. Mọi lựa chọn mà stage này thường hỏi — chiến lược triển khai, cổng thăng cấp, thời điểm chuyển lưu lượng, chiến lược migration — đều giả định có ít nhất hai môi trường. Không có môi trường thứ hai thì không có gì để chọn.

Ba điều đã được chốt trong `## Deployment` của `project.md` và đợt này không mở lại:

- "Phát hành" = chạy bốn bước từ mã nguồn sau khi CI xanh.
- Phiên bản = commit hash, cộng một mốc `CHANGELOG.md`; không có git tag.
- Không có bước build hay đóng gói.

## Ba thứ đáng lẽ là câu hỏi

| Đáng lẽ hỏi | Đã chốt ở đâu |
|---|---|
| Chiến lược triển khai nào? | Không áp dụng — không có môi trường. `deployment-strategy.md` ghi rõ vì sao blue/green và canary sai giả định |
| Có tag phát hành không? | Không — `## Deployment` nói phiên bản là commit hash |
| Có giữ bản sao lưu dữ liệu dẫn xuất không? | Không — sinh lại được bằng một lệnh; bản sao lưu là trạng thái phải đồng bộ |

Nếu bạn muốn thêm môi trường staging, đó là thay đổi hạ tầng và phạm vi; tôi sẽ ghi vào record trước khi làm, và nó sẽ kéo theo một đợt riêng chứ không chen vào đây.

## Consolidated Summary Confirmation

- Stage này không có câu hỏi nào, nên không có câu trả lời nào để tóm tắt.
- Nền của nó là ba điều đã chốt trong `## Deployment` của `project.md`: "phát hành" = bốn bước từ mã nguồn sau khi CI xanh; phiên bản = commit hash cộng mốc `CHANGELOG.md`, không có git tag; không có bước build hay đóng gói.
- Vì không có môi trường thứ hai, `cd-config.md` ghi rõ không có CD pipeline, và `deployment-strategy.md` ghi rõ blue/green và canary sai giả định.
- `rollback-runbook.md` lùi được cả bốn loại hỏng, ba trong bốn không mất dữ liệu vì `dataset/` bất biến.

- Looks correct
- Request changes

[Answer]: Looks correct

