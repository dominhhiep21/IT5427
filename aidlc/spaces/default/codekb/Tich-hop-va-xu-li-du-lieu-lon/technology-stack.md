# Công nghệ sử dụng — Olist E-commerce Data Pipeline

> Phiên bản lấy từ `requirements.txt` (ghim chính xác), `ruff.toml`, `pytest.ini` và
> `.github/workflows/ci.yml`, đọc lại ngày 2026-11-11 tại commit
> `ea77bdf88d1431de11c36e1b739972bd594063f0` (cây làm việc có thay đổi chưa commit).
> Không có `pyproject.toml`, `setup.py`, `poetry.lock` hay `Pipfile`, nên chỉ **phụ thuộc trực tiếp** được ghim.

## 1. Nền tảng và ngôn ngữ

| Hạng mục | Giá trị | Bằng chứng |
|---|---|---|
| Ngôn ngữ | Python 3.13 | `README.md`; `ruff.toml:4` (`target-version = "py313"`); `ci.yml:24` (`python-version: "3.13"`) |
| Hệ điều hành đích | Windows 10/11 (đường dẫn có ký tự tiếng Việt) | `README.md`, `docs/runbook.md`; CI ghim `windows-2022` (`ci.yml:18`) |
| Môi trường ảo | `.venv` tạo bằng `python -m venv --system-site-packages` (bị `.gitignore`) | `README.md` |
| Mã hóa | Bắt buộc UTF-8 khi chạy (`-X utf8` hoặc `PYTHONUTF8=1`) | `README.md`, `docs/runbook.md`, `ci.yml:40,45,48,53,58` |
| Kiểu gõ | Type hint hiện đại (`list[str]`, `dict[str, pd.DataFrame]`, `Path \| None`) + `from __future__ import annotations` | mọi mô-đun mới của đợt này (`report.py`, `statistics.py`, `model.py`, `analysis_tab.py`) |
| Mô hình chạy | Tiến trình đơn, batch, không container, không cloud | không có `Dockerfile`/`docker-compose.yml` |

## 2. Thư viện bên thứ ba (ghim trong `requirements.txt` — **12 gói**)

| Thư viện | Phiên bản | Vai trò | Nơi dùng chính |
|---|---|---|---|
| `pandas` | 2.2.3 | Khung dữ liệu, đọc/ghi CSV-Parquet, groupby/merge | toàn bộ tầng ETL, analytics, integration |
| `pyarrow` | 26.0.0 | Engine Parquet (`engine="pyarrow"`), kiểu `Int64`/`string` | `src/common/io.py`, mọi lần ghi Parquet |
| `duckdb` | 2.0.0 | Kho truy vấn trong tiến trình, đọc `read_parquet`, view | `src/integrate/connections.py`, `catalog.py`, `src/analytics/service.py`, `src/integration/rewrite.py` |
| `dash` | 4.4.1 | Framework web dashboard (`Dash`, `dcc`, `html`, `Input/Output`, `no_update`) | `src/dashboard/app.py`, `analysis_tab.py`, `components.py`, `src/integration/tab.py` |
| `dash-mantine-components` | 2.8.1 | Thành phần UI: tab "Tích hợp" **và** `dmc.MantineProvider`/`dmc.Title` của tab phân tích | `src/integration/tab.py`, `src/dashboard/analysis_tab.py` |
| `plotly` | 7.1.0 | Đối tượng đồ thị (`go.Figure`, `Scatter`, `Bar`) | `src/dashboard/app.py`, `components.py` |
| `PyYAML` | 6.0.2 | Đọc `config.yaml` + 3 hợp đồng YAML (`yaml.safe_load`); test `ci.yml` cũng đọc bằng PyYAML | `src/config.py`, `src/integration/schema.py`, `card.py`, `selector.py`, `tests/unit/test_ci_config.py` |
| `pytest` | 9.1.1 | Khung kiểm thử | `tests/` |
| `pytest-cov` | 7.1.0 | Đo độ phủ (`--cov=src`), **cưỡng chế 80% trong CI** | `ci.yml:53` |
| `ruff` | 0.17.4 | Lint + format | `ruff.toml`, `ci.yml:34-35` |
| **`scipy`** | **1.15.2** | **Phân phối chuẩn tắc** (`norm.ppf`, `norm.cdf`) cho khoảng Wilson/Newcombe và Fisher z; **chi bình phương** (`chi2_contingency`); **Pearson** (`pearsonr`) | chỉ `src/analytics/statistics.py` |
| **`scikit-learn`** | **1.6.1** | `LogisticRegression`, `StandardScaler`, `roc_auc_score`, `ConvergenceWarning` | chỉ `src/analytics/model.py` (+ `tests/unit/test_analytics_model.py` import trực tiếp `LogisticRegression`) |

Ghi chú từ `requirements.txt`:
- `dash-mantine-components` bị ghim dòng **2.x** vì dòng 3.x đòi `dash>=4.5.0` trong khi repo ghim
  `dash==4.4.1` (`:9-11`).
- `scipy` được chọn thay `statsmodels` vì "mọi phép ở đây đã có sẵn" (`:14-17`).
- `scikit-learn` được chọn thay vì tự viết: "tự viết là tự viết lại một thư viện" (`:18-22`).
- **`numpy` KHÔNG ghim** (`:23-26`): chỉ có mặt gián tiếp qua `pandas` 2.2.3 (hiện 2.2.1), và `scipy` 1.15.2
  được ghim theo đúng bản numpy đó. Tệp ghi rõ hệ quả: nếu một lần cài nâng numpy thì phải ghim lại
  `numpy==2.2.1` kèm lý do **và** chạy lại toàn bộ bộ test `slow`, vì nâng numpy có thể làm lệch số của các
  kiểm định đã kiểm chứng.

### Thư viện chuẩn được dùng

`argparse` (CLI), `dataclasses` (`AppConfig` + 14 hợp đồng dữ liệu + `replace`), `pathlib`, `hashlib`
(SHA-256), `json`, `os.replace` (ghi nguyên tử), `urllib.request`/`urllib.error` (IBGE, không dùng `requests`),
`datetime`/`timezone`, `uuid`, `shutil`, `math` (`sqrt`, `atanh`, `tanh` trong `statistics.py`),
`tracemalloc` (đo bộ nhớ), `warnings` (`catch_warnings` cho `ConvergenceWarning`),
`time.perf_counter` (đo thời lượng), `sys` (mã thoát), `re` (chỉ trong test).

### Thay đổi so với lần quét trước

Lần quét 2026-11-09 kết luận: "**không có thư viện thống kê / học máy**; `requirements.txt` ghim 10 gói".
Kết luận đó **nay sai**: `scipy` và `scikit-learn` đã được ghim kèm lý do, và `src/analytics/` import cả hai.
Khoảng trống còn lại **không** phải "thiếu gói" mà là "gói nào làm việc gì" (xem §6.3).

## 3. Định dạng dữ liệu và lưu trữ

| Hạng mục | Lựa chọn | Cấu hình |
|---|---|---|
| Dữ liệu nguồn | CSV UTF-8, phân tách bằng dấu phẩy, mọi trường được trích dẫn | `dataset/*.csv` (bất biến) |
| Định dạng trung gian | Apache Parquet, nén Snappy | `parquet.compression: snappy` |
| Kho truy vấn | DuckDB một tệp `warehouse/olist.duckdb`, chỉ chứa **11 view** | `duckdb.memory_limit: 1GB`, `duckdb.threads: 4` |
| Báo cáo | JSON (UTF-8, `ensure_ascii=False`, indent 2) | `data/reports/` — gồm `analysis.json` phiên bản **2** |
| **Mô hình đã huấn luyện** | **Không có định dạng** — mô hình chỉ sống trong RAM một lần chạy | không có `joblib`/`pickle`/`data/models/` trong mã |
| Kết quả tích hợp | JSON (UTF-8, `ensure_ascii=False`) | `data/integration/linkage-*.json` |
| Hợp đồng cấu hình | YAML tĩnh | `config/mediated-schema.yaml`, `config/integration-tab.yaml`, `config/integration-sources.yaml` |
| Nhật ký | JSON Lines, một dòng một sự kiện, giữ 10 tệp | `logs/<run_id>.jsonl` |
| Dữ liệu tham chiếu | JSON tĩnh `estados.json` + `metadata.json` (có SHA-256) | `dataset/external/ibge/` |
| Trạng thái micro-batch | JSON một tệp `inbox/manifest.json` | `src/pipeline/manifest.py` |

## 4. Giao diện và trình bày

- **Dash 4.4.1** với `dcc.Tabs`, `dcc.DatePickerRange`, `dcc.Dropdown`, `dcc.Graph`, `dcc.Store`,
  `dcc.Loading`, `html.*`, `no_update`; `dash-mantine-components` 2.8.1 cho tab "Tích hợp"
  **và** cho `dmc.MantineProvider`/`dmc.Title` của tab phân tích (DMC cần provider bao ngoài thì `Title` mới
  có theme — `analysis_tab.py:529-541`).
- **Chín callback**: hai của bốn tab báo cáo (`sync_filters`, `render_dashboard` với 9 output), sáu của
  tab "Tích hợp" (tổng quan, định tuyến, chạy truy vấn, đề xuất nguồn, tải lại, vùng lát cắt), một của tab
  "Kết quả phân tích".
- `suppress_callback_exceptions=True` bắt buộc vì thân tab và vùng kết quả được dựng trong callback.
- **CSS thuần** trong `assets/style.css` (không Tailwind/Bootstrap/JS tùy biến); bảng màu biểu đồ khai
  thành hằng trong `src/dashboard/app.py:42-48` để khớp token CSS; tab phân tích có khối `.analysis-tab`
  riêng, không được dùng token `--text-3` (chỉ đạt 3,85:1).
- **Định dạng số kiểu Brazil** (`1.234,56`, `R$`, `%`) trong `src/dashboard/formatting.py`; `format_percent`
  **không** nhân 100, người gọi tự nhân (`analysis_tab.py:191`).
- Font hệ thống `Segoe UI` — không tải webfont.

## 5. Công cụ phát triển và vận hành

| Hạng mục | Trạng thái | Chi tiết |
|---|---|---|
| Quản lý gói | `requirements.txt` (**12** ghim) | Không lock file, không `pyproject.toml` |
| Kiểm thử | `pytest` + `pytest.ini` | `testpaths = tests`, marker `slow`, `addopts = -ra`; **499** hàm test |
| Đo phủ | `pytest-cov`, **có ngưỡng trong CI** | `pytest --cov=src --cov-fail-under=80` trên toàn bộ bộ test (`ci.yml:53`); **không** khai trong `pytest.ini` |
| Lint/format | `ruff` 0.17.4 + `ruff.toml` | `line-length = 112`, `target-version = "py313"`, `select = ["E4","E7","E9","F"]`, 5 `per-file-ignores`, `extend-exclude` 8 mục (`assets`, `data`, `dataset`, `doc`, `inbox`, `logs`, `warehouse`, `.venv`) |
| Kiểm tra kiểu | **Không có** | Không `mypy`/`pyright` trong phụ thuộc hay CI (quyết định đã chốt) |
| CI/CD | **Có** — `.github/workflows/ci.yml` | `windows-2022`, Python 3.13, cache pip: cài (`:28`) → `ruff check .` + `ruff format --check` 35 mục (`:34-35`) → `run --stage all` (`:40`) → `run --stage stats` (`:45`) → `pytest -m "not slow"` (`:48`) → `pytest --cov=src --cov-fail-under=80` (`:53`) → smoke nạp `config/integration-sources.yaml` (`:58`) |
| Trigger CI | 3 nhánh | `main`, `feature/update-ui-ux`, `feature/analysis-and-models` (`ci.yml:5-13`), khai ở **cả** `push` và `pull_request` |
| Đóng gói phát hành | **Không có** | Chạy trực tiếp từ mã nguồn bằng `python -m`; phiên bản = commit hash; `CHANGELOG.md` ghi bốn mốc `v0.1.0`→`v0.4.0` |
| Quản lý phiên bản | `git` (nhánh `main`, `feature/update-ui-ux`, `feature/analysis-and-models`) | `data/`, `warehouse/`, `logs/`, `inbox/`, `.venv/`, `.coverage` bị `.gitignore` |

## 6. Rủi ro công nghệ

1. **Không ghim phụ thuộc bắc cầu.** `dash` kéo theo Flask/Werkzeug, `pandas` kéo theo NumPy,
   `scikit-learn` kéo theo `joblib`/`threadpoolctl`; không có lock file nên môi trường dựng lại có thể lệch.
   Đặc biệt quan trọng cho đợt này: **numpy vẫn không ghim** và *số của mọi kiểm định* phụ thuộc numpy/scipy.
2. **Ràng buộc chéo Dash ↔ Mantine.** `dash-mantine-components` phải ở dòng 2.x vì `dash` bị ghim 4.4.1;
   nâng `dash` là phải kiểm lại DMC (đã ghi trong `requirements.txt`). Tab phân tích **mới** phụ thuộc DMC
   (`dmc.MantineProvider`, `dmc.Title`), nên ràng buộc này lan sang cả tab đó.
3. **`scipy` + `scikit-learn` là hai phụ thuộc nặng mới** (kéo numpy/SciPy/joblib vào `.venv` và CI).
   `requirements.txt:18-22` yêu cầu kiểm bằng `pip show numpy scipy joblib threadpoolctl` sau khi cài;
   nếu numpy bị nâng, mọi con số đã kiểm chứng của tầng `stats` (Wilson, Fisher, χ², phân rã mùa vụ) có thể
   lệch mà không ai báo — trừ khi chạy lại bộ `slow`.
4. **Không có cơ chế lưu mô hình.** Huấn luyện lại mỗi lần `--stage stats` là hành vi **có chủ đích** hiện tại
   (`README.md` mục "Lưu ý"), nhưng `scikit-learn` không có API ổn định để tuần tự hóa xuyên phiên bản:
   lưu mô hình là một quyết định công nghệ mới (joblib + phiên bản sklearn trong tệp mô tả), không phải
   chi tiết cài đặt.
5. **DuckDB giữ đường dẫn tuyệt đối trong view.** Chuyển thư mục repo (hoặc đổi `workspace_root`)
   làm view trỏ sai chỗ → dashboard báo lỗi cho tới khi chạy lại `integrate`.
6. **Hai nguồn dữ liệu cho các tab.** Bốn tab báo cáo và tab phân tích đọc DuckDB/tệp báo cáo;
   tab "Tích hợp" đọc thẳng CSV qua `src.integration.load`. Không có test nào so chéo hai đường ở mức tổng.
7. **Không có ràng buộc phiên bản Python trong mã** (chỉ trong README và CI).
8. **Windows-first**: đường dẫn, `os.replace`, UTF-8 console. CI chạy `windows-2022` nên lỗi phụ thuộc nền
   tảng hiếm khi lọt; chạy trên Linux chưa được kiểm chứng.
9. **`ruff format --check` chỉ phủ danh sách khai tay 35 mục** (`ci.yml:35`): tệp mới quên thêm là không
   được kiểm format. `tests/unit/test_ci_config.py:14-29` canh 14 tệp của đợt vừa rồi, nhưng **không** canh
   tệp của đợt sau.
