# Logical Components — u1-statistics

Nguồn: `../functional-design/entities.md`, `../functional-design/rules.md`, `../nfr-requirements/*`, `../../../inception/domain-design/components.md`.

Đây là góc nhìn **thành phần logic** của đơn vị — nơi các mẫu NFR ở trên được áp vào. Nó không phải sơ đồ triển khai: tất cả chạy trong một tiến trình, một tệp.

## Đối chiếu với danh mục thành phần của Domain Design

`components.md` khai hai thành phần thuộc đơn vị này: `stats-module` (tính toán) và `stats-stage` (nối vào chuỗi `pipeline`); cộng `report-writer` và `report-reader` cho phần báo cáo. Các thành phần nội bộ dưới đây **nằm trong** `stats-module` — chúng là cách chia bên trong để cách ly lỗi, không phải thành phần mới ở cấp kiến trúc.

| Thành phần nội bộ | Thuộc | Trách nhiệm | Quy tắc | Miền hỏng riêng |
|---|---|---|---|---|
| `stats-orchestrator` | `stats-stage` | Đọc dữ liệu, gọi năm phép, gom `skipped`, dựng báo cáo, gọi ghi | BR1.1, BR1.6, BR1.11 | Không — lỗi ở đây dừng cả tầng |
| `late-rate-test` | `stats-module` | Tỉ lệ trễ + khoảng Wilson | BR1.1 | Không — trường bắt buộc, lỗi điều kiện dừng tầng |
| `state-comparison-test` | `stats-module` | So sánh bang cao nhất / thấp nhất, đếm đơn bị loại | BR1.2 | Có — lỗi điều kiện thành `skipped` |
| `correlation-test` | `stats-module` | Tương quan giá–phí + khoảng Fisher | BR1.3 | Có — `n < 4` thành `skipped` |
| `group-test` | `stats-module` | Vùng × trễ, chi-square | BR1.4 | Có — ô kỳ vọng dưới 5 thành `skipped` |
| `seasonal-test` | `stats-module` | Phân rã mùa vụ chuỗi doanh thu tháng | BR1.5 | Có — dưới 24 tháng thành `skipped` |
| `skip-collector` | `stats-module` | Giữ danh sách `SkipEntry`, không trùng tên | BR1.6 | Không |
| `report-writer` | `report-writer` | Tệp tạm → đọc lại kiểm → thay tệp | BR1.11 | Không — lỗi ném ở biên CLI |
| `report-reader` | `report-reader` | Bốn trạng thái, không ném | BR1.9, BR1.10 | Không — mọi lỗi thành `ReportView` |

## Tài nguyên dùng chung

| Tài nguyên | Ai dùng | Cách ly |
|---|---|---|
| `AnalyticsService` trên DuckDB | `stats-orchestrator` và ba phép cần đọc | Mỗi lời gọi phương thức tự mở và đóng kết nối; không có kết nối dùng chung nào được giữ qua các phép |
| `data/reports/analysis.json` | `report-writer`, `report-reader` | Chỉ ghi một lần ở cuối; đọc không bao giờ ghi |
| Logger JSONL | mọi thành phần | Một `run_id` cho cả tầng |

## Bán kính ảnh hưởng

| Hỏng ở | Ảnh hưởng | Vì sao dừng ở đó |
|---|---|---|
| `late-rate-test` | Dừng cả tầng, không ghi tệp | `late_rate` là trường bắt buộc trong C1; một báo cáo thiếu nó không hợp lệ |
| Một trong bốn phép còn lại | Chỉ mất kết quả của phép đó | BR1.6: `null` + `SkipEntry` |
| `report-writer` | Không có tệp mới; tệp cũ nguyên | Ghi qua tệp tạm rồi thay |
| `report-reader` | Không ảnh hưởng tầng ghi | Hai thành phần chỉ chia sẻ đường dẫn, không chia sẻ trạng thái |
| Dữ liệu mart | Dừng cả tầng | Không có gì để tính |

## Điều không có

Không có thành phần hạ tầng nào: không tiến trình nền, không hàng đợi, không bộ nhớ đệm, không dịch vụ. Danh sách trên dừng ở chín thành phần trong một tiến trình — và đó là toàn bộ.
