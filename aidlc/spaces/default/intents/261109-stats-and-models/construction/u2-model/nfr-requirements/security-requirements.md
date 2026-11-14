# Security Requirements — u2-model

Nguồn: `../functional-design/{functional-spec.md,rules.md,entities.md}`, `../../../inception/requirements-analysis/requirements.md`, `../../../inception/contract-design/contract-summary.md`, và quy tắc dự án trong `aidlc/spaces/default/memory/project.md`.

Requirements Analysis **không có yêu cầu bảo mật riêng** cho đơn vị này: NFR1–NFR4 không nói tới xác thực, phân quyền hay mã hoá. Tệp này ghi các ràng buộc kế thừa; không sinh mã `NFRx.y` mới, và `traceability.json` không có dòng nào cho phần bảo mật.

| Mã | Ràng buộc kế thừa | Nguồn |
|---|---|---|
| SEC-1 | Mọi truy vấn dựng bảng đặc trưng dùng placeholder `?`; tên cột lấy từ hằng số, không nối chuỗi | quy tắc dự án về SQL tham số hoá |
| SEC-2 | Chỉ đọc các view trong `VIEW_TABLES`; `dataset/` chỉ đọc | quy tắc dự án về `dataset/` |
| SEC-3 | Khối mô hình chỉ chứa số tổng hợp và tên cột mục tiêu — không `customer_id`, không địa chỉ, không mã bưu chính | `entities.md` |
| SEC-4 | Không bí mật, không khoá, không gọi dịch vụ ngoài; mô hình không được lưu ra đĩa | quy ước phụ thuộc của repo |
| SEC-5 | Đường dẫn báo cáo lấy từ `AppConfig` qua hàm ghi của U1 | SEC-5 của `u1-statistics` |

## Điều đáng chú ý riêng của đơn vị này

Rủi ro bảo mật thật sự ở đây không phải rò rỉ dữ liệu mà là **rò rỉ nhãn**: đưa một cột chỉ có sau khi giao vào đặc trưng sẽ cho AUC đẹp giả tạo. Đó là lý do BR2.3 và danh sách cột bị cấm tồn tại — chúng bảo vệ tính đúng đắn của kết quả, và được kiểm bằng test chứ không bằng rà soát mắt.

Mô hình **không được tuần tự hoá ra đĩa**: chỉ số của nó đi vào báo cáo, bản thân mô hình bị bỏ sau khi chạy. Lưu một tệp mô hình sẽ tạo thêm một tài sản phải quản lý phiên bản mà không ai đọc.

## Điều phải kiểm khi viết mã

| Mã | Cách kiểm |
|---|---|
| SEC-1 | Test khẳng định truy vấn dựng từ tham số, không nối chuỗi đầu vào |
| SEC-2 | Test khẳng định mọi bảng được đọc nằm trong `VIEW_TABLES` |
| SEC-3 | Test khẳng định khối `model` trong tệp không chứa `customer_id` hay `customer_unique_id` |
| SEC-4 | Không có lời gọi mạng trong mã; `ruff` không phát hiện hằng chuỗi giống khoá |
| SEC-5 | Test khẳng định đường dẫn báo cáo đến từ `AppConfig`, không từ tham số dòng lệnh |
