# NFR Design Patterns — U2 Integration & Analytics

## 1. IBGE Retry + Cache Pattern

**Mục tiêu**: Không phụ thuộc mạng mỗi lần chạy; lỗi mạng có kiểm soát.

**Cách làm**
1. Kiểm tra cache `dataset/external/ibge/estados.json`.
2. Cache hợp lệ nếu có 27 state, unique, metadata tồn tại.
3. Nếu không cache hoặc `refresh=True`:
   - Gọi API với timeout 10s.
   - Retry 2 lần, backoff 1s/2s.
   - Lưu JSON + metadata (URL, fetched_at, sha256, counts).
4. Nếu vẫn lỗi → `ExternalSourceError`.
5. Log `cache_hit` hoặc `fetched`.

**NFR**: U2-04, U2-08.

## 2. One-Pass Build Pattern

**Mục tiêu**: Integrate ≤ 3 phút, tránh loop Python.

- Dimensions build bằng merge/rename/assign vectorized.
- Facts build bằng merge một lần với dims/orders.
- Aggregates dùng `groupby().agg()` một pass.
- Không `iterrows`, không `apply` trên 100k+ dòng.

**NFR**: U2-01.

## 3. Build → Validate → Promote Pattern

**Mục tiêu**: Không công bố mart sai; không phá mart cũ.

1. Build tất cả DataFrame trong bộ nhớ.
2. Ghi vào `data/.tmp/{run_id}/marts/`.
3. Chạy `StarSchemaValidator` + `KpiReconciler` trên bản tạm.
4. Nếu pass: `os.replace` từng tệp sang `data/marts/`.
5. Nếu fail: giữ mart cũ, giữ temp để debug.
6. Sau promote: rebuild DuckDB catalog.

**NFR**: U2-06, U2-07.

## 4. Pre-Aggregation Full Rebuild Pattern

- `agg_sales_daily`, `agg_delivery_daily` rebuild toàn bộ mỗi lần integrate.
- Không append, không incremental.
- Grain `(date_key, state, region, category)`.
- Lý do: dữ liệu tĩnh, rebuild nhanh, tránh sai lệch lịch sử.

**NFR**: U2-01, U2-02.

## 5. DuckDB Memory Limit Pattern

```python
conn = duckdb.connect(db_path, read_only=False)
conn.execute("PRAGMA memory_limit='1GB'")
conn.execute("PRAGMA threads=4")
```

- Pipeline dùng write connection.
- Dashboard dùng read-only connection.
- Không mở quá nhiều connection song song.

**NFR**: U2-03, U2-05.

## 6. Read-Only Dashboard Connection Pattern

- `ConnectionFactory.read_only()` trả connection dùng chung trong process dashboard.
- `ConnectionFactory.write()` chỉ dùng trong pipeline.
- Dashboard không có quyền ghi.
- Khi pipeline promote mart, dashboard tiếp tục đọc bản cũ đến khi replace xong.

**NFR**: U2-05.

## 7. No Analytics Cache Pattern

- Không cache kết quả KPI trong bộ nhớ.
- Mỗi request query DuckDB/pre-aggregate.
- Lý do: dữ liệu nhỏ, query ≤ 1s; cache gây sai lệch sau rebuild.

**NFR**: U2-02, U2-07.

## 8. KPI Reconciliation Gate

- Tính KPI từ DataFrame mới trước khi promote:
  - revenue delivered = 15.419.773,75
  - orders = 96.478
  - AOV = 159,83
  - late = 7.826 / 96.478 = 8,11%
- Sai lệch > 0,01 → `QualityGateError`, không promote.
- Ghi `kpi-reconciliation.json`.

**NFR**: U2-06, U2-07.

## 9. Deterministic Ordering Pattern

- Top entity: sort revenue desc, ID asc.
- Aggregate: sort `date_key, state, region, category`.
- Dim: sort theo natural key.
- Không random.

**NFR**: U2-07.

## 10. Structured Logging Pattern

- Log JSON lines:
  - `ibge_cache_hit` / `ibge_fetch`
  - `build_dimension` (table, rows)
  - `build_fact` (table, rows)
  - `build_aggregate` (table, rows)
  - `kpi_reconciliation` (passed, deltas)
  - `catalog_created`
- Console summary ngắn.

**NFR**: U2-08.

## 11. Pattern → NFR mapping

| Pattern | NFR |
|---|---|
| IBGE retry/cache | U2-04, U2-08 |
| One-pass build | U2-01 |
| Build-validate-promote | U2-06, U2-07 |
| Full aggregate rebuild | U2-01, U2-02 |
| DuckDB memory limit | U2-03 |
| Read-only connection | U2-05 |
| No analytics cache | U2-02, U2-07 |
| KPI reconciliation | U2-06, U2-07 |
| Deterministic ordering | U2-07 |
| Structured logging | U2-08 |
