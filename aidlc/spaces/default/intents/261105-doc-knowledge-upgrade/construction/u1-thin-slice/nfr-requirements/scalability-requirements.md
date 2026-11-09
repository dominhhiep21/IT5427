# Scalability Requirements — u1-thin-slice

Nguồn: `inception/requirements-analysis/requirements.md` (NFR6 — chạy local), `ideation/feasibility/constraint-register.md` (TC-04).

Không có câu hỏi mới: hệ thống đã chốt chạy một máy, một người dùng.

| Mã | Yêu cầu | Ngưỡng |
|---|---|---|
| SC-U1-1 | Số người dùng đồng thời | 1 (một phiên dashboard) |
| SC-U1-2 | Kích thước dữ liệu | 99.441 đơn, không tăng trong đợt này |
| SC-U1-3 | Thêm dữ liệu | Không cần: đợt này không có nguồn mới, không có nạp tăng dần |

## Ghi chú

Không có yêu cầu mở rộng ngang, không có sharding, không có cache phân tán. Nếu sau này cần nhiều người dùng, đó là thay đổi phạm vi phải chốt lại.
