# Olist E-commerce Data Pipeline

Pipeline tích hợp, làm sạch và phân tích dữ liệu thương mại điện tử Olist, kèm dashboard Plotly Dash tiếng Việt.

## Kiến trúc

```
dataset/ (9 CSV, bất biến)
   ↓ ingest + schema + hash
data/raw/*.parquet
   ↓ clean + quality gate
data/cleaned/*.parquet
   ↓ IBGE + star schema + aggregate
data/marts/*.parquet + warehouse/olist.duckdb
   ↓
src/analytics  →  src/dashboard (Plotly Dash)
```

- **U1 Data Foundation**: ingestion, schema, cleaning, quality gate.
- **U2 Integration & Analytics**: IBGE, star schema, DuckDB, KPI.
- **U3 Dashboard & Operations**: dashboard, CLI, micro-batch, replay, docs.

## Yêu cầu

- Windows 10/11, Python 3.13.
- Không cần Spark, Kafka, Docker hay cloud.

## Cài đặt

```powershell
python -m venv --system-site-packages .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Chạy Python với UTF-8:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline --help
```

## Chạy pipeline

```powershell
# Toàn bộ: ingest → clean → quality → integrate → analyze
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all

# Từng stage
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage ingest
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage clean
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage integrate
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage analyze
```

Output:

- `data/raw/*.parquet`
- `data/cleaned/*.parquet`
- `data/marts/*.parquet`
- `warehouse/olist.duckdb`
- `data/reports/*.json`
- `data/integration/linkage-customer.json` + `data/integration/linkage-seller.json` — kết quả ghép bản
  ghi (hợp đồng C5), ghi một lần sau `integrate` bởi `src/linkage/`; sinh lại bằng
  `run --stage all` hoặc `run --stage integrate`
- `logs/{run_id}.jsonl`

`logs/` chỉ giữ **10 tệp nhật ký gần nhất**: cuối mỗi lần chạy pipeline tự dọn tệp `.jsonl` cũ
hơn (sự kiện `integration.logs.pruned`). Muốn giữ lại để điều tra thì chép tệp ra ngoài trước
khi chạy lần tiếp theo.

## Dashboard

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.dashboard
```

Mở `http://127.0.0.1:8050`.

Dashboard có 4 tab:

- **Tổng quan**: KPI, doanh thu theo tháng, top danh mục.
- **Danh mục**: doanh thu theo danh mục, top sản phẩm.
- **Giao vận**: tỷ lệ giao trễ theo bang/danh mục/tháng.
- **Tích hợp**: thẻ "Số đơn theo tháng" đọc thẳng `dataset/`, chạy truy vấn trên DuckDB
  in-memory nên không cần `warehouse/` và không phụ thuộc pipeline đã chạy hay chưa.

## Micro-batch

Cấu trúc:

```text
inbox/
  batch-001/
    orders.csv
    order_items.csv
  batch-002/
    payments.csv
```

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline micro-batch --inbox inbox
```

- Mỗi batch có thể chứa một hoặc nhiều bảng.
- Tên tệp = tên bảng nguồn.
- Hash SHA-256 + manifest đảm bảo idempotent.
- Batch lỗi không ghi đè cleaned/mart cũ.

## Replay (minh họa velocity)

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline replay --batches 3
```

Lệnh chia cleaned orders theo tháng, tạo batch lịch sử trong `inbox/replay/`, rồi xử lý tuần tự.

## Test

```powershell
# Nhanh (không dùng dữ liệu thật)
.\.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow"

# Toàn bộ
.\.venv\Scripts\python.exe -X utf8 -m pytest

# Coverage
.\.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-report=term
```

## Lint và định dạng

```powershell
.\.venv\Scripts\ruff check .
.\.venv\Scripts\ruff format --check src/integration
```

`ruff` (ghim trong `requirements.txt`) là cổng bắt buộc: `ruff check .` chạy toàn repo, còn
`ruff format --check` chạy trên mã của đợt nâng cấp — mã cũ được dọn theo từng tệp khi có
người sửa tới.

## CI

Workflow ở `.github/workflows/ci.yml`, chạy trên `windows-2022` khi push/pull request vào
`main` và `feature/update-ui-ux`. Sáu bước: checkout → Python 3.13 (cache theo
`requirements.txt`) → `pip install -r requirements.txt` → `ruff check .` + `ruff format --check`
→ `python -X utf8 -m src.pipeline run --stage all` → `python -X utf8 -m pytest -m "not slow"`.

Bước dựng dữ liệu là bắt buộc vì bộ test nhanh chưa hermetic (`TD-09`): năm test dashboard cần
`warehouse/olist.duckdb` và `data/marts/`. Workflow không truyền `--refresh-ibge`, nên nó chỉ
đọc cache IBGE đã commit; chỉ khi cache đó mất hoặc hỏng thì CI mới cần mạng.

Bộ test `slow` và cổng phủ 80% **không** chạy trong CI — chúng chạy tay trước mỗi mốc phát
hành: `python -X utf8 -m pytest --cov=src --cov-fail-under=80`.

## KPI baseline

| KPI | Giá trị |
|---|---|
| Doanh thu delivered | 15.419.773,75 BRL |
| Số đơn delivered | 96.478 |
| AOV | 159,83 BRL |
| Đơn giao trễ | 7.826 |
| Tỷ lệ giao trễ | 8,11% |

## Lưu ý

- `dataset/` là dữ liệu gốc, không sửa.
- API IBGE có thể không truy cập được; repo dùng cache bootstrap 27 bang tại `dataset/external/ibge/`. Dùng `--refresh-ibge` khi có mạng.
- Dashboard chỉ chạy localhost.
- ML dự báo giao trễ chưa triển khai (story Could).

## Tài liệu

- `docs/data-dictionary.md`
- `docs/runbook.md`
- `docs/3v.md`
- `aidlc-docs/` — tài liệu quy trình AI-DLC và thiết kế chi tiết.
