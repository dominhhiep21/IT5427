# Code Summary — u1-statistics

Nguồn: `code-generation-plan.md` (đã duyệt), `unit-test-instructions.md`, `../functional-design/*`, `../nfr-design/*`, `../infrastructure-design/cicd-pipeline.md`, `aidlc/spaces/default/memory/project.md`.

## Đã dựng gì

| # | Tệp | Nội dung |
|---|---|---|
| S1 | `src/analytics/report.py` (mới, 474 dòng) | `REPORT_VERSION = 2`; kiểu C1/C2 `SkipEntry`, `ProportionResult`, `ComparisonResult`, `CorrelationResult`, `GroupTestResult`, `SeasonalResult`, `StatsBlock`, `ModelBlock`, `AnalysisReport`, `ReportView`; `report_path(config)` lấy từ `AppConfig.reports_dir` (SEC-5); `write_report(config, report, writer=None)` ghi tệp tạm → `_verify_pending()` → `os.replace` (BR1.11); `read_report(path)` bốn trạng thái theo thứ tự tồn tại → parse → phiên bản → trường → khối (BR1.9, BR1.10). Làm tròn 4 chữ số, hệ số tương quan 3 chữ số, **chỉ trong `to_dict()`** (BR1.8). |
| S2 | `src/analytics/statistics.py` (mới, 313 dòng) | `ALPHA`/`confidence_for` (BR1.7); `wilson_interval` + `late_rate` (BR1.1); `compare_states` — ngưỡng 100 đơn, z gộp, p hai phía, khoảng Newcombe, `excluded` (BR1.2); `price_freight_correlation` — Fisher (BR1.3); `region_late_test` — ô kỳ vọng ≥ 5, `dof = số vùng - 1` (BR1.4); `seasonal_decomposition` — trục tháng liên tục, điền 0, rolling giữa có cửa sổ thu hẹp, `method = classical_additive_12`, `revenue_definition = REVENUE_DEFINITION` (BR1.5); `ordered_skips` + `collect_stats` gom `skipped` không trùng tên (BR1.6); `build_analysis_report` giữ khối `model` cũ và cảnh báo khi tệp cũ hỏng (BR1.11 note). |
| S3 | `src/analytics/service.py` (sửa) | Thêm `late_rates_by_state`, `late_rates_by_region`, `price_freight_pairs` dùng lại `_connect`/`_where`, trả DataFrame đã gộp ở SQL; ba hằng SQL và `MAX_CORRELATION_ROWS = 200_000`. Năm phương thức cũ **không đổi chữ ký**. |
| S4 | `src/pipeline/stages.py` (sửa) | `STAGES = ("ingest", "clean", "integrate", "analyze", "stats")`; nhánh `stats` trong `run_stage` gọi `build_analysis_report` → `write_report` và ghi sự kiện `stats_report_written`. |
| S5 | `src/pipeline/cli.py` (sửa) | `"stats"` vào `choices` của `--stage`; vẫn **3 lệnh con**. |
| S6 | `requirements.txt` (sửa) | `scipy==1.15.2` kèm lý do (phân phối chuẩn tắc cho Wilson/Newcombe/Fisher, chi bình phương cho vùng × trễ); **không** thêm `statsmodels`. `numpy` không bị nâng (vẫn 2.2.1, khớp `pandas 2.2.3`) nên không phải ghim lại. |
| S7 | `.github/workflows/ci.yml` (sửa) | `feature/analysis-and-models` vào **cả** `on.push.branches` và `on.pull_request.branches`; hai mô-đun mới + bốn tệp test mới + test end-to-end vào danh sách `ruff format --check`; bước `run --stage stats` đặt **sau** `--stage all` và **trước** bước test. |
| S8 | `README.md` (sửa) | Mục chạy pipeline thêm tầng `stats` kèm định nghĩa doanh thu; mục **Test** nêu bộ nhanh/bộ chậm và lệnh phủ 80%; mục **CI** khớp `ci.yml` (chín bước, cổng phủ tính trên toàn bộ bộ test). |
| S9 | `CHANGELOG.md` (sửa) | Mốc `v0.2.0 — 2026-11-10` theo ba nhóm **Thêm / Sửa / Nội bộ**. |
| S10 | `tests/unit/test_analytics_report.py` (mới) | Mười bảy ca: `rong`, JSON hỏng, JSON không phải đối tượng, `version = 1` (kiểm trước nhánh thiếu trường), thiếu trường, sai kiểu, `observed` lệch độ dài, `mot-phan` thiếu `model`, `mot-phan` thiếu `stats`, `day-du`, ghi rồi đọc, làm tròn, ghi không truyền writer, ghi thiếu cả hai khối, ghi hỏng giữa chừng (tệp cũ còn nguyên, không để tệp tạm), `_verify_pending` từ chối sai phiên bản, `report_path` lấy từ `AppConfig`. |
| S11 | `tests/unit/test_analytics_statistics.py` (mới) | Hai mươi lăm ca cho BR1.1–BR1.8 (kể cả `n = 3`, chuỗi không đổi, ô kỳ vọng dưới 5, dưới 24 tháng, hằng đẳng thức mùa vụ trên giá trị chưa làm tròn), `collect_stats` với service đầy đủ và service rỗng, và ba phương thức đọc mới trên DuckDB tạm + ca khẳng định SQL chỉ chạm view trong `VIEW_TABLES`. |
| S12 | `tests/unit/test_pipeline_stages.py` (mới) | `STAGES` và `choices` cùng có `stats`, CLI vẫn 3 lệnh con, `run_stage` từ chối tên lạ, `run --stage stats` thật trên mart tạm (5 phép đủ), giữ khối `model`, cảnh báo khi tệp cũ hỏng. |
| S13 | `tests/unit/test_ci_config.py` (mới) | `ci.yml` có nhánh trong cả hai danh sách, giữ nhánh cũ, mọi tệp mới có trong danh sách `ruff format --check`, danh sách không trỏ ra ngoài repo, thứ tự `all` → `stats` → test, cổng phủ không bị hạ. |
| S14 | `tests/integration/test_u1_stats_end_to_end.py` (mới, `slow`) | Dựng lại mart từ `dataset/` trong thư mục tạm rồi chạy `run_stage(..., "stats")`: dưới 300 giây (NFR1.1), đỉnh bộ nhớ dưới `memory_fail_mb` (NFR1.3), mỗi phép đọc dưới 60 giây (NFR1.2), số nhóm theo chiều bang/tháng (NFR1.7), 5 KPI baseline không đổi (NFR3.1), tệp đúng phiên bản và `mot-phan` thiếu `model`, mọi khẳng định BR1.1–BR1.5 trên dữ liệu thật, và hai lần chạy cho cùng nội dung sau khi bỏ `generated_at` (NFR3.4). |

Tệp không bị chạm: `dataset/**`, `config/*.yaml`, `src/dashboard/**`, `src/integrate/**`, `pytest.ini`, `ruff.toml`.

## Kiểm chứng (chạy thật, dán nguyên văn)

### 1. Bộ nhanh

```
python -X utf8 -m pytest -m "not slow"
438 passed, 10 deselected in 13.82s
```

### 2. `ruff check` và `ruff format --check` trên tệp đã chạm

```
python -X utf8 -m ruff check .
All checks passed!

python -X utf8 -m ruff format --check src/analytics/report.py src/analytics/statistics.py
      src/analytics/service.py src/pipeline/stages.py src/pipeline/cli.py
      tests/unit/test_analytics_report.py tests/unit/test_analytics_statistics.py
      tests/unit/test_pipeline_stages.py tests/unit/test_ci_config.py
      tests/integration/test_u1_stats_end_to_end.py
10 files already formatted
```

### 3. Cổng phủ trên toàn bộ bộ test (nhanh + `slow`)

```
python -X utf8 -m pytest --cov=src --cov-fail-under=80 --cov-report=term
src\analytics\report.py          232      6    97%
src\analytics\service.py         142      6    96%
src\analytics\statistics.py      137      0   100%
TOTAL                           4266    349    92%
Required test coverage of 80% reached. Total coverage: 91.82%
======================= 448 passed in 285.94s (0:04:45) =======================
```

**Số phủ: 91,82%** (ngưỡng 80% không bị hạ, đo trên cả bộ `slow` đúng như `ci.yml`).

### 4. Chuỗi bốn bước của nhóm trên workspace thật

```
python -X utf8 -m src.pipeline run --stage all
  ingest: success rows_in=1550922 rows_out=1550922 3.93s
  clean: success rows_in=1550922 rows_out=569774 4.48s
  quality: success rows_in=569774 rows_out=569774 0.6s
  integrate: success rows_in=0 rows_out=0 3.66s
  linkage: success rows_in=0 rows_out=0 4.0s
  analyze: success rows_in=0 rows_out=0 0.29s

python -X utf8 -m src.pipeline run --stage stats
run=20261110T144636-9847faf5 stage=stats success=True
  stats: success rows_in=0 rows_out=0 0.92s
```

Bước 4 (mở dashboard) chưa chạy: `--stage stats` chỉ mới ghi tệp báo cáo, còn vùng hiển thị thuộc U3 — chưa có tab nào đọc tệp này ở thời điểm này.

### 5. Nội dung tệp báo cáo sinh trên dữ liệu thật

```
version 2 model None
alpha/conf 0.05 0.95
late_rate {'successes': 7826, 'total': 96478, 'rate': 0.0811, 'ci_low': 0.0794, 'ci_high': 0.0829}
comparison AL RO p_value 0.0 significant True excluded 188
corr {'r': 0.413, 'n': 110197, 'ci_low': 0.4078, 'ci_high': 0.4176}
group {'test': 'chi_square_region_late', 'statistic': 535.9163, 'p_value': 0.0, 'dof': 4, 'min_expected': 145.686}
seasonal months 24 2016-09 2018-08
skipped []
```

Tổng doanh thu trên trục mùa vụ khớp baseline 15.419.773,75 BRL (khẳng định trong test `slow`), nên việc BR1.5 đọc qua `revenue_by_period` thay vì `v_agg_sales_daily` không làm lệch doanh thu.

## Chưa xong, và vì sao

| Hạng mục | Trạng thái | Lý do |
|---|---|---|
| NFR1.4 (chi phí phân rã mùa vụ tuyến tính) | **GAP** | `seasonal_decomposition` dùng một lượt `Series.rolling(center=True, min_periods=1)` nên chi phí tuyến tính theo số tháng (PD-4), nhưng chưa có test so thời gian trên hai chuỗi dài khác nhau như yêu cầu. Một test đo thời gian trong bộ nhanh sẽ chập chờn; chưa dựng nó. |
| NFR1.5 (dữ liệu vào 5 lần vẫn dưới 5 phút) | **GAP** | `dataset/` là bất biến và chỉ có một cỡ, không có dữ liệu 500.000 đơn để đo. Yêu cầu này vốn là một giả định. |
| NFR1.6 (bộ nhớ đỉnh tuyến tính theo số dòng) | **GAP** | Chưa có test `tracemalloc` trên bản sao dữ liệu nhân đôi. Lưu ý: tầng `stats` chỉ kéo dòng thô ở `price_freight_pairs` và có chặn `MAX_CORRELATION_ROWS = 200_000`, phần còn lại gộp ở SQL, nên bộ nhớ không tỉ lệ với số dòng — nhưng đó là lập luận thiết kế, không phải bằng chứng đo. |
| Bước 4 của chuỗi xác nhận (mở dashboard) | Không chạy | Vùng hiển thị báo cáo thuộc U3; chưa có tab đọc `data/reports/analysis.json`. |

Ba mục GAP ở trên đã ghi đúng trạng thái trong `traceability.json` (sensor `traceability` báo `pass: false` với `gaps = ["NFR1.4","NFR1.5","NFR1.6"]`; sensor có `default_severity: advisory`).

## Sai khác so với kế hoạch (và lý do)

1. **`write_report` nhận `config` chứ không nhận `path`.** C1 trong `contract-summary.md` khai `write_report(report, path) -> None`; đặc tả NFR (SEC-5) lại buộc đường dẫn lấy từ `AppConfig.reports_dir` và cấm nhận từ dòng lệnh. Chữ ký đã dựng là `write_report(config, report, writer=None) -> Path`. U2 khi ghi khối `model` cần dùng chữ ký này; nếu U2 muốn đúng C1 thì phải nâng phiên bản hợp đồng hoặc thêm một lớp bọc mỏng. Đã ghi ở đây để không phát hiện muộn.
2. **BR1.5 đọc doanh thu qua `revenue_by_period` (mart `v_fact_order_items`), không qua `v_agg_sales_daily`.** `rules.md` BR1.5 ghi nguồn là `v_agg_sales_daily`; `nfr-design/performance-design.md` PD-3 lại chốt dùng lại `revenue_by_period`. Bản dựng theo PD-3 (và theo S3 của kế hoạch: chỉ thêm ba phương thức). Tổng doanh thu khớp baseline từng xu nên hai đường là tương đương trên dữ liệu thật.
3. **`price_freight_pairs` chỉ lấy dòng hàng của đơn `delivered`.** `rules.md` BR1.3 chỉ nêu điều kiện "giá và phí khác null". Phương thức dùng `_where(..., status_column="f.order_status")` nên bộ lọc trạng thái tường minh của `KpiFilters` được áp dụng, đúng quy tắc dự án "lọc trạng thái đơn một cách tường minh cho mọi phân tích doanh thu/giao vận"; hệ quả là `n = 110.197` thay vì 112.650 dòng hàng. Đã ghi rõ trong test end-to-end.
4. **`src/analytics/service.py` và `src/pipeline/cli.py` được format lại toàn tệp.** Hai tệp vốn chưa sạch `ruff format`; vì đơn vị này sửa chúng nên chúng được dọn theo đúng thực hành "mã cũ dọn theo từng tệp khi có người sửa tới". Không thêm ngoại lệ nào vào `ruff.toml`. Hai tệp **không** được thêm vào danh sách `ruff format --check` của `ci.yml` (kế hoạch S7 chỉ yêu cầu tệp mới).
5. **Không tick được ô nào trong kế hoạch.** `code-generation-plan.md` đã duyệt không có bước nào ở dạng `- [ ]`; thứ tự thi công là danh sách số 1–7. Tệp kế hoạch được giữ nguyên, không sửa một chữ.

## Ghi chú vận hành

- `run --stage stats` phải chạy **sau** `--stage all` (cần `data/marts/` và `warehouse/olist.duckdb`); `ci.yml` đặt đúng thứ tự và `test_ci_config.py` khẳng định thứ tự đó.
- Tệp báo cáo ghi ra là `data/reports/analysis.json` (bị `.gitignore`); không test nào đọc tệp này của repo — mọi test tự dựng dữ liệu trong `tmp_path` (tránh lỗ hổng `TD-09`).
