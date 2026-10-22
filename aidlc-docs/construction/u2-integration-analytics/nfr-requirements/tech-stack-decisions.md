# Tech Stack Decisions — U2 Integration & Analytics

## 1. Quyết định

| Thành phần | Lựa chọn | Phiên bản | Lý do |
|---|---|---|---|
| Runtime | CPython | 3.13.5 | Có sẵn |
| DataFrame | pandas | 2.2.3 | Đã dùng U1 |
| Parquet | PyArrow | 26.0.0 | Đã cài |
| Catalog/query | DuckDB | Pin khi cài | View trên Parquet, SQL nhanh |
| HTTP | `urllib.request` (stdlib) | 3.13 | Không thêm dependency |
| JSON | stdlib | 3.13 | Cache/report |
| Test | pytest | 9.1.1 | Đã cài |
| Coverage | pytest-cov | 7.1.0 | Đã cài |
| Nén | Snappy | — | Đồng bộ U1 |

> DuckDB sẽ được cài trong venv U2 và pin chính xác trong `requirements.txt`.

## 2. Không sử dụng

| Công nghệ | Lý do |
|---|---|
| Spark | Không cần cho 1,5 triệu dòng |
| PostgreSQL/SQLite | Đã chốt DuckDB |
| `requests` | `urllib.request` đủ cho 2 endpoint |
| Airflow/Prefect | U3 dùng CLI đơn giản |
| Cloud | Chạy cục bộ |

## 3. Cấu hình DuckDB

```python
conn = duckdb.connect("warehouse/olist.duckdb", read_only=False)
conn.execute("PRAGMA memory_limit='1GB'")
conn.execute("PRAGMA threads=4")
```

Dashboard:
```python
conn = duckdb.connect("warehouse/olist.duckdb", read_only=True)
```

## 4. IBGE client

- `urllib.request.urlopen(url, timeout=10)`.
- Retry 2 lần với sleep 1s, 2s.
- Lưu JSON + metadata:
  ```json
  {
    "url": "...",
    "fetched_at": "...",
    "sha256": "...",
    "states": 27,
    "municipalities": 5570
  }
  ```
- Cache hợp lệ nếu `estados.json` có 27 bang và `metadata.json` tồn tại.

## 5. Analytics layer

- Fact/dim Parquet tại `data/marts/`.
- DuckDB view `v_*` trỏ tới Parquet.
- Pre-aggregate `agg_sales_daily`, `agg_delivery_daily`.
- Analytics module chỉ SELECT.

## 6. Hệ quả

- Cần cài `duckdb` (1 gói).
- Không cần server database.
- Dashboard U3 chỉ cần DuckDB read-only.
- Nếu DuckDB lỗi, có thể thay bằng view SQL trên Parquet nhưng vẫn giữ interface.
