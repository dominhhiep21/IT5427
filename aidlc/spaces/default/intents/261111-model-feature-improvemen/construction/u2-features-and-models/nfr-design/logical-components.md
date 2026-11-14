# Logical Components — u2-features-and-models

Đơn vị: `u2-features-and-models` (kind `library`). Nguồn: `security-design.md`, `../nfr-requirements/tech-stack-decisions.md` (TS2.1–TS2.10), `../functional-design/{functional-spec,rules,entities}.md` (W1–W6, `feature_contract`, BR2.1–BR2.12), `../../../inception/contract-design/contract-summary.md` (C2, C2b, C3), mã thật `src/pipeline/stages.py`, `src/analytics/{model,service,report,statistics}.py`, `src/config.py`, `src/common/io.py`.

Tài liệu này là **inventory thành phần logic**: chỗ nào có mặt trong luồng chạy, U2 có sửa không, ranh giới ở đâu, và khi một chỗ hỏng thì cái gì hỏng theo. Dự án không có hạ tầng triển khai, nên phần "hạ tầng" **rỗng có chủ đích**.

## Dòng chạy thật của `run --stage stats` (`src/pipeline/stages.py:241-259`)

Nhánh `stats` hôm nay đúng bốn câu:

```
build_analysis_report(config, logger=logger)   :242   ← khối stats, dựng AnalysisReport (statistics.py:313)
train_model(config, logger=logger)             :244   → AnalyticsService.training_frame() (service.py:377)
                                                      → train_from_frame (model.py:343)
report = replace(report, model=model)          :245
write_report(config, report, writer)           :246   ← ghi nguyên tử (report.py:248-267)
logger.info("stats_report_written", ...)       :251-259
```

`train_model` **không** ghi tệp và **không** đọc báo cáo (`model.py:379-383`); lần ghi duy nhất của nhánh nằm ở `:246`. Đó là lý do W5 gom mọi I/O về một chỗ thay vì rải trong mô-đun thuần.

Sau U2, **cùng bốn dòng đó**, phần thân đổi thành chuỗi W1→W5 (W6 không nằm trên dòng này):

```
W1    AnalyticsService.training_frame()     → (TrainingFrame, CohortCounts)      [sửa: grain + trả cặp]
W1b   validate_counts(CohortCounts)         → ModelError nếu lệch bốn bộ đếm     [mở rộng]
W2    split_frame / split_summary           → SplitPlan; giao rỗng, tổng = cohort_rows
W3    validate_features(FEATURES)           → 14 tên, đúng thứ tự, không cột cấm
W3b   encode_features(train, test)          → categories + scaler khớp TRÊN TRAIN
W3c   fit logistic → fit HistGradientBoosting → auc / auc_tree
W3d   choose_threshold(THRESHOLD_GRID, F1)  → threshold, precision, recall
W3e   đóng góp log-odds (W3 bước 7)         → gộp theo trường, ba lớn nhất [định nghĩa; KHÔNG chạy trong lần lô]
W4    measure_state_baseline(frame, cut)    → baseline_auc  [hàm của U1, chỉ gọi]
W4b   build_model_block                     → ModelBlock 11 trường, counts 9 khoá
W5    ReportContract.assemble_report(...)   → AnalysisReport v3  [thay build_analysis_report]
W5b   write_report                          → data/reports/analysis.json (tạm → parse → replace)
W5c   ModelPersistence.save(FittedModel)    → data/models/{logistic.pkl, logistic.json}
W5d   load_model(models_dir)                → nạp lại để kiểm (BR2.8)
```

**W3 bước 7 có chạy trong lần lô hay không: không.** `ModelBlock` có đúng 11 trường và C2 v3 không mang đóng góp, nên kết quả của bước 7 không có chỗ chứa trong lần chạy lô; nó chỉ được tính khi chấm **một** dòng ở W6 bước 5 (`PredictionOutcome` mang ba đóng góp gộp theo trường). Vì thế `W3e` đứng trong chuỗi để **đúng thứ tự** với `functional-spec.md` W3, nhưng không ghi gì ra đĩa và không thêm trường nào vào báo cáo. Điều phải giữ là **một** định nghĩa phép tính — hệ số × giá trị, gộp theo trường, ba lớn nhất — dùng chung cho lần lô (nếu sau này có chỗ chứa) và cho W6; hai định nghĩa là hai chỗ trôi.

Thay đổi lớn nhất không phải thêm bước, mà là **hình dạng trả về của W1**: một `DataFrame` kèm thuộc tính ẩn trở thành **cặp** `(TrainingFrame, CohortCounts)`, và `counts` của báo cáo thôi được đếm lại ở Python (BR2.1).

## Inventory

| # | Thành phần | Vai trò | U2 sửa? |
|---|---|---|---|
| LC2.1 | `PipelineStages.run_stage` nhánh `stats` (`stages.py:241-259`) | điểm ghép duy nhất của tầng; nơi W1→W5 nối lại và nơi duy nhất ghi tệp | **Có** — thân nhánh |
| LC2.2 | `AnalyticsService.training_frame` + `TRAINING_FRAME_SQL` (`service.py:377-387`, `:38-46`) | đọc mart, dựng khung grain dòng hàng, trả cặp cùng bốn bộ đếm | **Có** |
| LC2.3 | `validate_counts` (`model.py:296-305`) + kiểu `CohortCounts` | kiểm 110.195 / 96.476 / 8.713 / 2 trước khi huấn luyện; hôm nay hàm chỉ kiểm ba số của tập kiểm tra | **Có** — mở rộng bốn bộ đếm quần thể |
| LC2.4 | `split_frame` + `split_summary` (`model.py:203-215`) | chia theo `order_id`, kiểm giao rỗng và tổng theo `cohort_rows` | **Có** — bỏ `expected_total=EXPECTED_DELIVERED` |
| LC2.5 | `FEATURES`, `FORBIDDEN_COLUMNS`, `validate_features` (`model.py:45-100`) | hợp đồng 14 đặc trưng: tập tên, **thứ tự**, danh sách cấm | **Có** — 11 → 14, thêm kiểm thứ tự, thêm `order_approved_at` |
| LC2.6 | `encode_features` (one-hot + `StandardScaler`) | mã hoá khớp trên tập huấn luyện, lưu phạm trù và tham số scaler | **Có** — 11 → 14 đặc trưng (thêm `seller_state`, `handling_days`, `approval_days`) |
| LC2.7 | `train_classifier` (`model.py:262`) | hồi quy logistic — mô hình **triển khai** (TS2.2) | Đọc, giữ nguyên hành vi |
| LC2.8 | Cây chỉ để báo cáo (`HistGradientBoosting` → `auc_tree`) | trả lời "trần là do đặc trưng hay do dạng mô hình"; không dùng để quyết định | **Có** — thành phần mới cho `auc_tree` |
| LC2.9 | `choose_threshold` (`model.py:266`) | chọn ngưỡng trên `THRESHOLD_GRID` theo F1 trên tập kiểm tra | Đọc |
| LC2.10 | `measure_state_baseline` (`model.py:122`) | baseline một đặc trưng trên **đúng** tập kiểm tra; do U1 sở hữu | Đọc — **chỉ gọi**, không sửa |
| LC2.11 | `build_model_block` + `MODEL_AUC_FLOOR` + `beats_floor` | 11 trường, 9 khoá `counts`, hai cờ trên giá trị đã làm tròn, mốc sàn | **Có** |
| LC2.12 | `ReportContract.assemble_report` + `write_report` (`report.py:248-267`) | dựng `AnalysisReport` v3, ghi nguyên tử, `_model_block` kiểm đủ trường | **Có** |
| LC2.13 | `ModelPersistence.save` / `load_model` | `pickle` + metadata JSON; mô-đun riêng theo ADR-001 | **Có** — thành phần mới |
| LC2.14 | `score_item` + `PredictionOutcome` (W6, C3) | chấm một dòng hàng từ trạng thái đã lưu; **không** đọc tệp, không mở kết nối | **Có** — thành phần mới |
| LC2.15 | `AppConfig.models_dir` + `load_config` (`config.py:15-52`, `:142-155`) | trường cấu hình mới + tạo thư mục lúc nạp | **Có** |
| LC2.16 | Điểm đo ngân sách (test `slow`) | chỗ duy nhất đo 300 s tầng và 240 s bước mô hình (gồm cả lượt đọc mart) | **Có** — xem mục dưới |
| LC2.17 | Cổng kiểm của U2 (bảng, không phải thành phần) | nói rõ cái gì có cổng, cái gì không | — |

**Mười ba dòng đánh dấu "Có":** tám chỗ **sửa** (`LC2.1`, `LC2.2`, `LC2.3`, `LC2.4`, `LC2.5`, `LC2.6`, `LC2.11`, `LC2.12`) và năm chỗ **mới** (`LC2.8`, `LC2.13`, `LC2.14`, `LC2.15`, `LC2.16`). Ba chỗ chỉ **đọc** (`LC2.7` logistic, `LC2.9` ngưỡng, `LC2.10` baseline của U1); `LC2.17` là bảng chứ không phải thành phần. Mã đã có phần lớn vẫn đứng yên — đó là lý do đơn vị này xếp cỡ M chứ không phải L, dù có mười bốn đặc trưng và hai mô hình.

## LC2.16 — Điểm đo ngân sách (NFR1, NFR2)

Hai con số, **hai chỗ đo, không gộp** (TS2.7, TS2.8):

| Chỉ số | Đo ở đâu | Cách đo | Hằng | Ngưỡng |
|---|---|---|---|---|
| Ngân sách **tầng** `stats` | `tests/integration/test_u2_model_end_to_end.py` | `time.perf_counter()` bọc quanh `run_stage(real_config, "stats")` | `STAGE_BUDGET_SECONDS` 900 → **300** | < 300 s |
| Ngân sách **bước mô hình** | cùng tệp test | `perf_counter()` quanh lần gọi `train_model(real_config)` **thứ hai** (lần đầu làm nóng cache đĩa) — `tests/integration/test_u2_model_end_to_end.py:89-93` | `TRAIN_BUDGET_SECONDS` 900 → **240** | < 240 s, nằm trong 300 s |

**Cái 240 s bao gồm — nói rõ để không ai đọc thành "riêng phần fit".** Lần gọi được đo là `train_model` (`model.py:379-383`), và hàm đó **đọc mart trước** (`AnalyticsService(config).training_frame()`, `service.py:377-387`) rồi mới gọi `train_from_frame`. Vì thế 240 s là **toàn bộ bước mô hình trong tầng `stats`**: đọc DuckDB + dựng khung grain dòng hàng + fit logistic + fit `HistGradientBoosting` + chấm điểm hai mô hình + chọn ngưỡng (`train_from_frame`, `:343-376`). Nó **không** phải con số riêng cho phần fit, và câu "240 s chừa lại 60 s cho phần đọc DuckDB, dựng khung và ghi tệp" ở TS2.8 là **không khớp** với cách đo này: 60 s đó nằm **trong** 240 s, không cộng thêm. Hai tài liệu không được nói hai mức — muốn tách phần fit ra thành ngân sách riêng thì phải có **điểm đo riêng** (đo quanh lời gọi huấn luyện thuần trên khung đã dựng sẵn, không đo qua `train_model`), và khi đó sửa cả TS2.8, `team.md` và mục này cùng lúc.

**Một điều 240 s không phủ:** phần **ghi** hai tệp (`write_report`, `ModelPersistence.save`) nằm ngoài lần đo đó, nên nó chỉ được tính trong 300 s của tầng — đúng như dòng trên.

Đây là **ngân sách chống hồi quy**, không phải SLA: một lần đo trên một máy, không trung bình nhiều lần, không có giám sát thời gian chạy trong sản phẩm (không có APM, không có metrics endpoint — xem mục hạ tầng). Vượt ngưỡng ⇒ test `slow` đỏ ⇒ CI đỏ. Nới ngân sách phải sửa **có chủ đích** ở cả ba chỗ (test, `team.md`, tài liệu này), không nới ngầm.

## LC2.17 — Cổng kiểm của U2, và chỗ không có cổng

| Thứ được kiểm | Cổng | Chặn? |
|---|---|---|
| 14 **tên hợp đồng** của đặc trưng: tập tên, thứ tự, cột cấm, không tên lặp | `validate_features` lúc chạy + unit test | **Chặn** — ném trước khi huấn luyện. **Không** canh thứ tự cột của ma trận **đã mã hoá** (one-hot) — xem dòng dưới |
| Thứ tự cột **đã mã hoá** khớp lúc huấn luyện | so `list(cột của ma trận) == list(model.feature_names)` ở W6 bước 4 (ném `ModelError`), + kiểm vòng W5.5 (`load_model` → dựng lại ma trận → so `feature_names` **đã mở rộng**) | **Chặn ở chấm điểm** và **chặn ở W5.5**; **không** có validator nào ngoài U2 biết vector đặc trưng là gì |
| Bốn bộ đếm quần thể | `validate_counts` lúc chạy + test `slow` | **Chặn** trước khi ghi |
| Rò rỉ giữa hai tập (cùng đơn hai phía) | `split_summary` lúc chạy | **Chặn** trước khi ghi |
| Hình dạng C2: 11 trường, 9 khoá, v3 | **phía dựng/parse khối**: `build_model_block` sinh đủ 11 trường và 9 khoá, `_model_block`/`_stats_block` (`report.py:457-488`) parse đủ trường; `_verify_pending` **chỉ** kiểm parse + `version` + hai khối không cùng rỗng | **Chặn ở phía dựng** (`ModelError` trước khi ghi, `ReportError` khi parse); **cổng ghi không kiểm hình dạng** — tệp v3 thiếu `auc_tree` vẫn thay được tệp cũ |
| Trạng thái tiền xử lý khớp sau khi lưu | W5.5 `load_model` lúc chạy | **Chặn** — nhưng **sau** khi cả hai tệp đã ghi |
| Mốc sàn `max(MODEL_AUC_FLOOR, baseline_auc)` | **không có cổng runtime**; unit test U2 hai nhánh + test `slow` mốc sàn của **U3** trên tệp thật | **Không** — báo cáo vẫn được ghi, test đỏ |
| Số dòng 9 bảng mart + 11 view + 5 KPI | `StarSchemaValidator`, `KpiReconciler` — chạy trong **`integrate`**, không trong `stats` | **Không**, theo nghĩa: hỏng do U2 không bị bắt ở đây; chỉ test `slow` chạm tới |
| Độ phủ ≥ 80% | `pytest --cov=src --cov-fail-under=80` (`ci.yml:53`), toàn bộ bộ test | **Chặn merge** |
| Lint + format | `ruff check .`, `ruff format --check` (danh sách khai tay `ci.yml:35`) | **Chặn merge** |
| Ngân sách 300 s / 240 s | test `slow` (LC2.16) | **Chặn merge** |
| Tệp mô hình không vào git | `git check-ignore` + `git ls-files` (thủ công) | **Không** |
| Thông điệp lỗi không mang dữ liệu | unit test khẳng định **vắng** giá trị | **Không** |

**Đọc bảng này theo chiều nguy hiểm:** sáu dòng đầu chặn được, nhưng mỗi dòng chặn ở **một phạm vi khác nhau** — bốn dòng (tên hợp đồng, bộ đếm, rò rỉ, hình dạng khối) chặn *trước khi ghi* trong lần chạy lô, dòng thứ tự cột **đã mã hoá** chỉ chặn *lúc chấm điểm*, còn W5.5 chặn **sau** khi cả hai tệp đã ghi. Hai dòng cuối cùng của nhóm "chặn merge" không bảo vệ gì lúc chạy. Không có validator nào trong dự án biết `ModelBlock` hay tệp mô hình là gì — nên chất lượng tầng mô hình được giữ bằng test, và điều đó phải nói ra thay vì để người đọc bảng tưởng có cổng.

## Ranh giới thật

1. **`model.py` (LC2.5–LC2.11, LC2.14) — U2 sở hữu, U3 import.** U3 import `AUC_TARGET`, `MODEL_AUC_FLOOR`, `beats_floor`, `score_item`, `FittedModel`; U3 **không sửa** tệp. Đây là ranh giới **mỏng nhất** của đơn vị, và nó mỏng ở chỗ **thứ tự cột của ma trận đã mã hoá** — không phải thứ tự 14 tên hợp đồng. Hai thứ đó khác nhau, và câu "cùng một thứ tự" không dựng được thành mã.

   **Thứ tự mã hoá thật**, do `encode_features` dựng (`model.py:226-244`) và `score_item` phải tái lập y hệt (W6 bước 4):

   1. **Số** — sáu cột theo `NUMERIC_FEATURES` sau đợt này (`item_count`, `item_total`, `item_price_max`, `payment_installments`, `handling_days`, `approval_days`; bốn cột đầu ở `model.py:43`), đã chuẩn hoá bằng `StandardScaler` khớp **chỉ** trên tập huấn luyện (`:234`).
   2. **Cờ** — hai cột theo `FLAG_FEATURES` (`:44`), **không** chuẩn hoá (`:242`).
   3. **One-hot** — từng cột theo `CATEGORICAL_FEATURES` (`:36-42`), mỗi cột nở thành một khối cột đặt tên `tên_cột=giá_trị` (`:393-403`); danh sách phạm trù lấy từ `_categories` (`:386-390`), tức **đã sắp xếp** và luôn có `unknown`, khớp trên tập huấn luyện.

   Hệ quả bắt buộc phải nói: vì bước 3 **nở** cột, `feature_names` là **danh sách đã mở rộng** — nhiều hơn 14 rất nhiều, tuỳ số phạm trù mỗi cột phân loại — **không** phải 14 tên của `FEATURES` (`:45-57`). Nếu Code Generation đặt `feature_names = list(FEATURES)`, phép kiểm số cột ở W6 bước 4 từ chối **mọi** lần chấm điểm hợp lệ; `feature_names` phải là `list(train_matrix.columns)` sau khi mã hoá.

   **Cái gì canh cái gì** — hai phép kiểm, hai phạm vi, không thay nhau được:

   | Phép kiểm | Canh | **Không** canh |
   |---|---|---|
   | `validate_features` (`:87-100`; sau U2 thêm kiểm thứ tự) | **14 tên hợp đồng**: đúng tập, đúng thứ tự, không tên lặp, không cột cấm | thứ tự cột của ma trận **đã mã hoá**; nó không biết one-hot là gì |
   | W5.5 — `load_model` → dựng lại ma trận → so `feature_names` **đã mở rộng** với danh sách đã lưu | trạng thái đọc lại dựng được **đúng** ma trận đã huấn luyện, kể cả thứ tự cột | đường dựng vector lúc chấm điểm, nếu `score_item` sắp cột theo cách khác |

   Vì vậy phép kiểm thứ hai phải có **bản sao ở chỗ chấm điểm**: W6 bước 4 so `list(ma_tran.columns) == list(model.feature_names)` và ném `ModelError` khi lệch. Nếu chỉ so 14 tên hợp đồng thì lệch thứ tự **lọt**, và xác suất sai **im lặng** — không cổng nào ngoài U2 bắt được (bảng LC2.17), vì `StarSchemaValidator`/`KpiReconciler` không biết vector đặc trưng là gì. Test canh đúng chỗ này: chấm **một** dòng với 11 giá trị nhập cố định và khẳng định **một** xác suất kỳ vọng, chứ không chỉ khẳng định "không ném".
2. **`report.py` (LC2.12) — U2 sở hữu, U3 đọc qua C2.** Chỉ `report.py` dựng `AnalysisReport` (BR2.9, ADR-008). Hệ quả trực tiếp: `_model_block` phải kiểm **đủ** 11 trường và 9 khoá. Hôm nay nó đọc bảy trường và để mặc định (`report.py:457-468`), nên một tệp v3 thiếu `auc_tree` vẫn ra `day-du` — đúng thứ BR2.7 cấm. Sửa chỗ này là việc của U2; sửa fixture `version=2` của `test_dashboard_analysis_tab.py` là việc của U3, cùng lúc.
3. **LC2.2 ↔ mart: một chiều, chỉ đọc.** `training_frame` không sở hữu view; nó đọc `v_fact_order_items` và `v_dim_*` do `integrate` tạo. Đổi tên cột ở mart là U2 gãy — nhưng U1 đã xong và không mở lại (`functional-spec.md` W1).
4. **LC2.13 ↔ LC2.1: đường dẫn đi qua tham số.** `ModelPersistence` không đọc `AppConfig`, không tự dựng `Path`; `stages.py` truyền `config.models_dir` (SD2.3, SD2.7). Đổi lại: `ModelPersistence` không dùng được ở chỗ nào khác, và đó là điều muốn có.
5. **LC2.14 ↔ LC2.13: `score_item` là hàm thuần.** Nó **không** nạp tệp, **không** mở kết nối; U3 nạp `FittedModel` rồi truyền vào (C3). Nếu `score_item` tự nạp, W6 mọc thêm một chỗ `pickle.load` thứ hai và SD2.3 sụp — nên ranh giới này là một kiểm soát an toàn, không chỉ là kiến trúc đẹp.
6. **LC2.3/LC2.8/LC2.9/LC2.11 ↔ đĩa:** không chạm gì. Bốn thành phần này là hàm thuần trên `DataFrame`/`dict`; mọi I/O nằm ở `LC2.2` (đọc DuckDB), `LC2.12` (ghi báo cáo) và `LC2.13` (ghi/nạp mô hình).

## Điểm chệch so với Functional Design — ghi lại, không tự sửa tài liệu đã duyệt

`functional-design` của U2 đã qua cổng nên không được sửa sau đó. Hai câu của nó hẹp hơn thiết kế này, và đây là chỗ ghi lại:

| Chỗ | `functional-design` nói | Thiết kế này nói | Văn bản có hiệu lực |
|---|---|---|---|
| `functional-spec.md` W6 bước 4 | từ chối khi **số cột** lúc chấm điểm khác lúc huấn luyện | so **toàn bộ danh sách cột**: `list(ma_tran.columns) == list(model.feature_names)` | **Thiết kế này** — so số cột không bắt được lệch **thứ tự**, mà lệch thứ tự cho xác suất sai **im lặng**. Code Generation phải cài phép so danh sách, và sửa câu chữ W6 bước 4 khi mở tệp đó lần tới. |
| `rules.md` BR2.3 và `entities.md` | `FittedModel.feature_names` gắn với thứ tự **14 tên** hợp đồng | `feature_names` là **danh sách đã mở rộng** (`list(train_matrix.columns)` sau mã hoá) | **Thiết kế này** — đặt `feature_names = list(FEATURES)` sẽ khiến phép so ở W6 bước 4 từ chối **mọi** lần chấm điểm hợp lệ. |

## Tài nguyên chia sẻ

| Tài nguyên | Ai dùng chung | Rủi ro |
|---|---|---|
| `warehouse/olist.duckdb` | U2 đọc qua `read_only=True`; `integrate` ghi | Khoá tệp khi dashboard đang mở — đóng dashboard trước `integrate` (`docs/runbook.md`); và `read_only` không ngăn tiến trình khác ghi (SD2.1) |
| `data/marts/*.parquet` | `integrate` ghi; U2 **không mở tệp**, chỉ đọc qua view | Không có đường nào trong `src/analytics/` tham chiếu `marts_dir` |
| `data/reports/analysis.json` | U2 ghi (nguyên tử), U3 đọc (khác tiến trình) | Hai thế hệ có thể bị đọc chéo nếu `stats` chạy chen giữa; chỉ từng tệp được bảo vệ (SD2.8) |
| `data/models/` | U2 ghi, U3 đọc | `pickle` gắn phiên bản thư viện đã sinh ra nó; máy khác phải sinh lại, không chia sẻ tệp |
| `logs/*.jsonl` | mọi tầng ghi; U2 ghi `model.trained`, `stats_report_written` | Văn bản ngoại lệ của bên thứ ba không được lọc (SD2.6); `prune_logs` giữ 10 tệp gần nhất |
| `dataset/` | U2 **không chạm** ở bất kỳ bước nào | — |

## Điều tài liệu này không có: hạ tầng

U2 **không thêm dịch vụ nào**: không container, không queue, không scheduler, không worker, không hàng đợi huấn luyện, không kho mô hình (model registry), không endpoint. Toàn bộ đơn vị chạy như một phần của hai tiến trình đã có — `python -X utf8 -m src.pipeline run --stage stats` (W1–W5) và tiến trình dashboard (W6) — và "triển khai" nghĩa là chạy từ mã nguồn, không có bước đóng gói.

Khác U1, U2 **không có lời gọi mạng nào**: không API, không đối tác, không cache từ xa. Vì vậy phần hạ tầng ở đây **rỗng tuyệt đối**, không phải "rỗng trừ một ngoại lệ" như `u1-mart-and-baseline` (IBGE). Infrastructure Design ở stage sau ghi đúng như thế.
