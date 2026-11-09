# Kế hoạch NFR Design — U2 Integration & Analytics

**Unit**: U2 — Integration & Analytics
**Giai đoạn**: CONSTRUCTION - NFR Design (Planning)

## 1. Mục tiêu

Chuyển NFR U2 thành pattern và logical component:

- IBGE client có retry/cache.
- Star schema build theo thứ tự, ghi atomic.
- DuckDB read-only cho dashboard, memory limit.
- Pre-aggregate daily và KPI reconciliation.
- Analytics query nhanh, không side effect.

## 2. Pattern đề xuất

| NFR | Pattern | Cách áp dụng |
|---|---|---|
| U2-01 hiệu năng | Build một pass, vectorized | pandas groupby/merge; không loop |
| U2-02 query | Pre-aggregate + DuckDB view | `agg_*` cho dashboard; view cho ad hoc |
| U2-03 bộ nhớ | DuckDB memory limit | `PRAGMA memory_limit='1GB'` |
| U2-04 IBGE | Retry + cache | timeout 10s, retry 2, cache metadata |
| U2-05 đồng thời | Read-only connection | `duckdb.connect(read_only=True)` |
| U2-06 tin cậy | Validate trước khi replace | KPI reconciliation trước khi công bố |
| U2-07 tái lập | Deterministic sort | tie-break ID, không random |
| U2-08 quan sát | Structured log | row counts, KPI, cache hit |
| U2-09 bảo mật | Chỉ IBGE HTTP | không upload dữ liệu |
| U2-10 test | Contract tests | row counts, KPI baseline |

## 3. Logical component đề xuất

- `IbgeClient` — fetch/retry/cache.
- `RegionMapper` — 27 state → 5 region.
- `DimensionBuilder` — dim_customer/product/seller/geography/date.
- `FactBuilder` — fact_order_items/orders/payments/reviews.
- `Aggregator` — agg_sales_daily, agg_delivery_daily.
- `DuckDbCatalog` — tạo view, memory limit.
- `AnalyticsService` — KPI queries.
- `KpiReconciler` — so baseline.
- `StarSchemaValidator` — row counts, keys, fanout.
- `ConnectionFactory` — read-only/write connection.

## 4. Câu hỏi cần trả lời

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Chiến lược rebuild aggregate
Khi integrate chạy lại:

A) Rebuild toàn bộ `agg_*` từ fact (khuyến nghị)
B) Chỉ append ngày mới, giữ lịch sử
C) Materialized view, tính on-demand
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — Làm mới cache IBGE
Khi nào tải lại IBGE?

A) Chỉ khi cache thiếu/hỏng hoặc có cờ `--refresh-ibge` (khuyến nghị)
B) Tự động làm mới sau 30 ngày
C) Tải lại mỗi lần chạy
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — Vòng đời kết nối DuckDB
Cách quản lý connection:

A) Một connection read-only dùng chung cho dashboard; connection write riêng cho pipeline (khuyến nghị)
B) Mở connection mới cho mỗi query
C) Một connection duy nhất cho cả đọc và ghi
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Cache kết quả analytics
Có cache kết quả KPI trong bộ nhớ không?

A) Không cache; DuckDB + pre-aggregate đủ nhanh (khuyến nghị)
B) Cache TTL 60 giây cho mỗi bộ lọc
C) Cache đến khi pipeline chạy lại
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 5 — Kiểm tra trước khi công bố mart
Khi KPI lệch baseline:

A) Fail integrate, không thay mart cũ (khuyến nghị)
B) Ghi warning, vẫn công bố mart
C) Tự động sửa số liệu theo baseline
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 5. Checklist

- [x] Đọc NFR Requirements U2
- [x] Đề xuất pattern và logical component
- [x] Tạo kế hoạch và câu hỏi
- [x] Thu thập câu trả lời
- [x] Phân tích mơ hồ/mâu thuẫn
- [x] Tạo `nfr-design-patterns.md` + `logical-components.md`
- [x] Cập nhật state và trình bày phê duyệt
