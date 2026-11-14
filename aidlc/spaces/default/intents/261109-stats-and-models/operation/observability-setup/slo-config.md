# SLO Configuration

Nguồn: `alarms.md`, `../../construction/build-and-test/performance-test-instructions.md`, `aidlc/spaces/default/memory/phases/operation.md` (`## Observability`).

## Không có SLO, và đây không phải thiếu sót

Phase guardrail yêu cầu SLO phải định lượng kèm cửa sổ thời gian (ví dụ "99,9% trong 30 ngày"). Yêu cầu đó giả định có **lưu lượng liên tục** — có request, có người dùng, có thời gian chết đo được.

Dự án này không có: tiến trình chạy theo lệnh, kết thúc, không có ai gọi từ ngoài. "99,9% trong 30 ngày" cho một lệnh chạy 5 phút là một con số không đo được — không có mẫu số.

## Thay thế đúng loại: mốc nghiệm thu

| Mục | Mốc | Cách kiểm |
|---|---|---|
| Tầng `stats` | dưới 5 phút | đo trong test `slow` trên dữ liệu thật |
| Tab dựng | dưới 1 giây | `perf_counter` trong test đơn vị |
| Độ phủ test | ≥ 80% | cổng trong CI |
| Không hồi quy | 5 KPI baseline + 9 bảng + 11 view | `KpiReconciler`, `StarSchemaValidator` |

Đây là **mốc nghiệm thu**, không phải cam kết vận hành: chúng được đo một lần khi thay đổi, không theo dõi liên tục, và không có error budget.

## Vì sao không giả làm SLO

Một SLO không có mẫu số sẽ được đọc là "hệ thống cam kết 99,9%", và người đọc sau sẽ tin điều đó. Đó là loại tài liệu tệ hơn không có tài liệu.

## Điều kiện để có SLO thật

Nếu sau này có dịch vụ thường trực — ví dụ một API phục vụ dự đoán (mức B trong đợt cải thiện đặc trưng) — thì lúc đó SLO mới có nghĩa, và nó phải được viết lại từ đầu kèm cửa sổ đo. Không chuyển mốc nghiệm thu thành SLO bằng cách đổi nhãn.
