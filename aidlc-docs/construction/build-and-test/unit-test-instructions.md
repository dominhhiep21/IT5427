# Unit Test Execution

## Run Unit Tests

### 1. Chạy test nhanh (không dùng dữ liệu thật)

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow" -q
```

### 2. Chạy toàn bộ unit test

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/unit -q
```

### 3. Coverage

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-report=term -q
```

## Expected Results

- **Fast tests**: 39 passed.
- **Unit tests**: 30+ passed.
- **Coverage toàn dự án**: ~87%.
- **Coverage U1 cleaning/quality**: 100%.
- **Coverage U2 integrate/analytics**: ~89%.
- **Coverage U3 dashboard/pipeline**: ~75%.
- **Failures**: 0.

## Test Locations

- `tests/unit/` — cleaning, schema, quality, analytics, formatters, manifest, upsert, CLI, dashboard smoke.
- `tests/data_quality/` — baseline dữ liệu thật (marker `slow`).
- `tests/integration/` — end-to-end U1/U2/U3 (marker `slow`).

## Fix Failing Tests

1. Đọc output pytest: tên test, assertion, traceback.
2. Kiểm tra dữ liệu fixture hoặc baseline KPI.
3. Sửa code, không sửa baseline nếu chưa xác minh lại từ CSV.
4. Chạy lại test nhanh trước, sau đó full suite.
