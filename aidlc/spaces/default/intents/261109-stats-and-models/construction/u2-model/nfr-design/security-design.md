# Security Design — u2-model

Nguồn: `../nfr-requirements/security-requirements.md`, `../functional-design/rules.md`, `../nfr-requirements/tech-stack-decisions.md`, `../../../inception/contract-design/contract-summary.md`.

## Bối cảnh

Đơn vị không có bề mặt xác thực, không có biên mạng, không có người dùng thứ hai. Rủi ro thật của nó không phải rò rỉ dữ liệu mà là **rò rỉ nhãn** — đưa một cột chỉ có sau khi giao vào đặc trưng sẽ cho AUC đẹp giả tạo và một mô hình vô dụng trong thực tế.

## Quyết định

| # | Quyết định | Phục vụ | Vì sao |
|---|---|---|---|
| SD-1 | Danh sách 11 cột đặc trưng là **hằng số có tên** trong mã; tập cột bị cấm cũng là hằng số, và có hai test: hai tập rời nhau, và **khung đặc trưng thật** chỉ chứa đúng 11 tên đó | SEC-3, BR2.3 | Một danh sách viết trong tài liệu không chặn được ai; kiểm trên khung thật mới bắt được cột lọt vào qua đường ghép |
| SD-1b | `has_review` nằm trong tập cấm | SEC-3 | Nó là cột hậu giao cùng họ `has_*` với hai cờ được dùng, và có mặt trong `v_fact_orders`; để ngoài tập cấm là mở đúng cánh cửa mà SD-1 canh |
| SD-2 | Bảng đặc trưng dựng bằng một truy vấn tham số hoá, tên cột lấy từ hằng số | SEC-1 | Không có chuỗi người dùng nào vào SQL |
| SD-3 | Chỉ đọc các view trong `VIEW_TABLES`; không mở `dataset/` để ghi | SEC-2 | Ranh giới đọc/ghi của dự án |
| SD-4 | Khối `model` chỉ mang số tổng hợp và tên cột mục tiêu | SEC-3 | Báo cáo là tệp chia sẻ được, nó không mang định danh |
| SD-5 | Mô hình **không** tuần tự hoá ra đĩa | SEC-4 | Tệp mô hình là tài sản phải quản lý phiên bản mà không ai đọc |
| SD-6 | Đường dẫn báo cáo lấy từ `AppConfig`, qua hàm ghi của U1 — U2 không tự mở tệp | SEC-5 | Một đường dẫn do người dùng đặt là một bề mặt ghi đè tệp |

## Ranh giới tin cậy

```
mart (DuckDB/Parquet) ──đọc──▶ u2-model ──trả ModelBlock──▶ stats-stage (U1) ──write_report──▶ analysis.json
    tin cậy                        │                          │
                                   └── không nhận đầu vào ngoài, không gọi mạng, không tự ghi tệp ──┘
```

## Vì sao chống rò rỉ nhãn là việc bảo mật ở đây

Một mô hình bị rò rỉ nhãn không "hỏng" theo nghĩa kỹ thuật: nó chạy, nó cho AUC cao, và nó trả lời sai câu hỏi mà người dùng đặt ra. Đó là loại lỗi không ai phát hiện bằng cách nhìn kết quả — chỉ phát hiện bằng cách kiểm danh sách đặc trưng. Vì vậy nó được đối xử như một ràng buộc bảo mật, có test riêng.

## Kiểm khi viết mã

Năm phép kiểm ở `../nfr-requirements/security-requirements.md` § "Điều phải kiểm khi viết mã", cộng hai phép kiểm của SD-1: danh sách 11 đặc trưng và tập cột bị cấm không giao nhau, và khung đặc trưng thật chỉ chứa đúng 11 tên đó.
