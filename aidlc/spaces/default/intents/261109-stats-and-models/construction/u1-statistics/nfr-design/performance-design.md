# Performance Design — u1-statistics

Nguồn: `../nfr-requirements/performance-requirements.md`, `../functional-design/functional-spec.md`, `../../../inception/contract-design/contract-summary.md`.

## Quyết định

| # | Quyết định | Phục vụ | Vì sao |
|---|---|---|---|
| PD-1 | Mỗi phép đọc dữ liệu **một lần**, không đọc lại trong vòng lặp | NFR1.1 | Truy vấn là chi phí lớn nhất; năm truy vấn rẻ hơn nhiều truy vấn nhỏ |
| PD-2 | Đẩy phép gộp xuống SQL, không kéo dòng thô về Python | NFR1.1, NFR1.3 | Chỉ số dòng trả về là số nhóm (bang, tháng), không phải 99.441 dòng |
| PD-3 | Dùng lại các phương thức sẵn có của `AnalyticsService` khi chúng trả đúng thứ cần; thêm ba phương thức đọc mới cho phần chưa có | NFR1.1 | `kpi_summary` và `revenue_by_period` đã trả đúng tỉ lệ trễ và doanh thu kỳ; ba phép còn lại cần dữ liệu mà lớp hiện tại chưa phơi ra |
| PD-4 | Phân rã mùa vụ dùng `pandas.Series.rolling` một lượt qua chuỗi | NFR1.4 | Chi phí tuyến tính theo số tháng, không dựng ma trận |
| PD-5 | Ghi tệp một lần, sau khi mọi phép xong | NFR1.1 | Không ghi từng phần rồi ghép |

## Phương thức đọc cần có

`AnalyticsService` hiện có năm phương thức công khai: `kpi_summary`, `revenue_by_period`, `revenue_by_dimension`, `top_entities`, `delivery_kpis`. Đối chiếu với năm phép:

| Phép | Nguồn đọc | Trạng thái |
|---|---|---|
| BR1.1 tỉ lệ trễ | `kpi_summary` — đã có số đơn trễ và số đơn đã giao | Dùng lại |
| BR1.2 so sánh bang | `late_rates_by_state()` | **Thêm** — cần tỉ lệ trễ theo từng bang kèm số đơn |
| BR1.3 tương quan giá–phí | `price_freight_pairs()` | **Thêm** — cần cặp giá/phí ở grain dòng hàng, có chặn số dòng |
| BR1.4 vùng × trễ | `late_rates_by_region()` | **Thêm** — cần bảng đếm vùng × trễ |
| BR1.5 mùa vụ | `revenue_by_period` với kỳ tháng | Dùng lại |

Ba phương thức mới nằm trong `src/analytics/service.py`, dùng lại `_connect` và `_where`, và trả DataFrame đã gộp — không trả dòng thô. Việc mở rộng lớp này là chủ đích: quy tắc nhóm ghi rõ phân tích mới phải **đọc** mart qua lớp có sẵn chứ không định nghĩa lại doanh thu.

## Ngân sách thời gian

| Bước | Ngân sách | Ghi chú |
|---|---|---|
| Năm truy vấn đọc | ≤ 60 s tổng | Bốn view đã gộp sẵn; `price_freight_pairs` là truy vấn nặng nhất và có chặn số dòng |
| Năm phép kiểm định | ≤ 40 s mỗi phép, tổng ≤ 200 s | NFR1.2; đo trong test, không qua nhật ký. Phép tỉ lệ trễ tính cả vào đây |
| Dựng khối + làm tròn | ≤ 10 s | Trên vài chục số |
| Ghi tệp + kiểm đọc lại | ≤ 10 s | Tệp vài chục KB |
| **Tổng** | **≤ 280 s**, dưới mốc 300 s của NFR1.1 | Biên dự phòng khoảng 20 s |

Con số 5 phút ở NFR1.1 là **trần**, không phải tổng của các ngân sách: bảng trên cộng lại 280 s, và phần dư là biên cho máy chậm hơn máy phát triển.

## Điều không làm

- Không cache giữa các lần chạy: dữ liệu vào là mart, đã nằm trên đĩa, và một cache thứ hai chỉ tạo thêm một trạng thái phải làm mới.
- Không song song hoá năm phép: chúng chạy trong một tiến trình, `AnalyticsService` mở và đóng kết nối trong từng phương thức nên song song hoá chỉ thêm tranh chấp, và nó sẽ làm hỏng tính tất định của thứ tự `skipped`.
