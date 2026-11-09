# Infrastructure Specification — u6-integration-ui

Nguồn: `nfr-design/{performance-design,security-design,logical-components}.md`, `functional-design/functional-spec.md`, `inception/domain-design/components.md`, `inception/contract-design/contract-summary.md`.

## 1. Triển khai

| Hạng mục | Giá trị | Ghi chú |
|---|---|---|
| Loại | Ứng dụng Dash chạy local trong tiến trình Python | Không container, không cloud, không scheduler |
| Địa chỉ | `127.0.0.1:8050` | Giữ nguyên `config.yaml`; không mở ra mạng (SR-U6-1) |
| Tiến trình | Một tiến trình duy nhất phục vụ cả bốn tab | Tab mới là một `dcc.Tab` trong cùng app |
| Tệp cấu hình | `config.yaml`, `config/integration-tab.yaml` | `card_ids` + `result_region_ids: [don-theo-thang]`; chỉ bỏ `result_block_ids` (ADR-U6-S2) |
| Dữ liệu vào | Hợp đồng C3–C9 trong tiến trình; `data/`, `warehouse/` do pipeline sinh | Tab mới không ghi tệp nào |

## 2. Dịch vụ dùng chung

| Dịch vụ | Ai dùng | Ghi chú |
|---|---|---|
| `config.yaml` | Toàn app | Không thêm khoá mới cho U6 |
| `config/integration-tab.yaml` | Tab "Tích hợp" | `card_ids` bốn giá trị và `result_region_ids: [don-theo-thang]` |
| `src/common/kpis.py` | Không đọc trực tiếp | Định nghĩa KPI đến tab qua `kpi_definitions` của C4; tab không có đường dữ liệu thứ hai |
| `load_config()` | Các tab cũ và mới | U6 không đổi hành vi |

## 3. Không có hạ tầng

Không máy chủ, không cơ sở dữ liệu riêng, không hàng đợi, không bí mật, không sao lưu. "Triển khai" = chạy `python -X utf8 -m src.dashboard`.
