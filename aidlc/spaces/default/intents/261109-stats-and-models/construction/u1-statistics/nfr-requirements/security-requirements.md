# Security Requirements — u1-statistics

Nguồn: `../functional-design/functional-spec.md`, `../functional-design/rules.md`, `../../../inception/requirements-analysis/requirements.md`, `../../../inception/contract-design/contract-summary.md`, và các quy tắc đã chốt của dự án trong `aidlc/spaces/default/memory/project.md`.

Đơn vị này **không có yêu cầu bảo mật riêng trong Requirements Analysis**: NFR1–NFR4 không nói tới xác thực, phân quyền hay mã hoá. Vì vậy tệp này ghi lại các ràng buộc kế thừa, không sinh mã `NFRx.y` mới. Trong `traceability.json`, phần bảo mật không có dòng nào.

| Mã | Ràng buộc kế thừa | Nguồn |
|---|---|---|
| SEC-1 | Mọi truy vấn dùng placeholder `?`; tên cột và `GROUP BY` lấy từ dict hằng, không nối chuỗi | quy tắc dự án "truyền tham số SQL qua placeholder" |
| SEC-2 | Không đọc hay ghi bảng nào ngoài các view mart đã khai; `dataset/` chỉ đọc | quy tắc dự án về `dataset/` bất biến |
| SEC-3 | Báo cáo chỉ chứa số tổng hợp theo bang, vùng và tháng — không có `customer_id`, `customer_unique_id`, địa chỉ hay mã bưu chính | thiết kế `entities.md` |
| SEC-4 | Không có bí mật, khoá hay thông tin đăng nhập trong mã; không gọi dịch vụ ngoài | quy ước lỗi và phụ thuộc của repo |
| SEC-5 | Đường dẫn tệp báo cáo lấy từ `AppConfig`, không nhận từ đầu vào người dùng | `config.yaml` |

## Vì sao không có yêu cầu riêng

Đơn vị chạy trong tiến trình của người dùng, trên máy của người dùng, đọc dữ liệu công khai đã qua tổng hợp. Không có biên mạng, không có người dùng thứ hai, không có dữ liệu cá nhân ở mức định danh trong đầu ra. Áp thêm mốc xác thực hay mã hoá ở đây là thêm thứ không có gì để bảo vệ.

## Điều phải kiểm khi viết mã

| Mã | Cách kiểm |
|---|---|
| SEC-1 | Một test khẳng định truy vấn dựng từ tham số không nối chuỗi đầu vào |
| SEC-2 | Một test khẳng định danh sách bảng được đọc nằm trong `VIEW_TABLES`, và không tệp nào trong `dataset/` bị mở để ghi |
| SEC-3 | Một test khẳng định tệp báo cáo không chứa `customer_id` hay `customer_unique_id` |
| SEC-4 | `ruff` không phát hiện hằng chuỗi giống khoá; rà bằng mắt trong lần duyệt mã |
| SEC-5 | Một test khẳng định đường dẫn báo cáo lấy từ `AppConfig`, không nhận tham số dòng lệnh |
