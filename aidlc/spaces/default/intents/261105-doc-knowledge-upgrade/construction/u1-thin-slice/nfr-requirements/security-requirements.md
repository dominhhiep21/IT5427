# Security Requirements — u1-thin-slice

Nguồn: `inception/requirements-analysis/requirements.md` (NFR6, ràng buộc RC-01/RC-02 ở `constraint-register.md`), `contract-summary.md` (C8, C9 — hai hợp đồng U1 tham gia).

Không có câu hỏi mới: bước Feasibility đã xác nhận không có dữ liệu cá nhân và không có yêu cầu quy định.

| Mã | Yêu cầu | Cách đáp ứng |
|---|---|---|
| SR-U1-1 | Không có xác thực người dùng | Dashboard chỉ bind `127.0.0.1:8050`; không mở ra mạng ngoài |
| SR-U1-2 | Không có bí mật nào trong mã | Không có API key, token hay mật khẩu; toàn bộ dữ liệu đọc từ `dataset/` cục bộ |
| SR-U1-3 | Không nhận đầu vào người dùng dựng thành SQL | Đơn vị này chỉ chạy một truy vấn cố định; mọi tên cột/tên bảng lấy từ tệp khai báo phải **kiểm theo danh sách cho phép** (`checked_identifier`) trước khi ghép vào SQL, và mọi giá trị vẫn truyền qua placeholder `?` |
| SR-U1-4 | Dữ liệu cá nhân | Không xử lý; `ma_khach` là mã ẩn danh có sẵn trong dữ liệu nguồn |
| SR-U1-5 | Tệp cấu hình không chứa bí mật | `config.yaml` **không có khoá, mật khẩu hay token**; chỉ có đường dẫn, URL công khai (`ibge.url`) và các ngưỡng số (geolocation, quality, duckdb, micro_batch, cổng dashboard) |

## Rủi ro đã biết

Mở dashboard trên một máy dùng chung cho phép người khác xem số liệu. Chấp nhận: dữ liệu Olist công khai, không có dữ liệu cá nhân thật.
