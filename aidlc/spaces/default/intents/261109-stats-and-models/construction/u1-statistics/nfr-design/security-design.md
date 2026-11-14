# Security Design — u1-statistics

Nguồn: `../nfr-requirements/security-requirements.md`, `../functional-design/rules.md`, `../../../inception/contract-design/contract-summary.md`.

## Bối cảnh

Đơn vị không có bề mặt xác thực, không có biên mạng, không có người dùng thứ hai. Thiết kế bảo mật ở đây là **giữ cho ba điều đó vẫn đúng** khi viết mã, chứ không phải dựng thêm lớp bảo vệ cho một bề mặt không tồn tại.

## Quyết định

| # | Quyết định | Phục vụ | Vì sao |
|---|---|---|---|
| SD-1 | Mọi truy vấn đi qua `AnalyticsService._where`, tham số hoá bằng `?`; tên cột và `GROUP BY` lấy từ dict hằng | SEC-1 | Không có chuỗi nào do người dùng nhập đi vào SQL |
| SD-2 | Chỉ đọc các view trong `VIEW_TABLES`; không mở tệp nào trong `dataset/` để ghi | SEC-2 | Ranh giới đọc/ghi của dự án |
| SD-3 | Chỉ xuất số tổng hợp; không đưa `customer_id`, `customer_unique_id`, địa chỉ hay mã bưu chính vào báo cáo | SEC-3 | Báo cáo là tệp chia sẻ được, nên nó không mang định danh |
| SD-4 | Không có bí mật trong mã; không gọi dịch vụ ngoài | SEC-4 | Không có gì để rò rỉ và không có điểm mạng để chặn |
| SD-5 | Đường dẫn báo cáo lấy từ `AppConfig` (`reports_dir`), không nhận từ dòng lệnh | SEC-5 | Một đường dẫn do người dùng đặt là một bề mặt ghi đè tệp |

## Ranh giới tin cậy

```
mart (DuckDB/Parquet)  ──đọc một chiều──▶  u1-statistics  ──ghi một tệp──▶  data/reports/analysis.json
      tin cậy                                   │                              │
                                                └── không nhận đầu vào ngoài ───┘
```

Không có mũi tên nào từ ngoài vào. Đầu vào duy nhất là mart do chính dự án dựng, và đầu ra duy nhất là một tệp trong thư mục cấu hình.

## Kiểm khi viết mã

Năm phép kiểm ở `../nfr-requirements/security-requirements.md` § "Điều phải kiểm khi viết mã" là điều kiện nghiệm thu của tệp này.
