# Monitoring Design — u6-integration-ui

Nguồn: `nfr-design/performance-design.md`, `nfr-design/security-design.md`, `functional-design/functional-spec.md` (W5), `inception/requirements-analysis/requirements.md` (NFR1, NFR4).

## 1. Vì sao tab này cần giám sát nhẹ

Tab mới gọi bốn hợp đồng và ba đơn vị; khi một hợp đồng hỏng, người dùng phải thấy **cái gì** hỏng, không phải một màn hình trắng. Giám sát ở đây là **trạng thái hiển thị + log ứng dụng**, không phải hạ tầng.

## 2. Tín hiệu

| Tín hiệu | Nguồn | Ngưỡng | Hành động |
|---|---|---|---|
| Thời gian callback | `time.perf_counter` trong từng callback | > 2000 ms | Ghi WARNING vào log; màn hình hiện trạng thái chờ nếu còn đang chạy |
| Lỗi hợp đồng | Ngoại lệ bắt ở L1 | bất kỳ | `StateBlock("loi")` + log ERROR có `error_code` |
| Trạng thái một phần | `partial` của C4/C5/C7 | khác rỗng | `StateBlock("mot-phan")` liệt kê phần thiếu |
| Layout dựng được | `build_layout` | luôn | Test dashboard; lỗi ở đây là sự cố toàn app |

## 3. Nhật ký

Dùng logger của lần chạy (`src/common/logging.py`): `dashboard.tab.opened` (INFO), `dashboard.tab.slow` (WARNING, `callback`, `elapsed_ms`), `dashboard.tab.failed` (ERROR, `callback`, `error_code`). Không ghi dữ liệu ô, không ghi PII.

## 4. Không áp dụng

Không SLI/SLO, không alerting, không dashboard giám sát: sản phẩm chạy local, một người dùng. Sức khoẻ của app là "bốn tab mở được và test dashboard xanh".
