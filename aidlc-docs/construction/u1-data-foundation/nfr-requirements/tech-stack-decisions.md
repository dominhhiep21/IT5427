# Tech Stack Decisions — U1 Data Foundation

## 1. Quyết định

| Thành phần | Lựa chọn | Phiên bản | Lý do |
|---|---|---|---|
| Runtime | CPython | 3.13.5 | Có sẵn trên máy |
| DataFrame | pandas | 2.2.3 | Có sẵn; đủ cho 1,5 triệu dòng |
| Parquet engine | PyArrow | Pin khi cài | Đọc/ghi Parquet, Snappy |
| Config | PyYAML | Pin khi cài | Đọc `config.yaml` |
| Test | pytest | Pin khi cài | Chuẩn Python, dễ tích hợp |
| Coverage | pytest-cov | Pin khi cài | Đo coverage |
| Logging | stdlib `logging` | 3.13 | Không cần dependency ngoài |
| Đóng gói | `requirements.txt` | — | Đơn giản, tái lập |
| Nén | Snappy | — | Nhanh, phù hợp batch cục bộ |

> Các phiên bản PyArrow/PyYAML/pytest/pytest-cov sẽ được khóa chính xác sau khi cài trên môi trường thực tế và ghi vào `requirements.txt`. Không dùng dải phiên bản khi chạy.

## 2. Không sử dụng trong U1

| Công nghệ | Lý do |
|---|---|
| Spark / PySpark | Không cần cho 1,5 triệu dòng; chưa cài |
| DuckDB | Thuộc U2 (star schema/analytics) |
| SQLite/PostgreSQL | Đã chốt dùng DuckDB ở U2 |
| Kafka/Redpanda | Micro-batch mô phỏng bằng thư mục |
| Cloud SDK | Chạy cục bộ |
| Jupyter | Pipeline là module/CLI, không notebook |
| Great Expectations | Tự viết quality checks, tránh dependency nặng |

## 3. Cấu trúc dependency

```
requirements.txt
  pandas==2.2.3
  pyarrow==<pin>
  PyYAML==<pin>
  pytest==<pin>
  pytest-cov==<pin>
```

- Không pin transitive dependency thủ công; dùng `pip freeze` nếu cần lock đầy đủ.
- Tạo venv riêng; không cài global.

## 4. Quyết định kỹ thuật liên quan

### 4.1 Bộ nhớ
- Nạp toàn bộ CSV vào pandas DataFrame.
- Geolocation xử lý bằng `groupby` vectorized; không vòng lặp Python từng dòng.
- Nếu peak vượt 2 GB, chuyển geolocation sang đọc theo chunk (phương án dự phòng).

### 4.2 Ghi atomic
- Ghi vào `data/.tmp-{run_id}/`.
- Kiểm tra đủ tệp + đọc lại metadata.
- Thay thế thư mục đích; giữ bản cũ nếu thất bại.

### 4.3 Logging
- JSON lines file + console summary.
- Không log toàn bộ DataFrame/khách hàng.
- Mọi exception có `error_code`.

### 4.4 Encoding
- Đọc/ghi UTF-8.
- Chạy `python -X utf8` trên Windows.

## 5. Hệ quả

- Cần cài thêm 4 gói: `pyarrow`, `PyYAML`, `pytest`, `pytest-cov`.
- Không cần Docker/Java/Spark.
- Thời gian cài đặt thấp; phù hợp demo học thuật.
- Nếu sau này cần xử lý dữ liệu lớn hơn, có thể thay pandas bằng DuckDB/Polars mà giữ interface Parquet.
