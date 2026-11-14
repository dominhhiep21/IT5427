# Escalation Matrix

Nguồn: `incident-plan.md`, `runbooks.md`, `aidlc/spaces/default/memory/team.md` (`## Way of Working`).

## Không có ai để leo thang tới

Team là **một người**. Không có trực ca thứ hai, không có quản lý, không có nhóm nền tảng. Bảng leo thang vì vậy chỉ có một hàng thật, và việc trung thực là nói đúng như vậy thay vì vẽ một sơ đồ ba cấp không tồn tại.

| Mức | Người xử | Thời hạn | Khi nào leo thang |
|---|---|---|---|
| P1 | người làm | ngay, trước mọi việc khác | không có nơi để leo |
| P2 | người làm | ngay | không có nơi để leo |
| P3 | người làm | khi có thời gian | không có nơi để leo |

## Ba nơi *có* thể nhờ, và giới hạn của chúng

| Nguồn | Giúp được gì | Không giúp được gì |
|---|---|---|
| Kiến trúc sư AI trong phiên | soi thiết kế, tìm mâu thuẫn, kiểm bằng mã thật | không biết trạng thái máy, không sửa được thay người |
| CI trên GitHub | nói bước nào hỏng, trên máy sạch | không nói được gì về môi trường cục bộ |
| Tài liệu trong repo (`docs/runbook.md`, `CHANGELOG.md`, `code-summary.md`) | nhắc lại quy trình và điều đã thử | không cập nhật theo thực tế nếu không ai sửa |

## Điều đáng ghi vào record

Một người làm nghĩa là **không có kiểm tra độc lập nào ngoài kiểm tra tự động**. Đây là rủi ro đã ghi ở `team-allocation.md` từ giai đoạn lập kế hoạch, và đợt này xác nhận nó: mọi lỗi được bắt trong phiên này đều do kiến trúc sư AI hoặc do test bắt, không do người thứ hai.

Bù lại bằng ba thứ đã có: test end-to-end trên dữ liệu thật, `KpiReconciler` khẳng định baseline, và kiểm bằng mã thật thay vì đọc chữ.

## Điều không có

Không PagerDuty, không kênh Slack, không hotline, không nhà cung cấp. Không có gì để cấu hình.
