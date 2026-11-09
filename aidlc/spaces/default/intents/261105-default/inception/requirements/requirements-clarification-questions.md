# Câu hỏi làm rõ bổ sung

**Dự án**: Pipeline tích hợp, làm sạch và phân tích dữ liệu thương mại điện tử Olist
**Giai đoạn**: INCEPTION - Phân tích yêu cầu

Tôi đã ghi nhận 9 câu trả lời. Có 3 điểm cần chốt để tránh mâu thuẫn hoặc mơ hồ trước khi viết `requirements.md`.

---

## Câu 1
Bạn chọn **Câu 1 = C** (DuckDB + Parquet) và **Câu 2 = B** (star schema trên SQLite/PostgreSQL). Cần xác định rõ nơi lưu star schema:

A) DuckDB đọc Parquet và tạo star schema dưới dạng view/table trong DuckDB; không cần SQLite/PostgreSQL
B) Parquet là nguồn, nạp star schema vào SQLite (không cần cài server, dễ demo)
C) Parquet là nguồn, nạp star schema vào PostgreSQL (gần production, cần cài/server)
D) Parquet + DuckDB cho phân tích, đồng thời xuất star schema sang SQLite để bàn giao
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

---

## Câu 2
Bạn chọn **Câu 7 = B** (bổ sung dữ liệu tham chiếu Brazil). Cần chốt nguồn dữ liệu và cách lấy:

A) Chỉ bổ sung bảng ánh xạ 27 bang → 5 vùng + mã IBGE, đóng gói thành CSV trong repo (không cần internet)
B) Tải dữ liệu IBGE chính thức (bang/municipality) từ internet và lưu vào `dataset/external/`
C) Chỉ dùng dữ liệu tham chiếu để hiệu chỉnh geolocation ngoại lai, không thêm phân tích theo vùng
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: B

---

## Câu 3
Bạn chọn **Câu 6 = B** (mô phỏng streaming/micro-batch) nhưng engine là DuckDB. Cần chốt cơ chế mô phỏng:

A) Thư mục `inbox/` nhận các tệp CSV micro-batch mới; pipeline chạy lại theo từng lô nhỏ
B) Giả lập event log có timestamp rồi phát lại theo thời gian (replay), xử lý theo cửa sổ thời gian
C) Dùng Kafka/Redpanda + consumer thực (cần Docker và cài thêm hạ tầng)
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A
