# Security Design — u3-display

Nguồn: `../nfr-requirements/security-requirements.md`, `../functional-design/functional-spec.md`, `../functional-design/rules.md`, `../../../inception/contract-design/contract-summary.md` (C2).

## Bối cảnh

Tab bind `127.0.0.1`, một người dùng, đọc một tệp cục bộ. Không có bề mặt xác thực, không có biên mạng, không có đầu vào người dùng ngoài việc chọn tab — bộ chọn ngưỡng đã bị bỏ (Q1 = A).

## Quyết định

| # | Quyết định | Phục vụ | Vì sao |
|---|---|---|---|
| SDU-1 | Không có ô nhập, không có thanh trượt, không có tham số đường dẫn trong tab | SEC-U3-1 | Không có đầu vào thì không có bề mặt để khai thác |
| SDU-2 | Đường dẫn báo cáo lấy từ `AppConfig` qua `read_report`, không từ URL hay query string | SEC-U3-2 | Một đường dẫn do người dùng đặt là bề mặt đọc tệp tuỳ ý |
| SDU-3 | Chỉ hiển thị số tổng hợp; không đưa `customer_id`, `customer_unique_id`, địa chỉ hay mã bưu chính vào chuỗi hiển thị | SEC-U3-3 | Tab là bề mặt thứ hai của một tệp chia sẻ được |
| SDU-4 | Nội dung tệp được dựng qua thành phần `dmc`/`dash` như **dữ liệu**; không `dangerously_allow_html`, không `innerHTML` | SEC-U3-4 | Chuỗi từ tệp không bao giờ được chạy như mã |
| SDU-5 | Không tải tài nguyên ngoài; mọi thứ đến từ `assets/` của repo | SEC-U3-5 | Tab chạy offline, không có lý do gọi ra ngoài |

## Ranh giới tin cậy

```
data/reports/analysis.json ──read_report (C2)──▶ u3-display ──dmc/dash──▶ trình duyệt 127.0.0.1
     không tin cậy về nội dung                      │
                                                    └── không nhận đầu vào, không gọi mạng
```

Tệp báo cáo là **không tin cậy về nội dung**: nó có thể bị sửa tay, hỏng, hoặc do một phiên bản phần mềm khác ghi. `read_report` đã thuần hoá phần lớn rủi ro bằng bốn trạng thái, nhưng tab vẫn phải coi mọi chuỗi trong tệp là dữ liệu hiển thị, không phải mã.

## Điều phải kiểm khi viết mã

Năm phép kiểm ở `../nfr-requirements/security-requirements.md` § "Điều phải kiểm khi viết mã", cộng một phép nữa: tab gọi `read_report` **đúng một lần** trong một callback (NFR5.6) — vừa là hiệu năng, vừa để mỗi lần dựng chỉ đọc một ảnh nhất quán của tệp.
