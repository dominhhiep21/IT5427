# Observability Setup — câu hỏi

Không có câu hỏi mới. Stage này chốt việc **không** dựng hạ tầng giám sát, vì hệ chạy local một người dùng và đã có ba tín hiệu đủ dùng (nhật ký JSONL, `QualityGate`, `KpiReconciler`).

## Consolidated Summary Confirmation

Tóm tắt để bạn xác nhận:

1. **Không dựng dashboard giám sát riêng**: tab "Tích hợp" của chính sản phẩm, `QualityGate`, `KpiReconciler` và nhật ký JSONL đóng vai đó.
2. **Không có alarm/paging**: không có người nhận thứ hai; "cảnh báo" là danh sách dấu hiệu phải dừng, gồm `pipeline.completed success=False`, dòng `ERROR`, KPI lệch, `QualityGate` đỏ, và cổng đối chiếu lát cắt đỏ.
3. **SLO thay thế bằng tính đúng**: SLO-1 số trên vùng khớp phép tính độc lập (0 sai lệch), SLO-2 5 KPI lệch 0, SLO-3 11 view + 9 bảng mart khớp baseline. Không có SLO theo thời gian vì không có dịch vụ chạy nền.
4. **`run_id` đóng vai trace id**: mọi sự kiện của một lần chạy mang cùng `run_id`; `plan_id` nối một con số trên màn hình với một dòng nhật ký.
5. **Không phát hiện bất thường tự động**: ba bất thường nhận ra bằng luật đơn giản (số dòng nạp, `correct_rate`, truy vấn chậm) nhưng không tự động hoá, vì sẽ tạo cảnh báo giả hoặc cổng trùng.
6. **Không có OpenTelemetry/X-Ray/CloudWatch**: một tiến trình duy nhất, thêm tracing không đổi lấy thông tin nào.

Does this all look correct?

- A. Looks correct
- B. Request changes

[Answer]: Looks correct