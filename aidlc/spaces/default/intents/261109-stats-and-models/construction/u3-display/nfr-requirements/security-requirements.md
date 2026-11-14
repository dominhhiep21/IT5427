# Security Requirements — u3-display

Nguồn: `../functional-design/{functional-spec.md,rules.md}`, `../../../inception/requirements-analysis/requirements.md`, `../../../inception/contract-design/contract-summary.md` (C2), `aidlc/spaces/default/memory/project.md`.

Requirements Analysis không có yêu cầu bảo mật riêng cho đơn vị này. Tab bind `127.0.0.1`, một người dùng, đọc một tệp cục bộ. Tệp này ghi các ràng buộc kế thừa.

| Mã | Ràng buộc kế thừa | Nguồn |
|---|---|---|
| SEC-U3-1 | Tab không nhận đầu vào từ người dùng ngoài thao tác chọn tab; không có ô nhập, không có tham số đường dẫn | thiết kế: không có bộ chọn ngưỡng (Q1 = A) |
| SEC-U3-2 | Đường dẫn báo cáo lấy từ `AppConfig`, không từ URL hay tham số | quy tắc dự án |
| SEC-U3-3 | Chỉ hiển thị số tổng hợp; không có `customer_id`, địa chỉ, mã bưu chính | C2 và `entities.md` của U3 |
| SEC-U3-4 | Nội dung tệp được hiển thị như **dữ liệu**, không bao giờ chạy như mã; không `html.H1` từ chuỗi báo cáo | quy ước an toàn của Dash |
| SEC-U3-5 | Không gọi dịch vụ ngoài; không tải tài nguyên từ CDN lạ | repo hiện có |

## Điều phải kiểm khi viết mã

| Mã | Cách kiểm |
|---|---|
| SEC-U3-1 | Không có `dcc.Input`/`dcc.Slider` trong tab mới |
| SEC-U3-2 | Test khẳng định đường dẫn đến từ `AppConfig` |
| SEC-U3-3 | Test khẳng định chuỗi hiển thị không chứa `customer_id` hay `customer_unique_id` |
| SEC-U3-4 | Không dùng `dangerously_allow_html` hay `innerHTML` với chuỗi từ tệp |
| SEC-U3-5 | Không có URL ngoài trong mã tab |
