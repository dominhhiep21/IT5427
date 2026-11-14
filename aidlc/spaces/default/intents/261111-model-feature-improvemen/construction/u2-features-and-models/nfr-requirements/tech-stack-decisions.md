# Tech Stack Decisions — u2-features-and-models

Đơn vị: `u2-features-and-models`. Nguồn: `../functional-design/{functional-spec,rules}.md`, `../../../inception/contract-design/contract-summary.md` (C2, C2b, C3), `../../../inception/requirements-analysis/requirements.md` (NFR1–NFR5, RQ-01, RQ-04, RQ-06), `requirements.txt`, `ruff.toml`, `.github/workflows/ci.yml`, `config.yaml`.

**Kết luận ngắn: đơn vị này không chọn công nghệ mới nào.** Ba đặc trưng mới, mô hình thứ hai, tệp mô hình và hàm chấm điểm đều chạy trên ngăn xếp đã ghim. Điều đáng ghi lại không phải "dùng gì" mà là **vì sao không thêm gì** — và hai chỗ thật sự là quyết định: mô hình nào được triển khai, và hai hằng số mốc đặt ở đâu.

## Ngăn xếp đang dùng, và chỗ đơn vị này chạm vào

| Lớp | Công nghệ | Phiên bản | Đơn vị này dùng để |
|---|---|---|---|
| Ngôn ngữ | Python | 3.13 | toàn bộ |
| Xử lý dữ liệu | `pandas` | 2.2.3 | dựng khung grain dòng hàng, mã hoá one-hot, chuẩn hoá, chia tập |
| Học máy | `scikit-learn` | 1.6.1 | `LogisticRegression` (triển khai), `HistGradientBoostingClassifier` (chỉ báo cáo), `StandardScaler`, `roc_auc_score` |
| Kho phân tích | `duckdb` | 2.0.0 | đọc mart qua **kết nối chỉ đọc**; đơn vị này đổi câu truy vấn dựng khung, không đổi schema |
| Lưu tệp mô hình | `pickle` (thư viện chuẩn) | — | payload mô hình + trạng thái tiền xử lý; metadata đi kèm bằng `json` |
| Kiểm thử | `pytest` + `pytest-cov` | 9.1.1 / 7.1.0 | test đơn vị + test `slow` trên dữ liệu thật |
| Lint/format | `ruff` | 0.17.4 | `ruff check .`, `ruff format --check` |

## TS2.1 — Không thêm phụ thuộc nào: 12 gói, không `joblib`, không `shap`

**Quyết định:** `requirements.txt` giữ đúng **12** gói đang ghim. Đơn vị này không thêm gói nào, kể cả gói "tiện" cho một việc cụ thể.

**Ba cái tên dễ bị thêm nhất, và lý do từ chối từng cái:**
- **`joblib`** — chỉ để tuần tự hoá mô hình. `pickle` của thư viện chuẩn làm đúng việc đó (TS2.4); thêm `joblib` là thêm một gói bảo trì để đổi lấy không năng lực nào.
- **`shap`** — chỉ để giải thích dự đoán. Nhưng hợp đồng C3 đòi **ba đóng góp log-odds gộp theo trường**, và hệ số logistic × giá trị đặc trưng cho đúng con số đó mà không cần thư viện nào (BR2.10). `shap` còn là gói nặng, kéo theo `numba`/`llvmlite`, và không chạy được cho mọi mô hình trong cùng một câu.
- **`numpy`** — chỉ có mặt **gián tiếp** qua `pandas` 2.2.3 và `scipy` 1.15.2 (`requirements.txt:23-26`). Mã mới không được `import numpy` trực tiếp; mọi phép số đi qua `pandas` hoặc qua `scikit-learn`.

**Ràng buộc:** `project.md` `## Forbidden` cấm import thư viện bên thứ ba chưa ghim, và `RQ-01` nhắc lại. `pickle` không thuộc nhóm này vì là thư viện chuẩn — điều đó được nói rõ ở TS2.4 để không ai đọc thành "có ngoại lệ cho gói thứ ba".

**Kiểm:** `requirements.txt` vẫn đúng 12 dòng gói; mở rộng `tests/unit/test_ci_config.py::test_scikit_learn_is_pinned_with_an_exact_version` thành phép kiểm **cả danh sách** (12 tên, phiên bản ghim chính xác), không chỉ `scikit-learn`. `grep -rn "^import numpy\|^from numpy" src/` không có kết quả.

## TS2.2 — Logistic là mô hình triển khai, vì mỗi dự đoán phải giải thích được

**Quyết định:** mô hình được lưu, được nạp và được dùng để chấm điểm là **hồi quy logistic** (`model.py:247-250`), không phải cây.

**Vì sao — đây là ràng buộc hợp đồng, không phải sở thích:** C3 trả `contributions` gồm ba **trường** lớn nhất tính bằng log-odds, và BR2.10 bắt buộc gộp mọi cột one-hot của cùng một trường trước khi chọn. Với logistic, đóng góp của một trường là `hệ số × giá trị đặc trưng` — một phép nhân, tính lại được, và **cộng các đóng góp lại thì ra đúng log-odds của dự đoán**. Với mô hình cây, không có phân rã nào như thế trong `scikit-learn`: mọi cách "giải thích" cây đều là xấp xỉ, và một con số xấp xỉ đặt cạnh chữ "log-odds" là nói sai bản chất.

**Hệ quả:** `FittedModel` phải mang `coef_` của logistic cùng `categories`/`scaler_means`/`scaler_scales`/`feature_names`; `score_item` chỉ đọc trạng thái đó, không khớp lại (BR2.8, BR2.11).

**Kiểm:** test đơn vị khẳng định mô hình được lưu là `LogisticRegression` và `FittedModel` mang đủ bốn phần trạng thái; test khác khẳng định tổng ba đóng góp trả về (trước khi gộp) bằng log-odds của dự đoán trong sai số làm tròn.

## TS2.3 — `HistGradientBoosting` chỉ để báo cáo `auc_tree`, không bao giờ triển khai

**Quyết định:** cây được huấn luyện trên **cùng** ma trận, cùng mốc cắt, cùng quần thể, cùng `random_state = 42` (BR2.4), và kết quả của nó chỉ đi vào `model.auc_tree` — một trường để đọc, không cổng nào đọc nó.

**Vì sao vẫn huấn luyện:** nó trả lời một câu hỏi mà AUC của logistic không trả lời được — "chênh lệch còn lại là do mô hình hay do đặc trưng?". Nếu cây cũng chỉ đạt ngang logistic thì đặc trưng là trần; nếu cây vượt xa thì vấn đề nằm ở dạng mô hình. Câu trả lời đó rẻ (một lần fit) và không đổi sản phẩm.

**Vì sao không triển khai cây:** thiếu phân rã đóng góp theo trường (TS2.2), và `auc_below_target` (FR2.6) được tính cho **logistic** — dùng cây để tính cờ đó là đổi định nghĩa "mô hình đạt mốc" mà không nói ra.

**Kiểm:** `model.auc_tree` có mặt trong `ModelBlock` (C2) và được làm tròn 4 chữ số; test `slow` chạy `run --stage stats` **hai lần** và khẳng định `auc_tree` giống nhau (FR2.3, hệ quả của `random_state` cố định); test chấm điểm chỉ nhận `FittedModel` của logistic.

## TS2.4 — `pickle` của thư viện chuẩn là định dạng tệp mô hình; không `joblib`

**Quyết định:** payload mô hình ghi bằng `pickle.dump` và đọc bằng `pickle.load`, kèm tệp `json` chứa `feature_names`, `library_versions`, `trained_at` (C2b). Tên tệp là hằng của mô-đun `ModelPersistence` — **không** đặt trong `report.py`, vì `report.py` sở hữu hợp đồng báo cáo chứ không sở hữu định dạng tệp mô hình (ADR-001).

**Vì sao `pickle` chứ không phải định dạng có schema như JSON:** trạng thái cần lưu là **đối tượng** — bộ ước lượng đã fit cùng `StandardScaler` đã khớp. Viết nó ra JSON là tự viết lại phần tuần tự hoá của `scikit-learn` rồi phải kiểm nó khớp từng tham số; `pickle` làm đúng việc đó trong thư viện chuẩn, không thêm gói, không thêm định dạng phải bảo trì.

**Cái giá đã nhận, ghi ở đây chứ không để người sau phát hiện:** `pickle` gắn với phiên bản thư viện đã sinh ra nó, nên tệp của máy này **không** phải định dạng trao đổi giữa các máy — máy khác sinh lại tệp của mình. Và `pickle` nạp được mã, nên rủi ro tin cậy thuộc `security-requirements.md` `SEC2.3`, không phải một ghi chú ở đây.

**Vị trí đặt I/O:** `pickle.dump`/`pickle.load` là I/O nên **không** nằm trong `model.py` (hàm thuần trên `DataFrame`); chúng nằm trong mô-đun `ModelPersistence`, và `stages.py` là nơi duy nhất ghép các mảnh lại.

**Kiểm:** `grep -rn "pickle.dump\|pickle.load" src/` chỉ ra một mô-đun; `grep -rn "import joblib" src/` không có kết quả; unit test nạp lại tệp vừa ghi và khẳng định `feature_names` + trạng thái tiền xử lý trùng khớp với mô hình đã fit (BR2.8, W5 bước 5).

## TS2.5 — Hai hằng số mốc đặt cạnh nhau trong `model.py`: `AUC_TARGET` giữ 0,70, `MODEL_AUC_FLOOR` = 0,55

**Quyết định:** `AUC_TARGET = 0.70` giữ nguyên chỗ cũ (`model.py:25`) và giá trị cũ. `MODEL_AUC_FLOOR = 0.55` là hằng **mới**, đặt **ngay cạnh** nó trong cùng tệp, cùng mô-đun. Hàm thuần `beats_floor(auc, baseline_auc, floor=MODEL_AUC_FLOOR) -> bool` trả `auc >= max(floor, baseline_auc)`, so trên hai giá trị **đã làm tròn 4 chữ số** đọc từ báo cáo.

**Vì sao đặt cạnh nhau:** hai hằng này trả lời hai câu khác nhau nhưng dễ bị đọc lẫn — `AUC_TARGET` là **mốc mong muốn** (cờ `auc_below_target`), `MODEL_AUC_FLOOR` là **sàn chống thoái hoá** (NFR5). Để chúng ở hai tệp là mời người sau sửa một cái và quên cái kia. Ở cạnh nhau, chênh lệch 0,15 giữa chúng là thứ nhìn thấy được.

**Vì sao `beats_floor` lấy `max`:** nếu mốc sàn thấp hơn baseline đo lại (baseline có thể vượt 0,55 khi dữ liệu đổi), thì hai cổng sẽ cho hai kết luận trái nhau trên cùng một mô hình — "vượt sàn" và "kém baseline". `max` làm điều đó không xảy ra được, và đó là lý do mốc sàn **không bao giờ** thấp hơn baseline. Khi baseline vượt sàn thì sàn được **nâng**, không phải bỏ.

**Mốc sàn là cổng trên một chỉ số chất lượng, và đây là ngoại lệ có chủ đích so với luật của dự án.** NFR5 đặt một ngưỡng trên `auc` thành kỳ vọng của một test `slow` — đúng điều `project.md` `## Forbidden` (2026-11-12) đang cấm ("NEVER đặt một giá trị AUC … làm **kỳ vọng** của một test viết trước"). Mục này không giả vờ rằng nó tuân luật đó; nó ghi rõ ba điều:

**(a) Ngoại lệ là có chủ đích, và hẹp.** Mốc sàn không phải mục tiêu chất lượng mà là **cổng chống thoái hoá**: nó chỉ hỏi "mô hình còn hơn mốc đã có không", không hỏi "mô hình đã đủ giỏi chưa". Vì vậy phép so là với `max(MODEL_AUC_FLOOR, baseline_auc)` — một **mốc đã báo cáo**, đo trên cùng quần thể, cùng mốc cắt, cùng cách chia — chứ không so với một hằng số kỳ vọng đặt trước. `AUC_TARGET` (0,70) vẫn chỉ sinh cờ `auc_below_target`, không phải cổng; `auc` vẫn được **ghi ra và hiển thị**.

**(b) Nghĩa vụ bắt buộc, và mốc sàn chỉ hợp lệ khi đã làm xong.** Ngoại lệ này phải được ghi lại bằng **nghi thức learnings** ở cổng của stage NFR Requirements, và câu chữ `project.md` `## Forbidden` phải được sửa để hết mâu thuẫn — nêu đích danh ngoại lệ `NFR5`/`FR2.7` cùng điều kiện của nó (cổng chống thoái hoá, so với `max(sàn, baseline)` đã báo cáo, không phải mục tiêu chất lượng). **Nếu thiếu một trong hai việc đó, mốc sàn không được coi là hợp lệ**: một test đỏ vì mô hình "chưa đủ giỏi" mà không có luật cho phép chính là thứ luật đó sinh ra để chặn.

**(c) Test `slow` mốc sàn do U3 viết.** Theo `unit-of-work.md` > U3 ("dựng mốc sàn AUC trong bộ test `slow`" và "Điều kiện xong: test `slow` chỉ khẳng định **nhánh xanh trên tệp báo cáo thật**"), và theo C3 > `constants.MODEL_AUC_FLOOR` ("U3 chỉ import cho test mốc sàn"). U2 giao **hằng `MODEL_AUC_FLOOR`, hàm `beats_floor` và test đơn vị hai nhánh** — U2 không viết test `slow` đó, và việc U3 chưa viết không phải thiếu sót của U2.

**Kiểm:** test đơn vị cho `beats_floor` phủ **cả hai nhánh** — dưới sàn → `False`, trên `max(sàn, baseline)` → `True` — cộng nhánh `baseline_auc > floor` để chứng minh `max` có tác dụng; `floor` ngoài `(0,1)` → `ModelError` (BR2.12). Phép kiểm của **NFR5** không nằm trong đơn vị này: test `slow` của U3 trên `data/reports/analysis.json` gọi `beats_floor(model.auc, model.baseline_auc)` và khẳng định kết quả `True`.

## TS2.6 — U2 sở hữu `src/analytics/model.py` và `report.py`; U3 chỉ đọc

**Quyết định:** đơn vị này **sửa** `src/analytics/model.py` (14 đặc trưng, `MODEL_AUC_FLOOR`, `beats_floor`, `score_item`, `validate_features` kiểm thứ tự) và `src/analytics/report.py` (`REPORT_VERSION` 2 → 3, `ModelBlock` 11 trường, chín khoá `counts`, `_model_block` kiểm đủ trường mới). U3 **không** sửa hai tệp này: nó `import` hằng số và gọi hàm, và đọc tệp qua C2.

**Vì sao ranh giới này phải rõ:** `report.py` là nơi duy nhất dựng `AnalysisReport` (ADR-008, BR2.9); nếu U3 tự dựng khối hoặc tự tính cờ, tệp báo cáo có hai nguồn và "hai cổng không thể trái nhau" mất hiệu lực. Cùng lý do, `AUC_TARGET`/`MODEL_AUC_FLOOR` thuộc U2 (TS2.5) — U3 chỉ hiện "mốc đang áp", không tự suy cờ.

**Hệ quả về hình dạng tệp:** `ModelBlock` mọc từ 7 lên **11** trường, và `counts` từ 4 lên **9** khoá. `_model_block` (`report.py:457-468`) hiện chỉ đọc bảy khoá v2 và để giá trị mặc định, nên tệp v3 thiếu `auc_tree`/`beats_baseline` vẫn ra `day-du` — đơn vị này phải làm hai chỗ đó **kiểm đủ**, để thiếu trường thật sự rơi vào `loi` (C2, `## Contract ownership rules`).

**Hai chỗ khác khai cùng sự thật `REPORT_VERSION`, phải đổi cùng lúc với nó lên 3:**
- `README.md` (mục nói tầng `stats` sinh `data/reports/analysis.json` … "phiên bản 2", khoảng dòng 57) — **U2** sửa cùng thay đổi, vì đó là tài liệu của hợp đồng C2 mà U2 sở hữu.
- Fixture `report()` của `tests/unit/test_dashboard_analysis_tab.py` (`version=2`, dòng 146) — **U3** sửa, vì tệp test đó thuộc U3; U2 phải **báo trước** trong cùng thay đổi. Fixture này không chỉ đổi số phiên bản: nó đang dựng `ModelBlock` bảy trường với bốn khoá `counts`, nên phải thành v3 đủ **11** trường và **9** khoá, nếu không nó thôi đại diện cho tệp báo cáo thật mà U3 đọc.

**Kiểm:** test đơn vị khẳng định `REPORT_VERSION == 3`; đọc một tệp v3 thiếu `auc_tree` → trạng thái `loi` (không phải `day-du`); đọc một tệp `version: 2` → `loi` kèm thông điệp, **không ném** (BR2.7); `report.py` vẫn là nơi duy nhất dựng `AnalysisReport` (`grep -rn "AnalysisReport(" src/` chỉ ra `report.py`).

## TS2.7 — Ngân sách tầng `stats` (NFR1): **< 300 s** cho trọn tầng trên dữ liệu thật

**Quyết định:** một lần `python -X utf8 -m src.pipeline run --stage stats` trên `dataset/` thật phải xong **dưới 300 s**. Ngân sách này đi vào **ba chỗ** trong cùng thay đổi, với **hai giá trị khác nhau** — 300 s cho tầng, 240 s cho bước mô hình (TS2.8):

1. `STAGE_BUDGET_SECONDS` (`tests/integration/test_u2_model_end_to_end.py:31`): `900` → **`300`**.
2. `TRAIN_BUDGET_SECONDS` (`tests/integration/test_u2_model_end_to_end.py:32`): `900` → **`240`**, theo TS2.8 — **không** phải 300.
3. `team.md` `## Deployment`: phải ghi **hai** con số tách rời — **300 s cho tầng `stats`** và **240 s cho riêng bước mô hình**; chuỗi ba con số hiện có (300 / 900 / 900) rút lại còn đúng hai. Ghi 300 cho cả hai là xoá mất ranh giới tầng/bước mà TS2.8 dựng ra, và để NFR2 (< 240 s) không còn chỗ nào khai trong bộ luật của dự án.

Cả ba chỗ sửa trong **cùng** thay đổi; hai giá trị 300 và 240 không được gộp làm một.

**Vì sao 300 s là số đúng, không phải số chặt hơn:** khung mới có 110.195 dòng hàng thay vì 96.478 đơn, tức nhiều dòng hơn, nhưng số đặc trưng và số mô hình chỉ tăng một. 300 s là ngân sách **đã dùng cho tầng `stats` ở U1** (`tests/integration/test_u1_stats_end_to_end.py:22`) — giữ cùng một con số cho cùng một tầng nghĩa là ngân sách của tầng không bị nới chỉ vì nó có thêm việc; nếu vượt, đó là tín hiệu phải xem lại truy vấn, không phải tín hiệu phải nâng số.

**Đo thế nào:** `time.perf_counter()` bọc quanh `run_stage(real_config, "stats")`, trong test **`slow`** — không đặt vào bộ nhanh, vì nó cần mart thật và sẽ tái lập `TD-09`. Một lần đo trên máy này, không phải trung bình nhiều lần; đây là ngân sách chống hồi quy, không phải SLA.

**Kiểm:** `tests/integration/test_u2_model_end_to_end.py::test_u2_model_end_to_end`, dòng `assert stage_elapsed < STAGE_BUDGET_SECONDS` với hằng sửa thành `300`.

## TS2.8 — Ngân sách riêng bước huấn luyện hai mô hình (NFR2): **< 240 s**

**Quyết định:** phần **huấn luyện** — fit logistic + fit `HistGradientBoosting` + chấm điểm + chọn ngưỡng trên ma trận grain dòng hàng — phải xong **dưới 240 s**, và nằm **trong** 300 s của TS2.7. Hằng `TRAIN_BUDGET_SECONDS = 900` (`tests/integration/test_u2_model_end_to_end.py:32`) sửa thành `240`.

**Vì sao tách khỏi ngân sách tầng:** hai con số trả lời hai câu. 300 s nói "tầng này không được chậm đi"; 240 s nói "nếu chậm, chỗ chậm là huấn luyện hay là đọc mart?". Gộp làm một là mất khả năng phân biệt đó — và 240 s < 300 s giữ lại 60 s cho phần đọc DuckDB, dựng khung và ghi tệp.

**Vì sao `HistGradientBoosting` là rủi ro thời gian chính:** nó là phần đắt nhất trong đơn vị này và là phần **không** phục vụ dự đoán (TS2.3). Nếu vượt ngân sách, thứ tự xem xét là: giới hạn `max_iter`/`early_stopping` của cây trước, rồi mới tới việc nới ngân sách — và nới thì phải sửa **có chủ đích** ở đây, ở `team.md`, và ở test, không nới ngầm.

**Đo thế nào:** `time.perf_counter()` bọc quanh lần gọi huấn luyện **thứ hai** trên cùng dữ liệu (lần đầu đã làm nóng cache đọc đĩa), cùng test `slow` đó.

**Kiểm:** `tests/integration/test_u2_model_end_to_end.py`, dòng `assert model_elapsed < TRAIN_BUDGET_SECONDS` với hằng sửa thành `240`.

## TS2.9 — Cổng phủ 80% và bộ cổng kiểm giữ nguyên, không nới (NFR3)

**Quyết định:** không khai lại ngưỡng phủ ở đây và không hạ nó. Cổng duy nhất là `python -X utf8 -m pytest --cov=src --cov-fail-under=80` ở `ci.yml:53`, chạy trên **toàn bộ** bộ test (nhanh + `slow`). Ba điều cấm đi kèm, đều đã là luật của dự án và áp nguyên cho đơn vị này:
1. Không đặt `--cov-fail-under` lên riêng bộ nhanh, không hạ ngưỡng để một bước pass (`project.md` `## Forbidden`; `tests/unit/test_ci_config.py::test_the_coverage_gate_is_not_weakened` canh đúng điều này)..
2. Không thêm `per-file-ignores` mới trong `ruff.toml` cho mã mới; không thêm `# noqa` "chỉ lần này".
3. Không thêm kiểm kiểu tĩnh (`mypy`/`pyright`) — quyết định đã chốt, không phải thiếu sót. Type hint vẫn giữ theo quy ước (`from __future__ import annotations`).

**Hệ quả cụ thể cho đơn vị này:** các tệp **mới** của U2 phải vào **danh sách khai tay** của `ruff format --check` (`ci.yml:35`) **cùng lúc** với việc tạo tệp — danh sách đó không tự cập nhật, và một tệp ngoài danh sách là một tệp không ai kiểm định dạng. Tệp mới đã biết chắc là **mô-đun `ModelPersistence`** (khối riêng theo ADR-001, chịu `pickle` + metadata); `src/analytics/model.py` và `tests/integration/test_u2_model_end_to_end.py` **đã có** trong danh sách nên không thêm lại, còn `score_item` là phần sửa trong `model.py` chứ không phải tệp mới. **Đường dẫn cụ thể của `ModelPersistence` và danh sách tệp test mới sẽ chốt ở Code Generation**; khi đó mỗi tệp được thêm vào `ci.yml:35` ngay trong thay đổi tạo ra nó, không để lại một lượt "bổ sung danh sách" sau.

**Kiểm:** `ci.yml:53` giữ nguyên chuỗi `--cov-fail-under=80`; `tests/unit/test_ci_config.py` xanh — nó canh **hai** danh sách khai tay ấy: `test_every_new_file_is_in_the_manual_format_list` (tệp mới phải có mặt trong danh sách format, đối chiếu `NEW_FILES`) và `test_both_trigger_lists_*` (nhánh của đợt có trong cả hai danh sách trigger); `ruff check .` và `ruff format --check` sạch trên danh sách đã cập nhật; `requirements.txt` không có gói kiểm kiểu.

## TS2.10 — Đường gọi duy nhất là `run --stage stats`; không thêm lệnh con CLI

**Quyết định:** mọi thứ đơn vị này sinh ra — báo cáo v3 và tệp mô hình — chỉ được sinh bởi `python -X utf8 -m src.pipeline run --stage stats`. Không có lệnh con mới, không có cờ dòng lệnh cho đường dẫn mô hình, không có bước "build model" riêng. `STAGES` giữ **5** tên, CLI giữ **3** lệnh con (`run`, `micro-batch`, `replay`).

**Vì sao:** tệp mô hình và báo cáo là hai nửa của **cùng một** lần chạy tầng `stats`; tách chúng ra hai lệnh là tạo được trạng thái mô hình mới đi cùng báo cáo cũ — đúng thứ C2/C2b được thiết kế để không xảy ra. `RQ-04` cũng đã chốt điều này.

**Hệ quả đã biết:** `_run_all` hiện **không** chạy `stats` (`TD-11`), nên CI vẫn phải có hai bước riêng (`ci.yml:40` và `:45`). Đơn vị này không sửa `_run_all` — quyết định đó thuộc Delivery Planning (OQ-3).

**Kiểm:** `tests/unit/test_pipeline_stages.py` canh `STAGES` đủ 5 tên, `choices` của `--stage` khớp `STAGES | {"all"}`, và đúng **3** lệnh con; `grep -n "models_dir" src/pipeline/cli.py` không có kết quả.

## Điều tài liệu này không quyết

Không quyết phiên bản Python mới hơn, không quyết dịch vụ đám mây, không quyết hàng đợi hay scheduler, không quyết định dạng lưu khác cho mart. Dự án chạy từ mã nguồn trên máy một người; mọi lựa chọn hạ tầng nằm ngoài phạm vi đợt này. Cũng không quyết việc `--stage all` có nên bao gồm `stats` hay không — đó là OQ-3, thuộc Delivery Planning.

## Ánh xạ NFR gốc sang yêu cầu chi tiết của đơn vị

Mỗi NFR của Requirements Analysis được chi tiết hoá thành một yêu cầu con ở đơn vị này; cột giữa là mã con dùng cho truy vết của các stage sau.

| NFR gốc | Mã con | Yêu cầu chi tiết |
|---|---|---|
| `NFR1` | `NFR1.1` | Tầng `stats` chạy trong **300 s**; hằng số `STAGE_BUDGET_SECONDS` trong `tests/integration/test_u1_stats_end_to_end.py` giữ 300, không nới. Chi tiết ở `TS2.7`. |
| `NFR2` | `NFR2.1` | Bước huấn luyện hai mô hình **< 240 s**; `TRAIN_BUDGET_SECONDS` trong `tests/integration/test_u2_model_end_to_end.py` từ 900 xuống **240**, `team.md` ghi 240 cho bước mô hình. Chi tiết ở `TS2.8`. |
| `NFR3` | `NFR3.1` | Cổng phủ `pytest --cov=src --cov-fail-under=80` tại `ci.yml:53` giữ nguyên trên **toàn bộ** bộ test; không hạ ngưỡng, không tách cổng sang bộ nhanh. Chi tiết ở `TS2.9`. |
| `NFR4` | `NFR4.1` | U2 **không** đổi mart: 5 KPI, 9 bảng mart và 11 view giữ nguyên; mart chỉ đọc. Chi tiết ở `SEC2.1`. |
| `NFR5` | `NFR5.1` | Mốc sàn `max(MODEL_AUC_FLOOR, baseline_auc)`: U2 giao hằng `MODEL_AUC_FLOOR` (**0,55**) và hàm thuần `beats_floor(auc, baseline_auc, floor)`; test `slow` mốc sàn do **U3** viết trên báo cáo thật. Đây là **ngoại lệ có chủ đích** với luật "không đặt AUC làm kỳ vọng test", phải ghi qua nghi thức learnings và sửa `project.md` `## Forbidden`, nếu không thì mốc sàn không hợp lệ. Chi tiết ở `TS2.5`. |
| `NFR6` | `NFR6.1` | `N/A` — đơn vị không có bề mặt giao diện; tiếp cận thuộc `u3-prediction-ui`. |

