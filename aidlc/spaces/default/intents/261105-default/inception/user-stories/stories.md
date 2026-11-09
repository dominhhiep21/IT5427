# User Stories — Olist E-commerce Data Pipeline

## Quy ước

- **Persona**: P1 = Chuyên viên phân tích dữ liệu; P2 = Giảng viên/người đánh giá.
- **Ưu tiên**: MoSCoW — Must / Should / Could.
- **Acceptance criteria**: Given/When/Then.
- **Doanh thu mặc định**: `SUM(price + freight_value)` trên đơn `delivered`.
- **Doanh thu thanh toán**: `SUM(payment_value)` chỉ dùng đối soát.
- **Khách hàng duy nhất**: `customer_unique_id`.
- **Baseline**: 99.441 đơn; 96.478 delivered; 8,11% giao trễ; tổng `price + freight` toàn bộ = 15.843.553,24 BRL.

## Tổng quan epic

| Epic | Tên | Story | FR |
|---|---|---|---|
| E1 | Nền tảng ingestion và hợp đồng dữ liệu | US-01 → US-03 | FR-01, FR-08 |
| E2 | Làm sạch và chuẩn hóa dữ liệu Olist | US-04 → US-07 | FR-02 |
| E3 | Tích hợp star schema DuckDB/Parquet | US-08 → US-10 | FR-03 |
| E4 | Phân tích doanh thu và KPI | US-11 → US-14 | FR-04, FR-08 |
| E5 | Dashboard Plotly Dash | US-15 → US-17 | FR-05 |
| E6 | Micro-batch và dữ liệu IBGE | US-18 → US-19 | FR-06, FR-07 |
| E7 | Vận hành, tài liệu và ML tùy chọn | US-20 → US-22 | FR-08, FR-09, FR-10, FR-11 |

---

# E1 — Nền tảng ingestion và hợp đồng dữ liệu

## US-01 — Ingest đủ 9 tệp với kiểm tra schema

**Persona**: P2 · **Ưu tiên**: Must · **FR**: FR-01

**Câu chuyện**: Là người đánh giá, tôi muốn pipeline kiểm tra đủ 9 tệp và đúng cột trước khi xử lý, để lỗi dữ liệu đầu vào được phát hiện rõ ràng thay vì tạo ra kết quả sai.

**Giá trị**: Ngăn lỗi im lặng và tạo bằng chứng ingestion đầy đủ.

**Acceptance criteria**

- Given `dataset/` có 9 CSV, When chạy stage ingest, Then cả 9 tệp được đọc thành công và log ghi số dòng lần lượt: 99.441, 99.441, 112.650, 103.886, 99.224, 32.951, 3.095, 1.000.163, 71.
- Given một tệp thiếu cột hoặc sai thứ tự cột, When ingest, Then pipeline dừng với mã lỗi khác 0 và thông báo nêu tên tệp + cột thiếu.
- Given một tệp có encoding không phải UTF-8, When ingest, Then pipeline báo lỗi encoding thay vì đọc sai ký tự.

## US-02 — Bảo vệ dữ liệu gốc và ghi log lần chạy

**Persona**: P2 · **Ưu tiên**: Must · **FR**: FR-01

**Câu chuyện**: Là người đánh giá, tôi muốn dữ liệu gốc không bị sửa và mỗi lần chạy có log/hash, để có thể kiểm chứng tính tái lập.

**Giá trị**: Bảo vệ nguồn dữ liệu và tạo audit trail.

**Acceptance criteria**

- Given 9 CSV gốc, When chạy ingest, Then SHA-256 của từng tệp được ghi vào log và hash trước/sau khi chạy giống nhau.
- Given pipeline chạy lại, When hoàn tất, Then mỗi lần có `run_id` riêng và log ghi thời điểm bắt đầu/kết thúc từng stage.
- Given thư mục `dataset/`, When kiểm tra sau khi chạy, Then không có tệp nào bị sửa, thêm hoặc xóa.

## US-03 — Cổng kiểm tra chất lượng dữ liệu

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-08

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn pipeline chặn dữ liệu lỗi trước khi lên dashboard, để không đưa ra KPI sai.

**Giá trị**: Bảo đảm dashboard chỉ hiển thị dữ liệu đã qua kiểm tra.

**Acceptance criteria**

- Given dữ liệu đã ingest, When chạy quality gate, Then không có item/payment/review trỏ tới `order_id` không tồn tại.
- Given các khóa đã khai báo, When kiểm tra, Then `order_id` trong orders là duy nhất, `(order_id, order_item_id)` là duy nhất, `(order_id, payment_sequential)` là duy nhất.
- Given một kiểm tra thất bại, When pipeline chạy, Then pipeline dừng, log nêu bảng + khóa + số bản ghi lỗi, và không ghi đè mart cũ.

---

# E2 — Làm sạch và chuẩn hóa dữ liệu Olist

## US-04 — Chuẩn hóa thời gian, null và cờ ngoại lai

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-02

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn các cột thời gian đúng kiểu và các bất thường được gắn cờ, để tính đúng thời gian giao và không bỏ sót dữ liệu xấu.

**Giá trị**: KPI thời gian chính xác; ngoại lai vẫn có thể phân tích riêng.

**Acceptance criteria**

- Given các cột timestamp đang là chuỗi, When làm sạch, Then chúng được parse sang datetime và số null lần lượt là 160 (`order_approved_at`), 1.783 (`order_delivered_carrier_date`), 2.965 (`order_delivered_customer_date`).
- Given một timestamp không hợp lệ, When parse, Then bản ghi được gắn cờ lỗi và pipeline báo số lượng; không tự bịa giá trị thay thế.
- Given `price` và `freight_value`, When phân tích ngoại lai IQR, Then cờ `price_outlier` được tạo và không có dòng nào bị xóa; số dòng items vẫn là 112.650.

## US-05 — Gộp geolocation về một dòng mỗi zip

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-02

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn mỗi zip code có đúng một tọa độ đại diện, để join địa lý không làm nhân bản đơn hàng.

**Giá trị**: Ngăn lỗi nghiêm trọng nhất của bộ dữ liệu.

**Acceptance criteria**

- Given 1.000.163 dòng geolocation, When gộp theo `geolocation_zip_code_prefix`, Then còn 19.015 dòng và mỗi zip có đúng một lat/lng.
- Given customers và geolocation đã gộp, When join theo zip, Then kết quả có đúng 99.441 dòng, không phải 15.083.455.
- Given tọa độ nằm ngoài khung Brazil, When làm sạch, Then các dòng đó bị loại khỏi phép gộp và số lượng bị loại được log.
- Given 278 customer zip không có geolocation, When join, Then đơn vẫn được giữ với trường địa lý null, không bị mất.

## US-06 — Dịch danh mục với fallback rõ ràng

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-02

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn sản phẩm thiếu danh mục hoặc thiếu bản dịch vẫn xuất hiện trong báo cáo, để doanh thu không bị hụt.

**Giá trị**: Bảo toàn doanh thu và minh bạch chất lượng danh mục.

**Acceptance criteria**

- Given 610 sản phẩm thiếu `product_category_name`, When làm sạch, Then chúng được gán `unknown` và cờ `category_missing = true`.
- Given 2 danh mục không có trong bảng dịch (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`), When join, Then chúng giữ tên gốc, cờ `translation_missing = true`, và không bị loại khỏi mart.
- Given bảng products, When làm sạch, Then vẫn đủ 32.951 dòng.

## US-07 — Giữ đúng grain payment và review

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-02

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn payment và review được xử lý theo đúng grain, để join không làm tăng doanh thu hoặc số đánh giá.

**Giá trị**: Ngăn nhân bản số liệu khi tích hợp.

**Acceptance criteria**

- Given 103.886 dòng payment, When tích hợp, Then bảng payment giữ đủ 103.886 dòng theo `(order_id, payment_sequential)`.
- Given 99.224 dòng review và 547 đơn có nhiều đánh giá (551 dòng review dư), When tích hợp, Then bảng review giữ đủ 99.224 dòng và cờ `multiple_reviews_per_order = true` cho các đơn liên quan.
- Given items đã join với payment/review, When kiểm tra, Then số dòng items vẫn là 112.650.

---

# E3 — Tích hợp star schema DuckDB/Parquet

## US-08 — Tạo star schema từ dữ liệu sạch

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-03

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn truy vấn một mô hình star schema thay vì 9 CSV, để phân tích nhanh và nhất quán.

**Giá trị**: Chuẩn hóa mô hình phân tích và giảm phụ thuộc vào tệp thô.

**Acceptance criteria**

- Given dữ liệu đã làm sạch, When chạy integrate, Then tồn tại `fact_order_items`, `fact_orders`, `fact_payments`, `fact_reviews` và các dimension đã nêu trong requirements.
- Given từng bảng, When kiểm tra grain, Then `fact_order_items` = 112.650 dòng, `fact_orders` = 99.441, `fact_payments` = 103.886, `fact_reviews` = 99.224.
- Given DuckDB catalog, When mở, Then các view/table trỏ tới Parquet và truy vấn không đọc lại CSV thô.

## US-09 — Phân biệt khách hàng theo đơn và theo người

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-03

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn dimension khách hàng phân biệt `customer_id` và `customer_unique_id`, để đếm đúng khách hàng và phân tích mua lặp lại.

**Giá trị**: Tránh báo cáo sai số khách hàng.

**Acceptance criteria**

- Given customers, When tạo `dim_customer`, Then có 99.441 `customer_id` và 96.096 `customer_unique_id` duy nhất.
- Given một khách có nhiều đơn, When tính khách hàng duy nhất, Then metric dùng `customer_unique_id` và trả về 1, không phải số đơn.
- Given join orders với `dim_customer`, When kiểm tra, Then số dòng vẫn là 99.441.

## US-10 — Dimension địa lý, thời gian và cờ giao trễ

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-03

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn các dimension địa lý/thời gian và cờ giao trễ, để phân tích theo vùng và thời gian mà không phải tự join lại.

**Giá trị**: Tái sử dụng logic thời gian/địa lý nhất quán.

**Acceptance criteria**

- Given geolocation đã gộp và IBGE, When tạo `dim_geography`, Then có 19.015 zip, mỗi zip có bang và 1 trong 5 vùng.
- Given `dim_date`, When kiểm tra, Then bao phủ 2016-09-04 đến 2018-10-17 và có năm/quý/tháng.
- Given `fact_orders`, When tính cờ giao trễ, Then có 7.826 đơn trễ trên 96.478 đơn delivered; đơn không delivered không bị tính vào mẫu số.

---

# E4 — Phân tích doanh thu và KPI

## US-11 — Xu hướng doanh thu theo thời gian

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-04

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn xem doanh thu theo tháng/quý/năm, để nhận biết xu hướng và mùa vụ.

**Giá trị**: Trả lời câu hỏi kinh doanh cốt lõi.

**Acceptance criteria**

- Given marts, When tính doanh thu theo tháng trên toàn bộ trạng thái, Then tổng khớp 15.843.553,24 BRL (sai số ≤ 0,01).
- Given bộ lọc `delivered`, When tính lại, Then chỉ đơn delivered được cộng và tổng khớp truy vấn DuckDB đối soát.
- Given năm 2016 chỉ có 329 đơn, When hiển thị, Then có nhãn “dữ liệu 2016 chưa đầy đủ”.
- Given tháng đầu tiên, When tính tăng trưởng so với kỳ trước, Then trả về null thay vì chia cho 0.

## US-12 — Hiệu quả theo danh mục và vùng

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-04

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn so sánh doanh thu, số đơn, AOV và tỷ trọng phí vận chuyển theo danh mục và vùng, để biết đâu là động lực tăng trưởng.

**Giá trị**: Ưu tiên danh mục/khu vực đúng.

**Acceptance criteria**

- Given marts, When nhóm theo danh mục, Then sản phẩm `unknown` và 2 danh mục thiếu dịch vẫn xuất hiện với cờ tương ứng.
- Given nhóm theo vùng, When cộng doanh thu 5 vùng, Then tổng bằng tổng doanh thu toàn quốc (sai số ≤ 0,01).
- Given một danh mục, When xem AOV và tỷ trọng freight, Then công thức khớp định nghĩa trong requirements.

## US-13 — Xếp hạng sản phẩm và người bán

**Persona**: P1 · **Ưu tiên**: Should · **FR**: FR-04

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn xem top sản phẩm và seller theo doanh thu, để nhận diện đối tác/sản phẩm chủ lực.

**Giá trị**: Hỗ trợ quyết định danh mục và đối tác.

**Acceptance criteria**

- Given marts và bộ lọc thời gian, When xếp hạng top 10, Then chỉ tính đơn `delivered` và thứ tự ổn định khi doanh thu bằng nhau (tie-break theo ID).
- Given một seller không có đơn delivered, When xếp hạng, Then seller không xuất hiện trong top.
- Given thay đổi bộ lọc danh mục, When xem lại, Then bảng xếp hạng cập nhật theo đúng tập dữ liệu.

## US-14 — KPI giao hàng

**Persona**: P1 · **Ưu tiên**: Should · **FR**: FR-04, FR-08

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn theo dõi tỷ lệ giao trễ và thời gian giao, để đánh giá chất lượng vận hành.

**Giá trị**: Bổ sung góc nhìn vận hành cho phân tích doanh thu.

**Acceptance criteria**

- Given `fact_orders`, When tính tỷ lệ giao trễ toàn bộ, Then kết quả là 8,11% (7.826/96.478, sai số ≤ 0,01 điểm %).
- Given nhóm theo bang, When cộng số đơn trễ, Then tổng bằng 7.826.
- Given đơn chưa giao hoặc thiếu ngày giao, When tính, Then bị loại khỏi tử số và mẫu số.
- Given thời gian giao, When tính trung vị/trung bình, Then trung vị xấp xỉ 10,2 ngày và trung bình xấp xỉ 12,6 ngày.

---

# E5 — Dashboard Plotly Dash

## US-15 — Thẻ KPI và bộ lọc

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-05

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn lọc theo thời gian, bang/vùng, danh mục và trạng thái, để trả lời câu hỏi của từng báo cáo.

**Giá trị**: Tự phục vụ phân tích mà không cần viết SQL.

**Acceptance criteria**

- Given dashboard đang chạy, When mở lần đầu, Then hiển thị KPI doanh thu, số đơn, AOV, tỷ lệ giao trễ và mặc định trạng thái `delivered`.
- Given chọn khoảng ngày + bang + danh mục, When áp dụng, Then các KPI cập nhật trong ≤ 3 giây với dữ liệu mẫu.
- Given nhãn giao diện, When kiểm tra, Then toàn bộ nhãn, tiêu đề, tooltip là tiếng Việt.

## US-16 — Biểu đồ xu hướng, danh mục và khu vực

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-05

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn xem xu hướng doanh thu, so sánh danh mục và phân bố theo vùng, để kể câu chuyện bằng dữ liệu.

**Giá trị**: Trực quan hóa insight thay vì bảng số khô khan.

**Acceptance criteria**

- Given bộ lọc, When xem biểu đồ đường, Then trục thời gian và doanh thu khớp mart; đơn vị tiền là BRL.
- Given biểu đồ cột danh mục, When sắp xếp, Then hiển thị top danh mục theo doanh thu và có tooltip định nghĩa.
- Given dữ liệu theo vùng, When xem bản đồ hoặc bảng xếp hạng, Then đủ 5 vùng IBGE và tổng khớp KPI.
- Given bộ lọc không có dữ liệu, When render, Then hiển thị “Không có dữ liệu” thay vì biểu đồ trống/lỗi.

## US-17 — Định dạng, trạng thái lỗi và khả năng đọc

**Persona**: P2 · **Ưu tiên**: Should · **FR**: FR-05, NFR-05

**Câu chuyện**: Là người đánh giá, tôi muốn dashboard định dạng nhất quán và xử lý lỗi rõ ràng, để đánh giá chất lượng sản phẩm và độ tin cậy.

**Giá trị**: Tăng tính chuyên nghiệp và khả năng sử dụng.

**Acceptance criteria**

- Given ngày và tiền, When hiển thị, Then ngày theo dd/mm/yyyy và tiền theo định dạng BRL.
- Given DuckDB/Parquet không truy cập được, When mở dashboard, Then hiển thị thông báo lỗi tiếng Việt kèm gợi ý kiểm tra pipeline.
- Given màn hình 1366×768, When xem, Then KPI và biểu đồ không chồng lấn, không cắt nhãn.
- Given một KPI, When hover vào tooltip, Then hiển thị định nghĩa công thức.

---

# E6 — Micro-batch và dữ liệu IBGE

## US-18 — Micro-batch idempotent và replay

**Persona**: P2 · **Ưu tiên**: Must · **FR**: FR-06

**Câu chuyện**: Là người đánh giá, tôi muốn pipeline xử lý các tệp mới trong `inbox/` và chạy lại không tạo trùng, để minh họa velocity mà vẫn bảo đảm đúng dữ liệu.

**Giá trị**: Chứng minh 3V bằng cơ chế có kiểm soát, không cần Kafka.

**Acceptance criteria**

- Given 3 tệp CSV mới trong `inbox/`, When chạy micro-batch, Then cả 3 được xử lý và manifest ghi tên + hash + thời điểm.
- Given chạy lại với cùng 3 tệp, When hoàn tất, Then không có bản ghi trùng và số dòng mart không đổi.
- Given lệnh replay N lô lịch sử, When chạy, Then log ghi rõ lô nào đã phát lại và KPI cuối cùng khớp batch đầy đủ.
- Given một tệp lỗi schema, When xử lý, Then tệp đó bị đánh dấu failed, không chặn các tệp hợp lệ khác.

## US-19 — Tải, cache và ánh xạ IBGE

**Persona**: P1 · **Ưu tiên**: Must · **FR**: FR-07

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn dữ liệu IBGE được tải và cache tự động, để phân tích theo vùng mà không phụ thuộc mạng mỗi lần chạy.

**Giá trị**: Thêm chiều phân tích vùng và tăng độ tin cậy.

**Acceptance criteria**

- Given có internet, When chạy stage IBGE, Then dữ liệu được lưu vào `dataset/external/ibge/` kèm URL, thời điểm, hash.
- Given 27 bang, When ánh xạ, Then mỗi bang thuộc đúng 1 trong 5 vùng và không có bang null.
- Given mất mạng nhưng đã có cache, When chạy lại, Then pipeline dùng cache và ghi log “cache hit”.
- Given mất mạng và chưa có cache, When chạy, Then pipeline dừng với lỗi rõ ràng, không tạo vùng null âm thầm.

---

# E7 — Vận hành, tài liệu và ML tùy chọn

## US-20 — Một lệnh chạy pipeline và tài liệu vận hành

**Persona**: P2 · **Ưu tiên**: Must · **FR**: FR-09, FR-10

**Câu chuyện**: Là người đánh giá, tôi muốn chạy toàn bộ pipeline bằng một lệnh và làm theo README, để kiểm chứng đồ án trong thời gian ngắn.

**Giá trị**: Tái lập và bàn giao.

**Acceptance criteria**

- Given môi trường đã cài dependency, When chạy `python -m src.pipeline run --stage all`, Then pipeline tạo đủ raw/cleaned/marts và kết thúc mã 0.
- Given muốn chạy lại một phần, When dùng `--stage ingest|clean|integrate|analyze`, Then chỉ stage đó chạy và log đúng.
- Given README, When làm theo từ đầu, Then có đủ bước tạo venv, cài dependency, chạy pipeline, mở dashboard trong ≤ 15 phút.
- Given kết thúc lần chạy, When xem summary, Then có run_id, thời gian, số dòng vào/ra và trạng thái từng stage.

## US-21 — Kiểm thử tự động và đối soát

**Persona**: P2 · **Ưu tiên**: Must · **FR**: FR-08

**Câu chuyện**: Là người đánh giá, tôi muốn chạy test tự động, để xác nhận logic làm sạch và KPI không bị hỏng khi thay đổi code.

**Giá trị**: Bảo vệ chất lượng và tạo bằng chứng kiểm thử.

**Acceptance criteria**

- Given repo đã cài dependency, When chạy `pytest`, Then toàn bộ unit test và data quality test pass.
- Given test geolocation, When join customers, Then test khẳng định kết quả 99.441 dòng và fail nếu lớn hơn.
- Given test category, When có 610 sản phẩm thiếu danh mục và 2 danh mục thiếu dịch, Then test khẳng định không mất dòng.
- Given test KPI, When tính tỷ lệ giao trễ, Then test khẳng định 8,11% với dữ liệu mẫu.
- Given coverage module cleaning/integration, When đo, Then đạt ≥ 70%.

## US-22 — Mô hình dự báo giao trễ (tùy chọn)

**Persona**: P1 · **Ưu tiên**: Could · **FR**: FR-11

**Câu chuyện**: Là chuyên viên phân tích, tôi muốn thử dự báo đơn có nguy cơ giao trễ, để chủ động hỗ trợ khách hàng.

**Giá trị**: Mở rộng phân tích mô tả sang dự báo, không ảnh hưởng MVP.

**Acceptance criteria**

- Given MVP pipeline và dashboard đã hoàn tất, When huấn luyện mô hình, Then dùng split theo thời gian và báo cáo precision/recall/AUC trên tập test.
- Given mô hình, When đánh giá, Then không thay đổi KPI mặc định và không chặn pipeline chính.
- Given không đủ thời gian, When bỏ qua story này, Then các story Must/Should vẫn hoàn tất và được nghiệm thu.

---

# Truy vết yêu cầu

| FR | Story |
|---|---|
| FR-01 | US-01, US-02 |
| FR-02 | US-04, US-05, US-06, US-07 |
| FR-03 | US-08, US-09, US-10 |
| FR-04 | US-11, US-12, US-13, US-14 |
| FR-05 | US-15, US-16, US-17 |
| FR-06 | US-18 |
| FR-07 | US-19 |
| FR-08 | US-03, US-14, US-21 |
| FR-09 | US-20 |
| FR-10 | US-20 |
| FR-11 | US-22 |

# Kiểm tra INVEST

| Tiêu chí | Cách đáp ứng |
|---|---|
| Independent | Mỗi story tạo giá trị riêng; story tích hợp dùng mart đã có, không phụ thuộc thứ tự dashboard |
| Negotiable | Câu chuyện mô tả mục tiêu, không khóa giải thuật/UI cụ thể |
| Valuable | Mọi story gắn với persona P1/P2 và KPI/khả năng kiểm chứng |
| Estimable | Phạm vi rõ theo bảng/FR, acceptance criteria cụ thể |
| Small | Tối đa một mục tiêu/bảng hoặc một cụm UI; 22 story cho 7 epic |
| Testable | Mọi story có Given/When/Then với số liệu baseline hoặc hành vi quan sát được |

# Ghi chú chất lượng

- 18 story Must, 3 story Should, 1 story Could.
- Các con số baseline (99.441; 112.650; 103.886; 99.224; 8,11%; 15.843.553,24) được xác minh từ CSV thô.
- Story kỹ thuật được viết dưới góc nhìn P1/P2, không thêm persona kỹ sư.
