# Team-Level Rules

> This team's affirmed practices and corrections. Loaded after `org.md` as
> strict-additive guidance; contradictions with broader policy are rejected.
> Populated by the practices-discovery affirmation gate. Edit at the gate,
> not directly.

## Way of Working

- **Một người làm, một người quyết định.** Chúng tôi không có review chéo, không có PR gate, không có
  người phê duyệt thứ hai. Bằng chứng: `ideation/approval-handoff/decision-log.md` dòng 29 (`D-23` —
  "Bỏ qua Team Formation vì là dự án một người"), cùng với `code-structure.md` §1 (không có CI/Makefile)
  và `dependencies.md` §1.2 (ngoài API IBGE công khai không có dịch vụ ngoài nào).
- **Chúng tôi làm việc trên nhánh `feature/update-ui-ux`** cho tới hết đợt nâng cấp này (phỏng vấn Q2 = C).
  Nhánh đang bằng `main` (0 commit trước, 0 commit sau) và đã tồn tại sẵn; vì vậy chúng tôi **tiếp tục
  dùng nó** thay vì tạo nhánh mới cho từng đơn vị công việc hay commit thẳng lên `main`. Trunk vẫn là
  `main`; đây là nhánh làm việc dài hơi của đợt, không phải một quy ước "mỗi thay đổi một nhánh".
- **Thông điệp commit:** 2 trong 6 commit dùng tiền tố kiểu Conventional Commits (`feat:`, `fix:`), 4
  commit còn lại thì không (`Update plan U3`, `first commit`, `Remove aidlc v1`). Đây là **thói quen
  chưa thành quy ước** và phỏng vấn không đặt thành luật; chúng tôi giữ thói quen ở mức khuyến khích.
- **Chúng tôi viết test trước rồi mới viết code (TDD).** Chi tiết nhịp và hệ quả nằm ở `## Testing Posture`.
- **Một Unit chỉ xong khi test end-to-end của nó xanh trên dữ liệu thật.** Ba Unit U1, U2, U3 đều có
  test tích hợp riêng chạy toàn pipeline từ `dataset/`: `tests/integration/test_u1_end_to_end.py`,
  `test_u2_end_to_end.py`, `test_u3_end_to_end.py`. Đây là thực hành mạnh nhất mà bằng chứng xác lập được.
- **Trước khi commit, chúng tôi tự chạy bộ test nhanh:** `pytest -m "not slow"`
  (`README.md`, mục "Test"; `pytest.ini` khai báo `testpaths = tests` và marker `slow`), và theo ràng buộc
  cứng của repo thì mọi lệnh Python chạy bằng UTF-8 — `python -X utf8 -m pytest -m "not slow"`.
  Không có cổng tự động nào chặn commit — xem `## Deployment`.
- **Không hồi quy là điều kiện, không phải mong muốn.** KPI baseline (5 chỉ số) và số dòng của 9 bảng
  nguồn + 11 bảng mart là hợp đồng cứng, được `src/integrate/reconcile.py` và test tích hợp khẳng định
  lại. Ràng buộc này đã được ghi trong phạm vi đợt nâng cấp (`TC-06`, `ideation/scope-definition/scope-document.md`).
- **Quyết định được ghi thành văn bản trong workspace AI-DLC**, không chỉ trong đầu: mỗi intent có
  record riêng dưới `aidlc/spaces/default/intents/<YYMMDD>-<label>/` (state, decision log, câu hỏi,
  artifacts theo tầng). Trước đợt chuyển sang AI-DLC v2, cùng vai trò đó do `aidlc-docs/` đảm nhiệm
  (đã xoá ở commit `41c422f`; dấu vết còn trong `git show --stat b384da4`).
- **Thứ tự thi công theo phụ thuộc dữ liệu, không theo mức độ hấp dẫn của giao diện:** trong đợt này
  chúng tôi làm lược đồ trung gian → mô tả nguồn và luật chọn nguồn → viết lại truy vấn → ghép bản ghi
  → lớp ngữ nghĩa → tab "Tích hợp" → làm mới ba tab cũ (`scope-document.md`, mục "Thứ tự thi công").
  Thứ tự này vẫn đúng, nhưng món đầu tiên chạy qua toàn bộ đường ống là **lát cắt mỏng** ở mục dưới.
- **Phạm vi do một người chốt và được ghi lại trước khi làm.** Mỗi nhóm kiến thức trong đợt này có mức
  độ đã định (Sâu / Tối thiểu / Trung bình) và danh sách "Ngoài phạm vi" tương ứng; mở rộng ngoài danh
  sách đó là thay đổi phạm vi, phải chốt lại chứ không tự quyết trong lúc code.

## Walking Skeleton

- **Chúng tôi dựng lát cắt chạy được xuyên suốt trước, rồi mới làm rộng** (phỏng vấn Q6 = A). Scope đang
  chạy (`feature`) khai `skeleton: on` (`.aidlc/scopes/aidlc-feature.md` dòng 6), và nay quyết định của
  người làm khớp với cờ đó: Unit đầu tiên là một đường mỏng đi hết hệ thống, không phải một nhóm chức
  năng làm trọn vẹn.
- **Lát cắt của đợt này, đúng ba mảnh:** một thực thể trong lược đồ trung gian → một truy vấn viết lại →
  một thẻ hiển thị trên tab mới. Đây là định nghĩa "chạy được" mà chúng tôi dùng để nghiệm thu lát cắt;
  mọi thứ khác (các thực thể còn lại, các truy vấn còn lại, các thẻ còn lại) chỉ mở rộng sau khi lát cắt
  này xanh end-to-end.
- **Lệnh xác nhận end-to-end của một đơn vị công việc** (phỏng vấn Q7 = C), đúng thứ tự:
  1. `pytest -m "not slow"` — bộ test nhanh phải xanh trước;
  2. `python -m src.pipeline run --stage all` — pipeline chạy hết các tầng trên dữ liệu thật;
  3. mở dashboard — xem tab mới bằng mắt, vì hình dạng UI là một phần của "chạy đúng".

  Mọi lệnh Python ở trên chạy theo ràng buộc UTF-8 của repo (`python -X utf8 -m ...` hoặc
  `PYTHONUTF8=1`), nếu không sẽ `UnicodeEncodeError` với đường dẫn tiếng Việt.
- **Điều lát cắt mỏng không hứa:** nó không thay bộ test `slow` hiện có, và không miễn cho chúng tôi
  việc giữ 5 KPI cùng số dòng 11 view khớp baseline — `KpiReconciler` vẫn là cổng của bước 2.
- **Chưa xác định:** có dừng lại cho người xem ngay sau lát cắt mỏng (checkpoint) hay đi tiếp tự động.
  Phỏng vấn không hỏi điểm này; nó do `construction_policy` của scope quyết định ở Construction, và
  chúng tôi sẽ không tự đặt thêm một cổng ngoài scope.

## Testing Posture

- **Methodology**: tdd
- **Methodology evidence**: Người làm chốt ở phỏng vấn Q1 = B — "viết test trước rồi mới viết code".
  Bằng chứng tĩnh trong repo **không** phân biệt được thứ tự: lịch sử git chỉ có 6 commit và mã nguồn
  cùng test của U3 được đưa vào **cùng một commit** (`b384da4 feat: Add U3 feature`, có cả `src/**` và
  `tests/**`). Vì vậy giá trị `tdd` ở đây đến từ quyết định của người làm, không phải từ git; nó thay
  cho mặc định `test-after` của `org.md` mà bản nháp trước đang dùng tạm.
- **Ordering**: Với mỗi lớp chạy được của một Unit, chúng tôi viết test trước cho hành vi mong muốn và
  chạy nó để thấy đỏ, rồi mới viết mã cho tới khi test đó xanh, rồi chuyển sang lớp kế tiếp và chạy lại
  toàn bộ bộ nhanh trước khi coi Unit là xong.
- **Ngưỡng phủ tối thiểu 80%** (phỏng vấn Q3 = C), áp cho `src/`. Đây là ngưỡng **đặt ra**, không phải
  ngưỡng đang được cưỡng chế: `pytest-cov` đã có trong `requirements.txt` và `README.md` có lệnh
  `--cov=src`, nhưng `pytest.ini` chưa có `--cov-fail-under` và repo chưa có CI. Chúng tôi đo bằng
  `pytest --cov=src` trên bộ nhanh + bộ `slow` trước khi coi một đơn vị công việc là xong.
- **Mọi module mới đều phải có test riêng** (phỏng vấn Q5 = A) — kể cả module "chỉ nối dây". Đây là
  chỗ chúng tôi **thắt chặt** so với hiện trạng: `src/analytics/service.py`, `src/integrate/validate.py`,
  `reconcile.py`, `catalog.py`, `connections.py`, `src/pipeline/micro_batch.py`, `stages.py` hiện không
  có unit test trực tiếp, và khoảng trống đó không còn được chấp nhận cho mã mới.
- **`ruff` là cổng lint + format** (phỏng vấn Q4 = B): `ruff check` và `ruff format --check` phải sạch
  trước khi một thay đổi được coi là xong. Chúng tôi chọn ruff đơn lẻ, **không** thêm `mypy`; type hint
  vẫn giữ theo quy ước hiện có chứ chưa bị kiểm tra kiểu tự động.
- **Loại test đang có** (bằng chứng: `code-quality-assessment.md` §3.1, `pytest.ini`):
  - unit — 21 mô-đun, 37 hàm, dùng fixture DataFrame nhỏ trong `tests/conftest.py` (320 dòng);
  - integration end-to-end — 3 hàm, `@pytest.mark.slow`, chạy toàn pipeline trên `dataset/` thật;
  - data-quality baseline — 3 hàm, `@pytest.mark.slow`, khẳng định hằng số dị thường trên CSV thật
    (19.015 mã bưu chính sau gộp, 610 sản phẩm thiếu danh mục, 8.427 outlier giá).
- **Khối lượng hiện tại**: 25 mô-đun test, 47 hàm test, 6 hàm `slow`. Dưới TDD + yêu cầu test cho mọi
  module mới + ngưỡng 80%, khối lượng này sẽ tăng đáng kể trong đợt nâng cấp — rủi ro đã ghi ở
  `evidence.md` mục "Interview decisions".
- **Bộ nhanh và bộ chậm tách bằng marker**, không tách bằng thư mục riêng: `-m "not slow"` là bộ nhanh,
  `-m slow` là bộ cần dữ liệu thật/sinh ra.
- **Bộ test nhanh hiện chưa hermetic** (`TD-09`): 5 test trong `tests/unit/test_dashboard_smoke.py` và
  `tests/unit/test_cli.py::test_main_analyze_stage` gọi `load_config()` của repo, nên cần
  `warehouse/olist.duckdb` và `data/marts/` đã tồn tại — hai thư mục bị `.gitignore`. Trên máy mới clone,
  bộ "nhanh" sẽ đỏ. Phỏng vấn chưa chốt có sửa `TD-09` trong đợt này hay không, nên tạm thời chúng tôi
  vẫn chấp nhận: bộ nhanh chỉ được coi là xanh trên máy đã chạy `--stage all` ít nhất một lần.
- **Test là chốt hồi quy dữ liệu, không chỉ chốt mã.** Mọi thay đổi cleaning/ghép bản ghi có chủ đích
  phải cập nhật đồng thời `src/quality/allowlist.py`, `src/integrate/reconcile.py`, `README.md` và test
  tích hợp — nếu không, chế độ `quality full` và `KpiReconciler` sẽ đỏ (`TD-15`, `TD-02`).
- **Test áp đặt cả hình dạng UI**: `tests/unit/test_dashboard_smoke.py` khẳng định 3 tab, 2 callback,
  9 output; `tests/integration/test_u3_end_to_end.py` khẳng định lại 2 callback. Thêm tab "Tích hợp"
  là thay đổi có chủ đích, phải sửa test trong cùng thay đổi (§7.1 của `code-quality-assessment.md`).

## Guard Policy

<!-- Affirmed by the team. Mode: strict, relaxed, or off. Strict here holds for every intent, whatever one person asks in chat; relaxed or off here applies to every intent whose policy came from its scope, unless project.md or the person sets another; changing this line changes it. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

- **Chưa có môi trường triển khai.** Không có staging, không có production, không có Docker/cloud, không
  có scheduler: `technology-stack.md` §5 ghi rõ "CI/CD — Không có", "Đóng gói phát hành — Không có";
  `dependencies.md` §1.2 ghi "không có dịch vụ đám mây, không có cơ sở dữ liệu mạng, không có xác thực".
  Vì vậy mặc định "deploy on merge" của `org.md` **không áp dụng** ở đây; phỏng vấn cũng không đặt môi
  trường thứ hai nào cho đợt này.
- **"Phát hành" của chúng tôi = chạy từ mã nguồn trên máy local**, và từ nay có một chuỗi xác nhận cố
  định (phỏng vấn Q7 = C): `pytest -m "not slow"` → `python -m src.pipeline run --stage all` → mở
  dashboard. Chạy từng bước, dừng ngay khi một bước đỏ; không bước nào được bỏ qua vì "lần trước vẫn
  chạy được".
- **Pipeline và giao diện là hai lệnh riêng**, đúng `README.md`: `python -X utf8 -m src.pipeline run
  --stage all` và `python -X utf8 -m src.dashboard` (bind `127.0.0.1:8050`, cấu hình ở `config.yaml`).
  Không có bước build, không có bước copy artifact.
- **Phiên bản = commit hash**, không có tag hay số phát hành. Các artifact codekb đều ghi "quét tại
  commit `41c422f...`" thay vì ghi số phiên bản — đó là cách chúng tôi neo một lần chạy vào mã. Phỏng
  vấn không hỏi có cần tag/CHANGELOG cho mốc nộp hay không, nên điểm này **vẫn chưa xác định**.
- **Cổng kiểm tra sau khi chạy đóng vai trò "kiểm tra khói" của chúng tôi:** `QualityGate` (21 check
  cấu trúc, chế độ `full` thêm 9 check số dòng + 10 dị thường allowlist) và `KpiReconciler` (5 KPI với
  dung sai riêng). Pipeline chỉ được coi là chạy đúng khi hai cổng này xanh — xem `architecture.md` §4.
- **Vận hành đã biết trước, phải tuân khi chạy lại** (`docs/runbook.md`, 9 tình huống):
  - phải **đóng dashboard trước khi `integrate`** — cùng một tệp `warehouse/olist.duckdb` bị khoá;
  - view DuckDB chứa **đường dẫn tuyệt đối** vào Parquet, nên chuyển thư mục repo hoặc dùng worktree
    khác là phải chạy lại `integrate` trước khi mở dashboard;
  - mọi lệnh Python phải chạy UTF-8, nếu không sẽ `UnicodeEncodeError` với đường dẫn tiếng Việt.
- **Dữ liệu vào là bất biến và không có môi trường thứ hai:** `dataset/` chỉ đọc; `data/`, `warehouse/`,
  `logs/`, `inbox/` là sản phẩm sinh ra và bị `.gitignore`. "Triển khai lại từ đầu" = xoá bốn thư mục
  sinh ra và chạy lại `--stage all`.

## Code Style

- **Ngôn ngữ và môi trường**: Python 3.13, Windows 10/11, chạy từ `.venv` tạo bằng
  `python -m venv --system-site-packages` (`README.md`; `technology-stack.md` §1). Chuỗi hiển thị cho
  người dùng bằng **tiếng Việt**, dữ liệu gốc giữ **tiếng Bồ Đào Nha**, số hiển thị theo định dạng Brazil
  (`1.234,56`, `R$`, `%`) trong `src/dashboard/formatting.py`.
- **Chúng tôi thêm `ruff` cho cả lint và format** (phỏng vấn Q4 = B). `requirements.txt` sẽ ghim thêm
  `ruff`, cấu hình đặt ở một chỗ duy nhất trong repo, và `ruff check` + `ruff format --check` là bước
  bắt buộc trước khi coi một thay đổi là xong — chạy cạnh `pytest -m "not slow"`. Chúng tôi **không**
  thêm `mypy`: kiểm tra kiểu chưa phải cổng của đợt này.
- **Hình thức tệp** (giữ nguyên, và nay do `ruff format` bảo đảm thay vì soát tay): 4 dấu cách, không
  tab; dòng dài nhất trong `src/` là **112 ký tự**; 41 trong 55 tệp mở đầu bằng
  `from __future__ import annotations` và dùng type hint hiện đại (`list[str]`,
  `dict[str, pd.DataFrame]`, `Path | None`). Giới hạn 112 ký tự hiện chưa được khai trong config nào —
  phỏng vấn không chốt nó thành luật, nên đây vẫn là **chưa xác định**, và cấu hình `ruff` sẽ là nơi
  biến nó thành con số thật nếu chúng tôi giữ.
- **Đặt tên** (`code-structure.md` §3.2): mô-đun/hàm `snake_case`, lớp `PascalCase`, hằng `UPPER_SNAKE`;
  tiền tố bảng đích `dim_`, `fact_`, `agg_`; cột cờ là mệnh đề khẳng định (`is_delivered`, `has_items`,
  `category_missing`, `translation_missing`, `price_outlier`); ID check chất lượng theo nhóm
  (`U-` unique, `F-` foreign key, `D-` miền giá trị, `R-` số dòng, `A-` dị thường, `C-` count, `J-` join,
  `L-` logic).
- **Mẫu lặp lại chúng tôi giữ** (`code-structure.md` §3.1):
  - hàm làm sạch thuần theo bảng, chữ ký `clean_<table>(df, ...) -> DataFrame`, luôn `out = df.copy()`
    trước khi sửa, **gắn cờ thay vì lọc dòng**;
  - builder không giữ trạng thái, chỉ có `build_all`/`validate`; tiêm `config` qua tham số (không dùng DI
    container);
  - ghi tệp qua `AtomicWriter` (temp → đọc lại kiểm số dòng → `os.replace`), không ghi đè trực tiếp;
  - báo cáo = dataclass → JSON UTF-8 (`ensure_ascii=False`, indent 2); nhật ký JSONL mỗi lần chạy một
    `run_id`, mọi sự kiện có `timestamp`, `level`, `run_id`, `stage`, `event`;
  - lỗi theo tầng: `SchemaError` (đầu vào), `QualityGateError` (chất lượng), `ExternalSourceError`
    (nguồn ngoài), `ConfigurationError` (cấu hình); CLI bắt lỗi ở biên và trả mã thoát 1;
  - SQL tham số hoá bằng `?`, tên cột/`GROUP BY` lấy từ dict hằng, không nối chuỗi từ đầu vào người dùng.
- **Chú thích**: docstring một dòng ở đầu mô-đun/hàm; không có docstring mô tả tham số/trả về; phần giải
  thích dài đặt ngoài mã (`README.md`, `docs/data-dictionary.md`, `docs/runbook.md`, `docs/3v.md`).
  `src/` hiện có 0 `TODO`/`FIXME`/`HACK` — chúng tôi không mang ghi chú nợ dang dở trong mã. Phỏng vấn
  không bàn tới việc nâng thành docstring tham số, nên quy ước một dòng **vẫn giữ** cho mọi mô-đun mới.
- **Mã mới phải qua `ruff` trước, không có ngoại lệ "chỉ lần này".** Mã cũ chưa sạch `ruff` được xử lý
  theo từng tệp khi có người sửa tới, không bằng một lần format toàn repo lẫn vào thay đổi chức năng.
- **Hướng phụ thuộc là quy ước, không chỉ là sở thích**: `config`/`common` ở gốc, rồi
  `ingest → clean → quality → integrate → analytics → dashboard`, `external` chỉ được `integrate` dùng,
  `pipeline` là điểm ghép nối (`code-structure.md` §3.3). Ngoại lệ đang tồn tại là **nợ kỹ thuật**
  (`TD-06`: import thừa `integrate → analytics`), không phải mẫu để noi theo.
- **Cấu hình tập trung, bất biến**: đọc `config.yaml` một lần thành `AppConfig` (`frozen dataclass`),
  không rải hằng số đường dẫn trong mã; `load_config` tạo sẵn thư mục đầu ra (tác dụng phụ có chủ đích).
## Forbidden

<!-- Team-specific forbidden patterns -->

## Mandated

<!-- Team-specific mandates -->

## Corrections

<!-- Self-learning loop appends here. -->
