# CI/CD Pipeline — u2-features-and-models

Đơn vị: `u2-features-and-models` (kind `library`). Nguồn: `../../../inception/domain-design/components.md` (khối `ModelModule`, `ReportContract`, `ModelPersistence` — quyết định U2 sở hữu `model.py` và `report.py`, và U3 chỉ đọc), `../nfr-design/logical-components.md` (LC2.1–LC2.17), `../nfr-requirements/tech-stack-decisions.md` (TS2.1–TS2.10), `../nfr-requirements/security-requirements.md` (SEC2.1–SEC2.7), `../functional-design/functional-spec.md` (W1–W6), `.github/workflows/ci.yml`, `tests/unit/test_ci_config.py`, `pytest.ini`, `.gitignore`.

**Kết luận ngắn: không có hạ tầng nào để dựng.** Pipeline đã tồn tại và đang chạy; đơn vị này không thêm môi trường, không thêm dịch vụ, không thêm bước CI. Tài liệu này chỉ ghi U2 **chạm vào chỗ nào của pipeline hiện có**, chỗ nào phải sửa cùng lúc với mã, và chỗ nào cố ý để nguyên.

Khác `u1-mart-and-baseline`, U2 **không có lời gọi mạng nào** — không API, không đối tác, không cache từ xa (SEC2.5). Phần hạ tầng ở đây vì thế rỗng tuyệt đối, không phải "rỗng trừ một ngoại lệ".

## Pipeline hiện có — 9 bước, và U2 chạm vào đâu

`.github/workflows/ci.yml` dài **58 dòng**: `runs-on: windows-2022` (dòng 18, ghim image), Python `"3.13"` + `cache: pip` (dòng 22-25), trigger `push` **và** `pull_request` trên ba nhánh `main`, `feature/update-ui-ux`, `feature/analysis-and-models` (dòng 3-13).

| # | Bước (dòng trong `ci.yml`) | U2 có đổi bước này? |
|---|---|---|
| 1 | `actions/checkout@v4` (20) | Không |
| 2 | `actions/setup-python@v5`, 3.13, cache pip (22-25) | Không |
| 3 | `pip install -r requirements.txt` (27-28) | **Không** — vẫn đúng **12** gói ghim; không `joblib`, không `shap`, không `import numpy` trực tiếp (TS2.1) |
| 4 | `ruff check .` + `ruff format --check` trên danh sách khai tay (30-35) | **Có** — mọi tệp mới phải được thêm vào danh sách ở dòng 35, cùng lúc với việc tạo tệp (CP2.1) |
| 5 | `run --stage all` (37-40) | **Không** — U2 không sửa tầng nào của bước này; nó là cổng giữ mart, và U2 giữ nó bằng cách không chạm vào (CP2.5) |
| 6 | `run --stage stats` (42-45) | **Có** — nơi duy nhất sinh báo cáo v3 **và** tệp mô hình, và là nơi câu truy vấn dựng khung mới chạy trên dữ liệu thật (CP2.2) |
| 7 | `pytest -m "not slow"` (47-48) | **Có** — thêm test đơn vị (`beats_floor` hai nhánh, `score_item`, `ModelPersistence`, `REPORT_VERSION == 3`); bộ này vẫn phải xanh |
| 8 | `pytest --cov=src --cov-fail-under=80` (50-53) | **Không đổi cổng** — ngưỡng 80% và phạm vi "toàn bộ bộ test" giữ nguyên (CP2.1); nhưng đây là nơi bộ `slow` chạy, tức nơi ngân sách tầng 300 s — khai ở test của **U1** và U2 phải về cùng con số — cùng 240 s của bước mô hình được đo (CP2.3) |
| 9 | Smoke nạp `config/integration-sources.yaml` (55-58) | Không |

**Một câu bình luận trong workflow sẽ cũ đi sau U2, và nên đọc đúng nghĩa.** `ci.yml:44` ghi "Không test nào đọc tệp bước này sinh ra". Sau U2, test `slow` của đơn vị **có** đọc `data/reports/analysis.json` tại đúng đường dẫn bước 6 ghi (`read_report(report_path(real_config))`), nhưng nó tự sinh lại tệp đó trong cùng một test trước khi đọc. Điều bước 6 bảo đảm vì thế vẫn đúng, chỉ hẹp hơn câu chữ: không test nào **phụ thuộc** vào tệp do bước 6 để lại.

## CP2.1 — Tệp mới phải vào **hai** danh sách khai tay, và test chỉ canh được một chiều

**Vấn đề.** Bước 4 chạy `ruff check .` trên toàn repo nhưng `ruff format --check` chỉ trên **danh sách khai tay** ở `ci.yml:35` — hiện **38 mục**, hai trong số đó là thư mục (`src/integration`, `src/linkage`) (`TD-20`; `team.md` ghi "34 mục", con số đó đã cũ). Một tệp mới không có trong danh sách thì **không được kiểm định dạng**, và không có gì đỏ lên.

**Yêu cầu.** Mỗi tệp `.py` mới của U2 phải được thêm vào **cả hai** chỗ trong **cùng một thay đổi** tạo ra nó:
1. danh sách của `ruff format --check` ở `ci.yml:35`;
2. tuple `NEW_FILES` ở `tests/unit/test_ci_config.py:14-29` (hiện **14** mục).

Tệp **đã có** trong danh sách nên không thêm lại: `src/analytics/model.py`, `src/analytics/report.py`, `src/analytics/service.py`, `tests/unit/test_analytics_model.py`, `tests/integration/test_u2_model_end_to_end.py`. Tệp mới đã biết chắc là mô-đun `ModelPersistence` (LC2.13) cùng các tệp test mới của nó; đường dẫn cụ thể chốt ở Code Generation (TS2.9), nhưng việc thêm vào hai danh sách không được dời sang một lượt sau.

**Cổng phủ 80% không đổi, và nó không phải một danh sách khai tay.** `ci.yml:53` chạy `python -X utf8 -m pytest --cov=src --cov-fail-under=80` trên **toàn bộ** bộ test — bộ nhanh **và** bộ `slow` — với ngưỡng 80% giữ nguyên: U2 không hạ ngưỡng, không đặt cờ lên riêng bộ nhanh, không tách cổng sang bước khác để cho một bước pass (NFR3.1). Việc U2 thêm mã và test làm cổng này **khó giữ hơn** (mẫu số lớn hơn), không phải dễ hơn — nên đây cũng là lý do thứ hai để mọi mô-đun mới phải có test riêng ngay từ đầu, chứ không phải nợ lại.

**Cái bẫy, nói thẳng.** `test_every_new_file_is_in_the_manual_format_list` chỉ khẳng định `set(NEW_FILES) <= targets`. Nghĩa là:
- thiếu trong `ci.yml:35` ⇒ **đỏ** ở bước 7;
- **có trong `ci.yml:35` mà thiếu `NEW_FILES` ⇒ không test nào đỏ** — và cũng không có bước CI nào khác đọc `NEW_FILES`. Cặp hai danh sách chỉ được giữ với nhau bởi một phép so một chiều.

**Hệ quả nếu quên.** Tệp mới vào repo mà không ai kiểm định dạng; lần sau có người dời/đổi tên tệp, `test_the_format_list_has_no_entry_pointing_outside_the_repository` (`:82-85`, khẳng định `(ROOT / target).exists()`) mới đỏ — ở một thay đổi không liên quan, với thông điệp không nói vì sao đường dẫn cũ còn nằm đó.

**Cách kiểm.** `python -X utf8 -m pytest tests/unit/test_ci_config.py -q` (chạy ở bước 7, và chạy được cục bộ trong bộ nhanh), rồi `ruff format --check <danh sách>` ở bước 4. Hai phép kiểm này khác nhau: cái đầu canh **danh sách**, cái sau canh **định dạng thật**.

## CP2.2 — Bước 6 là chỗ duy nhất sinh tệp mô hình, và không có artifact phát hành

**Vấn đề.** Một tệp mô hình là đúng loại thứ mà pipeline thường đóng gói và tải lên như artifact — và ở dự án này làm thế là sai.

**Yêu cầu.** `python -X utf8 -m src.pipeline run --stage stats` (`ci.yml:45`) là **đường duy nhất** sinh ra cả báo cáo v3 lẫn tệp mô hình (TS2.10). Ba điều đi kèm, đều đã đúng và phải giữ:
1. `data/models/` thừa hưởng `.gitignore:7` (`data/`) — **không** thêm ngoại lệ, không `git add -f` (SEC2.2);
2. workflow **không** có `actions/upload-artifact` và không cache tệp mô hình — 9 bước ở trên là toàn bộ, không có bước thứ mười nào bị bỏ sót;
3. không có lệnh con CLI mới, không cờ dòng lệnh cho đường dẫn mô hình (TS2.10, SEC2.7).

**Hệ quả nếu quên.** Commit tệp mô hình là tạo nguồn sự thật thứ hai cho cùng một mô hình, đồng thời đưa vào repo một `pickle` **có nguồn ngoài pipeline** — đúng thứ SEC2.3 chặn. Tải nó lên làm artifact còn tệ hơn: `pickle` gắn với phiên bản thư viện đã sinh ra nó (TS2.4), nên máy nhận không dùng được mà vẫn tưởng dùng được.

**Cách kiểm.** `git check-ignore -v data/models/logistic.pkl` phải in ra quy tắc `.gitignore:7:data/`; `git ls-files data/models` phải rỗng; và đọc `ci.yml` phải thấy đúng 9 bước, không bước nào tên `upload`. Trong CI, mỗi lần chạy sinh lại tệp từ đầu — tệp không được mang theo giữa các lần chạy, và đó là chủ ý.

## CP2.3 — Ngân sách thời gian là một phần của cổng, nhưng nó đang bị khai ở **hai** tệp

**Vấn đề.** Ngân sách tầng `stats` **không phải** một con số mới của U2: nó đã được cưỡng chế sẵn từ trước, ở một tệp khác, trên cùng tầng, cùng marker `slow`, cùng bước 8. Đọc đúng sự thật đó trước, rồi mới nói U2 làm gì.

| Tệp (dòng) | Hằng | Hiện | Đo quanh cái gì | Câu khẳng định |
|---|---|---|---|---|
| `tests/integration/test_u1_stats_end_to_end.py:22` | `STAGE_BUDGET_SECONDS` | **`300`** (đã có sẵn) | `run_stage(real_config, "stats")` (`:42-44`); test còn chạy tầng này **lần thứ hai** ở `:125` | `:48` `assert elapsed < STAGE_BUDGET_SECONDS` |
| `tests/integration/test_u2_model_end_to_end.py:31` | `STAGE_BUDGET_SECONDS` | `900` | `run_stage(real_config, "stats")` (`:45-47`) | `:50` `assert stage_elapsed < STAGE_BUDGET_SECONDS` |
| `tests/integration/test_u2_model_end_to_end.py:32` | `TRAIN_BUDGET_SECONDS` | `900` | lần gọi `train_model` **thứ hai** (`:89-91`) | `:93` `assert model_elapsed < TRAIN_BUDGET_SECONDS` |

Hai dòng đầu **đo cùng một thứ**: độ dài của một lần `run_stage(config, "stats")` trên dữ liệu thật — nhưng bằng hai con số khác nhau. Đây là **một sự thật bị khai hai nơi**, và hệ quả không đối xứng: bộ `slow` chạy cả hai, `300` là con số thấp hơn, nên **`300` ở U1 mới là ngân sách có hiệu lực**; con số `900` ở U2 không cưỡng chế thêm được gì.

**Yêu cầu.** Ba việc, việc thứ nhất là sửa chỗ khai trùng:

1. **Hạ `STAGE_BUDGET_SECONDS` ở `tests/integration/test_u2_model_end_to_end.py:31` từ `900` xuống `300`** — hoặc bỏ hẳn hằng trùng ở U2 và để U1 giữ bản duy nhất, nếu test của U2 vẫn đọc rõ khi mượn hằng từ U1. Nếu giữ cả hai con số thì phải **ghi chú ngay tại hằng của U2** rằng nó đo **cùng một thứ** với `test_u1_stats_end_to_end.py:22`, và hai con số phải bằng nhau; lệch nhau là chỗ trôi tiếp theo, và lần trôi đó sẽ không ai thấy.
2. **Hạ `TRAIN_BUDGET_SECONDS` từ `900` xuống `240`**, đặt ở đúng chỗ đo riêng của bước mô hình (NFR2.1). Con số này **không** thay cho ngân sách tầng và không được suy ra từ nó.
3. **Ghi `300 s` và `240 s` vào `team.md` `## Deployment` qua nghi thức learnings ở cổng stage**, không phải bằng một dòng sửa tay trong thay đổi chức năng. `team.md:3-6` tự khai các mục practices được điền ở cổng ("Edit at the gate, not directly"), nên sửa thẳng ở đây là bỏ qua bước ghi nhận và làm bản ghi quyết định lệch khỏi bộ luật. Hiện `team.md:267-268` ghi "300 s cho tầng `stats`, 900 s cho tầng và 900 s cho riêng bước mô hình" — câu đó vừa tự lặp vừa tự mâu thuẫn, nên nó phải được thay bằng đúng **hai** con số tách rời; nếu cổng đó chưa chạy thì đây là mục mở có tên bước chịu trách nhiệm, không phải việc đã xong.

Hai điều phải nói kèm, nếu không các con số bị đọc sai:
- **Cả ba phép đo nằm trong test `slow`**, tức chúng chỉ chạy ở **bước 8**. Bước 7 dùng `-m "not slow"` nên **không** đo gì — một hồi quy thời gian không làm bước 7 đỏ. Việc tách bộ nhanh/bộ chậm đã có sẵn trong `pytest.ini:4` (marker `slow`), U2 không sửa `pytest.ini`.
- **240 s không phải "riêng phần fit".** Lần gọi được đo là `train_model`, hàm này đọc mart **trước** rồi mới huấn luyện, nên 240 s bao gồm đọc DuckDB + dựng khung grain dòng hàng + fit hai mô hình + chấm điểm + chọn ngưỡng (LC2.16). Phần **ghi** hai tệp nằm ngoài lần đo đó và chỉ được tính trong 300 s của tầng.

**Hệ quả thật — và là chỗ cách đọc cũ sai.** Khi U2 dựng khung grain dòng hàng và huấn luyện mô hình thứ hai, tầng `stats` dài ra. Test đỏ trước là **`test_u1_stats_end_to_end`**, không phải `test_u2_model_end_to_end`: U1 đo cùng lời gọi ấy với ngưỡng `300` và còn chạy tầng đó hai lần, còn U2 đo với ngưỡng `900`. Nghĩa là **canary của NFR1.1 nằm trong đơn vị khác**. Người thấy test của U1 đỏ mà đi tìm nguyên nhân trong mã U1 sẽ tìm sai chỗ — mã U1 không đổi; thứ U2 đụng là **thời gian** của tầng `stats`, chứ không phải dữ liệu mart (CP2.5 vẫn đúng: U2 không sửa `src/integrate|clean|ingest|quality`). Phải nói trước điều này, vì dấu hiệu đầu tiên sẽ hiện ra ở một tệp mà đợt này không ai định sửa.

**Hệ quả nếu quên.** Nếu để nguyên `900` ở U2 mà không nói U1 đã có `300`: (a) ngân sách thật vẫn là 300 và U1 vẫn là cái đỏ, nhưng tài liệu chỉ vào U2 — người đọc đi sai chỗ và mất thời gian đổ lỗi cho mã U2; (b) hai con số cùng đo một thứ sẽ trôi khỏi nhau ở thay đổi sau, và `900` sẽ được đọc như "ngân sách của đợt này" trong khi nó chưa bao giờ có hiệu lực. Còn nếu nới ngầm một trong hai hằng để một lần chạy pass: cổng thành trang trí — muốn nới thì sửa **có chủ đích** ở cả hai test, ở `team.md` (qua cổng, không sửa tay) và ở `logical-components.md` LC2.16 cùng lúc.

**Cách kiểm.** `python -X utf8 -m pytest -m slow tests/integration/test_u1_stats_end_to_end.py tests/integration/test_u2_model_end_to_end.py -q` trên dữ liệu thật; CI chạy cả hai ở bước 8 — test của U1 nằm trong cùng bộ `slow`, không phải một bước riêng. Đây là ngân sách chống hồi quy, không phải SLA: một lần đo trên một máy, không trung bình nhiều lần, không APM, không metrics endpoint nào trong sản phẩm.

## CP2.4 — `--stage all` không chạy `stats`, nên CI phải giữ **hai** bước riêng

**Vấn đề.** Hai bước 5 và 6 trông như một bước bị viết hai lần; người sửa workflow rất dễ gộp lại cho gọn.

**Sự thật trong mã.** `STAGES` có **5** tên, gồm `stats` (`src/pipeline/stages.py:24`), nhưng `_run_all` (`:91-177`) ghi **sáu** `StageResult` — `ingest`, `clean`, `quality`, `integrate`, `linkage`, `analyze` — trong đó `quality` và `linkage` không nằm trong `STAGES`, và **`stats` không được gọi** (`TD-11`). Vì vậy `--stage all` **không** sinh báo cáo và **không** sinh tệp mô hình.

**Yêu cầu.** Giữ nguyên cả `ci.yml:40` và `ci.yml:45`; U2 **không** sửa `_run_all`. Việc `stats` có nên nằm trong `all` hay không là OQ-3, thuộc Delivery Planning (TS2.10) — không phải thứ một đơn vị tự quyết trong lúc code.

**Hệ quả nếu quên.** Bỏ bước 6 vì tin rằng bước 5 đã phủ nó: trong CI, tầng `stats` vẫn được chạy nhưng chỉ qua test `slow` ở bước 8 — và trên máy người làm, `--stage all` là lệnh hay chạy trước khi mở dashboard, nên báo cáo sẽ cũ và tệp mô hình sẽ vắng, đúng trạng thái "mô hình chưa sẵn" mà U3 phải hiển thị. Còn nếu gộp `stats` vào `_run_all` ngay trong U2: `--stage all` đổi nghĩa — một lệnh "dựng dữ liệu" bắt đầu ghi báo cáo và tệp mô hình — và đó là thay đổi hợp đồng CLI mà `tests/unit/test_pipeline_stages.py` đang canh.

**Cách kiểm.** `tests/unit/test_ci_config.py::test_stats_stage_runs_after_the_data_build_and_before_the_tests` (`:88-95`) khẳng định thứ tự `all` → `stats` → bộ nhanh trong danh sách bước. Thứ tự đó không phải thẩm mỹ: bộ nhanh chưa hermetic (`TD-09`), nên nó cần `warehouse/` và `data/marts/` do bước 5 dựng, và tầng `stats` đọc đúng hai thứ đó nên phải đứng sau.

## CP2.5 — Bước 5 không đổi, và đó là cách NFR4 được giữ ở phía CI

**Vấn đề.** U2 **viết lại câu truy vấn dựng khung huấn luyện** (LC2.2). Kiểu hỏng nguy hiểm nhất của một phép join 1:N không gộp trước không phải một con số xấu mà là **một mart khác** — và câu hỏi đúng là: bước nào của CI bắt được điều đó?

**Trả lời thẳng: không bước nào bắt được, và đó là lý do phải giữ nó bằng cách khác.** Không có bước CI nào chạy câu truy vấn của U2 rồi so với mart; `StarSchemaValidator` (9 check số dòng) và `KpiReconciler` (5 KPI) chạy **trong `integrate`**, tức trong bước 5, **trước** bước 6 và không đọc gì của U2.

**Yêu cầu.** Ba điều, đều là điều kiện để NFR4 đứng:
1. U2 **không** sửa tệp nào dưới `src/integrate/`, `src/clean/`, `src/ingest/`, `src/quality/` — mart chỉ được đọc (SEC2.1);
2. mọi lần đọc của U2 đi qua kết nối `read_only=True` của `AnalyticsService`, nên "đừng ghi vào mart" là một lỗi `duckdb` nếu ai đó thử, không phải một quy ước;
3. bốn bộ đếm quần thể của U2 — 110.195 dòng hàng / 96.476 đơn / 8.713 dòng trễ / 2 đơn thiếu carrier date — khẳng định **khung huấn luyện**, và **không thay** phép kiểm mart: chúng không nói gì về 9 bảng mart hay 11 view.

**Hệ quả nếu quên.** Nếu ba cột mới được thêm bằng cách sửa `integrate` thay vì sửa truy vấn của tầng `stats`, bước 5 sẽ đỏ — và lỗi sẽ hiện ra như một hồi quy mart trong đơn vị của người khác. Nếu U2 đọc mart ở chế độ ghi, CI có thể sửa `warehouse/olist.duckdb` mà không cổng nào đọc lại kết quả.

**Cách kiểm.** Phạm vi `git diff --stat` của đơn vị này (không có tệp dưới bốn thư mục trên); `grep -rn "read_only=False" src/analytics/` không có kết quả; và bước 5 xanh là bằng chứng mart không bị đụng — đúng nghĩa "không đổi", không phải "đã kiểm".

## CP2.6 — Mốc sàn AUC không có bước CI riêng, và phần kiểm của nó nằm ở hai bộ khác nhau

**Vấn đề.** NFR5 đặt một ngưỡng trên `auc` (`MODEL_AUC_FLOOR = 0,55`, so với `max(sàn, baseline_auc)`). Một tài liệu pipeline phải nói rõ ngưỡng đó được cưỡng chế ở đâu — và không được ngầm cho rằng CI có một bước kiểm AUC, vì nó không có.

**Yêu cầu.** U2 **không** thêm bước CI nào, không thêm dòng `run` nào. Phần của U2 là hằng `MODEL_AUC_FLOOR` cạnh `AUC_TARGET` trong `src/analytics/model.py`, hàm thuần `beats_floor`, và **test đơn vị hai nhánh** — chúng chạy ở **bước 7**. Test `slow` khẳng định mốc sàn trên tệp báo cáo thật thuộc **U3** và sẽ chạy ở **bước 8**, nơi bộ `slow` chạy (TS2.5(c)).

Điều kiện đi kèm không nằm trong pipeline: ngoại lệ này so với luật "không đặt AUC làm kỳ vọng của test viết trước" (`project.md` `## Forbidden`) chỉ hợp lệ khi được ghi qua **nghi thức learnings** ở cổng NFR Requirements **và** câu chữ `project.md` được sửa cho hết mâu thuẫn. Không bước CI nào kiểm được việc đó — nó là cổng của stage, không phải của workflow.

**Trạng thái của ngoại lệ hiện tại: chưa được ghi lại, nên mốc sàn chưa có hiệu lực.** Trên đĩa, `aidlc/spaces/default/memory/project.md:87` **vẫn còn** nguyên câu NEVER cấm đặt AUC (hay precision/recall/ngưỡng) làm kỳ vọng của một test viết trước, và `## Corrections` của cả `project.md` lẫn `team.md` không có dòng nào về ngoại lệ này. Vì vậy mốc sàn **chỉ** hợp lệ sau khi qua nghi thức learnings và `project.md` được sửa; trước đó nó là một điều kiện mở chặn, không phải một điều kiện giả định đã xong — và không ai được dựa vào nó như một cổng đã có luật cho phép.

**Hệ quả nếu quên.** Nếu U2 tự viết test `slow` mốc sàn, bước 8 sẽ đỏ vì "mô hình chưa đủ giỏi" — đúng kiểu hỏng mà luật đó sinh ra để chặn, và người làm sẽ bị đẩy vào việc chỉnh ngưỡng cho test xanh. Nếu ngoại lệ không được ghi lại, mốc sàn là một cái cổng không có luật cho phép: ở trạng thái hiện tại nó **chưa có hiệu lực**, nên chưa ai được dựa vào nó để chặn hay để cho qua.

**Cách kiểm.** `tests/unit/test_analytics_model.py` (đã có trong `ci.yml:35`) phủ cả ba nhánh của `beats_floor`; sau U3, `grep -rln "beats_floor" tests/integration/` phải trả về **một** tệp, không phải hai.

## Điều U2 không làm

- **Không thêm bước deploy.** "Phát hành" của dự án là chạy từ mã nguồn sau khi CI xanh; không có môi trường thứ hai để deploy tới, và một bước deploy luôn xanh còn tệ hơn không có bước nào.
- **Không thêm dịch vụ nào:** không container, không queue, không scheduler, không worker, không model registry, không endpoint. U2 chạy như một phần của hai tiến trình đã có — `run --stage stats` (W1–W5) và tiến trình dashboard (W6) — và "triển khai" nghĩa là chạy từ mã nguồn, không có bước đóng gói.
- **Không đổi runner hay phiên bản Python:** `windows-2022` (`ci.yml:18`) và `3.13` (`ci.yml:24`) giữ nguyên, cache pip giữ nguyên.
- **Không đổi danh sách nhánh:** ba nhánh ở `ci.yml:5-8` và `10-13` đã gồm `feature/analysis-and-models` — nhánh của đợt này. U2 không mở nhánh mới; nếu có, phải thêm vào **cả** hai danh sách cùng lúc với việc tạo nhánh.
- **Không thêm `per-file-ignores`** trong `ruff.toml`: năm mục hiện có (`:23`, `:26-29`) là nợ cũ có ghi chú, không phải mẫu để noi theo. Mã mới cũng không thêm `# noqa` "chỉ lần này".
- **Không thêm kiểm kiểu tĩnh** (`mypy`/`pyright`) và không thêm gói nào vào `requirements.txt` (TS2.1, TS2.9).

## Điều tài liệu này không thiết kế

Không VPC, không IAM, không container registry, không môi trường staging/production, không giám sát hạ tầng, không chứng chỉ, không sao lưu. Không có gì để đặt chúng lên: dự án chạy trên một máy, một người, từ mã nguồn. `infrastructure-specification.md` và `monitoring-design.md` không được sinh cho đơn vị này vì `kind: library` — và với U2 thì càng đúng, vì đơn vị này không có lời gọi mạng nào để mà giám sát.
