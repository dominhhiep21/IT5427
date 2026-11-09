# NFR Requirements — U2 Integration & Analytics

## 1. Mục tiêu chất lượng

U2 phải xây star schema và lớp analytics đủ nhanh cho dashboard, ổn định khi IBGE lỗi, và không làm hỏng mart đang được dashboard đọc.

## 2. Yêu cầu phi chức năng

### NFR-U2-01 — Hiệu năng integrate
- **Mục tiêu**: Toàn bộ U2 (IBGE + dimensions + facts + aggregates + DuckDB catalog) ≤ **3 phút**.
- **Đo**: từ lúc bắt đầu stage integrate đến khi ghi xong catalog.
- **Điều kiện**: cleaned Parquet đã có; IBGE cache có sẵn hoặc tải một lần.
- **Kiểm chứng**: log `duration_seconds`; benchmark trên máy hiện tại.

### NFR-U2-02 — Hiệu năng analytics
- **Mục tiêu**: Query KPI phổ biến (`kpi_summary`, doanh thu theo tháng/danh mục/vùng) ≤ **1 giây**.
- **Đo**: `time.perf_counter()` quanh query DuckDB; lấy median 5 lần.
- **Điều kiện**: DuckDB view/agg đã tạo; dữ liệu trong page cache.
- **Kiểm chứng**: benchmark script/test; ghi kết quả.

### NFR-U2-03 — Bộ nhớ
- **Mục tiêu**: Tiến trình ≤ **2 GB**; DuckDB `memory_limit = 1GB`.
- **Cấu hình**: `PRAGMA memory_limit='1GB'`, `PRAGMA threads=4`.
- **Đo**: `tracemalloc` cho Python; DuckDB tự giới hạn native memory.
- **Kiểm chứng**: không OOM khi integrate; query vẫn chạy với 1 GB.

### NFR-U2-04 — IBGE resilience
- **Timeout**: 10 giây/request.
- **Retry**: 2 lần, backoff 1s/2s; sau đó `ExternalSourceError`.
- **Cache**: dùng cache nếu có 27 estados hợp lệ; `refresh=True` để tải lại.
- **Không** gọi API nếu cache hợp lệ.
- **Kiểm chứng**: mock timeout → retry đúng; cache hit không gọi mạng.

### NFR-U2-05 — Đồng thời
- Dashboard mở DuckDB **read-only**.
- Pipeline ghi từng mart atomic (`os.replace`).
- Không khóa file lâu; không ghi đè file đang đọc.
- **Kiểm chứng**: mở read-only connection khi integrate chạy; dashboard vẫn đọc bản cũ.

### NFR-U2-06 — Tin cậy
- Fail-fast khi: IBGE không map được state, sai grain, KPI lệch baseline, DuckDB lỗi.
- Không ghi đè mart nếu bước validate fail.
- **Kiểm chứng**: inject lỗi state → exception; mart cũ giữ nguyên.

### NFR-U2-07 — Tái lập
- Cache IBGE có SHA-256.
- Natural keys, không random.
- KPI baseline cố định trong test.
- **Kiểm chứng**: chạy 2 lần, row counts và KPI không đổi.

### NFR-U2-08 — Quan sát
- Log: IBGE cache/fetch, row counts từng dim/fact, thời gian integrate, KPI reconciliation.
- Báo cáo: `integration-report.json`, `kpi-reconciliation.json`.
- **Kiểm chứng**: log có `run_id`, stage, table, rows.

### NFR-U2-09 — Bảo mật
- Chỉ gọi IBGE; không gửi dữ liệu Olist ra ngoài.
- Không lưu secret.
- DuckDB/file chỉ trong workspace.
- **Kiểm chứng**: review HTTP calls; không có upload.

### NFR-U2-10 — Bảo trì và kiểm thử
- Test: row counts, unique keys, region map 27/5, KPI baseline, no fanout.
- Coverage `src.integrate` + `src.analytics` ≥ **70%**.
- **Kiểm chứng**: `pytest`; coverage report.

## 3. Ràng buộc và đánh đổi

| Quyết định | Đánh đổi |
|---|---|
| DuckDB 1 GB | An toàn bộ nhớ; query rất lớn có thể spill |
| Pre-aggregate daily | Dashboard nhanh; thêm dung lượng và bước rebuild |
| Natural keys | Truy vết tốt; join chuỗi chậm hơn int một chút |
| Read-only dashboard | An toàn khi rebuild; không cho phép ghi từ UI |
| Cache IBGE vô thời hạn | Không phụ thuộc mạng; cần refresh thủ công khi IBGE đổi |

## 4. Tiêu chí nghiệm thu NFR

- [ ] Integrate ≤ 3 phút.
- [ ] KPI query ≤ 1 giây.
- [ ] DuckDB chạy với memory_limit 1 GB.
- [ ] IBGE retry/timeout đúng; cache hit không gọi mạng.
- [ ] Dashboard read-only đọc được khi integrate chạy.
- [ ] KPI baseline khớp: 15.419.773,75 BRL; 96.478 đơn; AOV 159,83; 7.826 trễ; 8,11%.
- [ ] `pytest` pass; coverage integrate/analytics ≥ 70%.
