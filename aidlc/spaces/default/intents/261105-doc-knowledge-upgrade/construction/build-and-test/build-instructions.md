# Build Instructions — Olist integration upgrade

Áp dụng cho Windows 10/11, Python 3.13, repo tại `C:\Users\Admin\Desktop\Tích hợp và xử lí dữ liệu lớn`.

## 1. Dựng môi trường

```powershell
python -m venv --system-site-packages .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` ghim 10 gói, gồm `dash==4.4.1`, `plotly==7.1.0`, `duckdb`, `pandas==2.2.3`, `ruff==0.17.4`, `dash-mantine-components==2.8.1`. Không có bước build, không có bundler: sản phẩm chạy trực tiếp từ mã nguồn.

## 2. Dựng dữ liệu

```powershell
.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all
```

Sáu tầng: `ingest → clean → quality → integrate → linkage → analyze`. Lệnh này sinh `data/`, `warehouse/olist.duckdb`, `logs/` — cả ba bị `.gitignore`. `dataset/` chỉ đọc, không bao giờ bị ghi.

## 3. Chạy sản phẩm

```powershell
.venv\Scripts\python.exe -X utf8 -m src.dashboard
```

Bind `127.0.0.1:8050` theo `config.yaml`. Bốn tab: ba tab báo cáo cũ và tab "Tích hợp".

## 4. Cổng chất lượng (chạy trước mỗi lần phát hành)

```powershell
.venv\Scripts\python.exe -X utf8 -m ruff check .
.venv\Scripts\python.exe -X utf8 -m ruff format --check src/integration src/linkage tests/unit/test_integration_*.py tests/unit/test_linkage_*.py tests/unit/test_log_pruning.py
.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow"
.venv\Scripts\python.exe -X utf8 -m pytest -m slow
.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80
```

## 5. Ràng buộc bắt buộc

- **UTF-8**: mọi lệnh Python phải có `-X utf8` (hoặc `PYTHONUTF8=1`). Đường dẫn workspace có ký tự tiếng Việt và dữ liệu có ký tự Bồ Đào Nha; thiếu cờ này sẽ `UnicodeEncodeError`.
- **Đóng dashboard trước khi chạy `integrate`**: cùng một tệp `warehouse/olist.duckdb` bị khoá.
- **View DuckDB chứa đường dẫn tuyệt đối** vào Parquet: chuyển thư mục repo hoặc dùng worktree khác thì phải chạy lại `integrate` trước khi mở dashboard.
- **`dataset/` bất biến**: không sửa, không "làm sạch tại chỗ".

## 6. Dựng lại từ đầu

Xoá `data/`, `warehouse/`, `logs/`, `inbox/` rồi chạy lại bước 2 và 3. Không có migration cơ sở dữ liệu nào phải đảo.
