# Đánh giá chất lượng mã — Olist E-commerce Data Pipeline

> Đánh giá tĩnh từ việc đọc mã (không chạy test, không chạy build theo yêu cầu của lần quét).
> Cập nhật tập trung ngày 2026-11-11 tại commit `ea77bdf88d1431de11c36e1b739972bd594063f0`
> (cây làm việc có thay đổi chưa commit) cho `src/analytics/`, `src/integrate/`, `src/dashboard/`,
> `src/pipeline/`, `tests/`. Số liệu đo trên đĩa: **74** tệp Python trong `src/` (**11.333** dòng),
> **54** tệp test (**49** mô-đun, **499** hàm test, **12** hàm `slow`, **10.086** dòng).
> Nợ kỹ thuật được đánh mã `TD-nn` và tham chiếu từ các artifact khác.

## 1. Điểm mạnh

- **Ranh giới tầng rõ ràng**: mỗi bước ETL một gói, hợp đồng dữ liệu tập trung ở `src/common/types.py`;
  `AnalyticsService` vẫn là **nơi duy nhất** mở kết nối DuckDB, kể cả sau khi thêm kiểm định và mô hình.
- **Suy luận được tách khỏi I/O**: `statistics.py` và `model.py` là tập hàm thuần trên `DataFrame`/`dict`;
  chúng **không** đọc tệp, **không** mở kết nối, **không** giữ trạng thái. Nhờ vậy 1.098 dòng suy luận được
  kiểm bằng DuckDB tạm + `DataFrame` nhỏ thay vì phải chạy dữ liệu thật.
- **Chốt hồi quy mạnh**: số dòng kỳ vọng, allowlist dị thường, 5 KPI baseline và baseline quần thể mô hình
  biến mọi thay đổi hành vi thành lỗi nhìn thấy được thay vì sai lệch âm thầm.
- **Cổng tự động đã có thật**: `ruff check` + `ruff format --check`, CI trên `windows-2022`, ngưỡng phủ 80%
  cưỡng chế trong CI trên toàn bộ bộ test (`ci.yml:53`), và nay CI chạy **thật** tầng `stats`
  (`ci.yml:45`) trước khi test.
- **Ghi tệp an toàn, hai lớp**: `AtomicWriter` (temp → đọc lại kiểm số dòng → `os.replace`) và thêm một lớp
  riêng cho báo cáo phân tích — `write_report` **parse lại** tệp tạm, kiểm phiên bản và "không phải cả hai
  khối đều null" trước khi thay tệp (`report.py:248-267, 318-328`).
- **Hợp đồng lỗi có ngữ nghĩa**: `ModelError` (mô hình không dựng được khối hợp lệ) và `ReportError` (báo cáo
  không ghi/không đọc lại được) đều kế thừa `PipelineError`, nên CLI xử lý như mọi lỗi tầng.
- **Không im lặng trước bất thường**: không hội tụ là **lỗi** (`train_classifier`), AUC dưới mốc là **cờ được
  ghi ra** (`auc_below_target`) chứ không bị ẩn, kiểm định không chạy được là **mục được liệt kê kèm lý do**
  (`skipped`), khối thiếu là trạng thái `mot-phan` chứ không phải trang trắng.
- **Tài liệu vận hành thực dụng**: `docs/runbook.md` bao phủ đúng các sự cố đã gặp (DuckDB lock, IBGE timeout,
  `UnicodeEncodeError`, batch lỗi); `CHANGELOG.md` bốn mốc `v0.1.0`→`v0.4.0` viết cho người đọc.
- **Không có TODO/FIXME/HACK** trong `src/` (0 lần, đếm lại toàn bộ).
- **Kiểm soát SQL an toàn**: mọi truy vấn dùng tham số `?`; tên cột/`GROUP BY` chọn từ dict hằng; bốn hằng SQL
  mới là chuỗi tĩnh cấp mô-đun, chỉ nối thêm mệnh đề `_where`.
- **Hợp đồng giao diện được khai báo, không hard-code**: tab "Tích hợp" đọc id từ YAML, tab phân tích ánh xạ
  thẳng `ReportView.status` → token (không đoán trạng thái bằng cách dò chuỗi thông điệp,
  `analysis_tab.py:125-134`), lỗi hiển thị tại chỗ thay vì làm sập app.
- **Test mới tự dựng dữ liệu của mình** (`tmp_path` + DuckDB tạm), nên 5 mô-đun test của đợt này **không**
  làm bộ "nhanh" phụ thuộc thêm `data/marts/` — đúng hướng sửa `TD-09`.

## 2. Bảng đánh giá nhanh

| Tiêu chí | Mức | Bằng chứng / ghi chú |
|---|---|---|
| Đặt tên rõ ràng | **Tốt** | Tên bảng/cờ tự giải thích; `dim_/fact_/agg_`, `U-/F-/D-/R-/A-` cho check; token giao diện đóng; hằng số suy luận đều có tên (`SPLIT_DATE`, `AUC_TARGET`, `THRESHOLD_METHOD`…) |
| Kích thước hàm | **Trung bình → kém ở vài chỗ** | Đa số hàm < 30 dòng; ngoại lệ: `QualityGate.run` (~245 dòng), `src/integration/tab.py` (1.380 dòng/tệp), `build_layout` (~180 dòng), `build_dashboard_outputs` (~78 dòng), `report.py` (502 dòng với 20+ hàm parser nhỏ), `analysis_tab.py` (566 dòng) |
| Xử lý lỗi | **Trung bình, tốt hơn ở tầng mới** | Cây ngoại lệ 11 lớp (thêm `ModelError`, `ReportError`); `model.py`/`report.py` **không** bắt rộng; nhưng vẫn `except Exception` ở `src/dashboard/app.py:93-94, 531-532`, `analysis_tab.py:556-557`, `external/ibge.py`, `integrate/connections.py:26-29`, `pipeline/{cli,stages,micro_batch}.py` |
| Hiện diện kiểm thử | **Tốt về số lượng, trung bình về độ phủ** | 499 hàm test, +146 so với lần trước; tầng `stats`/mô hình/tab phân tích có test đơn vị thật; nhưng `kpi_summary`/`revenue_by_*`/`top_entities`/`delivery_kpis`, `run_all`, `validate`/`reconcile`/`catalog`, nhánh lỗi `micro_batch` vẫn chỉ có bộ `slow` hoặc không có |
| Trùng lặp | **Trung bình, lan thêm** | Số dòng/KPI/khóa khai 3–6 nơi (TD-02); baseline quần thể mô hình nay là chỗ khai **thứ tư** của 96.478/7.826 (TD-21); danh sách đặc trưng khai ở `model.py` + `service.py` + 2 test (TD-22); "số tab/callback/output" ở mã + 4 test |
| Mã chết | **Trung bình, giảm một phần** | `MemoryProbe` **nay có người dùng** (test slow); `memory_warn_mb` vẫn không ai đọc; `analytics/filters.py` vẫn là shim; import thừa `integrate → analytics` vẫn còn; 9 `# noqa` với mã không nằm trong `select` (TD-27) |
| Chú thích | **Tốt (mức vừa)** | Docstring một dòng ở đầu mô-đun/hàm; **không** docstring tham số; docstring mới giàu tham chiếu ID (`BR1.1`, `TS-9`, `PD-2`, `SEC-5`) — hữu ích nhưng phụ thuộc tài liệu ngoài repo (record AI-DLC) |
| An toàn/secret | **Tốt** | Không credential; chỉ một URL công khai cấu hình được; dashboard localhost; SQL tham số hóa |
| Khả năng kiểm chứng | **Tốt hơn trước** | CI + lint + ngưỡng phủ + chạy thật tầng `stats`; nhưng bộ "nhanh" vẫn chưa hermetic (TD-09) và không có kiểm tra kiểu (đã chốt) |

## 3. Kiểm thử

### 3.1 Hiện trạng

| Nhóm | Số mô-đun | Số hàm test | Đặc điểm |
|---|---:|---:|---|
| `tests/unit` | 43 | 490 | Fixture DataFrame nhỏ trong `tests/conftest.py`; nhiều mô-đun tự dựng **DuckDB tạm** trong `tmp_path` (`test_analytics_statistics`, `test_analytics_model`, `test_pipeline_stages`) |
| `tests/integration` | 5 | 5 (+1 test phụ trong `test_u3`) | `@pytest.mark.slow`, chạy toàn pipeline trên `dataset/` thật: U1, U2, U3, `test_u1_stats_end_to_end`, `test_u2_model_end_to_end` |
| `tests/data_quality` | 1 | 3 | `@pytest.mark.slow`, khẳng định hằng số dị thường (19.015 zip, 610 thiếu danh mục, 8.427 outlier) |
| Khác | `conftest.py` | — | 361 dòng fixture: `config`, `real_config`, `small_*`, `region_map`, `small_cleaned` |

Tổng **499** hàm test, **12** hàm `slow`, **10.086** dòng (lần trước: 353 / 9 / 7.358). Ngưỡng phủ 80% được
CI cưỡng chế trên **toàn bộ** bộ test (`ci.yml:50-53`) — vì bảy mô-đun `src/` chỉ có phần phủ đến từ bộ `slow`.

### 3.2 Lỗ hổng kiểm thử (theo mô-đun)

| Mô-đun không có test đơn vị trực tiếp | Rủi ro |
|---|---|
| `src/analytics/service.py` — **năm phương thức KPI cũ** | Bốn phương thức mới **đã** có test thật trên DuckDB tạm; `kpi_summary`/`revenue_by_period`/`revenue_by_dimension`/`top_entities`/`delivery_kpis` vẫn chỉ được phủ bởi `test_u2_end_to_end` (slow) và smoke dashboard (dùng dữ liệu thật). Lỗi SQL ở năm phương thức này chỉ lộ khi có mart thật |
| `src/integrate/validate.py`, `reconcile.py` | Chốt chặn quan trọng nhất nhưng không có test đơn vị; `EXPECTED`/`BASELINE` chỉ được xác nhận gián tiếp qua test slow. **Không có test nào canh `EXPECTED` khớp số dòng thật sau khi thêm cột** |
| `src/integrate/catalog.py`, `connections.py` | Test gián tiếp qua `list_views` trong `test_u2_end_to_end` (slow) |
| `src/integrate/facts.py`, `dimensions.py`, `aggregates.py` | Có `test_facts.py` (33 dòng), `test_dimensions.py` (19), `test_aggregates.py` (22) — mỏng so với 367 dòng mã; **không** khẳng định **tập cột** của `fact_orders`/`fact_order_items` |
| `src/pipeline/micro_batch.py` | Chỉ có 1 test slow (`test_u3_end_to_end`) không đi vào nhánh lỗi/skip |
| `src/pipeline/stages.py` — **`run_all`** | `run_stage` (kể cả nhánh `stats`, thứ tự stats→model, giữ khối model cũ) **đã** có test đơn vị (`test_pipeline_stages.py`); đường `--stage all` vẫn **không** có test nào |
| `src/pipeline/manifest.py` | Có test (2) nhưng không kiểm kịch bản "gate fail sau khi upsert" (TD-01) |
| `src/quality/checks.py` | Chỉ test gián tiếp qua `QualityGate` |
| `src/dashboard/app.py` | Test smoke khẳng định hình dạng (5 tab/9 callback/9 output) và 3 hành vi; **không** kiểm nội dung 8 figure |
| `src/dashboard/analysis_tab.py` | **Tốt**: 39 ca, gồm trạng thái, thứ tự khối, bốn thẻ, nhánh thiếu khối, a11y, lớp CSS, callback đọc tệp đúng một lần |
| `src/pipeline/cli.py` | 2 ca parser + 1 ca chạy thật `--stage analyze`; **không** test mã thoát 1 hay nhánh lỗi |

### 3.3 Tính cô lập của bộ test "nhanh"

`pytest -m "not slow"` **vẫn không** hermetic: `tests/unit/test_dashboard_smoke.py` (5 test gọi
`load_config()`) và `tests/unit/test_cli.py::test_main_analyze_stage` cần `warehouse/olist.duckdb` và
`data/marts/` (bị `.gitignore`). CI che lỗi bằng cách chạy `run --stage all` **và** `run --stage stats` trước
bước test. Trên máy mới clone bộ "nhanh" vẫn đỏ. Đây là `TD-09`, vẫn nguyên — nhưng **không** lan sang 5 mô-đun
test mới (chúng dựng mart trong `tmp_path`).

### 3.4 Chi phí bảo trì bộ test

Bộ test (10.086 dòng) nay bằng **0,89 lần** khối lượng `src/` (11.333 dòng). Bảy mô-đun lớn nhất:
`test_integration_tab.py` (983), `test_integration_selector.py` (752), `test_integration_rewrite.py` (748),
`test_analytics_model.py` (646), `test_dashboard_analysis_tab.py` (627), `test_integration_schema.py` (585),
`test_integration_card.py` (473) — chiếm 48% số dòng test.
Đây là hệ quả trực tiếp của TDD + quy ước "mọi mô-đun mới đều phải có test riêng"; tốt cho đúng đắn nhưng
làm mỗi thay đổi hình dạng giao diện/hợp đồng đắt hơn.

## 4. Lint, kiểm tra kiểu, CI/CD

- **Lint + format**: `ruff` 0.17.4, `ruff.toml` (`line-length = 112`, `target-version = "py313"`,
  `select = ["E4","E7","E9","F"]`, `extend-exclude` 8 mục). Năm `per-file-ignores` ghi rõ nợ cũ: `F401` cho
  `src/integrate/connections.py`, `src/integrate/pipeline.py`, `src/pipeline/micro_batch.py`,
  `src/quality/gate.py`; `E402` cho `tests/conftest.py`.
- **`ruff format --check` chỉ chạy trên danh sách khai tay 35 mục** (`ci.yml:35`), không toàn repo — đúng
  chính sách "dọn theo từng tệp khi có người sửa tới". Hệ quả: mã mới **phải** được thêm vào danh sách đó.
  `tests/unit/test_ci_config.py` canh 14 tệp của đợt vừa rồi (`:14-29`) — một bước tiến rõ rệt so với lần
  trước, nhưng danh sách kỳ vọng vẫn khai tay nên đợt sau phải tự thêm.
- **Không có** kiểm tra kiểu tĩnh (`mypy`/`pyright` không có trong phụ thuộc) — quyết định đã chốt.
- **CI**: `.github/workflows/ci.yml`, `windows-2022`, Python 3.13, cache pip; **7 bước**: cài → lint/format →
  `run --stage all` → `run --stage stats` → test nhanh → phủ 80% → smoke nạp cấu hình nguồn. Ba nhánh trigger
  ở cả `push` và `pull_request`.
- **Không có** bước build/đóng gói, không có deploy — phù hợp mô hình chạy từ mã nguồn.
- **Không có** kiểm tra "số dòng của `EXPECTED` khớp dữ liệu" ngoài bộ `slow`, và **không có** kiểm tra
  "tập cột của mart" ở bất kỳ đâu (xem TD-22).

## 5. Tài liệu

| Tệp | Chất lượng | Nhận xét |
|---|---|---|
| `README.md` | Tốt | Kiến trúc, lệnh, đầu ra, dashboard **5 tab**, CI có bước `stats`, KPI baseline, lưu ý; nay nói rõ tầng `stats` sinh cả hai khối và mô hình **không** được lưu ra đĩa (`:203-204`). Vẫn nhắc `aidlc-docs/` (tham chiếu chết) |
| `CHANGELOG.md` | Tốt | Bốn mốc `v0.1.0` (2026-11-06), `v0.2.0`/`v0.3.0`/`v0.4.0` (2026-11-11) theo ba nhóm **Thêm/Sửa/Nội bộ** |
| `docs/data-dictionary.md` | Tốt nhưng **lệch phạm vi** | Mô tả **11 bảng mart** với grain/cột (đối chiếu `facts.py`/`dimensions.py`: khớp). Nhưng **không** mô tả `v_*`, **không** mô tả `data/reports/analysis.json`, và không có cột `order_delivered_carrier_date` (vì mã cũng không có) |
| `docs/runbook.md` | Tốt (chưa đọc lại) | 9 tình huống sự cố kèm lệnh |
| `docs/3v.md` | Đủ (chưa đọc lại) | Volume/Variety/Velocity; thừa nhận giới hạn mô phỏng |
| `AGENTS.md` | Tốt cho người, **đã cũ ở phần môi trường** | Vẫn nói thiếu `duckdb`/`pyarrow` và "chưa có mô hình/kiểm định" — sai hiện trạng |
| Docstring trong mã | Mức vừa | Một dòng mỗi mô-đun/hàm; **không** mô tả tham số/trả về; `AnalyticsService` không có docstring lớp; `model.py`/`statistics.py`/`report.py` có docstring dẫn ID yêu cầu |

## 6. Sổ nợ kỹ thuật

| ID | Mức | Vấn đề | Bằng chứng | Ảnh hưởng |
|---|---|---|---|---|
| TD-01 | **Cao** | Manifest đánh dấu tệp `success` **trước** khi quality gate chạy; batch fail sau upsert sẽ bị `skipped` ở lần chạy lại | `src/pipeline/micro_batch.py:146` so với `:149-158`; `src/pipeline/manifest.py:30-35` | Batch lỗi "biến mất" khỏi hàng đợi |
| TD-02 | **Trung bình (rộng hơn)** | Cùng một sự thật khai ở 3–6 nơi | `src/ingest/schemas.py`, `src/quality/gate.py`, `src/integrate/validate.py`, `src/integrate/reconcile.py`, `src/common/kpis.py`, `src/analytics/model.py`, `README.md`, test | Đổi dữ liệu/KPI phải sửa nhiều nơi; định nghĩa doanh thu có 4 chỗ |
| TD-03 | Thấp | Khối rename vô nghĩa trong `clean_products` | `src/clean/products.py` | Mã gây nhiễu |
| TD-04 | Thấp (**đã đóng một phần**) | `MemoryProbe` nay được dùng bởi một test `slow`; `memory_warn_mb` vẫn không nơi nào tiêu thụ | `src/common/memory.py`, `src/config.py:49-50`, `config.yaml:27-28`, `test_u1_stats_end_to_end.py:16,40-49` | Người đọc tưởng có cảnh báo bộ nhớ; chỉ có ngưỡng fail được test dùng |
| TD-05 | Thấp | `src/analytics/filters.py` chỉ re-export `KpiFilters` | `src/analytics/filters.py` (7 dòng) | Lớp trung gian không cần thiết |
| TD-06 | **Trung bình (nặng hơn)** | Import thừa tạo phụ thuộc ngược chiều `integrate → analytics` | `src/integrate/pipeline.py:10`; `ruff.toml:27` miễn trừ | Cản trở tách gói; kéo `scipy`/`scikit-learn` vào đường phụ thuộc của gói mô hình hóa |
| TD-07 | Trung bình | Dashboard: hai output vẽ **cùng** một figure; nút "Thử lại" không có callback; hằng số ma thuật `"2017-01"`; câu "329 đơn" chép tay | `src/dashboard/app.py:530,563-564`, `src/dashboard/components.py:99,108` | Lãng phí tính toán, UI gây hiểu nhầm |
| TD-08 | Thấp | `except Exception` bắt rộng ở biên; hai chỗ nuốt lỗi im lặng | `src/dashboard/app.py:93-94,531-532`, `analysis_tab.py:556-557`, `src/external/ibge.py`, `src/integrate/connections.py:26-29`, `src/pipeline/*` | Lỗi cấu hình bị che thành "không có dữ liệu" |
| TD-09 | **Cao (DX)** | Bộ test `not slow` phụ thuộc `warehouse/olist.duckdb` và `data/marts/` | `tests/unit/test_dashboard_smoke.py:114,121,127,136`, `tests/unit/test_cli.py:20-21` | Máy mới clone không chạy được test nhanh; CI phải dựng dữ liệu trước. **Không** lan sang test mới của đợt này |
| TD-10 | **Đã đóng** | Trước: không lint/CI/ngưỡng phủ | `ruff.toml`, `ci.yml:30-53` | Chỉ còn: format chưa phủ toàn repo, không kiểm tra kiểu (đã chốt) |
| TD-11 | **Trung bình (rõ hơn)** | `STAGES` có **5** tên nhưng `_run_all` ghi **6** `StageResult` và **không chạy `stats`**; `ingest_all` đặt `passed=False` mà pipeline vẫn chạy tiếp | `src/pipeline/stages.py:24` so với `:91-179`, `src/ingest/reader.py` | `--stage all` không sinh báo cáo phân tích; báo cáo tầng khó diễn giải; thêm tầng mới không có chỗ tự nhiên |
| TD-12 | Thấp | Mọi truy vấn doanh thu inner join `v_dim_date`; đơn có `date_key` NULL bị loại khỏi KPI mà không cảnh báo | `src/analytics/service.py:17-18,26,34,128,135,148,163,218,248,282,317` | Chênh lệch KPI khó truy vết nếu timestamp lỗi tăng |
| TD-13 | Thấp | `process_inbox` sao toàn bộ `data/cleaned` sang temp cho từng batch và nạp 9 bảng vào RAM | `src/pipeline/micro_batch.py:127-128,150-157` | Chi phí O(kích thước cleaned) mỗi batch |
| TD-14 | **Đã đóng** | Bốn nhóm kiến thức tích hợp nay có biểu diễn hạng nhất | `src/integration`, `src/linkage`, tab "Tích hợp" | Chi phí chuyển sang bảo trì gói 4.138 dòng (TD-18) |
| TD-15 | Trung bình | Allowlist dị thường là hằng số gắn với đúng phiên bản dữ liệu | `src/quality/allowlist.py:3-13` | Nâng cấp dễ "đỏ" hàng loạt |
| TD-16 | Trung bình | `src/dashboard/app.py` giữ trạng thái toàn cục `_INTEGRATION_RUNS`; test phải gọi `reset_integration_logs()` | `src/dashboard/app.py:50,475-508` | Trạng thái rò giữa các test/lần chạy |
| TD-17 | Trung bình | Đầu ra dashboard là **tuple vị trí 9 phần tử** ở cả hai nhánh; `_tab_config(config)` được gọi hai lần cho một app | `src/dashboard/app.py:216-228,233,469,511-589` | Thêm một output/tab phải sửa 2 chỗ mã + 3 test |
| TD-18 | Trung bình | `src/integration/tab.py` 1.380 dòng; `register_callbacks` gộp **6** callback | `src/integration/tab.py:1301-1380` | Khó đọc/khó test; sửa thẻ rất đắt |
| TD-19 | Thấp (DX) | Bộ test phình to, 7 mô-đun > 470 dòng (lớn nhất 983) | xem §3.4 | Mỗi thay đổi giao diện/hợp đồng phải sửa nhiều tệp lớn |
| TD-20 | Thấp | `ruff format --check` chỉ phủ danh sách khai tay | `ci.yml:35`; `tests/unit/test_ci_config.py:14-29` | Tệp mới quên thêm là không được kiểm format |
| **TD-21** | **Cao cho đợt này** | Baseline quần thể mô hình (96.478 / 7.826) nay là chỗ khai **thứ tư** và là **hằng số grain đơn** cứng: `delivered_population` **từ chối** khung khác, `split_summary` buộc tổng = 96.478 | `src/analytics/model.py:22-23,103-119,159-179`; `src/integrate/reconcile.py:8-14`; `README.md`; 2 test | Đổi đơn vị dự đoán (đơn → dòng hàng) **bắt buộc** sửa cả ba chỗ mã + 2 test, và phải có bộ số mới được đo lại |
| **TD-22** | **Cao cho đợt này** | Danh sách đặc trưng bị khoá hai lớp: (a) `validate_features` buộc **đúng 11** cột; (b) `FORBIDDEN_COLUMNS` cấm `order_delivered_carrier_date` — cột **không tồn tại** trong mart, nhưng lại là mốc của khung "bàn giao cho đơn vị vận chuyển" | `src/analytics/model.py:36-70,87-100`; `src/integrate/facts.py:99-115` (không có cột đó); `test_analytics_model.py:193-219` | Mọi thay đổi đặc trưng phải sửa hằng số + luật + ≥3 test; luật cấm hiện đang cấm một cột không thể xuất hiện, tức là **không** bảo vệ được gì nhưng vẫn chặn ý định mới |
| **TD-23** | **Cao cho đợt này** | Tab phân tích bị khai là **chỉ đọc** ở ba nơi: câu chữ `TEXTS["model_caption"]`, test `test_model_block_offers_no_input_control`, README mục Dashboard | `src/dashboard/analysis_tab.py:58,419-446`; `test_dashboard_analysis_tab.py:456-463`; `README.md:101-105` | Thêm vùng **nhập liệu** dự đoán là thay đổi có chủ đích phải sửa cả ba; nếu không, test đỏ và tài liệu nói sai |
| **TD-24** | Trung bình | Hợp đồng báo cáo cứng: `version: 2`, `ModelBlock` đúng **7 trường**, `_model_block` **từ chối** tệp thiếu trường; không có chỗ "mở" cho số liệu mới (baseline AUC, AUC của cây, hệ số mô hình) ngoài túi `counts` | `src/analytics/report.py:15,190-211,457-468,491-502` | Mọi số liệu mới phải nằm trong `counts` (không kiểu, không tài liệu) hoặc **tăng phiên bản** (mọi reader + 3 test phải theo) |
| **TD-25** | Trung bình | Không có chỗ lưu mô hình: `AppConfig` 34 trường không có thư mục mô hình, `src/` không import `joblib`/`pickle`, `.gitignore` không có `data/models/`, `requirements.txt` không khai cách tuần tự hóa | `src/config.py:15-52`; `requirements.txt`; `.gitignore` | "Lưu mô hình" là thay đổi cấu hình + phụ thuộc + tài liệu, không phải một dòng `dump` |
| **TD-26** | Thấp | Tab phân tích phụ thuộc chéo vào lớp tích hợp: lấy `STATE_ICONS` và `TEXTS` từ `src/integration/card.py` để đồng bộ nhãn trạng thái | `src/dashboard/analysis_tab.py:27,151-158`; `src/integration/card.py` | Đổi nhãn/icon của tab "Tích hợp" làm đổi tab phân tích; hai tab không còn độc lập như ADR tuyên bố |
| **TD-27** | Thấp | Chín `# noqa` với mã **không** nằm trong `select` của `ruff.toml` (`BLE001`, `ANN001`) → ghi chú không tác dụng, nhưng tạo tiền lệ tắt cảnh báo tại chỗ | `analysis_tab.py:556,565`; `integration/tab.py:1295,1325,1335,1350,1361,1375`; `card.py:333`; `rewrite.py:750` | Nếu sau này bật thêm luật, chúng thành ngoại lệ thật; hiện là nhiễu |

## 7. Rủi ro cho đợt nâng cấp (intent `261111-model-feature-improvemen`)

Intent hiện tại: **cải thiện đặc trưng cho mô hình dự đoán đơn trễ** — đổi **khung dự đoán** (từ lúc đặt đơn
sang lúc bàn giao cho đơn vị vận chuyển), đổi **đơn vị dự đoán** (từ đơn sang dòng hàng), thêm đặc trưng, lưu
mô hình, và thêm **vùng nhập liệu dự đoán** vào tab thứ năm. Ba hạng mục U1/U2/U3 trong
`ideation/scope-definition/scope-document.md`. Các điểm chạm đã biết:

### 7.1 Hình dạng dashboard/CLI là hợp đồng cứng

Thêm tab/output/lệnh sẽ **làm fail** các test đang khẳng định số lượng:

- `tests/unit/test_dashboard_smoke.py:57` → `len(tabs.children) == 5`; `:62` → `len(app.callback_map) == 9`;
  `:115,131` → `len(outputs) == 9`; `:49-51` tra tab **theo value** (không theo vị trí — ràng buộc
  `children[-1]` của lần trước **đã bị bỏ**, xem ghi chú trong `_tab`).
- `tests/integration/test_u3_end_to_end.py:83` → 9 callback; `:87` → 5 tab; `:88` → `{"tich-hop",
  TAB_VALUE} <= values`.
- `tests/unit/test_integration_tab.py:938` → **6** callback của riêng tab "Tích hợp".
- `tests/unit/test_pipeline_stages.py:134-135,149-161` → 5 tên tầng, `choices` khớp `STAGES|{"all"}`,
  **3** lệnh con.
- `tests/unit/test_dashboard_analysis_tab.py:293-300,456-463` → **4** thẻ tóm tắt đúng thứ tự, và khối mô hình
  **không** có `Slider`/`Input`/`RangeSlider`.

Đây là **thay đổi có chủ đích** nhưng phải cập nhật test cùng lúc. Riêng ràng buộc "khối mô hình không có ô
nhập" **mâu thuẫn trực tiếp** với hạng mục U3 (vùng nhập liệu dự đoán) — xem TD-23.

### 7.2 Khung dự đoán mới cần dữ liệu mà mart **chưa** mang

| Hạng mục (scope) | Hiện trạng trong mã | Việc phải làm trước khi code |
|---|---|---|
| U1 — thêm 2 cột mốc vào `v_fact_orders` | `FactBuilder.build_orders` trả **13 cột**, không có `order_delivered_carrier_date`/`order_approved_at` (`facts.py:99-115`) | Sửa danh sách cột trong builder; cập nhật `docs/data-dictionary.md`; **không** đổi số dòng nên `StarSchemaValidator.EXPECTED` giữ nguyên; `VIEW_TABLES` vẫn 11 |
| U1 — thêm `seller_state` vào `v_fact_order_items` | `build_order_items` trả **12 cột** có `seller_id`, không có `seller_state` (`facts.py:27-42`); `shipping_limit_date` bị làm rơi | Hoặc join `dim_seller` ở truy vấn (không cần đổi builder), hoặc denormalize vào fact (phải sửa builder + tài liệu). Hai lựa chọn cho **kết quả khác nhau** về số cột và về chi phí join |
| U1 — truy vấn quần thể grain **dòng hàng** | `TRAINING_FRAME_SQL` gộp về grain **đơn** (`service.py:38-74`); `training_frame()` ném lỗi khi `order_id` lặp | Viết truy vấn mới hoặc tham số hóa; quyết định grain của **nhãn** (`is_late` là thuộc tính của **đơn**, không của dòng hàng — mọi dòng của một đơn chia sẻ nhãn, nên "96.478 / 7.826" không còn là mẫu số đúng) |
| U1 — đo baseline `customer_state` | Không có baseline này trong mã | Cần một chỗ ghi số đo lại (record) **và** một test tái lập được |
| U2 — đặc trưng từ khung bàn giao | `FEATURES` 11 tên + `validate_features` buộc đúng 11 + `FORBIDDEN_COLUMNS` cấm `order_delivered_carrier_date` | Sửa cả ba (TD-22); nếu mốc bàn giao trở thành **mốc quan sát** thì cột đó phải **rời** danh sách cấm và các cột "sau bàn giao" mới là cấm |
| U2 — logistic (triển khai) + `HistGradientBoosting` (báo cáo) | `build_estimator` chỉ tạo `LogisticRegression`; `ModelBlock` chỉ có 4 chỉ số | Thêm estimator thứ hai **chỉ để báo cáo**; chỗ chứa số của nó là `counts` (TD-24) hoặc phiên bản mới |
| U2 — lưu mô hình vào `data/models/` + JSON mô tả | Không có `models_dir`, không serializer, không `.gitignore` | Thêm trường `AppConfig` + tạo thư mục + chọn cách tuần tự hóa (TD-25). **Lưu ý**: `.gitignore` hiện chặn `data/` nên `data/models/` sẽ không được commit — cần quyết định có chủ đích |
| U3 — vùng nhập liệu trên tab 5 | Tab khai "chỉ đọc" ở 3 nơi; không có callback thứ hai cho tab | Thêm callback/output ⇒ số callback 9 → 10 và số output của tab; phải sửa TD-23 + đếm lại ở 3 test |
| U3 — mốc sàn 0,55 trong CI | CI chỉ có ngưỡng **phủ** 80%, không có mốc AUC | Thêm bước kiểm AUC từ `analysis.json`; `tests/unit/test_ci_config.py:98-101` đang canh "cổng phủ không bị hạ" — thêm bước mới phải **giữ** cổng đó |

### 7.3 Rủi ro dữ liệu, rò rỉ và hồi quy

1. **Rò rỉ đặc trưng (leakage) — rủi ro lớn nhất, và định nghĩa vừa đổi.** Khung cũ dự đoán **tại lúc đặt
   đơn**, nên ba cột `order_delivered_customer_date`, `delivery_days`, `is_late` bị cấm. Khung mới dự đoán
   **tại lúc bàn giao cho đơn vị vận chuyển**, nên `order_delivered_carrier_date` trở thành **hợp lệ** (mốc
   quan sát) trong khi `order_delivered_customer_date`, `delivery_days`, `is_late`, `has_review`, review phải
   tiếp tục bị cấm. Danh sách cấm hiện tại **không** diễn đạt được sự phân biệt này (nó cấm cả mốc bàn giao).
2. **`order_estimated_delivery_date` là đặc trưng hợp lệ nhưng chưa được dùng**: cột có trong
   `v_fact_orders` mà `TRAINING_FRAME_SQL` không chọn. Đây là ứng viên mạnh nhất cho khung mới — và **không**
   phải rò rỉ ở cả hai khung.
3. **`shipping_limit_date` bị làm rơi ở mart** dù có trong cleaned: nếu khung mới cần "hạn giao cho đơn vị
   vận chuyển", nó chỉ tiếp cận được qua `data/cleaned/` (một đường đọc thứ ba hiện **chưa** có) hoặc phải
   thêm vào fact.
4. **Nhãn là thuộc tính của đơn, không của dòng hàng.** Ở grain dòng hàng, mọi dòng của cùng một đơn có cùng
   `is_late`; nếu chia tập theo ngày thì **không** có rò rỉ chéo tập, nhưng nếu tính AUC trên dòng hàng thì
   con số **không so được** với AUC 0,5133 hiện tại (mẫu số khác, trọng số khác). Baseline so sánh phải được
   đo lại trong đúng khung/đơn vị — chính là U1 của scope.
5. **Chia theo thời gian là đúng hướng nhưng mốc cắt đang gắn với grain đơn**: `SPLIT_DATE = "2018-04-01"`,
   đơn rơi đúng ngày cắt thuộc tập kiểm tra (`model.py:140-156`). Nếu khung mới dùng ngày bàn giao thay ngày
   đặt, `date_key` của mart là **ngày đặt** — phải quyết định cắt theo ngày nào.
6. **Allowlist và KPI là hợp đồng cứng** (TD-15, TD-02): mọi thay đổi cleaning sẽ làm `quality full` hoặc
   `KpiReconciler` fail. Thêm **cột** thì an toàn (không đổi số dòng), nhưng thay đổi **lọc** thì không.
7. **Số view = 11** bị khẳng định trong `tests/integration/test_u2_end_to_end.py:44`. Thêm **cột** thì an toàn;
   thêm **view** thì phải sửa `VIEW_TABLES` + test + `docs/data-dictionary.md`.
8. **Ngân sách thời gian đã thành test**: 300 s cho tầng `stats` (`test_u1_stats_end_to_end.py:22,48`) và
   900 s cho tầng + 900 s cho riêng bước mô hình (`test_u2_model_end_to_end.py:31-32,50,93`). Mô hình thứ hai
   (`HistGradientBoosting`) và khung grain dòng hàng (≈112.650 dòng thay vì 96.478) đẩy thời gian lên.
9. **Tính lặp lại đã thành test**: hai lần huấn luyện phải cho cùng bốn chỉ số đã làm tròn
   (`test_u2_model_end_to_end.py:95`). Mọi yếu tố ngẫu nhiên mới (`random_state`, thứ tự one-hot, chia tập)
   phải cố định.
10. **`TD-09`**: thay đổi dashboard cần chạy được bộ nhanh; bộ nhanh cần mart đã dựng sẵn. 5 test mới dựng
    mart trong `tmp_path` là mẫu nên theo.
11. **`TD-16`**: nếu callback mới dùng log, hãy đi qua `_integration_logger`/`reset_integration_logs` thay vì
    thêm cache toàn cục thứ hai.
12. **`TD-26`**: tab 5 đang mượn `STATE_ICONS`/`TEXTS` của `src/integration/card.py`; thêm vùng nhập liệu là
    dịp tốt để tách hai bảng nhãn đó ra khỏi lớp tích hợp.

## 8. Khuyến nghị ưu tiên

1. **Chốt định nghĩa "khung dự đoán" bằng một bảng đặc trưng có tài liệu** (mốc quan sát, cột hợp lệ, cột cấm,
   grain của nhãn) **trước** khi viết mã, và ghi nó vào `docs/` để test kiểm được. Đây là thứ đang bị khoá
   bởi `FORBIDDEN_COLUMNS` + luật "đúng 11 cột" (TD-22).
2. **Tách hằng số baseline của mô hình khỏi baseline KPI** (TD-21): một khung/đơn vị mới cần bộ ba số riêng
   (số dòng, số nhãn dương, mốc cắt). Đừng sửa `reconcile.BASELINE`.
3. **Đo baseline `customer_state` trước khi huấn luyện mô hình mới** (U1 của scope) — không có mốc so thì mọi
   con số sau đều vô nghĩa.
4. **Làm rõ nghĩa vụ "chỉ đọc" của tab 5** (TD-23): hoặc chấp nhận vùng nhập liệu là **dự đoán** (không phải
   đọc báo cáo) và đặt nó ở section riêng với câu chữ riêng, hoặc đặt vùng nhập liệu ở một tab khác. Sửa
   `TEXTS["model_caption"]`, `test_model_block_offers_no_input_control` (đổi thành "khối **kết quả** mô hình
   không có ô nhập") và `README.md:101-105` trong **cùng** thay đổi.
5. **Chốt cách chứa số liệu mới trong báo cáo** (TD-24): thêm khoá vào `counts` (nhanh, không kiểu) hay tăng
   `REPORT_VERSION` lên 3 (đúng, nhưng 3 test + tab phải theo). Đừng để mỗi đơn vị tự chọn.
6. **Chốt cách lưu mô hình** (TD-25) kèm quyết định `.gitignore`: `data/` đang bị chặn nên `data/models/`
   sẽ **không** được commit — nếu mô hình cần tái lập được từ repo thì phải ghi cả `scikit-learn` version
   và seed vào tệp mô tả.
7. **Sửa `TD-11` khi chạm `stages.py`**: quyết định `stats` có nằm trong `--stage all` hay không (hiện
   `STAGES` nói có, `_run_all` nói không) — đợt này sẽ sửa tầng `stats` nên đây là dịp rẻ nhất.
8. **Sửa `TD-01`/`TD-06` khi có dịp chạm** — rẻ, giảm nhiễu.
9. **Thêm tệp mới vào danh sách `ruff format --check` trong `ci.yml` cùng lúc với việc tạo tệp** (TD-20), và
   thêm tệp đó vào `NEW_FILES` của `test_ci_config.py` để lần sau không quên.
