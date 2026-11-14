# Build Instructions — intent `261111-model-feature-improvemen`

Không có bước biên dịch: repo chạy từ mã nguồn Python. "Build" ở đây là dựng môi trường và sinh artefact dữ liệu.

## 1. Môi trường

| Hạng mục | Giá trị |
|---|---|
| Hệ điều hành | Windows 10/11 |
| Python | 3.13 (`.venv` tạo bằng `python -m venv --system-site-packages`) |
| Phụ thuộc | `requirements.txt` — **12 gói ghim**, không thêm gói nào trong đợt này |
| Mã hoá | mọi lệnh chạy `python -X utf8` (đường dẫn có tiếng Việt, dữ liệu có tiếng Bồ Đào Nha) |

```
python -m venv --system-site-packages .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 2. Sinh dữ liệu (bắt buộc trước khi chạy dashboard)

```
python -X utf8 -m src.pipeline run --stage all
python -X utf8 -m src.pipeline run --stage stats
```

- Bước 1 dựng `data/`, `warehouse/olist.duckdb` (9 bảng mart, 11 view, 5 KPI).
- Bước 2 sinh `data/reports/analysis.json` (phiên bản 3) **và** `data/models/logistic.pkl`.
- Không có bước 2 thì mục Dự đoán không dùng được — đây là hành vi đã thiết kế, giao diện hiện câu hướng dẫn.

## 3. Chạy

```
python -X utf8 -m src.dashboard
```

Bind `127.0.0.1:8050` (`config.yaml`). Không có bước đóng gói, không có deploy.

## 4. Làm lại từ đầu

```
xóa data/ warehouse/ logs/ inbox/
python -X utf8 -m src.pipeline run --stage all
python -X utf8 -m src.pipeline run --stage stats
```

`dataset/` là dữ liệu gốc, **không** sửa. Mọi artefact sinh ra đều bị `.gitignore`.

## 5. Kiểm sau khi build

| Cổng | Lệnh | Kỳ vọng |
|---|---|---|
| Bộ nhanh | `python -X utf8 -m pytest -m "not slow" -q` | **708 passed, 15 deselected** |
| Lint/format | `python -X utf8 -m ruff check .` và `ruff format --check` (danh sách 50 mục trong `ci.yml`) | sạch |
| Toàn bộ + phủ | `python -X utf8 -m pytest --cov=src --cov-fail-under=80` | **723 passed**, phủ **92,71%** |
| Chuỗi xác nhận | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_intent.ps1` | bốn bước xanh |
