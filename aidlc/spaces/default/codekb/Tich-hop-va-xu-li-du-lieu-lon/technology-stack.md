# Công nghệ sử dụng — Olist E-commerce Data Pipeline

> Phiên bản lấy từ `requirements.txt` (ghim chính xác) và `README.md`. Không có `pyproject.toml`,
> `setup.py`, `poetry.lock` hay `Pipfile`, nên chỉ **phụ thuộc trực tiếp** được ghim.

## 1. Nền tảng và ngôn ngữ

| Hạng mục | Giá trị | Bằng chứng |
|---|---|---|
| Ngôn ngữ | Python 3.13 | `README.md` ("Windows 10/11, Python 3.13"); cú pháp dùng `X \| None`, `from __future__ import annotations` |
| Hệ điều hành đích | Windows 10/11 (đường dẫn có ký tự tiếng Việt) | `README.md`, `docs/runbook.md`, ghi chú `AGENTS.md` |
| Môi trường ảo | `.venv` tạo bằng `python -m venv --system-site-packages` (bị `.gitignore`) | `README.md` |
| Mã hóa | Bắt buộc UTF-8 khi chạy (`-X utf8` hoặc `PYTHONUTF8=1`) | `README.md`, `docs/runbook.md` |
| Kiểu gõ | Type hint hiện đại (`list[str]`, `dict[str, pd.DataFrame]`, `Path \| None`) + `from __future__ import annotations` | hầu hết tệp trong `src/` |
| Mô hình chạy | Tiến trình đơn, batch, không container, không cloud | `docs/3v.md`, không có `Dockerfile`/`docker-compose.yml` |

## 2. Thư viện bên thứ ba (ghim trong `requirements.txt`)

| Thư viện | Phiên bản | Vai trò | Nơi dùng chính |
|---|---|---|---|
| `pandas` | 2.2.3 | Khung dữ liệu, đọc/ghi CSV-Parquet, groupby/merge | toàn bộ tầng ETL và analytics |
| `pyarrow` | 26.0.0 | Engine Parquet (`engine="pyarrow"`), kiểu `Int64`/`string` | `src/common/io.py`, mọi lần ghi Parquet |
| `duckdb` | 2.0.0 | Kho truy vấn trong tiến trình, đọc `read_parquet`, view | `src/integrate/connections.py`, `catalog.py`, `src/analytics/service.py`, `src/dashboard/app.py` |
| `dash` | 4.4.1 | Framework web dashboard (`Dash`, `dcc`, `html`, `Input/Output`) | `src/dashboard/app.py`, `components.py` |
| `plotly` | 7.1.0 | Đối tượng đồ thị (`go.Figure`, `Scatter`, `Bar`) | `src/dashboard/app.py`, `components.py` |
| `PyYAML` | 6.0.2 | Đọc `config.yaml` (`yaml.safe_load`) | `src/config.py` |
| `pytest` | 9.1.1 | Khung kiểm thử | `tests/` |
| `pytest-cov` | 7.1.0 | Đo độ phủ (`--cov=src`) — chỉ có lệnh trong README, **không cấu hình** | CI/đo phủ thủ công |

### Thư viện chuẩn được dùng

`argparse` (CLI), `dataclasses` (`AppConfig` và 14 hợp đồng dữ liệu), `pathlib`, `hashlib` (SHA-256),
`json`, `os.replace` (ghi nguyên tử), `urllib.request`/`urllib.error` (IBGE, không dùng `requests`),
`datetime`/`timezone`, `uuid`, `shutil`, `tracemalloc` (đo bộ nhớ), `time.perf_counter` (đo thời lượng),
`sys` (mã thoát).

## 3. Định dạng dữ liệu và lưu trữ

| Hạng mục | Lựa chọn | Cấu hình |
|---|---|---|
| Dữ liệu nguồn | CSV UTF-8, phân tách bằng dấu phẩy, mọi trường được trích dẫn | `dataset/*.csv` (bất biến) |
| Định dạng trung gian | Apache Parquet, nén Snappy | `parquet.compression: snappy` |
| Kho truy vấn | DuckDB một tệp `warehouse/olist.duckdb`, chỉ chứa **view** | `duckdb.memory_limit: 1GB`, `duckdb.threads: 4` |
| Báo cáo | JSON (UTF-8, `ensure_ascii=False`, indent 2) | `data/reports/` |
| Nhật ký | JSON Lines, một dòng một sự kiện | `logs/<run_id>.jsonl` |
| Dữ liệu tham chiếu | JSON tĩnh `estados.json` + `metadata.json` (có SHA-256) | `dataset/external/ibge/` |
| Trạng thái micro-batch | JSON một tệp `inbox/manifest.json` | `src/pipeline/manifest.py` |

## 4. Giao diện và trình bày

- **Dash 4.4.1** với `dcc.Tabs`, `dcc.DatePickerRange`, `dcc.Dropdown`, `dcc.Graph`, `dcc.Store`, `html.*`.
- **Hai callback** duy nhất (đồng bộ bộ lọc → `filters-store`; render 9 output).
- **CSS thuần** trong `assets/style.css` (277 dòng): biến CSS (`--ink #0b1f1a`, `--paper #f6f7f2`,
  `--ochre #d9a441`, `--clay #b5532f`), lưới biểu đồ, KPI card, bảng dữ liệu, banner lỗi, badge.
  Không dùng Tailwind/Bootstrap/JS tùy biến.
- **Định dạng số kiểu Brazil** (`1.234,56`, `R$`, `%`) trong `src/dashboard/formatting.py`.
- Font hệ thống `Segoe UI` — không tải webfont.

## 5. Công cụ phát triển và vận hành

| Hạng mục | Trạng thái | Chi tiết |
|---|---|---|
| Quản lý gói | `requirements.txt` (8 ghim) | Không có lock file, không có `pyproject.toml` |
| Kiểm thử | `pytest` + `pytest.ini` | `testpaths = tests`, marker `slow`, `addopts = -ra` |
| Đo phủ | `pytest-cov` (có cài) | Không có `[coverage]`/`--cov-fail-under`; tệp `.coverage` tồn tại cục bộ nhưng bị `.gitignore` |
| Lint/format | **Không có** | Không `.flake8`, `ruff.toml`, `mypy.ini`, `pyproject.toml`, `.pre-commit-config.yaml` |
| Kiểm tra kiểu | **Không có** | Type hint chỉ để đọc, không có `mypy`/`pyright` trong phụ thuộc |
| CI/CD | **Không có** | Không `.github/workflows`, `.gitlab-ci.yml`, `azure-pipelines.yml` |
| Đóng gói phát hành | **Không có** | Chạy trực tiếp từ mã nguồn bằng `python -m` |
| Quản lý phiên bản | `git` (nhánh `main`, 6 commit) | `dataset/`, `data/`, `warehouse/`, `logs/`, `inbox/` bị `.gitignore` |

## 6. Rủi ro công nghệ

1. **Không ghim phụ thuộc bắc cầu.** `dash` kéo theo Flask/Werkzeug, `pandas` kéo theo NumPy; không có
   lock file nên môi trường dựng lại có thể lệch. Khuyến nghị: thêm lock (`pip freeze` hoặc `uv`/`poetry`).
2. **Phiên bản lớn, non-trivial.** `pyarrow 26`, `duckdb 2.0`, `dash 4.4`, `plotly 7.1`, `pytest 9` đều là
   dòng mới; API dùng trong mã là cơ bản (`read_parquet`, `PRAGMA`, `dcc.*`, `go.Figure`) nên ít rủi ro,
   nhưng nâng cấp pandas lên 3.x sẽ ảnh hưởng copy-on-write và `Series.get`/`fillna(downcast)`.
3. **DuckDB giữ đường dẫn tuyệt đối trong view.** Chuyển thư mục repo (hoặc đổi `workspace_root`)
   làm view trỏ sai chỗ → dashboard báo lỗi cho tới khi chạy lại `integrate`. Đây là rủi ro trực tiếp
   cho đợt nâng cấp nếu thêm môi trường/worktree khác.
4. **Ghi chú môi trường trong `AGENTS.md` không còn khớp `requirements.txt`**: ghi chú nói máy toàn cục
   *không* có `duckdb`, `pyarrow`; trong khi `requirements.txt` ghim chúng và `warehouse/olist.duckdb`
   đã tồn tại. Cần xác nhận `.venv` hiện có đủ gói trước khi chạy pipeline (không kiểm chứng trong lần quét này).
5. **Không có ràng buộc phiên bản Python trong mã** (chỉ trong README). Python 3.12 sẽ vẫn chạy; Python 3.14
   chưa được kiểm chứng.
6. **Windows-first**: đường dẫn, `os.replace`, UTF-8 console. Chạy trên Linux cần kiểm tra lại `-X utf8`
   và đường dẫn có dấu; mã dùng `as_posix()` khi nhúng đường dẫn vào SQL nên tương đối an toàn.
