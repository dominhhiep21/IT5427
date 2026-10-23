# Build Instructions

## Prerequisites

- **OS**: Windows 10/11.
- **Python**: 3.13.x.
- **RAM**: ≥ 8 GB.
- **Disk**: ≥ 2 GB trống (data + venv + Playwright optional).
- **Không cần**: Docker, Java, Spark, Kafka, cloud.
- **Dependencies**: xem `requirements.txt`.

## Build Steps

### 1. Tạo virtual environment

```powershell
python -m venv --system-site-packages .venv
```

### 2. Cài dependency

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Cấu hình

- `config.yaml` đã có giá trị mặc định.
- Kiểm tra `dataset/` có 9 CSV.
- Cache IBGE: `dataset/external/ibge/estados.json`.
- Chạy UTF-8:

```powershell
$env:PYTHONUTF8=1
```

### 4. Build / kiểm tra cú pháp

```powershell
.\.venv\Scripts\python.exe -X utf8 -m compileall -q src tests
```

### 5. Chạy pipeline đầy đủ

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all
```

## Expected Output

- Exit code 0.
- Log:
  `run_id=... success=True stages=['ingest','clean','quality','integrate','analyze']`.
- Artifacts:
  - `data/raw/*.parquet`
  - `data/cleaned/*.parquet`
  - `data/marts/*.parquet`
  - `warehouse/olist.duckdb`
  - `data/reports/*.json`
  - `logs/{run_id}.jsonl`

## Troubleshooting

### Dependency errors

- Kiểm tra Python 3.13.
- Cài lại:
  ```powershell
  .\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
  ```

### `UnicodeEncodeError`

- Luôn dùng `-X utf8` hoặc `$env:PYTHONUTF8=1`.

### `FileNotFoundError` cleaned/marts

- Chạy `run --stage all` trước.
- Kiểm tra `data/cleaned`, `data/marts`.

### `ExternalSourceError` IBGE

- API IBGE có thể timeout.
- Kiểm tra cache `dataset/external/ibge/estados.json`.
- Chỉ dùng `--refresh-ibge` khi có mạng.
