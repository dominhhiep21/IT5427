# Câu hỏi làm rõ yêu cầu

**Dự án**: Pipeline tích hợp, làm sạch và phân tích dữ liệu thương mại điện tử Olist
**Giai đoạn**: INCEPTION - Phân tích yêu cầu

Vui lòng trả lời từng câu bằng cách điền chữ cái vào sau thẻ `[Answer]:` (ví dụ `[Answer]: A`). Nếu không có phương án nào phù hợp, chọn `X` và mô tả mong muốn của bạn ngay sau thẻ. Khi hoàn tất, hãy trả lời `done`.

---

## Câu 1
Pipeline nên sử dụng engine xử lý nào? (Máy hiện tại chỉ cài Python + pandas; chưa cài Spark.)

A) Python + pandas chạy cục bộ (đơn giản nhất, phù hợp với ~100 nghìn đơn hàng)
B) Apache Spark / PySpark (chạy cục bộ hoặc qua Docker) với data lake định dạng Parquet
C) DuckDB + Parquet (SQL phân tích trong bộ nhớ, dạng cột, nhẹ)
D) Engine quản lý trên cloud (Databricks, BigQuery, Snowflake)
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: C

---

## Câu 2
Dữ liệu sau khi tích hợp nên được lưu trữ như thế nào?

A) Chỉ lưu tệp CSV/Parquet đã làm sạch
B) Kho dữ liệu quan hệ theo mô hình star schema (SQLite hoặc PostgreSQL)
C) Data lake Parquet nhiều tầng (bronze/silver/gold), truy vấn bằng DuckDB hoặc Spark SQL
D) Object storage trên cloud + kho dữ liệu cloud
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: B

---

## Câu 3
Phạm vi sản phẩm bàn giao bắt buộc của dự án là gì?

A) Pipeline đầy đủ: ingestion, làm sạch, tích hợp, phân tích và dashboard tương tác
B) Pipeline kèm notebook/báo cáo phân tích, không có dashboard
C) Chỉ dashboard và phân tích, bắt đầu từ dữ liệu đã làm sạch
D) Pipeline đầy đủ kèm mô hình machine learning và dashboard
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

---

## Câu 4
Mảng phân tích nào là trọng tâm chính? (Chọn một mảng quan trọng nhất.)

A) Doanh thu, xu hướng bán hàng và hiệu quả theo danh mục sản phẩm
B) Hiệu quả giao hàng và phân tích giao hàng trễ
C) Giữ chân khách hàng, phân khúc RFM và hành vi mua lặp lại
D) Hiệu quả người bán và phân tích điểm đánh giá/cảm xúc
E) Kết hợp cân bằng cả bốn mảng trên
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

---

## Câu 5
Nên sử dụng công nghệ dashboard nào?

A) Streamlit (Python, xây dựng nhanh nhất)
B) Plotly Dash (Python, kiểm soát bố cục tốt hơn)
C) Power BI hoặc Tableau (công cụ BI bên ngoài)
D) Báo cáo HTML tĩnh hoặc xuất notebook (không có dashboard trực tiếp)
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: B

---

## Câu 6
Đồ án yêu cầu chứng minh đặc trưng big data (3V). Dữ liệu hiện có là tĩnh, khoảng 100 nghìn đơn hàng và 1 triệu dòng geolocation. Nên chứng minh velocity/volume như thế nào?

A) Dùng toàn bộ dữ liệu tĩnh và mô tả trung thực volume/variety; chỉ mô phỏng velocity nếu cần
B) Bổ sung tầng ingestion streaming/tăng dần mô phỏng (micro-batch) để chứng minh velocity
C) Giữ toàn bộ xử lý theo lô (batch); ưu tiên chiều sâu phân tích hơn việc chứng minh 3V
D) Mở rộng quy mô bằng nguồn dữ liệu công khai bổ sung để tăng volume
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: B

---

## Câu 7
Có cần tích hợp nguồn dữ liệu ngoài 9 tệp CSV Olist được cung cấp không?

A) Chỉ dùng 9 tệp CSV Olist được cung cấp
B) Bổ sung dữ liệu tham chiếu công khai của Brazil (ví dụ IBGE theo bang/vùng, hiệu chỉnh geolocation)
C) Bổ sung một bộ dữ liệu thương mại điện tử hoặc đánh giá khác để minh họa tích hợp schema
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: B

---

## Câu 8
Có bắt buộc phải có mô hình machine learning/AI không?

A) Có, cần ít nhất một mô hình dự báo (ví dụ dự báo giao hàng trễ hoặc dự báo điểm đánh giá)
B) Chỉ là mục tiêu tùy chọn/mở rộng
C) Không, phân tích thống kê và trực quan hóa là đủ
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: B

---

## Câu 9
Báo cáo, tài liệu và nhãn trên dashboard cuối cùng nên dùng ngôn ngữ nào?

A) Tiếng Việt
B) Tiếng Anh
C) Song ngữ: báo cáo/dashboard tiếng Việt, code và tài liệu kỹ thuật tiếng Anh
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A
