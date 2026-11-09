# Code Summary — U1 Data Foundation

**Ngày hoàn tất**: 2026-10-22
**Run xác minh**: `20261022T162147-be5a3c14`
**Trạng thái**: Code + test hoàn tất; chờ phê duyệt

## 1. Tệp đã tạo

### Cấu hình và tài liệu dự án
- `requirements.txt` — pin pandas 2.2.3, pyarrow 26.0.0, PyYAML 6.0.2, pytest 9.1.1, pytest-cov 7.1.0.
- `pytest.ini` — marker `slow`, testpaths.
- `config.yaml` — đường dẫn, bbox, IQR, memory thresholds, compression.
- `.gitignore` — loại trừ `.venv/`, `data/`, `warehouse/`, `logs/`.

### `src/`
- `src/config.py` — `AppConfig`, `load_config`.
- `src/common/types.py` — `TableSpec`, `RunContext`, report dataclasses.
- `src/common/exceptions.py` — `PipelineError`, `SchemaError`, `QualityGateError`, `ConfigurationError`.
- `src/common/logging.py` — `new_run_context`, `JsonLogger`.
- `src/common/io.py` — `sha256_file`, `read_csv`, `validate_columns`, `AtomicWriter`.
- `src/common/memory.py` — `MemoryProbe` (tracemalloc).
- `src/ingest/schemas.py` — 9 `TableSpec`.
- `src/ingest/reader.py` — `ingest_table`, `ingest_all`.
- `src/ingest/reports.py` — `ReportWriter`, `reconcile_payments`.
- `src/clean/common.py` — normalize/parse/IQR helpers.
- `src/clean/customers.py`, `sellers.py`, `products.py`, `orders.py`, `items.py`, `payments.py`, `reviews.py`, `geolocation.py`.
- `src/clean/pipeline.py` — `clean_all`.
- `src/quality/checks.py` — unique/FK/row-count/domain checks.
- `src/quality/allowlist.py` — baseline bất thường.
- `src/quality/gate.py` — `QualityGate` full/incremental.

### `tests/`
- `tests/conftest.py` — fixture tổng hợp + config tạm.
- `tests/unit/` — 8 file test.
- `tests/data_quality/test_real_dataset.py` — baseline geolocation/category/outlier.
- `tests/integration/test_u1_end_to_end.py` — pipeline đầy đủ trên CSV thật.

## 2. Cách chạy

```powershell
# Test nhanh (không dùng dữ liệu thật)
.\.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow"

# Toàn bộ test, gồm integration trên CSV thật
.\.venv\Scripts\python.exe -X utf8 -m pytest

# Coverage cleaning/quality
.\.venv\Scripts\python.exe -X utf8 -m pytest --cov=src.clean --cov=src.quality --cov-report=term
```

U1 chưa có CLI; U3 sẽ thêm `src/pipeline`. Có thể gọi trực tiếp:

```python
from src.config import load_config
from src.common.logging import new_run_context, JsonLogger
from src.common.io import AtomicWriter
from src.ingest.reader import ingest_all
from src.clean.pipeline import clean_all
from src.quality.gate import QualityGate

config = load_config()
run = new_run_context("u1", config.logs_dir, config.temp_dir)
writer = AtomicWriter(run, config.parquet_compression)
logger = JsonLogger(run)
raw, ingest = ingest_all(config, run, writer, logger)
cleaned, cleaning = clean_all(raw, config, run, writer, logger)
report = QualityGate(logger).run(cleaned, "full", cleaning.geolocation, run.run_id)
```

## 3. Kết quả xác minh

| Kiểm tra | Kết quả |
|---|---|
| Test suite | **20 passed** |
| Coverage `src.clean` + `src.quality` | **100%** |
| Quality gate | **40/40 checks pass** |
| Orders | 99.441 |
| Order items | 112.650 |
| Payments | 103.886 |
| Reviews | 99.224 |
| Products | 32.951 |
| Geolocation raw | 1.000.163 |
| Geolocation zip sau gộp | 19.015 |
| Zip không có tọa độ | 5 |
| Price outlier IQR 1.5 | 8.427 |
| Sản phẩm thiếu category | 610 |
| Sản phẩm thiếu translation | 13 (thuộc 2 danh mục) |
| Đơn nhiều review | 547 (551 dòng review dư) |
| Lệch payment/item | 378 (warning) |
| Join customers × geo | 99.441 dòng |

## 4. Điều chỉnh so với phân tích ban đầu

Trong quá trình triển khai và kiểm thử, ba con số được xác minh lại:

1. **Đơn nhiều review**: **547 đơn** có > 1 review, tạo ra **551 dòng review dư**. Trước đó ghi nhầm là 551 đơn (551 là số dòng dư, không phải số đơn). Có 543 đơn 2 review và 4 đơn 3 review.
2. **Thiếu bản dịch**: **13 sản phẩm** thuộc **2 danh mục** (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`), không phải 2 sản phẩm.
3. **Zip nhiều biến thể city**: **8.555 zip** sau chuẩn hóa (trước chuẩn hóa là 8.556).

Các tài liệu requirements, stories, reverse engineering và functional design đã được cập nhật tương ứng.

## 5. Giới hạn hiện tại

- Chưa có CLI orchestration (U3).
- Chưa có star schema/KPI (U2).
- Chưa có dashboard (U3).
- Full batch chỉ chạy qua hàm Python; micro-batch sẽ bổ sung ở U3.
- `MemoryProbe` đã có nhưng chưa gắn vào run summary; sẽ tích hợp khi có CLI.

## 6. Output đã tạo trong workspace

- `data/raw/*.parquet` — 9 bảng.
- `data/cleaned/*.parquet` — 9 bảng sạch.
- `data/reports/ingest-report.json`
- `data/reports/cleaning-report.json`
- `data/reports/quality-report.json`
- `data/reports/reconciliation.json`
- `logs/{run_id}.jsonl`
