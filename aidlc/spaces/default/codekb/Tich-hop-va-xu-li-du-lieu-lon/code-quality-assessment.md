# Đánh giá chất lượng mã — Olist E-commerce Data Pipeline

> Đánh giá tĩnh từ việc đọc mã (không chạy test, không chạy build theo yêu cầu của lần quét).
> Số liệu: 55 tệp Python trong `src/` (~4.200 dòng), 25 mô-đun test, 47 hàm test.
> Nợ kỹ thuật được đánh mã `TD-nn` và tham chiếu từ các artifact khác.

## 1. Điểm mạnh

- **Ranh giới tầng rõ ràng**: mỗi bước ETL một gói, hợp đồng dữ liệu tập trung ở `src/common/types.py`.
- **Chốt hồi quy mạnh**: số dòng kỳ vọng, allowlist dị thường và 5 KPI baseline biến mọi thay đổi hành vi
  thành lỗi nhìn thấy được thay vì sai lệch âm thầm.
- **Ghi tệp an toàn**: `AtomicWriter` (temp → đọc lại kiểm số dòng → `os.replace`) và mart ghi qua temp.
- **Nhật ký có cấu trúc**: mỗi lần chạy có `run_id`, log JSONL, báo cáo JSON theo tầng.
- **Tài liệu vận hành thực dụng**: `docs/runbook.md` bao phủ đúng các sự cố đã gặp (DuckDB lock, IBGE timeout,
  `UnicodeEncodeError`, batch lỗi), kèm lệnh cụ thể.
- **Không có TODO/FIXME/HACK** trong `src/` (0 lần) — mã không mang theo ghi chú nợ dang dở.
- **Kiểm soát SQL an toàn**: mọi truy vấn dùng tham số `?`; tên cột/`GROUP BY` chọn từ từ điển hằng.

## 2. Bảng đánh giá nhanh

| Tiêu chí | Mức | Bằng chứng / ghi chú |
|---|---|---|
| Đặt tên rõ ràng | **Tốt** | Tên bảng/cờ tự giải thích; `dim_/fact_/agg_`, `U-/F-/D-/R-/A-` cho check |
| Kích thước hàm | **Trung bình** | Đa số hàm < 30 dòng; ngoại lệ: `QualityGate.run` (~245 dòng), `build_layout` (~170), `build_dashboard_outputs` (~80) |
| Xử lý lỗi | **Trung bình** | Cây ngoại lệ tốt, nhưng 8 chỗ `except Exception`; 2 chỗ nuốt lỗi im lặng trong dashboard (`_options`, `build_dashboard_outputs` trả banner) và `connections.read_only` |
| Hiện diện kiểm thử | **Trung bình** | 47 hàm test; phủ tốt clean/integrate cơ bản; thiếu unit cho analytics service, validate/reconcile/catalog, micro-batch, stages |
| Trùng lặp | **Trung bình** | Số dòng/KPI/khóa khai báo lặp ở 3–6 nơi (`TD-02`); danh sách bảng lặp ở 4 nơi |
| Mã chết | **Trung bình** | `MemoryProbe` không dùng; 2 khóa cấu hình bộ nhớ không dùng; `analytics/filters.py` là shim; khối rename vô nghĩa trong `clean_products` |
| Chú thích | **Tốt (mức vừa)** | Docstring một dòng ở đầu mô-đun/hàm; không có docstring tham số; tài liệu ngoài (`docs/`) bù lại |
| An toàn/secret | **Tốt** | Không có credential; chỉ một URL công khai cấu hình được; dashboard localhost |
| Khả năng kiểm chứng | **Trung bình** | Test "nhanh" phụ thuộc sản phẩm sinh ra (`TD-09`); không có CI |

## 3. Kiểm thử

### 3.1 Hiện trạng

| Nhóm | Số mô-đun | Số hàm test | Đặc điểm |
|---|---:|---:|---|
| `tests/unit` | 21 | 37 | Dùng fixture DataFrame nhỏ trong `tests/conftest.py`; một số chạm dữ liệu thật |
| `tests/integration` | 3 | 3 | `@pytest.mark.slow`, chạy toàn pipeline trên `dataset/` thật, khẳng định 5 KPI |
| `tests/data_quality` | 1 | 3 | `@pytest.mark.slow`, khẳng định hằng số dị thường (19.015 zip, 610 thiếu danh mục, 8.427 outlier) |
| Khác | `conftest.py` | — | 320 dòng fixture: `config`, `real_config`, `small_*`, `region_map`, `small_cleaned` |

Tổng 47 hàm test, 6 hàm `slow`. Không có `coverage` cấu hình; `.coverage` tồn tại cục bộ nhưng bị `.gitignore`.

### 3.2 Lỗ hổng kiểm thử (theo mô-đun)

| Mô-đun không có test đơn vị trực tiếp | Rủi ro |
|---|---|
| `src/analytics/service.py` | Chỉ được phủ bởi `test_u2_end_to_end` (slow); lỗi SQL/`_where` chỉ lộ khi chạy dữ liệu thật |
| `src/integrate/validate.py`, `reconcile.py` | Chốt chặn quan trọng nhất nhưng không có test đơn vị (không kiểm tra được nhánh fail rẻ) |
| `src/integrate/catalog.py`, `connections.py` | Test gián tiếp qua `list_views` trong test slow |
| `src/pipeline/micro_batch.py` | Chỉ có 1 test slow (`test_u3_end_to_end`) không đi vào nhánh lỗi/skip |
| `src/pipeline/stages.py` | `run_all` (đường `--stage all`) không có test nào; `run_stage("analyze")` có trong `test_cli` nhưng cần DuckDB thật |
| `src/pipeline/manifest.py` | Có test (2) nhưng không kiểm tra kịch bản "gate fail sau khi upsert" (`TD-01`) |
| `src/quality/checks.py` | Chỉ test gián tiếp qua `QualityGate` |
| `src/dashboard/app.py` | 5 test smoke; không kiểm tra nội dung 8 figure còn lại |

### 3.3 Tính cô lập của bộ test "nhanh"

`pytest -m "not slow"` **không** hermetic: `tests/unit/test_dashboard_smoke.py` gọi `load_config()` của repo
(3 test cần `warehouse/olist.duckdb` + `data/marts/`), `tests/unit/test_cli.py::test_main_analyze_stage`
cần DuckDB đã dựng. Trên máy mới clone (không có `data/`, `warehouse/` vì bị `.gitignore`), nhóm test này
sẽ fail hoặc trả banner lỗi. Đây là nợ kỹ thuật `TD-09`, mức cao cho trải nghiệm phát triển.

## 4. Lint, kiểm tra kiểu, CI/CD

- **Không có** cấu hình lint/format: không `.flake8`, `ruff.toml`, `mypy.ini`, `pyproject.toml`, `.pre-commit-config.yaml`.
- **Không có** kiểm tra kiểu tĩnh dù mã dùng type hint khá đều (`config` lại không được annotate).
- **Không có** CI: không `.github/workflows`, `.gitlab-ci.yml`, `azure-pipelines.yml`.
- **Không có** cổng độ phủ: `pytest-cov` được cài và README có lệnh `--cov=src`, nhưng không có ngưỡng.
- Hệ quả: chất lượng được giữ bởi kỷ luật con người + 47 test, không bởi chốt tự động.

## 5. Tài liệu

| Tệp | Chất lượng | Nhận xét |
|---|---|---|
| `README.md` | Tốt | Kiến trúc, lệnh, đầu ra, KPI baseline, lưu ý vận hành; **có tham chiếu chết** tới `aidlc-docs/` |
| `docs/data-dictionary.md` | Tốt | Mô tả 11 bảng mart, grain, cột; khớp mã (đã đối chiếu) |
| `docs/runbook.md` | Tốt | 9 tình huống sự cố kèm lệnh; phản ánh đúng mã |
| `docs/3v.md` | Đủ | Luận điểm Volume/Variety/Velocity; thừa nhận giới hạn mô phỏng |
| `AGENTS.md` | Tốt cho người | Trạng thái repo, môi trường, bẫy dữ liệu; **một số ghi chú môi trường đã cũ** (nói thiếu duckdb/pyarrow) |
| Docstring trong mã | Mức vừa | Một dòng mỗi mô-đun/hàm; không mô tả tham số/trả về; không có docstring cho lớp `AnalyticsService` |

## 6. Sổ nợ kỹ thuật

| ID | Mức | Vấn đề | Bằng chứng | Ảnh hưởng |
|---|---|---|---|---|
| TD-01 | **Cao** | Manifest đánh dấu tệp `success` **trước** khi quality gate chạy; batch fail sau upsert sẽ bị `skipped` ở lần chạy lại, dữ liệu không được promote | `src/pipeline/micro_batch.py` dòng 146 (`meta["status"] = "success"`), 169–175 (giữ nguyên success khi fail), 110–122 (skip theo `has_success`), `src/pipeline/manifest.py` 30–35 | Batch lỗi "biến mất" khỏi hàng đợi; người vận hành tưởng đã xử lý |
| TD-02 | Trung bình | Cùng một sự thật (số dòng, KPI, khóa) khai báo ở 3–6 nơi | `src/ingest/schemas.py:22–130`, `src/quality/gate.py:188–198`, `src/integrate/validate.py:12–22`, `src/integrate/reconcile.py:8–22`, `README.md`, test tích hợp | Đổi dữ liệu phải sửa nhiều nơi, dễ lệch |
| TD-03 | Thấp | Khối rename vô nghĩa (ánh xạ cột về chính nó) trong `clean_products` | `src/clean/products.py:38–43` | Mã gây nhiễu, không có tác dụng |
| TD-04 | Thấp | Mã/cấu hình chết: `MemoryProbe` không được gọi; `memory_warn_mb`/`memory_fail_mb` không được tiêu thụ | `src/common/memory.py`, `src/config.py:45–46,123–124`, `config.yaml:22–24` | Người đọc tưởng có giám sát bộ nhớ |
| TD-05 | Thấp | `src/analytics/filters.py` chỉ re-export `KpiFilters` | `src/analytics/filters.py` (7 dòng), chỉ test dùng | Lớp trung gian không cần thiết |
| TD-06 | Trung bình | Import thừa tạo phụ thuộc ngược chiều `integrate → analytics` | `src/integrate/pipeline.py:10` | Cản trở tách gói; mầm vòng import |
| TD-07 | Trung bình | Dashboard: hai output vẽ cùng một figure; nút "Thử lại" không có callback; hằng số ma thuật `"2017-01"` và câu "329 đơn" | `src/dashboard/app.py:423,449–461`, `src/dashboard/components.py:99,108` | Lãng phí tính toán, UI gây hiểu nhầm, dễ lệch dữ liệu |
| TD-08 | Thấp | `except Exception` bắt rộng ở biên (8 chỗ); hai chỗ nuốt lỗi im lặng | `src/dashboard/app.py:68,424`, `src/external/ibge.py:56`, `src/integrate/connections.py:28`, `src/pipeline/{cli,stages,micro_batch}.py` | Lỗi cấu hình bị che thành "không có dữ liệu" |
| TD-09 | **Cao** (DX) | Bộ test `not slow` phụ thuộc `warehouse/olist.duckdb` và `data/marts/` (bị gitignore) | `tests/unit/test_dashboard_smoke.py:15,23,30`, `tests/unit/test_cli.py:21` | Máy mới clone không chạy được test nhanh |
| TD-10 | Trung bình | Không lint/type-check/CI/ngưỡng phủ | không có tệp cấu hình tương ứng | Chất lượng chỉ dựa vào kỷ luật |
| TD-11 | Thấp | `ingest_all` đặt `passed=False` nhưng pipeline vẫn chạy tiếp; `StageResult` có mục `quality` trong khi `STAGES` chỉ có 4 tầng | `src/ingest/reader.py:68`, `src/pipeline/stages.py:19,122–130` | Báo cáo tầng khó diễn giải |
| TD-12 | Thấp | Mọi truy vấn doanh thu inner join `v_dim_date`; đơn có `date_key` NULL bị loại khỏi KPI mà không có cảnh báo | `src/analytics/service.py:54–103` | Chênh lệch KPI khó truy vết nếu timestamp lỗi tăng |
| TD-13 | Thấp | `process_inbox` sao toàn bộ `data/cleaned` sang temp cho từng batch và nạp 9 bảng vào RAM | `src/pipeline/micro_batch.py:127–128,149–157` | Chi phí O(kích thước cleaned) mỗi batch; chậm khi dữ liệu lớn |
| TD-14 | **Cao** (theo intent) | Bốn nhóm kiến thức tích hợp trong `doc/` **chưa có biểu diễn hạng nhất trong mã**: không có bảng ánh xạ lược đồ/mediation cấu hình được, không có mô-đun ghép bản ghi (ngoài khử trùng lặp geolocation), không có lớp viết lại truy vấn, không có sổ đăng ký chọn nguồn | `src/ingest/schemas.py` chỉ *kiểm tra*; `src/clean/geolocation.py` chỉ khử trùng lặp; `src/analytics/service.py` dựng SQL trực tiếp; `src/external/ibge.py` là nguồn ngoài duy nhất | Chính là phạm vi đợt nâng cấp — xem mục 7 |
| TD-15 | Trung bình | Allowlist dị thường là hằng số gắn với đúng phiên bản dữ liệu; mọi thay đổi cleaning làm fail chế độ `full` | `src/quality/allowlist.py:3–14` | Nâng cấp dễ "đỏ" hàng loạt, cần quy trình cập nhật allowlist |

## 7. Rủi ro cho đợt nâng cấp (intent hiện tại)

Intent: *nâng cấp hệ thống để thể hiện bốn nhóm kiến thức tích hợp dữ liệu và thêm tab "Tích hợp"*.
Các điểm chạm và rủi ro cụ thể:

### 7.1 Tab "Tích hợp" — phạm vi ảnh hưởng đã biết

Thêm tab thứ tư và/hoặc output mới sẽ **làm fail các test đang khẳng định số lượng cứng**:

- `tests/unit/test_dashboard_smoke.py:14–19` → `len(tabs[0].children) == 3` và `len(app.callback_map) == 2`.
- `tests/unit/test_dashboard_smoke.py:22–26` → `len(outputs) == 9`.
- `tests/integration/test_u3_end_to_end.py:46–48` → `len(app.callback_map) == 2`.

Đây là **thay đổi có chủ đích** nhưng phải cập nhật test cùng lúc; nếu không, Build and Test sẽ đỏ.
Ngoài ra: `build_dashboard_outputs` trả tuple vị trí — thêm output phải sửa cả hai nhánh (thành công và
nhánh lỗi trả 9 phần tử) để callback không lệch số output.

### 7.2 Bốn nhóm kiến thức tích hợp — khoảng trống cần lấp

| Nhóm kiến thức (`doc/`) | Hiện trạng trong mã | Việc nâng cấp sẽ phải chạm |
|---|---|---|
| Đồng nhất lược đồ / lược đồ trung gian | `TABLE_SPECS` kiểm tra tên + thứ tự cột; không có ánh xạ khai báo được; 2 danh mục thiếu bản dịch chỉ được đánh cờ | `src/ingest/schemas.py`, `src/clean/products.py`, có thể thêm marts mới |
| Ghép bản ghi (record linkage) | Chỉ khử trùng lặp geolocation (`drop_duplicates`) và chuẩn hóa chuỗi; không có so khớp mờ | `src/clean/geolocation.py` dùng làm mẫu; cần thư viện mới (chưa có trong `requirements.txt`) |
| Viết lại truy vấn | SQL dựng chuỗi trong `AnalyticsService`; không có lớp rewrite/tối ưu | `src/analytics/service.py`; test slow khẳng định kết quả từng truy vấn |
| Chọn nguồn dữ liệu | Một nguồn ngoài (IBGE) với cache/fallback | `src/external/*`, `config.yaml` |

Hệ quả kiến trúc: bốn nhóm này hiện **không có** chỗ đặt tự nhiên; đợt nâng cấp nên tạo gói mới
(ví dụ `src/integration_knowledge/` hoặc mở rộng `src/integrate/`) thay vì nhồi vào mô-đun sẵn có.

### 7.3 Rủi ro dữ liệu và hồi quy

1. **Allowlist và KPI là hợp đồng cứng** (`TD-15`, `TD-02`): mọi thay đổi cleaning/ghép bản ghi sẽ làm
   `quality full` hoặc `KpiReconciler` fail. Cần quyết định rõ: cập nhật baseline có kiểm soát hay giữ nguyên
   và thêm tầng mới song song.
2. **Số view = 11** bị khẳng định trong `tests/integration/test_u2_end_to_end.py:44`. Thêm view cho tab mới
   phải sửa test và `VIEW_TABLES`.
3. **Phụ thuộc ngoài mới**: ghép bản ghi mờ cần gói mới (ví dụ `rapidfuzz`/`recordlinkage`), hiện
   `requirements.txt` không có; cần tạo venv + cập nhật requirements như ghi chú `AGENTS.md`.
4. **DuckDB bị khóa**: thêm truy vấn/tab làm tăng khả năng tranh chấp tệp `warehouse/olist.duckdb`
   (runbook đã cảnh báo: đóng dashboard trước khi `integrate`).
5. **`TD-01` (manifest)**: nếu tab "Tích hợp" minh họa idempotency micro-batch, lỗi này sẽ lộ ra khi demo —
   nên sửa trước khi trình diễn.
6. **`TD-09`**: mọi thay đổi dashboard cần chạy được test nhanh; hiện test nhanh cần mart đã dựng sẵn.

## 8. Khuyến nghị ưu tiên

1. Sửa `TD-01` (trạng thái manifest) — lỗi đúng đắn dữ liệu, chi phí nhỏ.
2. Tách hằng số dữ liệu (`TD-02`) về một tệp cấu hình/JSON duy nhất trước khi thêm tầng mới.
3. Xóa import thừa (`TD-06`) và mã chết (`TD-03`, `TD-04`, `TD-05`) — dọn rẻ, giảm nhiễu.
4. Làm bộ test nhanh hermetic (`TD-09`) bằng fixture DuckDB tạm hoặc đánh dấu `slow` cho test phụ thuộc dữ liệu.
5. Thêm lint + CI tối thiểu (`ruff`, `pytest -m "not slow"`) (`TD-10`).
6. Khi thêm tab "Tích hợp": cập nhật đồng thời `build_dashboard_outputs` (cả nhánh lỗi), test số tab/output/callback,
   và tài liệu `README.md` (đang mô tả 3 tab).
