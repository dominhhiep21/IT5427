# Code Summary — u3-display

Đơn vị: `u3-display`. Intent: `261109-stats-and-models`. Giai đoạn: Construction / Code Generation.
Kế hoạch đã duyệt: `code-generation-plan.md` (sha256 `c4202e8d…`), hợp đồng kiểm thử
`sha256:c6029e50…`. Kế hoạch được thi công nguyên văn, không viết lại; sáu điểm lệch (đều là lựa chọn thi
công, không phải thay đổi phạm vi) được nêu ở § "Sai lệch so với kế hoạch".

Nguồn: `../functional-design/{functional-spec.md,rules.md,entities.md}`, `../nfr-design/*`,
`../infrastructure-design/*`, và `../../../inception/units-generation/unit-of-work.md` — bản ghi này của
`units-generation` giao U3 một "bộ chọn ngưỡng"; `functional-design-questions.md` (Q1 = A) bỏ hạng mục đó
vì hợp đồng C3 chỉ mang một ngưỡng đã chọn sẵn, nên đơn vị này **không** dựng thanh trượt nào.

## Đã dựng gì

Tab thứ năm **Kết quả phân tích** của dashboard: đọc `data/reports/analysis.json` bằng `read_report`
(U1) **trong callback** rồi dựng dải tóm tắt bốn thẻ, mục thống kê năm phép kiểm định, dải `skipped`
và mục mô hình chỉ đọc. Tab **không tính toán gì**: mọi con số đến từ tệp báo cáo; không ghi tệp, không
chạm `dataset/`, `src/analytics/**`, `src/integrate/**`, `config/*.yaml`.

| # | Tệp | Việc đã làm |
|---|---|---|
| S1 | `src/dashboard/analysis_tab.py` **(mới)** | Tám thành phần của `logical-components.md`: `tab-callback` (`render_analysis`, `register_callback`), `loading-shell` (`AnalysisTab` + `custom_spinner`), `state-mapper` (`pending_state`, `state_for`), `summary-strip` (`summary_cards`, `build_summary_section`, `_auc_note`), `stats-section` (`build_stats_items` + bốn hàm mục), `skipped-banner` (`build_skipped_banner`), `model-section` (`build_model_section`, `_model_figures`), `formatter` (nhân 100 cho `late_rate.rate`) |
| S2 | `src/dashboard/app.py` | Thêm tab thứ năm (`AnalysisTab()`) sau tab "Tích hợp" trong `build_layout`; nối một callback trong `create_app` qua `register_analysis_callback` |
| S3 | `assets/style.css` | **Đã sửa** — thêm khối `.analysis-tab` đặt `--text-2` cho sáu lớp chữ nhỏ và hai nhánh huy hiệu `chua-chay`/`rong` (NFR5.1). Không thêm token mới |
| S4 | `tests/unit/test_dashboard_analysis_tab.py` **(mới)** | 37 test: mỗi BR một ca, năm trạng thái, bốn thẻ, thứ tự, nhãn, `skipped`, mục null, đọc một lần, `MantineProvider`, và ca định dạng `8,11%` |
| S5 | `tests/unit/test_dashboard_smoke.py` | 4 tab → 5 tab, 8 callback → 9, **output giữ nguyên 9**; thay ba chỗ `tabs.children[-1]` bằng `_tab(tabs, value)` tra theo giá trị |
| S6 | `tests/integration/test_u3_end_to_end.py` | Số callback 8 → 9, số tab 5; **thêm ca `slow` thứ hai** `test_u3_analysis_tab_renders_the_real_report` chạy `--stage stats` rồi dựng tab từ báo cáo thật |
| S7 | `.github/workflows/ci.yml` | `src/dashboard/analysis_tab.py` **và** `tests/unit/test_dashboard_analysis_tab.py` vào danh sách `ruff format --check` |
| S8 | `tests/unit/test_ci_config.py` | Hai tệp trên vào tuple `NEW_FILES` |
| S9 | `README.md`, `CHANGELOG.md` | README: mục **Dashboard** (4 tab → 5 tab, thêm mô tả tab mới) và mục **Test** (ba test `slow`); CHANGELOG: mốc `v0.4.0 — 2026-11-11` |

## Kiểm chứng (output dán nguyên văn)

**Ruff check toàn repo** — `python -X utf8 -m ruff check .`:

```
All checks passed!
```

**ruff format --check** trên sáu tệp đã chạm:

```
6 files already formatted
```

**Bộ nhanh** — `python -X utf8 -m pytest -m "not slow"`:

```
522 passed, 12 deselected in 16.50s
```

**Toàn bộ bộ test kèm cổng phủ 80%** — `python -X utf8 -m pytest --cov=src --cov-fail-under=80 --cov-report=term`:

```
src\dashboard\analysis_tab.py     171      1    99%
src\dashboard\app.py              135     10    93%
src\dashboard\components.py        19      0   100%
src\dashboard\formatting.py        25      4    84%
TOTAL                            4634    350    92%
Required test coverage of 80% reached. Total coverage: 92.45%
======================= 534 passed in 278.43s (0:04:38) =======================
```

**Chuỗi xác nhận bốn bước** (`## Deployment` trong `team.md`):

```
$ python -X utf8 -m src.pipeline run --stage all
run=20261111T070054-f384df14 success=True stages=['ingest', 'clean', 'quality', 'integrate', 'linkage', 'analyze']
  ingest: success rows_in=1550922 rows_out=1550922 3.75s
  clean: success rows_in=1550922 rows_out=569774 3.86s
  quality: success rows_in=569774 rows_out=569774 0.36s
  integrate: success rows_in=0 rows_out=0 2.86s
  linkage: success rows_in=0 rows_out=0 3.41s
  analyze: success rows_in=0 rows_out=0 0.29s

$ python -X utf8 -m src.pipeline run --stage stats
run=20261111T070225-fed17dab stage=stats success=True
  stats: success rows_in=0 rows_out=0 2.02s
```

**Hai test `slow` của U3** — `python -X utf8 -m pytest tests/integration/test_u3_end_to_end.py -q`:

```
2 passed in 36.29s
```

## Xem bằng mắt ở 1280px (bước 4, kết quả thật)

Dashboard chạy bằng `python -X utf8 -m src.dashboard` (bind `127.0.0.1:8050`), cửa sổ đặt đúng
**1280 × 900**, bấm tab "Kết quả phân tích" và đọc trên dữ liệu thật (`data/reports/analysis.json`
vừa sinh lại ở bước 3). Kết quả:

- Tab thứ năm hiện đúng ở cuối thanh tab, không có tab nào bị đẩy khỏi màn hình:
  `["Tổng quan", "Danh mục", "Giao vận", "Tích hợp", "Kết quả phân tích"]`.
- Nội dung dựng đủ ba khối theo thứ tự tóm tắt → thống kê → mô hình; dải tóm tắt bốn thẻ một hàng
  (`8,11%` · `96.478` · `0` · `0,5133` kèm "không đạt mốc 0,70"); mục thống kê năm mục một cột; mục mô
  hình bốn số đọc cộng bốn viên nhãn (`Đích: is_late`, cỡ mẫu hai tập, `Đã gắn cờ: 5.910 đơn`).
- **Không tràn ngang**: `documentElement.scrollWidth == clientWidth == 1265`, `horizontalOverflow: false`.
- **Không cắt chữ**: quét `.chart-card`, `.chart-subtitle`, `.kpi-card`, `.integration-total`,
  `.integration-detail` → `clipped: []`. Phụ đề dài nhất ("Bốn chỉ số đọc từ báo cáo, không tính lại
  trong trình duyệt") kết thúc ở 1216 px trong khi thẻ kết thúc ở 1233 px, tức còn nằm trong thẻ.
- **Không có phần tử tương tác** trong tab: `interactiveCount: 0` cho
  `a, button, input, select, textarea, [tabindex]` — khớp BR3.7/NFR5.3.
- Vùng có nhãn: `ariaRegions: ["Tóm tắt", "Thống kê", "Mô hình"]` và có `role="status"`.
- Console trình duyệt: chỉ hai cảnh báo có sẵn của **thanh lọc** ở đầu trang ("No label associated with a
  form field", 5 chỗ; "A form field element should have an id or name attribute", 4 chỗ). Tab mới không
  thêm cảnh báo nào và không có lỗi Dash.
- **Ngân sách NFR5.5**: đo 20 lần đọc tính bằng `render_analysis` trên tệp báo cáo thật —
  `median_ms=1.06 max_ms=2.97`, dưới mốc 1 s rất xa.

Sau khi xem xong, dashboard đã được đóng (giải phóng khoá `warehouse/olist.duckdb`).

## Độ phủ

92,45 % toàn bộ `src/` (cổng 80 % đạt, không hạ ngưỡng). Riêng phần mới: **`src/dashboard/analysis_tab.py`
99 %** (171 câu lệnh, 1 chưa phủ là dòng 564 — thân hàm callback bên trong `register_callback`, chỉ chạy
khi Dash phục vụ một request thật trong trình duyệt; đường mã tương đương được phủ bởi
`render_analysis` mà callback gọi). `src/dashboard/app.py` 93 %; mười câu lệnh chưa phủ
(`93-94, 169-179, 221-222, 441, 465`) đều là nhánh cũ có từ trước (`_options` khi không có warehouse,
`_integration_logger`, `sync_filters`, nhánh lỗi của `build_dashboard_outputs`), không do thay đổi này.

## Sai lệch so với kế hoạch, kèm lý do

1. **`assets/style.css` đã được sửa sau vòng kiểm đầu.** Bản dựng đầu dùng hoàn toàn lớp đã có, nhưng
   các lớp đó vẽ chữ phụ bằng `--text-3` (3,85:1), dưới mốc 4,5:1 của NFR5.1. Bản sửa thêm **một khối
   phạm vi** `.analysis-tab` đặt `--text-2` cho sáu lớp chữ nhỏ và hai nhánh huy hiệu `chua-chay`/`rong`;
   ba tab cũ giữ nguyên `--text-3`. **Không thêm token màu nào**, nên tinh thần BR3.9 vẫn giữ.
   Kèm một lần **chỉnh bố cục trong mã** vì lý do nhìn bằng mắt: năm mục thống kê lúc đầu dính
   liền nhau (nhãn của mục sau nằm ngay dưới dòng chi tiết của mục trước). Cách sửa là bọc thân mỗi khối
   trong `html.Div(..., className="chart-stack")` — lớp **đã có sẵn** trong `assets/style.css` với
   `display: grid; gap: var(--space-4)`. Ảnh chụp trước/sau ở 1280px xác nhận khoảng cách đã đủ.
2. **Tab thứ năm dùng `dmc.Title` cho tiêu đề của chính nó** ("Báo cáo phân tích và mô hình") và
   `html.H3` cho tiêu đề từng khối. Lý do: `dmc.Title` là cơ chế NFR5.2 nêu tên, và nó buộc tab phải tự
   bọc `dmc.MantineProvider` như `src/integration/tab.py` — đúng bẫy 2 của `cicd-pipeline.md`. `H3` cho
   từng khối để không phải nhân bản kiểu chữ Mantine cho ba tiêu đề và giữ đúng tầng bậc tiêu đề hiện có.
3. **`test_u3_end_to_end.py` thêm hẳn một hàm test `slow` mới** thay vì nhồi vào hàm cũ. Lý do: hàm cũ
   đã chạy `--stage analyze` + replay batch và đã dài; nhồi thêm `--stage stats` vào đó sẽ làm một ca
   chứa hai kịch bản, còn tách ra thì ca mới chỉ chạy đúng đường "stats ghi tệp → tab đọc tệp thật".
   Chi phí đo được: cả hai ca `slow` của U3 chạy 36,29 s.
4. **Không đặt cổng thời gian cho NFR5.5 trong CI** — theo đúng `performance-design.md` ("Không đặt ngưỡng
   thời gian làm cổng CI"); ngân sách được đo một lần và ghi ở § "Xem bằng mắt ở 1280px".
5. **`dcc.Loading` truyền literal `color="#2F7D6A"`** giống `src/integration/tab.py`, vì prop này cần một
   giá trị màu chứ không nhận biến CSS. Đây không phải token màu mới trong `assets/style.css` (tệp không
   bị sửa) mà là dùng lại đúng literal tab cũ đang dùng.
6. **Tra tab theo `value` thay vì theo `id`.** Yêu cầu ghi "tra theo `id`"; `dcc.Tab` không có trường `id`
   trong layout này (id duy nhất của tab là **`value`**, cũng chính là giá trị mà callback và `ctx` dùng).
   Hàm `_tab(tabs, value)` vì vậy khẳng định tìm được **đúng một** tab với `value` đã cho
   (`"tich-hop"` và `"phan-tich"`), tức danh tính chứ không phải vị trí — đúng điều cần sửa. Ba chỗ
   `children[-1]` đã được thay, và test mới của tab khẳng định tab "Tích hợp" vẫn tra được khi không còn
   nằm ở vị trí cuối.

## Ghi chú kỹ thuật

- `state_for` không bao giờ tự đặt token khác `ReportView.status`; `pending_state()` là chỗ duy nhất sinh
  `chua-chay`, và nó chỉ tồn tại trong khoảng callback đang chạy (khối chờ của `custom_spinner`).
- Dấu đạt/không đạt của thẻ AUC lấy từ `counts.auc_below_target` của tệp (U2 tính trên AUC **đã làm
  tròn**, BR2.6). Chỉ khi tệp cũ không có cờ thì tab mới so `auc < 0.70` — để tab không tự mâu thuẫn với
  tệp ở biên 0,69996.
- `_comparison_item` lấy ngưỡng "100 đơn" từ `MIN_STATE_ORDERS` của `src/analytics/statistics.py` thay vì
  viết lại con số, đúng luật "một sự thật khai một nơi" của repo.
- Mọi chuỗi lấy từ tệp báo cáo (kể cả `revenue_definition`) được dựng qua `html`/`dmc` như **dữ liệu**;
  không `dangerously_allow_html`, không `innerHTML` (SDU-4).
- Không test nào của U3 đọc `data/reports/analysis.json` của repo: bộ nhanh dựng `ReportView` trong bộ
  nhớ; chỉ ca `slow` mới chạy tầng `stats` trên dữ liệu thật, và nó dùng `real_config` trỏ vào thư mục tạm
  (lỗ hổng `TD-09` không nặng thêm).

## Còn lại

- Dòng 564 của `analysis_tab.py` (thân callback trong `register_callback`) là câu lệnh duy nhất chưa được
  phủ: nó chỉ chạy khi Dash phục vụ một request thật, và repo không chạy trình duyệt trong CI
  (`cicd-pipeline.md` § "Không thay đổi"). Đường mã tương đương đã được phủ qua `render_analysis`, và tab
  đã được xác nhận chạy thật trên trình duyệt ở 1280px.
- `TD-09` (bộ nhanh cần `warehouse/` và `data/marts/`) vẫn còn: `test_dashboard_smoke.py` và test mới dùng
  `build_layout` đều gọi `load_config()` của repo. Việc sửa `TD-09` chưa được chốt cho đợt này.
- Chưa commit: thay đổi đang nằm trong working tree trên nhánh đợt `feature/analysis-and-models`.
