# Thực hành của nhóm — Olist E-commerce Data Pipeline

> Bản chốt để trình cổng xác nhận, dựng từ bằng chứng tĩnh tại commit
> `ea77bdf88d1431de11c36e1b739972bd594063f0` (xem `evidence.md`) và sáu quyết định của
> người làm tại buổi phỏng vấn (`practices-discovery-questions.md`). Mọi điểm bằng chứng
> không trả lời được đã chốt; phần còn chưa chắc nằm ở `evidence.md`, mục "Còn chưa chắc".

## Way of Working

- **Một người làm, một người quyết định.** Chúng tôi không có review chéo, không có người phê duyệt thứ
  hai, không có quy ước "mỗi thay đổi một nhánh". Cổng tự động duy nhất là CI. Lịch sử git chỉ có 14 commit
  trên một dòng công việc, và lần hợp nhất duy nhất là gộp cả nhánh nâng cấp vào `main`
  (`9ed73e2 chore: hợp nhất nhánh nâng cấp tích hợp và giao diện vào main`) — không có nhánh ngắn hạn nào
  được hợp nhất qua pull request có review. (`git log --oneline -15`;
  `ideation/approval-handoff/decision-log.md` dòng 29 — `D-23`.)
- **Chúng tôi làm việc trên một nhánh dài hơi của đợt, không phải trên `main`.** Hiện tại là
  `feature/analysis-and-models` (đi trước `main` 1 commit). Trunk vẫn là `main`; nhánh đợt chỉ để gom thay
  đổi rồi hợp nhất một lần — không phải nhánh cho từng đơn vị công việc.
- **Mở nhánh là một việc hai bước: tạo nhánh, rồi thêm nhánh đó vào danh sách trigger của CI** (phỏng vấn
  Q1 = A). `.github/workflows/ci.yml` khai tay `on.push.branches` và `on.pull_request.branches`; hiện có
  `main` và `feature/update-ui-ux`, nên đợt này **bổ sung `feature/analysis-and-models`** vào **cả hai**
  danh sách. Chúng tôi không chấp nhận "đợt này không có cổng tự động": một nhánh không có trong danh sách
  trigger là một nhánh làm việc không có ai kiểm. Vì danh sách khai tay, việc thêm nhánh được làm cùng lúc
  với việc đặt tên nhánh, không để lại sau — và đi kèm là dòng trigger trong `README.md` mục "CI", nơi đang
  chép lại đúng hai nhánh cũ.
- **Thông điệp commit theo Conventional Commits là thói quen đã thành nếp, chưa thành luật.**
  11 trong 14 commit gần nhất có tiền tố (`feat:`, `fix:`, `chore:`); ba commit cũ (`first commit`,
  `Update plan U3`, `Remove aidlc v1`) thì không. Chúng tôi giữ ở mức khuyến khích, không chặn commit vì
  thiếu tiền tố.
- **Một đơn vị công việc chỉ xong khi test end-to-end của nó xanh trên dữ liệu thật.** Ba Unit của đợt
  trước đều có test tích hợp riêng chạy toàn pipeline từ `dataset/`:
  `tests/integration/test_u1_end_to_end.py`, `test_u2_end_to_end.py`, `test_u3_end_to_end.py`, cộng
  `tests/data_quality/test_real_dataset.py` khẳng định dị thường trên CSV thật. Đây là thực hành mạnh
  nhất mà bằng chứng xác lập được, và đợt này là chỗ nó phải gánh nhiều nhất — xem
  `## Walking Skeleton`.
- **Trước khi commit chúng tôi chạy bộ nhanh, sau khi push CI chạy phần còn lại.** Cục bộ:
  `python -X utf8 -m pytest -m "not slow"`. Trên CI: `ruff check .` → `ruff format --check` (danh sách tệp
  khai trong `ci.yml:33`) → `python -X utf8 -m src.pipeline run --stage all` → bộ nhanh → cổng phủ 80% →
  smoke nạp `config/integration-sources.yaml`.
- **Không hồi quy là điều kiện, không phải mong muốn.** 5 KPI baseline (doanh thu delivered
  15.419.773,75 BRL; 96.478 đơn delivered; AOV 159,83 BRL; 7.826 đơn trễ; 8,11% tỷ lệ trễ), số dòng của
  9 bảng nguồn, số dòng 11 bảng mart và 11 view DuckDB là hợp đồng cứng, được `KpiReconciler`,
  `StarSchemaValidator` và test tích hợp khẳng định lại. Đợt này chạm lớp phân tích nên hợp đồng đó vẫn
  nguyên hiệu lực.
- **Quyết định được ghi thành văn bản trong workspace AI-DLC**, không chỉ trong đầu: mỗi intent có record
  riêng dưới `aidlc/spaces/default/intents/<YYMMDD>-<label>/` (state, decision log, câu hỏi, artifact theo
  tầng).
- **Thứ tự thi công theo phụ thuộc dữ liệu, không theo mức độ hấp dẫn của giao diện.** Đợt này
  (`ideation/scope-definition/scope-document.md` §4): kiểm định thống kê trước (cho kết quả thấy được sớm
  nhất), mô hình sau (cần dựng đặc trưng và kiểm rò rỉ), hiển thị trên dashboard cuối cùng (khi báo cáo
  đã có hình dạng ổn định). Mỗi phần được làm **trọn vẹn** rồi mới sang phần kế tiếp (phỏng vấn Q2 = B) —
  chi tiết ở `## Walking Skeleton`.
- **Phạm vi do một người chốt và ghi lại trước khi làm.** Mỗi hạng mục có mức (Bắt buộc / Nên có) và danh
  sách "Ngoài phạm vi"; mở rộng ra ngoài danh sách đó là thay đổi phạm vi, phải chốt lại chứ không tự
  quyết trong lúc code.

## Walking Skeleton

- **Đợt này chúng tôi KHÔNG dựng lát cắt mỏng chạy xuyên suốt trước** (phỏng vấn Q2 = B, trả lời thẳng
  cho câu hỏi "có dựng lát cắt mỏng trước không": **không**). Chúng tôi làm trọn vẹn từng phần theo thứ tự
  đã chốt — **thống kê → mô hình → hiển thị** — nghĩa là phần mô hình chỉ bắt đầu khi phần thống kê đã
  xong theo định nghĩa "xong" của nó, và phần hiển thị chỉ bắt đầu khi báo cáo mô hình đã có hình dạng ổn
  định. Đây là câu trả lời thay cho thế đứng "dựng lát cắt mỏng trước" mà bản nháp trước ghi; với đợt này,
  không có Unit "đường mỏng" nào để nghiệm thu sớm.
- **Cái giá chúng tôi chấp nhận, và cách bù.** Không có lát cắt mỏng nghĩa là rủi ro khớp nối bị dồn về
  cuối (khi nối báo cáo thống kê vào một tab của dashboard). Chúng tôi bù bằng ba thứ: (a) mỗi phần phải
  có test end-to-end riêng chạy trên dữ liệu thật **ngay khi phần đó xong**, không đợi tới phần cuối;
  (b) tầng thống kê vào chuỗi xác nhận của mọi đơn vị công việc (`## Deployment`); (c) tab hiển thị được
  làm bằng một thay đổi nhỏ ngay sau phần mô hình, không gộp vào một lần nối lớn.
- **Chuỗi xác nhận end-to-end của một đơn vị công việc** được khai **một chỗ duy nhất** ở
  `## Deployment` (bốn bước, có tầng `stats`). Mục này không nhắc lại để khỏi lệch — nguyên tắc "một sự
  thật khai một nơi" của repo áp cho cả artifact lẫn mã.
- **Điều việc bỏ lát cắt mỏng không hứa:** nó không thay bộ test `slow`, không miễn việc giữ 5 KPI và số
  dòng 11 view khớp baseline, không miễn cổng phủ 80%, và không miễn test end-to-end cho từng phần.
- **Xung đột phải nêu rõ, không được lờ:** scope đang chạy (`feature`) khai `skeleton: on`
  (`.aidlc/scopes/aidlc-feature.md` dòng 6). Quyết định "không dựng lát cắt mỏng" **đi ngược cờ đó**. Bản
  ghi này giữ nguyên văn câu trả lời của người làm và không tự sửa scope; việc xử lý thuộc về
  delivery-planning (đừng giả định có Unit skeleton) và cổng vào Construction (chọn chế độ
  `construction_policy` cho khớp), hoặc một lần chỉnh scope có chủ đích. Cho tới khi một trong hai việc đó
  xảy ra, đây là điểm lệch đã biết giữa practice và scope.
- **Có dừng lại cho người xem giữa các phần hay đi tiếp tự động** vẫn là quyết định của
  `construction_policy` trong scope, không phải một cổng chúng tôi tự đặt thêm.

## Testing Posture

- **Methodology**: tdd
- **Ordering**: Với mỗi lớp chạy được của một phần, chúng tôi viết test trước cho hành vi mong muốn và chạy nó để thấy đỏ, rồi mới viết mã cho tới khi test đó xanh, rồi mới chuyển sang lớp kế tiếp — và chỉ chuyển sang **phần** kế tiếp (thống kê → mô hình → hiển thị) khi phần đang làm đã có test end-to-end riêng xanh trên dữ liệu thật và toàn bộ bộ nhanh vẫn xanh.
- **Bằng chứng cho `tdd` là quyết định của người làm, không phải git.** Lịch sử chỉ có 14 commit và mã
  nguồn cùng test của U3 vào **cùng một commit** (`b384da4 feat: Add U3 feature` có cả `src/**` và
  `tests/**`), nên bằng chứng tĩnh không phân biệt được thứ tự. Giá trị `tdd` kế thừa từ lần phỏng vấn
  trước và **đã được xác nhận lại ở đợt này** (Q3 = A: giữ TDD cho cả phần mô hình, dù phần đó khó viết
  test trước hơn). Nó thay cho mặc định `test-after` của `org.md`.
- **Ngưỡng phủ 80% đã được cưỡng chế trong CI, và phạm vi đo đã chốt là "giữ nguyên như CI"** (phỏng vấn
  Q6 = A). `ci.yml:46` chạy `python -X utf8 -m pytest --cov=src --cov-fail-under=80` trên **toàn bộ** bộ
  test (nhanh + `slow`), vì bảy mô-đun `src/` chỉ có phần phủ đến từ bộ `slow`. Chúng tôi không hạ ngưỡng
  và không tách cổng sang bộ nhanh để cho một bước pass. `README.md` mục "CI" đang nói ngược lại (rằng bộ
  `slow` và cổng phủ không chạy trong CI) — đó là **trôi tài liệu** và README là bên phải sửa, không phải
  `ci.yml`.
- **Mọi mô-đun mới đều phải có test riêng**, kể cả mô-đun "chỉ nối dây". Khoảng trống còn lại
  (`src/analytics/service.py`, `src/integrate/validate.py`, `reconcile.py`, `catalog.py`, `connections.py`,
  `src/pipeline/micro_batch.py`, `stages.py`) là nợ đã biết, không phải mẫu để noi theo — và
  `src/analytics/service.py` đúng là chỗ đợt này sẽ mở rộng, nên mô-đun thống kê mới không được lặp lại
  khoảng trống đó.
- **Khối lượng hiện tại** (đo trên đĩa): 70 tệp Python trong `src/` (9.444 dòng), 40 mô-đun test với
  **353** hàm test (9 hàm `slow`), 7.358 dòng test — tương đương 78% khối lượng `src/`. Dưới TDD + yêu cầu
  test cho mọi mô-đun mới + không có lát cắt mỏng, khối lượng này còn tăng trong đợt này.
- **Bộ nhanh và bộ chậm tách bằng marker**, không tách bằng thư mục: `-m "not slow"` là bộ nhanh,
  `-m slow` là bộ cần dữ liệu thật/sinh ra (`pytest.ini`).
- **Bộ nhanh chưa hermetic** (`TD-09`): 5 test trong `tests/unit/test_dashboard_smoke.py` và
  `tests/unit/test_cli.py::test_main_analyze_stage` gọi `load_config()` của repo nên cần
  `warehouse/olist.duckdb` và `data/marts/` — hai thư mục bị `.gitignore`. CI che lỗ hổng này bằng bước
  dựng dữ liệu trước khi test; trên máy mới clone, bộ "nhanh" vẫn đỏ. Chưa chốt có sửa `TD-09` trong đợt này.
- **Test là chốt hồi quy dữ liệu, không chỉ chốt mã.** Mọi thay đổi cleaning/ghép bản ghi có chủ đích phải
  cập nhật đồng thời `src/quality/allowlist.py`, `src/integrate/reconcile.py`, `README.md` và test tích hợp;
  nếu không, `quality` chế độ `full` và `KpiReconciler` sẽ đỏ.
- **Test áp đặt cả hình dạng giao diện và CLI.** Hiện có **4 tab, 8 callback, 9 output, 11 view** và **3
  lệnh con CLI**; `tests/unit/test_dashboard_smoke.py` khẳng định số tab/callback/output,
  `tests/integration/test_u3_end_to_end.py` khẳng định lại số callback,
  `tests/integration/test_u2_end_to_end.py` khẳng định `len(views) == 11`, và `tests/unit/test_cli.py` khẳng
  định parser có 3 lệnh con. Thêm tab/thẻ/output/lệnh là thay đổi có chủ đích và phải sửa các test đó
  **trong cùng thay đổi**. Việc thống kê là **tầng thứ năm của `run --stage`** (không phải lệnh con thứ tư)
  nên con số 3 lệnh con giữ nguyên; cái thay đổi là `STAGES` trong `src/pipeline/stages.py` — và vì danh
  sách đó hiện **không có test riêng**, việc thêm test cho nó nằm trong yêu cầu "mọi mô-đun mới có test
  riêng" ở trên, không phải tuỳ chọn.
- **`ruff` là cổng lint + format.** `ruff check .` chạy toàn repo; `ruff format --check` chỉ chạy trên danh
  sách tệp khai tay trong `ci.yml:33` (`TD-20`), nên tệp mới **phải** được thêm vào danh sách đó cùng lúc
  với việc tạo tệp. Mã cũ chưa sạch ruff được dọn theo từng tệp khi có người sửa tới.
- **Không có kiểm tra kiểu tĩnh.** `mypy`/`pyright` không có trong phụ thuộc và không có trong CI; type
  hint vẫn giữ theo quy ước hiện có nhưng không phải cổng.
- **Scope `feature` áp thêm sàn phủ 80% và yêu cầu chạy trong CI trước khi hợp nhất** — trùng với thực hành
  đã có, không mâu thuẫn.

## Deployment

- **Chưa có môi trường triển khai.** Không staging, không production, không Docker/cloud, không scheduler,
  không dịch vụ ngoài nào ngoài API IBGE công khai. Vì vậy mặc định "deploy on merge" của `org.md` **không
  áp dụng**; chúng tôi không có bước build hay đóng gói phát hành.
- **CI là cổng tự động thật, chạy trên GitHub Actions.** `.github/workflows/ci.yml`: `windows-2022`, Python
  3.13, cache pip, trigger `push`/`pull_request` vào `main`, `feature/update-ui-ux` **và
  `feature/analysis-and-models`** (nhánh của đợt, thêm theo phỏng vấn Q1 = A — xem `## Way of Working`).
  Chưa có bước deploy nào trong workflow — đúng với mô hình chạy từ mã nguồn.
- **"Phát hành" của chúng tôi = chạy từ mã nguồn trên máy local, sau khi CI xanh**, theo chuỗi xác nhận
  **bốn bước**, đúng thứ tự, dừng ngay khi một bước đỏ, không bước nào được bỏ qua vì "lần trước vẫn chạy
  được" (phỏng vấn Q4 = A, Q5 = B):
  1. `python -X utf8 -m pytest -m "not slow"` — bộ test nhanh phải xanh trước;
  2. `python -X utf8 -m src.pipeline run --stage all` — pipeline chạy hết các tầng trên dữ liệu thật, qua
     `QualityGate` và `KpiReconciler`;
  3. `python -X utf8 -m src.pipeline run --stage stats` — **bước mới của đợt này**: sinh lại báo cáo thống
     kê trên dữ liệu thật và kiểm nó khớp những gì dashboard sẽ đọc;
  4. mở dashboard — xem kết quả bằng mắt, vì hình dạng giao diện là một phần của "chạy đúng".

  Bước 3 đứng **trước** bước 4 chứ không phải sau: mở dashboard khi báo cáo thống kê chưa được sinh lại là
  xem một màn hình có thể đang đọc báo cáo cũ.
- **Hình dạng lệnh thống kê: một tầng mới trong chuỗi `run --stage`, không phải lệnh con riêng** (phỏng vấn
  Q5 = B). Tức là `python -m src.pipeline run --stage stats` (tên tầng `stats`), bổ sung vào danh sách tầng
  hiện có; CLI vẫn **3 lệnh con**. Hệ quả phải xử lý cùng lúc: danh sách tầng và báo cáo liệt kê tầng đang
  lệch nhau (`TD-11` — `STAGES` có 4 tên trong khi một báo cáo ghi 6), nên thêm `stats` là dịp sửa luôn chỗ
  lệch đó chứ không chồng thêm một tầng nữa lên một danh sách đã sai.
- **Hai lệnh riêng cho hai nửa hệ thống, không có bước build:** pipeline (nay có thêm tầng `stats`) và
  `python -X utf8 -m src.dashboard` (bind `127.0.0.1:8050`, cấu hình trong `config.yaml`).
- **Phiên bản = commit hash, cộng một mốc CHANGELOG.** Không có git tag; `CHANGELOG.md` ghi mốc `v0.1.0`
  (2026-11-06) theo ba nhóm **Thêm / Sửa / Nội bộ**, viết cho người đọc. Đợt này thêm bề mặt mới (tầng
  `stats`, mô hình, vùng hiển thị) nên CHANGELOG phải có mốc tiếp theo; đánh số tag vẫn chưa được đặt thành
  luật.
- **Cổng kiểm tra sau khi chạy đóng vai trò "kiểm tra khói":** `QualityGate` (21 check cấu trúc; chế độ
  `full` thêm 9 check số dòng và 10 dị thường allowlist) và `KpiReconciler` (5 KPI với dung sai riêng).
  Pipeline chỉ được coi là chạy đúng khi hai cổng này xanh. Báo cáo thống kê mới **không thay** hai cổng
  này, và việc bước 3 xanh cũng không cho phép bỏ qua bước 2.
- **Vận hành đã biết trước, phải tuân khi chạy lại** (`docs/runbook.md`): đóng dashboard trước khi chạy
  `integrate` (khoá `warehouse/olist.duckdb`); view DuckDB chứa đường dẫn tuyệt đối vào Parquet nên chuyển
  thư mục repo hoặc dùng worktree khác phải chạy lại `integrate`; mọi lệnh Python phải chạy UTF-8.
- **Dữ liệu vào là bất biến, không có môi trường thứ hai:** `dataset/` chỉ đọc; `data/`, `warehouse/`,
  `logs/`, `inbox/` là sản phẩm sinh ra và bị `.gitignore`. "Triển khai lại từ đầu" = xoá bốn thư mục sinh
  ra và chạy lại `--stage all`.

## Code Style

- **Ngôn ngữ và môi trường:** Python 3.13, Windows 10/11, chạy từ `.venv` tạo bằng
  `python -m venv --system-site-packages`. Mọi lệnh Python chạy UTF-8 (`-X utf8` hoặc `PYTHONUTF8=1`) vì
  đường dẫn có ký tự tiếng Việt và dữ liệu có ký tự Bồ Đào Nha. Chuỗi hiển thị cho người dùng bằng **tiếng
  Việt**, dữ liệu gốc giữ **tiếng Bồ Đào Nha**, số hiển thị theo định dạng Brazil (`1.234,56`, `R$`, `%`)
  trong `src/dashboard/formatting.py`.
- **`ruff` là một cấu hình duy nhất cho cả lint và format** (`ruff.toml`): `line-length = 112`,
  `target-version = "py313"`, `select = ["E4", "E7", "E9", "F"]` — bắt lỗi thật, không đụng kiểu chữ. Bốn
  `per-file-ignores` là nợ cũ có ghi chú (`F401` cho `src/integrate/connections.py`,
  `src/integrate/pipeline.py`, `src/pipeline/micro_batch.py`, `src/quality/gate.py`; `E402` cho
  `tests/conftest.py`). Mã mới không được thêm ngoại lệ "chỉ lần này".
- **Hình thức tệp:** 4 dấu cách, không tab; dòng tối đa 112 ký tự (nay do `ruff format` bảo đảm, không soát
  tay); 55 trong 70 tệp `src/` mở đầu bằng `from __future__ import annotations` và dùng type hint hiện đại
  (`list[str]`, `dict[str, pd.DataFrame]`, `Path | None`).
- **Đặt tên:** mô-đun/hàm `snake_case`, lớp `PascalCase`, hằng `UPPER_SNAKE`; tiền tố bảng đích `dim_`,
  `fact_`, `agg_`; cột cờ là mệnh đề khẳng định (`is_delivered`, `is_late`, `has_items`,
  `category_missing`, `translation_missing`, `price_outlier`); ID check chất lượng theo nhóm (`U-` unique,
  `F-` foreign key, `D-` miền giá trị, `R-` số dòng, `A-` dị thường, `C-` count, `J-` join, `L-` logic).
  Lớp tích hợp dùng định danh **tiếng Việt không dấu** cho thực thể/trường (`don_hang`, `ma_don`,
  `trang_thai`) và id kebab-case tiếng Việt cho thành phần giao diện (`tich-hop`, `don-theo-thang`); trạng
  thái giao diện là token đóng (`rong`, `chua-chay`, `dang-tai`, `day-du`, `mot-phan`, `loi`).
- **Mẫu lặp lại chúng tôi giữ:** hàm làm sạch thuần theo bảng `clean_<table>(df, ...) -> DataFrame`, luôn
  `out = df.copy()` trước khi sửa và **gắn cờ thay vì lọc dòng**; builder không giữ trạng thái
  (`build_all`/`validate`), tiêm `config` qua tham số (không dùng DI container); ghi tệp qua `AtomicWriter`
  (temp → đọc lại kiểm số dòng → `os.replace`); báo cáo = dataclass → JSON UTF-8 (`ensure_ascii=False`,
  indent 2); nhật ký JSONL mỗi lần chạy một `run_id`, mọi sự kiện có `timestamp`, `level`, `run_id`,
  `stage`, `event`; lỗi theo tầng (`SchemaError`, `QualityGateError`, `ExternalSourceError`,
  `ConfigurationError`, `QueryExecutionError`, `KpiMismatchError`, `NoSourceAvailableError`,
  `LinkageResultError`), bắt ở biên (CLI/`run_stage`/`process_inbox`/`tab.py`) và trả mã thoát 1; SQL
  tham số hoá bằng `?`, tên cột/`GROUP BY` lấy từ dict hằng.
- **Chú thích:** docstring một dòng ở đầu mô-đun/hàm; không docstring mô tả tham số/trả về; giải thích dài
  đặt ngoài mã (`README.md`, `docs/data-dictionary.md`, `docs/runbook.md`, `docs/3v.md`, `CHANGELOG.md`).
  `src/` hiện có 0 `TODO`/`FIXME`/`HACK` — chúng tôi không mang ghi chú nợ dang dở trong mã.
- **Hướng phụ thuộc là quy ước:** `config`/`common` ở gốc, rồi
  `ingest → clean → quality → integrate → analytics → dashboard`; `external` chỉ được `integrate` dùng;
  `integration` và `linkage` là mặt cắt ngang được `dashboard`/`pipeline` gọi; `pipeline` là điểm ghép nối.
  Mô-đun thống kê và mô hình mới **đọc mart/DuckDB hiện có** qua lớp có sẵn thay vì định nghĩa lại doanh
  thu hay KPI theo cách khác, và nằm cùng hướng phụ thuộc đó. Ngoại lệ đang tồn tại
  (`src/integrate/pipeline.py:10` import thừa `AnalyticsService`, miễn trừ `F401` trong `ruff.toml`) là
  **nợ kỹ thuật** `TD-06`, không phải mẫu để noi theo.
- **Cấu hình tập trung, bất biến:** đọc `config.yaml` một lần thành `AppConfig` (`frozen dataclass`), không
  rải hằng số đường dẫn trong mã; `load_config` tạo sẵn thư mục đầu ra (tác dụng phụ có chủ đích). Ba hợp
  đồng YAML trong `config/` là phụ thuộc cứng của runtime.
- **Mã cũ được dọn theo từng tệp khi có người sửa tới**, không bằng một lần format toàn repo lẫn vào thay
  đổi chức năng.
