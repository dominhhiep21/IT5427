# Escalation Matrix

## 1. Không có leo thang tới ai khác

Dự án một người. Không có on-call rotation, không có kênh thông báo, không có người phê duyệt thứ hai. Vì vậy "ma trận leo thang" ở đây là **leo thang theo mức độ**, không phải theo người.

## 2. Leo thang theo mức

| Từ | Sang | Điều kiện | Việc phải làm |
|---|---|---|---|
| P3 | P2 | lỗi lặp lại ≥ 3 lần trong một tuần, hoặc chặn một việc đang làm | ghi thành mục trong `incident-plan.md`, xử lý trong ngày |
| P2 | P1 | phát hiện số liệu cũng sai, không chỉ hệ không chạy | dừng mọi việc khác; chạy cổng đối chiếu trước |
| bất kỳ | dừng hẳn | nguyên nhân nằm ngoài phạm vi đợt (ví dụ dữ liệu nguồn đổi) | chốt lại phạm vi với người, không tự mở rộng |

## 3. Leo thang ra ngoài hệ

Chỉ một trường hợp: **dữ liệu nguồn `dataset/` bị thay đổi**. Khi đó mọi con số baseline trong `AGENTS.md` và mọi test dị thường đều vô hiệu. Việc đúng là dừng, báo người, và chốt lại baseline — không tự cập nhật.

## 4. Không có

- Không có kênh Slack/email/webhook: NFR6 cấm dashboard gọi mạng, và không có người nhận.
- Không có SLA phản ứng theo giờ: "trong ngày" cho P2, "ngay" cho P1 là mức thực tế của một người.
- Không có người trực thay: khi vắng thì hệ đứng yên, không có gì tự chạy để hỏng thêm.
