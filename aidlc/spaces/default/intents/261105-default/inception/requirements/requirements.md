# Yêu cầu dự án — Olist E-commerce Data Pipeline

## 1. Tóm tắt phân tích ý định

- **Yêu cầu người dùng**: “Xây dựng quy trình tích hợp, làm sạch và phân tích dữ liệu thương mại điện tử từ bộ dữ liệu Olist.”
- **Loại yêu cầu**: Dự án mới (greenfield).
- **Phạm vi**: Nhiều thành phần — ingestion, cleaning, integration, storage, analytics, dashboard.
- **Độ phức tạp**: Trung bình đến phức tạp (dữ liệu nhiều grain, nhiều bẫy chất lượng, yêu cầu dashboard và minh họa 3V).
- **Mục tiêu**: Tạo pipeline chạy cục bộ, có thể tái lập, biến 9 CSV Olist thô thành mô hình star schema trong DuckDB/Parquet và dashboard Plotly Dash phục vụ phân tích doanh thu.

## 2. Mục tiêu và tiêu chí thành công

1. Ingestion đầy đủ 9 CSV Olist, không sửa dữ liệu gốc.
2. Làm sạch và tích hợp thành star schema, xử lý đúng các bẫy đã phát hiện trong reverse engineering.
3. Dashboard tiếng Việt trả lời được các câu hỏi về doanh thu, xu hướng và danh mục.
4. Minh họa đặc trưng big data (volume, variety, velocity) bằng micro-batch có kiểm soát.
5. Có kiểm thử dữ liệu, log và tài liệu để người khác chạy lại.

**Chỉ số thành công**

| Chỉ số | Mục tiêu |
|---|---|
| Số tệp nguồn ingest | 9/9 |
| Đối soát số dòng | Khớp 100% với CSV gốc sau bước raw |
| Khóa trùng sau làm sạch | 0 ở các khóa đã khai báo |
| Orphan record | 0 ở các quan hệ bắt buộc |
| Thời gian chạy full batch | ≤ 10 phút trên máy cá nhân |
| Thời gian phản hồi dashboard | ≤ 3 giây cho bộ lọc thông thường |
| Độ phủ kiểm thử logic | ≥ 70% cho module cleaning/integration |

## 3. Phạm vi

### Trong phạm vi

- 9 CSV Olist trong `dataset/`.
- Dữ liệu tham chiếu chính thức của Brazil (IBGE) tải từ internet, lưu cache.
- Pipeline batch + mô phỏng micro-batch qua thư mục `inbox/`.
- Star schema trong DuckDB, dữ liệu trung gian và mart dạng Parquet.
- Dashboard Plotly Dash.
- Báo cáo, tài liệu, nhãn giao diện bằng tiếng Việt.
- ML là hạng mục tùy chọn, không chặn MVP.

### Ngoài phạm vi

- Kafka/Redpanda, Spark Structured Streaming hoặc streaming thật.
- Cloud (Databricks, BigQuery, Snowflake), Docker bắt buộc.
- Đăng nhập, phân quyền, multi-tenant.
- NLP cảm xúc chuyên sâu, deep learning.
- Ứng dụng mobile.
- Sửa hoặc chuẩn hóa ngược vào `dataset/`.

## 4. Yêu cầu chức năng

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-01 | Ingestion 9 CSV với kiểm tra schema, encoding và đối soát số dòng | Must |
| FR-02 | Làm sạch kiểu dữ liệu, null, trùng lặp, danh mục và địa lý | Must |
| FR-03 | Tích hợp star schema trong DuckDB/Parquet | Must |
| FR-04 | Phân tích doanh thu, xu hướng, danh mục, khu vực | Must |
| FR-05 | Dashboard Plotly Dash tiếng Việt | Must |
| FR-06 | Micro-batch ingestion qua `inbox/` | Must |
| FR-07 | Tích hợp dữ liệu tham chiếu IBGE | Must |
| FR-08 | Kiểm thử dữ liệu và đối soát doanh thu | Must |
| FR-09 | CLI điều phối pipeline, log và báo cáo lần chạy | Must |
| FR-10 | Tài liệu vận hành, data dictionary, README | Must |
| FR-11 | Mô hình ML dự báo giao trễ hoặc điểm đánh giá | Could |

### FR-01 — Ingestion

- Đọc 9 CSV UTF-8, không BOM, phân tách bằng dấu phẩy.
- Kiểm tra sự hiện diện và thứ tự cột theo hợp đồng dữ liệu.
- Ghi log: tên tệp, số dòng, số cột, hash SHA-256, thời điểm đọc.
- Không ghi đè hoặc sửa `dataset/`.
- Lưu bản raw đã kiểm tra dưới dạng Parquet trong `data/raw/`.

### FR-02 — Làm sạch

- Parse tất cả cột thời gian sang kiểu datetime; ghi nhận số null.
- Chuẩn hóa `customer_city`, `seller_city`, `geolocation_city`: trim, lowercase, bỏ khoảng trắng thừa; không tự động sửa tên không chắc chắn.
- Geolocation: loại tọa độ ngoài khung Brazil, gộp về **một dòng/zip** bằng trung vị lat/lng; lưu số dòng gốc và số dòng sau gộp.
- Danh mục: left join bảng dịch; 2 danh mục thiếu bản dịch giữ tên gốc và gắn cờ `translation_missing`.
- Sản phẩm thiếu danh mục: gán `unknown`, giữ cờ `category_missing`.
- Reviews: giữ tất cả đánh giá; tạo cờ `multiple_reviews_per_order` cho 547 đơn (551 dòng review dư).
- Payments: giữ grain `(order_id, payment_sequential)`; không cộng dồn trước khi join item.
- Đơn không có item: giữ trong `fact_orders`, cờ `has_items = false`.
- Không xóa outlier doanh thu mặc định; tạo cờ `price_outlier` theo IQR để phân tích riêng.

### FR-03 — Tích hợp star schema

Mô hình tối thiểu:

- `fact_order_items`: grain `(order_id, order_item_id)`; giá, phí vận chuyển, khóa sản phẩm/seller/khách hàng/ngày.
- `fact_orders`: grain `order_id`; trạng thái, các mốc thời gian, cờ giao trễ, cờ có item/thanh toán/đánh giá.
- `fact_payments`: grain `(order_id, payment_sequential)`.
- `fact_reviews`: grain `review_id` + `order_id` (không giả định `review_id` duy nhất).
- Dimensions: `dim_customer`, `dim_product`, `dim_seller`, `dim_category`, `dim_geography`, `dim_date`.
- `dim_customer` phải phân biệt `customer_id` (theo đơn) và `customer_unique_id` (theo người).
- `dim_geography` một dòng/zip, có bang, vùng IBGE và tọa độ đã gộp.
- Tất cả bảng mart lưu Parquet; DuckDB tạo view/table star schema trỏ tới Parquet.

### FR-04 — Phân tích

Trọng tâm chính: **doanh thu, xu hướng bán hàng và hiệu quả theo danh mục**.

Bắt buộc:

- Doanh thu theo tháng/quý/năm; tăng trưởng so với kỳ trước.
- Doanh thu, số đơn, số lượng bán theo danh mục và theo bang/vùng.
- Giá trị đơn trung bình (AOV), tỷ trọng phí vận chuyển.
- Top sản phẩm, top seller theo doanh thu.
- Phân bố trạng thái đơn và tỷ lệ giao trễ (KPI phụ).

Quy ước:

- **Doanh thu mặc định** = `SUM(price + freight_value)` trên đơn `delivered`.
- **Doanh thu thanh toán** = `SUM(payment_value)` dùng để đối soát, không dùng thay thế mặc định.
- **Tỷ lệ giao trễ** = số đơn `delivered` có `order_delivered_customer_date > order_estimated_delivery_date` / tổng đơn `delivered`.
- **Khách hàng duy nhất** dùng `customer_unique_id`.
- Dữ liệu 2016 chỉ có 329 đơn; hiển thị nhưng gắn nhãn “dữ liệu chưa đầy đủ”.

### FR-05 — Dashboard

- Công nghệ: Plotly Dash.
- Bộ lọc: khoảng thời gian, bang/vùng, danh mục, trạng thái đơn.
- Thành phần tối thiểu:
  - Thẻ KPI: doanh thu, số đơn, AOV, tỷ lệ giao trễ.
  - Biểu đồ đường doanh thu theo thời gian.
  - Biểu đồ cột doanh thu theo danh mục.
  - Bản đồ hoặc bảng xếp hạng theo bang/vùng.
  - Bảng top sản phẩm/seller.
- Nhãn, tiêu đề, tooltip bằng tiếng Việt; định dạng tiền BRL và ngày dd/mm/yyyy.
- Dashboard đọc từ DuckDB/Parquet, không đọc lại CSV thô.

### FR-06 — Micro-batch

- Thư mục `inbox/` nhận các tệp CSV micro-batch mới.
- Mỗi lần chạy xử lý các tệp chưa có trong manifest, ghi nhận tệp + hash + thời điểm.
- Chạy lại cùng một tệp không tạo bản ghi trùng (idempotent).
- Có lệnh replay để phát lại dữ liệu lịch sử theo lô nhỏ.
- Không cần Kafka hay hạ tầng streaming thật.

### FR-07 — Dữ liệu IBGE

- Tải dữ liệu bang/municipality chính thức của IBGE từ internet.
- Lưu vào `dataset/external/ibge/` kèm metadata: URL, thời điểm tải, hash.
- Ánh xạ 27 bang → 5 vùng.
- Nếu tải thất bại: pipeline dừng với lỗi rõ ràng, không âm thầm bỏ qua; cho phép dùng cache đã có.
- Không dùng dữ liệu IBGE để thay thế zip code Olist.

### FR-08 — Kiểm thử và đối soát

- Test đơn vị cho cleaning, dedupe geolocation, dịch danh mục, tính KPI.
- Test dữ liệu: khóa duy nhất, orphan, số dòng, khoảng giá trị.
- Đối soát số dòng: raw vs cleaned vs mart.
- Đối soát doanh thu: chênh lệch `payment_value` và `price + freight_value` phải được báo cáo, không tự động sửa.
- Báo cáo kết quả test trong log/lần chạy.

### FR-09 — CLI và vận hành

- Lệnh thống nhất, ví dụ: `python -m src.pipeline run --stage all`.
- Hỗ trợ chạy từng stage: `ingest`, `clean`, `integrate`, `analyze`.
- Log ra console và tệp; mỗi lần chạy có run_id.
- Lỗi schema/khóa phải làm pipeline fail-fast với thông báo rõ.

### FR-10 — Tài liệu

- `README.md`: cài đặt, cách chạy, cấu trúc thư mục.
- Data dictionary tiếng Việt cho các bảng mart.
- Mô tả nguồn IBGE và giấy phép.
- Hướng dẫn khởi động dashboard.

### FR-11 — ML tùy chọn

- Có thể bổ sung dự báo giao trễ hoặc điểm đánh giá.
- Chỉ triển khai sau khi MVP pipeline + dashboard hoàn tất.
- Kết quả ML không được thay đổi KPI mặc định.

## 5. Yêu cầu phi chức năng

| ID | Yêu cầu | Tiêu chí |
|---|---|---|
| NFR-01 | Hiệu năng batch | Full pipeline ≤ 10 phút trên máy cá nhân |
| NFR-02 | Hiệu năng dashboard | Phản hồi ≤ 3 giây với bộ lọc thông thường |
| NFR-03 | Tái lập | Venv + `requirements.txt` có phiên bản; chạy được từ CSV gốc |
| NFR-04 | Toàn vẹn dữ liệu | Không mất dòng hợp lệ; mọi mất mát phải được log |
| NFR-05 | Khả dụng | Dashboard tiếng Việt, định dạng ngày/tiền Việt Nam |
| NFR-06 | Quan sát | Log có run_id, stage, số dòng vào/ra, thời gian |
| NFR-07 | Bảo mật | Không chứa secret; chỉ chạy cục bộ |
| NFR-08 | Tương thích | Windows, Python 3.13, UTF-8 |
| NFR-09 | Bảo trì | Code tách module, type hints, test tự động |
| NFR-10 | Chịu lỗi nguồn ngoài | IBGE dùng cache; lỗi mạng không làm hỏng mart cũ |

## 6. Ràng buộc kỹ thuật

- Ngôn ngữ: Python 3.13.
- Xử lý: pandas + DuckDB; dữ liệu mart dạng Parquet (PyArrow).
- Dashboard: Plotly Dash.
- Kiểm thử: pytest.
- **Không** dùng SQLite/PostgreSQL cho star schema; quyết định làm rõ là DuckDB quản lý star schema trên Parquet.
- **Không** dùng Spark, Kafka, cloud.
- Dữ liệu gốc `dataset/` là bất biến.
- Cấu trúc thư mục dự kiến:
  - `src/` — pipeline, cleaning, integration, analytics, dashboard.
  - `data/raw/`, `data/cleaned/`, `data/marts/` — Parquet trung gian.
  - `warehouse/olist.duckdb` — catalog/view.
  - `inbox/` — micro-batch.
  - `dataset/external/ibge/` — dữ liệu tham chiếu.
  - `tests/` — unit + data quality.
  - `aidlc-docs/` — tài liệu quy trình.

## 7. Quy tắc dữ liệu và KPI

| Quy tắc | Định nghĩa |
|---|---|
| Doanh thu mặc định | `SUM(price + freight_value)` trên đơn `delivered` |
| Doanh thu thanh toán | `SUM(payment_value)` để đối soát |
| AOV | Doanh thu mặc định / số đơn `delivered` duy nhất |
| Tỷ lệ giao trễ | Đơn `delivered` giao sau `order_estimated_delivery_date` / tổng đơn `delivered` |
| Khách hàng duy nhất | `COUNT(DISTINCT customer_unique_id)` |
| Tỷ lệ mua lặp | Khách có ≥ 2 đơn `delivered` / khách có ≥ 1 đơn `delivered` |
| Tỷ lệ hoàn tất | Đơn `delivered` / tổng đơn |
| Danh mục thiếu dịch | Giữ tên gốc + cờ `translation_missing` |

**Baseline đã xác minh từ dữ liệu thô**

- 99.441 đơn; 96.478 đơn `delivered` (97,0%).
- 112.650 dòng hàng; 103.886 giao dịch thanh toán; 99.224 đánh giá.
- 7.826 đơn giao trễ / 96.478 đơn delivered = 8,11%.
- Thời gian giao trung vị 10,2 ngày; trung bình 12,6 ngày.
- Điểm đánh giá trung bình ~4,09/5.
- Tổng `price + freight_value` = 15.843.553,24 BRL; tổng `payment_value` = 16.008.872,12 BRL.

## 8. Tiêu chí chấp nhận

| ID | Tiêu chí |
|---|---|
| AC-01 | Chạy một lệnh từ môi trường sạch tạo đủ raw/cleaned/marts và DuckDB catalog |
| AC-02 | 9/9 tệp được ingest; số dòng raw khớp CSV gốc |
| AC-03 | Join khách hàng với geolocation cho đúng 99.441 dòng, không bùng nổ |
| AC-04 | Grain `order_items` giữ 112.650 dòng; payments/reviews không nhân bản dòng hàng |
| AC-05 | 610 sản phẩm thiếu danh mục và 2 danh mục thiếu dịch được giữ lại với cờ tương ứng |
| AC-06 | Dashboard hiển thị KPI và biểu đồ, lọc theo ngày/bang/danh mục, nhãn tiếng Việt |
| AC-07 | Tỷ lệ giao trễ tính được và khớp baseline 8,11% khi không lọc |
| AC-08 | Chạy lại micro-batch với cùng tệp không tạo bản ghi trùng |
| AC-09 | 27 bang được ánh xạ đủ 5 vùng IBGE |
| AC-10 | Test dữ liệu và unit test chạy bằng một lệnh, kết quả pass |

## 9. Giả định và rủi ro

**Giả định**

- Máy có internet khi tải IBGE lần đầu; sau đó dùng cache.
- Người dùng chấp nhận cài `duckdb`, `pyarrow`, `dash`, `plotly`, `pytest`.
- Dữ liệu Olist là đầy đủ cho giai đoạn 2016-2018; không cần crawl thêm.
- Dashboard chạy cục bộ, một người dùng.

**Rủi ro**

| Rủi ro | Ảnh hưởng | Giảm thiểu |
|---|---|---|
| IBGE đổi URL/định dạng | Không map được vùng | Cache + kiểm tra schema + lỗi rõ ràng |
| Cài DuckDB/PyArrow thất bại trên Windows | Không chạy pipeline | Pin phiên bản, hướng dẫn riêng |
| Nhầm grain khi join | Sai KPI | Test số dòng + khóa duy nhất |
| Dữ liệu 2016 thưa | Xu hướng sai | Gắn nhãn, không nội suy |
| ML vượt thời gian | Trễ MVP | Để ML sau, không chặn dashboard |
| Dashboard chậm | Trải nghiệm kém | Mart pre-aggregate, index/view DuckDB |

## 10. Truy vết quyết định

| Câu hỏi | Trả lời | Thể hiện trong |
|---|---|---|
| Q1 Engine | C — DuckDB + Parquet | Mục 6, FR-03 |
| Q2 Storage | B — Star schema | FR-03; làm rõ: DuckDB thay SQLite/PostgreSQL |
| Q3 Deliverable | A — Full pipeline + dashboard | Mục 3, FR-05 |
| Q4 Analytics focus | A — Doanh thu/danh mục | FR-04 |
| Q5 Dashboard | B — Plotly Dash | FR-05 |
| Q6 3V/velocity | B — Micro-batch | FR-06 |
| Q7 External data | B — IBGE | FR-07 |
| Q8 ML | B — Tùy chọn | FR-11 |
| Q9 Language | A — Tiếng Việt | FR-05, FR-10, NFR-05 |
| Clarification 1 | A — DuckDB star schema | FR-03, Mục 6 |
| Clarification 2 | B — Tải IBGE, lưu `dataset/external/ibge/` | FR-07 |
| Clarification 3 | A — `inbox/` micro-batch | FR-06 |
