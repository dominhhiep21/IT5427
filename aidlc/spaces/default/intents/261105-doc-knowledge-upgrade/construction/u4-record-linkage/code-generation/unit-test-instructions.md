# Unit Test Instructions — u4-record-linkage

## Runner xác nhận (Bước 2)

| Kiểm tra | Kết quả |
|---|---|
| `pytest --version` | `pytest 9.1.1` (pytest-cov 7.1.0 đã cài trong `.venv`) |
| `pytest.ini` → `testpaths` | `tests` — pytest chỉ quét `tests/`, không quét `src/` |
| `pytest.ini` → markers | `slow: integration/data-quality tests that use the full Olist dataset` |
| `pytest.ini` → addopts | `-ra` |

## Lệnh unit-scoped của đơn vị này

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_linkage_models.py tests/unit/test_linkage_index.py tests/unit/test_linkage_score.py tests/unit/test_linkage_result.py
```

Lệnh dựng lại tệp ghi:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_linkage_models.py
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_linkage_index.py
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_linkage_score.py
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_linkage_result.py
```

Bộ nhanh (dùng trước khi coi Unit là xong):

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow"
```

Đo độ phủ (ngưỡng 80% cho `src/`):

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow" --cov=src --cov-report=term
```

Mọi lệnh Python chạy bằng `-X utf8` theo ràng buộc UTF-8 của repo (đường dẫn workspace có ký tự
tiếng Việt, dữ liệu có ký tự Bồ Đào Nha).
