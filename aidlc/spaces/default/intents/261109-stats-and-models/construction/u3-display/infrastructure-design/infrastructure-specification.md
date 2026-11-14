# Infrastructure Specification — u3-display

Nguồn: `../nfr-design/{logical-components.md,security-design.md,performance-design.md}`, `../functional-design/functional-spec.md`, `../../../inception/domain-design/components.md`, `../../../inception/contract-design/contract-summary.md`.

## Bối cảnh: đơn vị này không có hạ tầng triển khai

Tab chạy trong tiến trình Dash sẵn có trên máy người làm, bind `127.0.0.1:8050`, đọc một tệp JSON cục bộ. Không container, không dịch vụ đám mây, không môi trường thứ hai. Tệp này không mô tả VPC, IAM hay autoscaling — mô tả chúng cho một tab giao diện là bịa hạ tầng không tồn tại.

## Bốn thứ thật sự là hạ tầng của tab

| # | Thành phần | Hiện trạng | Vai trò với U3 |
|---|---|---|---|
| INF-U3-1 | Tiến trình `python -X utf8 -m src.dashboard` | Có | Nơi tab chạy |
| INF-U3-2 | `data/reports/analysis.json` | Sinh bởi tầng `stats` | Nguồn dữ liệu duy nhất |
| INF-U3-3 | `assets/style.css` | Có | Nguồn token màu, khoảng cách, cỡ chữ |
| INF-U3-4 | `.github/workflows/ci.yml` | Có | Cổng tự động duy nhất |

## Yêu cầu lên hạ tầng

| Mã | Yêu cầu | Vì sao |
|---|---|---|
| INDU-1 | Cần quyền ghi lên **gốc workspace**, không chỉ `logs/` | `load_config()` tạo 11 thư mục lúc khởi động (`inbox/`, `data/`, `warehouse/`, `dataset/external/ibge`, …), nên tiến trình dashboard cần quyền ghi ở gốc, không phải chỉ ở `logs/`. Tab chỉ đọc tệp báo cáo, nhưng nó chạy trong tiến trình có tác dụng phụ đó |
| INDU-2 | Không cần quyền mạng lúc chạy | Mọi tài nguyên đến từ `assets/` của repo |
| INDU-3 | Không có phụ thuộc mới | TSU-2: tab dựng trên `dash` và `dash-mantine-components` đã ghim |
| INDU-4 | Không có tệp cấu hình mới | Đường dẫn lấy từ `AppConfig` |

## Điều không có, và vì sao

- **Không container hoá.** Tab chạy chung tiến trình với bốn tab cũ; tách nó ra nghĩa là hai tiến trình cùng bind một cổng.
- **Không môi trường thứ hai.** Tab đọc cùng tệp với dashboard hiện có; một staging sẽ phải giữ cùng tệp mà không có lợi ích nào.
- **Không sao lưu.** Báo cáo sinh lại được bằng một lệnh.

## Rủi ro hạ tầng

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Gốc ứng dụng không bọc `dmc.MantineProvider` | `dmc.Title` lỗi lúc chạy, không lỗi lúc test tĩnh | Tab mới tự bọc provider quanh nội dung của nó, như `src/integration/tab.py` đang làm |
| Dashboard đang mở khi chạy lại `integrate` | Khoá `warehouse/olist.duckdb` | Đóng dashboard trước khi chạy, đã ghi trong `docs/runbook.md` |
| Báo cáo chưa sinh lúc mở tab | Tab hiện `rong` kèm lệnh cần chạy | Hành vi đúng theo BR3.5, không phải sự cố |
