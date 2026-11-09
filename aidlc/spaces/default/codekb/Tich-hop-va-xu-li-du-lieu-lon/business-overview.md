# Tổng quan nghiệp vụ — Olist E-commerce Data Pipeline

> Phạm vi: repo `Tich-hop-va-xu-li-du-lieu-lon`, quét toàn bộ `./` tại commit
> `41c422ffd7f3b27a2f78a67eaccc43a00d13c77e`. Chi tiết kỹ thuật xem
> `architecture.md`, `component-inventory.md`, `code-quality-assessment.md`.

## 1. Bối cảnh nghiệp vụ

Hệ thống phục vụ bài toán **tích hợp và xử lý dữ liệu lớn** trên bộ dữ liệu công khai
**Olist Brazilian E-Commerce** (Brazil, 09/2016 – 10/2018). Đây là đồ án môn học: thư mục
`doc/` chứa đề bài (`doc/Projects.pdf`) và slide bài giảng về bốn nhóm kiến thức tích hợp
dữ liệu (đồng nhất lược đồ và lược đồ trung gian, ghép bản ghi, xử lý truy vấn, chọn nguồn).

Dữ liệu mô tả **một sàn thương mại điện tử**: đơn hàng, khách hàng, người bán, sản phẩm,
dòng hàng, thanh toán, đánh giá, vị trí địa lý theo mã bưu chính (CEP) và bảng dịch danh mục.
Sản phẩm bàn giao là **pipeline batch chạy cục bộ** biến 9 tệp CSV thô thành **star schema**
trong Parquet + DuckDB, kèm **dashboard Plotly Dash tiếng Việt** để đọc KPI.

## 2. Mục đích hệ thống

| Mục tiêu | Cách hệ thống đáp ứng | Bằng chứng |
|---|---|---|
| Tích hợp nhiều nguồn lệch lược đồ | Hợp đồng lược đồ tường minh cho 9 bảng, chuẩn hóa tên/kiểu, ánh xạ danh mục qua bảng dịch | `src/ingest/schemas.py`, `src/clean/products.py` |
| Bảo đảm chất lượng dữ liệu | Cổng chất lượng 21 check cấu trúc; chế độ `full` thêm 9 check số dòng và 10 dị thường có allowlist | `src/quality/gate.py`, `src/quality/allowlist.py` |
| Mô hình hóa phân tích | 5 dimension, 4 fact, 2 aggregate; kiểm tra grain và khóa duy nhất | `src/integrate/dimensions.py`, `src/integrate/facts.py`, `src/integrate/aggregates.py` |
| Truy vấn phân tích | 11 view DuckDB trên Parquet, dịch vụ truy vấn chỉ đọc | `src/integrate/catalog.py`, `src/analytics/service.py` |
| Trình bày kết quả | Dashboard 3 tab (Tổng quan, Danh mục, Giao vận) | `src/dashboard/app.py` |
| Mô phỏng vận tốc dữ liệu | Micro-batch theo `inbox/<batch_id>/<table>.csv`, manifest SHA-256 idempotent, replay theo tháng | `src/pipeline/micro_batch.py`, `src/pipeline/replay.py` |

## 3. Chức năng chính (theo lát cắt người dùng)

1. **Chạy toàn bộ pipeline** bằng một lệnh CLI: `python -m src.pipeline run --stage all`
   (ingest → clean → quality → integrate → analyze).
2. **Chạy từng tầng** riêng lẻ để gỡ lỗi (`--stage ingest|clean|integrate|analyze`).
3. **Nạp dữ liệu tăng dần** từ hộp thư `inbox/`, upsert theo khóa tự nhiên, bỏ qua batch đã
   xử lý theo hash.
4. **Replay lịch sử**: cắt dữ liệu đã làm sạch theo tháng gần nhất để tạo batch và xử lý tuần tự.
5. **Xem KPI và biểu đồ** theo bộ lọc ngày/bang/vùng/danh mục/trạng thái đơn.

## 4. Chỉ số nghiệp vụ chuẩn (KPI baseline)

Các con số dưới đây là **hợp đồng hồi quy** của hệ thống: `src/integrate/reconcile.py` chặn
pipeline nếu lệch quá dung sai, và test tích hợp khẳng định lại chúng.

| KPI | Giá trị | Định nghĩa |
|---|---|---|
| Doanh thu đơn `delivered` | 15.419.773,75 BRL | Tổng `price + freight_value` của dòng hàng thuộc đơn đã giao |
| Số đơn `delivered` | 96.478 | `COUNT(DISTINCT order_id)` trên dòng hàng đã giao |
| AOV | 159,83 BRL | Doanh thu / số đơn giao được |
| Đơn giao trễ | 7.826 | `delivered_customer_date > estimated_delivery_date` |
| Tỷ lệ giao trễ | 8,11% | Đơn trễ / đơn đã giao |

Nguồn: `src/integrate/reconcile.py` (hằng số `BASELINE`), `README.md`, `docs/3v.md`.
Lưu ý: doanh thu ở đây **gồm phí vận chuyển**; tổng `payment_value` không khớp tuyệt đối
(378 đơn lệch > 0,01 BRL — xem `reconcile_payments` trong `src/ingest/reports.py`).

## 5. Đối tượng sử dụng

| Vai trò | Nhu cầu | Bề mặt sử dụng |
|---|---|---|
| Kỹ sư dữ liệu / người vận hành | Chạy lại pipeline, xử lý batch lỗi, đọc log | CLI `src.pipeline`, `logs/<run_id>.jsonl`, `docs/runbook.md` |
| Nhà phân tích nghiệp vụ | Xem doanh thu, danh mục, giao vận theo bộ lọc | Dashboard Dash tại `http://127.0.0.1:8050` |
| Giảng viên / người chấm | Đối chiếu 3V, kiến trúc, bằng chứng chất lượng | `docs/3v.md`, `docs/data-dictionary.md`, báo cáo JSON trong `data/reports/` |
| Lập trình viên mở rộng | Thêm nguồn, thêm tab, đổi mô hình | `src/` theo tầng, `tests/` |

## 6. Ba đặc trưng dữ liệu lớn (3V) như hệ thống tuyên bố

- **Volume**: 1.550.922 dòng trên 9 CSV; riêng `geolocation` 1.000.163 dòng.
- **Variety**: grain khác nhau (đơn, dòng hàng, thanh toán, đánh giá), dữ liệu tham chiếu
  ngoài (IBGE 27 bang → 5 vùng), nhiều kiểu thuộc tính (giao dịch, vận chuyển, địa lý, văn bản).
- **Velocity**: batch đầy đủ + micro-batch + replay theo tháng; **không phải streaming thật**
  (không Kafka), đây là mô phỏng có chủ đích (`docs/3v.md`).

## 7. Ranh giới và giả định nghiệp vụ

- `dataset/` là **nguồn bất biến**; mọi dẫn xuất ghi vào `data/`, `warehouse/`, `logs/`, `inbox/`.
- Chỉ phân tích đơn `delivered` theo mặc định (`KpiFilters.order_status = "delivered"`).
- Không có xác thực/người dùng: dashboard chỉ chạy localhost, một người dùng.
- Không có mô hình ML dự báo giao trễ (README ghi rõ "chưa triển khai").
- Toàn bộ thông điệp hiển thị cho người dùng bằng **tiếng Việt**; dữ liệu gốc giữ nguyên tiếng Bồ Đào Nha.

## 8. Thuật ngữ

| Thuật ngữ | Nghĩa trong hệ thống |
|---|---|
| **Grain** | Đơn vị một dòng: đơn (`order_id`), dòng hàng (`order_id, order_item_id`), thanh toán (`order_id, payment_sequential`), đánh giá (`review_id, order_id`) |
| **Mart** | Bảng Parquet dẫn xuất trong `data/marts/` (dimension, fact, aggregate) |
| **Cleaned** | Tầng dữ liệu đã chuẩn hóa kiểu/chuỗi trong `data/cleaned/` |
| **Raw** | Bản sao Parquet của CSV gốc trong `data/raw/` |
| **Allowlist dị thường** | Bộ đếm dị thường được chấp nhận cho lô đầy đủ (`src/quality/allowlist.py`) |
| **Đơn trễ** | Đơn `delivered` có ngày giao thực tế muộn hơn ngày dự kiến |
| **Batch** | Thư mục `inbox/<batch_id>/` chứa các CSV cùng lược đồ nguồn |

## 9. Liên kết

- Cách các thành phần ráp lại và luồng một đơn hàng: `architecture.md`.
- Danh sách thành phần, trách nhiệm, phụ thuộc: `component-inventory.md`.
- Bề mặt lệnh, hàm, view, tệp: `api-documentation.md`.
- Nợ kỹ thuật và rủi ro cho đợt nâng cấp: `code-quality-assessment.md`.
