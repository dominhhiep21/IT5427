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

# Kiểm định thống kê — đọc data/marts/ và warehouse/olist.duckdb nên chạy sau `--stage all`
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage stats
```

Tầng `stats` sinh `data/reports/analysis.json` — tệp báo cáo dùng chung (hợp đồng C2, phiên bản 3)
với hai khối `stats` và `model`. Tầng này ghi **cả hai** khối trong một lần ghi duy nhất: khối `stats` do
năm phép kiểm định dựng, rồi bước mô hình huấn luyện bộ phân loại đơn trễ và trả khối `model` để tầng `stats`
ghép vào. Doanh thu trong khối mùa vụ luôn đi kèm trường `revenue_definition` (định nghĩa duy nhất:
`price + freight_value` của đơn `delivered`).

Bước mô hình giữ đúng hợp đồng C2/C3: dự đoán ở **grain dòng hàng** (110.195 dòng hàng, 96.476 đơn,
8.713 dòng trễ, 2 đơn loại vì thiếu carrier date), chia tập **theo `order_id`** tại mốc **2018-04-01**
(mọi dòng hàng của một đơn nằm cùng một phía, đơn rơi đúng ngày cắt thuộc tập kiểm tra), dùng **14 cột đặc
trưng** biết được lúc đặt hàng — 11 cột cũ cộng `seller_state`, `handling_days`, `approval_days` — chọn
ngưỡng cảnh báo trên lưới 19 điểm 0,05…0,95 sao cho F1 cao nhất
(`threshold_method = "max_f1_on_test_grid005"`), và ghi rõ `auc_below_target = true` khi AUC dưới 0,70.
Khối `model` còn mang `unit` (nhãn "dòng hàng"), `auc_tree` (mô hình cây chỉ để báo cáo), `baseline_auc`
(baseline `customer_state` đo lại trong **cùng** khung) và `beats_baseline`. Tệp mô hình lưu bằng `pickle`
trong `data/models/`. Cỡ mẫu lệch baseline, danh sách đặc trưng sai tên hay sai thứ tự, hay bộ phân loại
không hội tụ đều là lỗi: tầng dừng và tệp báo cáo giữ nguyên bản cũ.

Output:

- `data/raw/*.parquet`
- `data/cleaned/*.parquet`
- `data/marts/*.parquet`
- `warehouse/olist.duckdb`
- `data/reports/*.json`, trong đó `data/reports/analysis.json` là báo cáo thống kê dùng chung
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

Dashboard có 5 tab:

- **Tổng quan**: KPI, doanh thu theo tháng, top danh mục.
- **Danh mục**: doanh thu theo danh mục, top sản phẩm.
- **Giao vận**: tỷ lệ giao trễ theo bang/danh mục/tháng.
- **Tích hợp**: thẻ "Số đơn theo tháng" đọc thẳng `dataset/`, chạy truy vấn trên DuckDB
  in-memory nên không cần `warehouse/` và không phụ thuộc pipeline đã chạy hay chưa.
- **Kết quả phân tích**: đọc `data/reports/analysis.json` trong callback rồi dựng dải tóm tắt bốn thẻ
  (tỉ lệ trễ, số đơn, số kiểm định bị bỏ, AUC kèm dấu đạt/không đạt mốc 0,70), mục thống kê năm phép
  kiểm định, mục mô hình và mục **Dự đoán** — nhập thông tin một dòng hàng rồi bấm nút để chấm bằng tệp
  mô hình trong `data/models/` (tệp này do `run --stage stats` sinh ra, không nằm trong git). Bốn trạng
  thái `rong`, `mot-phan`, `day-du`, `loi` hiện bằng bốn câu chữ khác nhau; trạng thái `chua-chay` chỉ
  tồn tại trong lúc đang đọc. Tab không tính lại chỉ số nào: dải tóm tắt và mục mô hình đọc thẳng từ tệp
  báo cáo, còn mục Dự đoán chỉ gọi `score_item` với ngưỡng đọc từ chính tệp đó.

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

# Toàn bộ, kèm cổng phủ 80% — đúng lệnh CI chạy
.\.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80 --cov-report=term
```

Bộ nhanh có **691 test** (`-m "not slow"`); bộ chậm (`-m slow`) có **mười lăm** test, phần lớn dựng lại
pipeline trên dữ liệu thật: `tests/integration/test_u1_end_to_end.py`, `test_u1_mart_columns_end_to_end.py`,
`test_u1_stats_end_to_end.py`, `test_u2_end_to_end.py`, `test_u2_model_end_to_end.py`, `test_u3_end_to_end.py`
và test cổng mốc sàn `test_u3_floor_end_to_end.py`, cộng ba test chất lượng dữ liệu trong
`tests/data_quality/test_real_dataset.py` và bốn test nằm trong `tests/unit/`. Bộ nhanh và bộ chậm tách bằng
marker trong `pytest.ini`.

Các test mới của tầng `stats`, của bước mô hình và của tab "Kết quả phân tích" tự dựng dữ liệu của mình trong
bộ nhớ và không đọc `data/reports/analysis.json` hay `warehouse/olist.duckdb` của repo; năm test dashboard cũ
vẫn cần hai thư mục sinh ra đó, đúng như mục CI mô tả (`TD-09`). Riêng `test_u3_end_to_end.py` có ca
`test_u3_analysis_tab_renders_the_real_report` đọc báo cáo thật mà tầng `stats` vừa ghi, và
`test_u3_floor_end_to_end.py` là chỗ **duy nhất** khẳng định một ngưỡng chất lượng của mô hình
(`beats_floor`): nó chạy trong bộ `slow` trên báo cáo thật chứ không ghim một giá trị AUC.

## Lint và định dạng

```powershell
.\.venv\Scripts\ruff check .
.\.venv\Scripts\ruff format --check src/integration
```

`ruff` (ghim trong `requirements.txt`) là cổng bắt buộc: `ruff check .` chạy toàn repo, còn
`ruff format --check` chạy trên mã của đợt nâng cấp — mã cũ được dọn theo từng tệp khi có
người sửa tới.

## CI

Workflow ở `.github/workflows/ci.yml`, chạy trên `windows-2022` khi push/pull request vào `main`,
`feature/update-ui-ux` và `feature/analysis-and-models`. Chín bước: checkout → Python 3.13 (cache theo
`requirements.txt`) → `pip install -r requirements.txt` → `ruff check .` + `ruff format --check` →
`python -X utf8 -m src.pipeline run --stage all` → `python -X utf8 -m src.pipeline run --stage stats` →
`python -X utf8 -m pytest -m "not slow"` → `python -X utf8 -m pytest --cov=src --cov-fail-under=80`
→ smoke nạp `config/integration-sources.yaml`.

Bước dựng dữ liệu là bắt buộc vì bộ test nhanh chưa hermetic (`TD-09`): năm test dashboard cần
`warehouse/olist.duckdb` và `data/marts/`. Workflow không truyền `--refresh-ibge`, nên nó chỉ
đọc cache IBGE đã commit; chỉ khi cache đó mất hoặc hỏng thì CI mới cần mạng.

Bước `run --stage stats` đứng **sau** `--stage all` vì nó đọc `data/marts/` và `warehouse/olist.duckdb`,
và **trước** các bước test để cổng CI chạy thật tầng mới. Vì tầng đó sinh `data/reports/analysis.json`,
không test nào được đọc tệp ấy — nếu không, bộ "nhanh" sẽ xanh trong CI mà đỏ trên máy mới clone.

Cổng phủ 80% tính trên **toàn bộ** bộ test (nhanh + `slow`), đúng như `ci.yml` chạy: bảy mô-đun `src/`
chỉ có phần phủ đến từ bộ `slow`, nên đặt `--cov-fail-under` lên riêng bộ nhanh sẽ đỏ ngay lần đầu. Lệnh
tương đương chạy tay trước mỗi mốc phát hành:
`python -X utf8 -m pytest --cov=src --cov-fail-under=80`.

Chính bước cuối đó là chỗ bộ `slow` chạy trong CI, nên test cổng mốc sàn `test_u3_floor_end_to_end.py` cũng
chạy ở đây chứ không cần thêm bước nào; ngưỡng 80% và số bước của workflow giữ nguyên.

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
- Mô hình dự báo giao trễ chạy trong tầng `stats`, đi vào báo cáo dưới dạng khối `model`, **và** được lưu
  bằng `pickle` tại `data/models/` (hợp đồng C2b) để màn hình dự đoán nạp lại mà không phải huấn luyện lại.
  `data/` nằm trong `.gitignore`, nên tệp mô hình là sản phẩm sinh ra chứ không phải artifact phát hành: một
  máy mới clone không có tệp nào cho tới khi chạy `--stage stats`, và giao diện phải chịu được trạng thái
  "chưa có mô hình" thay vì sập.

## Tài liệu

- `docs/data-dictionary.md`
- `docs/runbook.md`
- `docs/3v.md`
- `aidlc-docs/` — tài liệu quy trình AI-DLC và thiết kế chi tiết.
