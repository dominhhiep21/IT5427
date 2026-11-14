# Code Summary — u2-model

Đơn vị: `u2-model`. Intent: `261109-stats-and-models`. Giai đoạn: Construction / Code Generation.
Kế hoạch đã duyệt: `code-generation-plan.md` (sha256 `c4202e8d…`), hợp đồng kiểm thử
`sha256:c6029e50…`. Kế hoạch được thi công nguyên văn, không sửa.

## Đã dựng gì

Bước mô hình huấn luyện bộ phân loại đơn giao trễ và **trả về** một `ModelBlock`; tầng `stats` ghép khối đó
với khối `stats` của U1 rồi ghi tệp một lần. U2 không đọc và không ghi `data/reports/analysis.json`, không
lưu mô hình ra đĩa, không chạm `dataset/`, `src/dashboard/`, `src/integrate/`, `config/*.yaml` hay
`src/analytics/report.py`.

| # | Tệp | Việc đã làm |
|---|---|---|
| S1 | `src/analytics/model.py` **(mới)** | 11 cột đặc trưng + 10 cột bị cấm là hằng số có tên; `delivered_population` (BR2.1), `build_feature_frame` (BR2.3, TS-8), `split_frame`/`split_summary` (BR2.2), `encode_features` (TS-6, TS-9), `build_estimator`/`train_classifier` (BR2.4, TS-9), `choose_threshold` (BR2.5), `auc_below_target` (BR2.6), `validate_counts`/`build_model_block` (BR2.7, BR2.9), `train_from_frame`/`train_model` (BR2.8) |
| S2 | `src/analytics/service.py` | `TRAINING_FRAME_SQL` + `AnalyticsService.training_frame()`: một truy vấn tham số hoá trên các view trong `VIEW_TABLES`, gộp dòng hàng và dòng thanh toán về grain đơn trước khi ghép |
| S3 | `src/pipeline/stages.py` | Nhánh `stats` gọi `train_model` **sau** `build_analysis_report`, ghép khối bằng `dataclasses.replace`, ghi tệp một lần; sự kiện `stats_report_written` mang thêm `model_auc`, `model_threshold`, `model_auc_below_target` |
| S4 | `requirements.txt` | Ghim `scikit-learn==1.6.1` kèm lý do và ghi chú về `numpy` gián tiếp |
| S5 | `.github/workflows/ci.yml` | Thêm `src/analytics/model.py`, `src/analytics/service.py`, `tests/unit/test_analytics_model.py`, `tests/integration/test_u2_model_end_to_end.py` vào danh sách `ruff format --check` |
| S6 | `README.md`, `CHANGELOG.md` | README mục **Chạy pipeline** (tầng `stats` ghi cả hai khối, hợp đồng mô hình), **Test** (hai test `slow`), **Lưu ý** (không lưu tệp mô hình); CHANGELOG thêm mốc `v0.3.0 — 2026-11-11` |
| S7 | `tests/unit/test_analytics_model.py` **(mới)** | 45 test: mỗi BR một ca, hai ca rò rỉ nhãn, TS-6/TS-8/TS-9, tái lập, bốn ca cho `AnalyticsService.training_frame()` trên DuckDB tạm, và bốn ca cho các nhánh lỗi của BR2.1/BR2.2 |
| S8 | `tests/integration/test_u2_model_end_to_end.py` **(mới, `slow`)** | Chạy `run --stage stats` trên dữ liệu thật: khối `model` có mặt, cỡ mẫu 96.478 / 7.826, ngưỡng và bốn chỉ số đã làm tròn, NFR1.1/NFR1.2 dưới 15 phút, NFR1.3 hai lần chạy cho cùng khối |

Ngoài manifest, ba tệp phải sửa vì hình dạng chúng khẳng định đã đổi theo đúng kế hoạch — xem
§ "Sai lệch so với kế hoạch":

- `tests/unit/test_pipeline_stages.py` — mart tạm thêm `v_fact_payments` và cột `weekday`; ca `stats` nay
  khẳng định tệp đủ hai khối; thêm ca khẳng định bước mô hình chạy **sau** bước thống kê.
- `tests/unit/test_ci_config.py` — `NEW_FILES` phủ bốn tệp mới; thêm ca khẳng định `requirements.txt` ghim
  `scikit-learn==1.6.1`.
- `tests/integration/test_u1_stats_end_to_end.py` — trạng thái báo cáo sau `--stage stats` là `day-du` chứ
  không còn `mot-phan`, và khối `model` phải có mặt.

## Bước 1 — cổng phụ thuộc (đã qua)

Ghim trước, cài sau, rồi mới viết `import sklearn`:

```
$ ./.venv/Scripts/python.exe -X utf8 -m pip install "scikit-learn==1.6.1"
Installing collected packages: scikit-learn
Successfully installed scikit-learn-1.6.1

$ ./.venv/Scripts/python.exe -X utf8 -m pip show numpy scipy joblib threadpoolctl scikit-learn
Name: numpy
Version: 2.2.1
Name: scipy
Version: 1.15.2
Name: joblib
Version: 1.6.0
Name: threadpoolctl
Version: 3.8.0
Name: scikit-learn
Version: 1.6.1
```

`numpy` **vẫn 2.2.1** và `scipy` **vẫn 1.15.2**, nên không phải ghim lại `numpy` và baseline KPI của U1 không
đổi. `joblib`/`threadpoolctl` chỉ được thêm, không thay bản cũ; `scikit-learn` nằm trong `.venv`
(`.venv\Lib\site-packages`), bản 1.9.1 có sẵn trong môi trường Python toàn cục không bị đụng tới.

Baseline U1 trước khi thêm mô hình, chạy đúng theo yêu cầu của kế hoạch:

```
$ ./.venv/Scripts/python.exe -X utf8 -m pytest -m slow -q
..........                                                               [100%]
10 passed, 438 deselected in 202.95s (0:03:22)
```

## Kiểm chứng

**Bộ nhanh** — `python -X utf8 -m pytest -m "not slow"`:

```
485 passed, 11 deselected in 14.44s
```

**Toàn bộ bộ test kèm cổng phủ 80%** — `python -X utf8 -m pytest --cov=src --cov-fail-under=80 --cov-report=term`:

```
src\analytics\model.py           174      0   100%
src\analytics\report.py          241      6    98%
src\analytics\service.py         151      6    96%
src\analytics\statistics.py      137      0   100%
src\pipeline\stages.py           144     63    56%
TOTAL                           4461    349    92%
Required test coverage of 80% reached. Total coverage: 92.18%
======================= 496 passed in 234.84s (0:03:54) =======================
```

**Lint** — `python -X utf8 -m ruff check .`:

```
All checks passed!
```

**Định dạng** — `python -X utf8 -m ruff format --check` trên tám tệp đã chạm:

```
8 files already formatted
```

**Chuỗi xác nhận bốn bước của nhóm** (`## Deployment` trong `team.md`):

```
$ python -X utf8 -m src.pipeline run --stage all
run=20261111T024559-53a5f6a7 success=True stages=['ingest','clean','quality','integrate','linkage','analyze']

$ python -X utf8 -m src.pipeline run --stage stats
run=20261111T024700-30a28e4f stage=stats success=True
```

Bước 4 (mở dashboard) thuộc phần hiển thị của U3, đơn vị này không sửa `src/dashboard/**`; thay vào đó đọc
lại tệp báo cáo để xác nhận nó đủ hai khối.

## Khối mô hình trên dữ liệu thật

`data/reports/analysis.json` sau `run --stage stats`:

```json
{
  "target": "is_late",
  "split": {
    "train_start": "2016-09-15",
    "train_end": "2018-03-31",
    "test_start": "2018-04-01",
    "test_end": "2018-08-29",
    "train_n": 64322,
    "test_n": 32156
  },
  "auc": 0.5133,
  "threshold": 0.4,
  "precision": 0.0866,
  "recall": 0.2645,
  "counts": {
    "flagged": 5910,
    "not_flagged": 26246,
    "total": 32156,
    "threshold_method": "max_f1_on_test_grid005",
    "auc_below_target": true
  }
}
```

`train_n + test_n = 96.478` đúng baseline; `flagged + not_flagged = total = test_n`; bốn số có đúng 4 chữ số.
`auc_below_target = true` là **kết quả thật, không phải lỗi thi công**: với 11 cột chỉ biết lúc đặt hàng,
AUC trên dữ liệu thật là 0,5133, dưới mốc 0,70. BR2.6 buộc phải ghi rõ điều đó thay vì ẩn đi, và kế hoạch
không cho phép thêm cột hậu giao để đẩy AUC — đó đúng là rò rỉ nhãn mà SD-1 canh.

## Độ phủ

92,18 % toàn bộ `src/` (cổng 80 % đạt, không hạ ngưỡng). Riêng phần mới: **`src/analytics/model.py` 100 %**
(174/174 câu lệnh), `src/analytics/service.py` 96 %. Sáu câu lệnh chưa phủ của `service.py` nằm ở `_where`
(nhánh lọc theo danh mục và khoảng ngày của các phương thức cũ), không thuộc đơn vị này.

## Sai lệch so với kế hoạch, kèm lý do

1. **Ba tệp test ngoài manifest** (danh sách ở § "Đã dựng gì"). Kế hoạch đổi hình dạng tệp báo cáo và hình
   dạng mart tạm mà ba tệp này đang khẳng định; quy tắc nhóm bắt buộc sửa chúng **trong cùng thay đổi**, nếu
   không bộ nhanh đỏ ngay. Không nới lỏng khẳng định nào: `test_u1_stats_end_to_end.py` chỉ đổi `mot-phan` →
   `day-du` và thêm một dòng khẳng định khối `model` có mặt.
2. **`src/analytics/service.py` vào danh sách `ruff format --check`** cùng `model.py`. Tệp này bị sửa bởi S2
   nên vào danh sách là đúng quy tắc; nó vốn đã sạch `ruff format` nên không kéo theo lần dọn định dạng nào.
3. **`train_from_frame` nhận `expected_delivered`/`expected_late`** (mặc định là baseline 96.478/7.826). Lý do:
   BR2.1 buộc cỡ mẫu phải khớp baseline, nên một fixture 120 dòng không thể đi qua đúng đường mã nếu các con
   số bị đóng cứng. Đường sản xuất `train_model` luôn gọi với mặc định, và có test khẳng định **chính
   `train_model`** từ chối một mart 730 dòng.
4. **`counts.auc_below_target` tính trên AUC đã làm tròn.** BR2.6 nói cờ đúng khi và chỉ khi `auc < 0.70`, mà
   `auc` trong tệp là giá trị đã làm tròn (BR2.9); tính trên giá trị thô sẽ tạo tệp tự mâu thuẫn ở biên
   (0,69996 → `auc: 0.7` nhưng cờ `true`).
5. **Ca `stats` ở bộ nhanh dùng `small_model`** — gọi thật `train_from_frame` trên mart tạm 730 đơn với
   `expected_delivered=730`, không mock. Cùng đường mã, chỉ khác cỡ mẫu; đường sản xuất được kiểm bởi
   `tests/integration/test_u2_model_end_to_end.py` (marker `slow`) trên 96.478 đơn thật.
6. **Nhãn phạm trù của `purchase_month`/`purchase_weekday`** lấy từ `str()` của giá trị, nên fixture (float)
   cho `"3.0"` còn dữ liệu thật (integer) cho `"3"`. Nhãn này chỉ sống trong ma trận đặc trưng, không vào báo
   cáo, và hai tập của cùng một lần chạy luôn dùng chung một danh sách phạm trù nên không sai lệch hành vi.

Trong lúc viết test, một kỳ vọng của chính tôi sai (ca hoà F1 kỳ vọng ngưỡng 0,75 trong khi điểm cao nhất
trên lưới giữ F1 = 1 là 0,80). Tôi sửa **kỳ vọng của test**, không sửa mã — mã đã đúng luật BR2.5.

## Ghi chú kỹ thuật

- `split_frame` đọc `date_key` bằng `pd.to_datetime(..., format="%Y-%m-%d", errors="coerce")`: mọi nơi trong
  repo sinh `date_key` bằng `strftime('%Y-%m-%d')`, nên nêu rõ định dạng vừa nhanh hơn vừa không rơi vào
  `dateutil` từng phần tử (pandas phát `UserWarning` khi gặp giá trị không đọc được). Giá trị không đọc được
  thành `NaT` và bị chặn bởi BR2.2, không lọt vào tập nào.
- `AnalyticsService.training_frame()` từ chối kết quả ghép bị nhân dòng (`ValueError`) thay vì trả một bảng
  có `order_id` lặp — đó là cùng lỗi mà `StarSchemaValidator` canh ở lớp tích hợp, kiểm lại ở đây vì bảng
  này là đầu vào huấn luyện.

## Còn lại

- Bước 4 của chuỗi xác nhận (mở dashboard) do người làm thực hiện; phần hiển thị thuộc U3 và đơn vị này bị
  cấm chạm `src/dashboard/**`. Tệp báo cáo đã ở trạng thái `day-du` nên U3 có đủ dữ liệu.
- `src/pipeline/stages.py` phủ 56 % — nợ đã biết từ trước (`team.md` § Testing Posture), không phải do đợt
  này; phần mới của nhánh `stats` được phủ bởi `tests/unit/test_pipeline_stages.py` và test `slow`.
- Chưa commit: thay đổi đang nằm trong working tree trên nhánh đợt `feature/analysis-and-models`.
