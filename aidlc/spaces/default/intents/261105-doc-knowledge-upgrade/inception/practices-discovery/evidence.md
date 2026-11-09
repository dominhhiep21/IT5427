# Bằng chứng — Practices Discovery (brownfield)

> Ghi lại: đã đọc gì, suy ra gì và từ đâu, độ tin cậy của từng kết luận, và những gì bằng chứng
> **không** thể xác lập nên phải hỏi người quyết định. Mọi đường dẫn tính từ gốc workspace
> `C:\Users\Admin\Desktop\Tích hợp và xử lí dữ liệu lớn`, tại commit
> `41c422ffd7f3b27a2f78a67eaccc43a00d13c77e`.
>
> Bản này đã được **tích hợp ở bước 5**: §1–§4 là phần suy ra từ bằng chứng, §6 là phần hợp nhất câu
> trả lời phỏng vấn (nguồn quyết định), §5 và §7 giữ lại để thấy điều gì đã đóng và điều gì còn mở.

## 1. Phạm vi và cách làm

- **Loại dự án**: brownfield (đã có 55 tệp Python trong `src/`, 25 mô-đun test, 6 commit).
- **Người làm**: một người. Không có thành viên khác, không có CI, không có môi trường triển khai.
  Vì vậy bước 3 (review độc lập của các agent hỗ trợ) không chạy — brief xác nhận `collaborators: off`;
  bằng chứng tĩnh cộng với câu trả lời phỏng vấn ở §6 là cơ sở của mọi thực hành trong
  `team-practices.md`.
- **Nguyên tắc**: chỉ kết luận khi có bằng chứng đọc được; chỗ thiếu thì ghi "chưa xác định từ bằng chứng"
  thay vì đoán. Không chạy test, build hay pipeline (theo brief) — mọi kết luận là đọc tĩnh; phần duy
  nhất không đến từ đọc tĩnh là các câu trả lời phỏng vấn, và chúng luôn được ghi rõ nguồn.

## 2. Nguồn đã đọc

### 2.1 Artifact reverse-engineering (nguồn chính)

| Tệp | Dùng để suy ra |
|---|---|
| `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/code-structure.md` | Bố cục gói, 55 tệp/4.200 dòng, quy ước đặt tên (§3.2), mẫu lặp lại (§3.1), hướng phụ thuộc (§3.3), điểm vào (§4), ghi chú biên (§5), "không có `pyproject.toml`, `setup.py`, CI, Makefile" |
| `.../technology-stack.md` | Python 3.13, Windows, `.venv`, UTF-8 bắt buộc (§1); 8 phụ thuộc ghim (§2); không lint/format/type-check/CI/đóng gói (§5); rủi ro công nghệ (§6) |
| `.../dependencies.md` | Phụ thuộc ngoài (§1), phụ thuộc dữ liệu bất biến (§1.3), đồ thị gói và vòng phụ thuộc (§2), **chi phí 10 điểm khi thêm một bảng** và bảng "cùng sự thật khai nhiều nơi" (§3), rủi ro (§4) |
| `.../code-quality-assessment.md` | Điểm mạnh (§1), bảng đánh giá (§2), hiện trạng test 47 hàm/25 mô-đun (§3.1), lỗ hổng test (§3.2), tính cô lập của bộ nhanh (§3.3), không lint/CI/ngưỡng phủ (§4), sổ nợ `TD-01..TD-15` (§6), rủi ro cho đợt nâng cấp (§7) |
| `.../architecture.md` | Monolith theo tầng, mô hình read-model (§2), luồng dữ liệu và ai ghi gì (§4), 7 quyết định kiến trúc (§5), cơ hội cải thiện (§7) |
| `.../business-overview.md` | Bối cảnh đồ án (§1), KPI baseline (§4), đối tượng sử dụng (§5), 3V (§6), ranh giới: `dataset/` bất biến, chỉ phân tích đơn `delivered`, không auth, hiển thị tiếng Việt (§7) |

### 2.2 Bằng chứng workspace (đọc trực tiếp)

| Tệp / lệnh | Điều xác nhận được |
|---|---|
| `README.md` | Lệnh chạy pipeline và dashboard; cách tạo `.venv`; ba lệnh test (`-m "not slow"`, toàn bộ, `--cov=src`); mục "Lưu ý": `dataset/` không sửa, dashboard chỉ localhost; "3 tab" |
| `config.yaml` | Đường dẫn tập trung; `duckdb.memory_limit/threads`; `micro_batch.max_rows`; `dashboard.host: 127.0.0.1`, `port: 8050` |
| `requirements.txt` | Đúng 8 gói ghim phiên bản, không có gói ghép mờ/HTTP client/retry/orchestration |
| `pytest.ini` | `testpaths = tests`; marker `slow`; `addopts = -ra`; **không** có `--cov-fail-under` |
| `.gitignore` | `data/`, `warehouse/`, `logs/`, `inbox/`, `.venv/`, `.coverage` bị loại; khối AI-DLC loại cursor và runtime cục bộ |
| `AGENTS.md` | Bốn chỉ thị vận hành tường minh: `dataset/` bất biến; UTF-8 bắt buộc; profile trước khi biến đổi; nêu grain + kiểm số dòng/khoá sau join; giữ tầng tách rời và tái lập được (dòng 7, 17, 44–46) |
| `tests/unit/test_schema.py` | Hợp đồng lược đồ bị cưỡng chế (thiếu cột và sai thứ tự cột đều ném `SchemaError`) |
| `tests/unit/test_dashboard_smoke.py` | Test cưỡng chế hình dạng: 3 tab, 2 callback, 9 output |
| `tests/integration/test_u2_end_to_end.py` | Test cưỡng chế số dòng mart, 5 KPI, 11 view, các bộ lọc, các nhánh `ValueError` |
| `tests/data_quality/test_real_dataset.py` | Test cưỡng chế hằng số dị thường trên CSV thật (19.015; 610; 13; 2; 8.427) |
| `tests/integration/test_u1_end_to_end.py`, `test_u3_end_to_end.py` | Mỗi Unit có một test end-to-end trên dữ liệu thật |
| `ideation/scope-definition/scope-document.md` | Mức độ từng nhóm kiến thức; **thứ tự thi công theo phụ thuộc**; ràng buộc `TC-05` (`dataset/` bất biến), `TC-06` (không hồi quy KPI và test), `TC-03`/`TC-04` (thư viện nhỏ, chạy local) |
| `ideation/approval-handoff/decision-log.md` | `D-23`: "Bỏ qua Team Formation vì là dự án một người" — bằng chứng cho phạm vi nhóm một người |
| `.aidlc/scopes/aidlc-feature.md` dòng 6 | Scope `feature` khai `skeleton: on` → ceremony lát cắt mỏng sẽ áp dụng |

### 2.3 Lệnh chỉ đọc đã chạy

| Lệnh | Kết quả dùng cho |
|---|---|
| `git log --oneline -20` | 6 commit: `2342538 first commit`, `43e7a26 Update plan U3`, `b384da4 feat: Add U3 feature`, `fd2cf52 fix: Fix filter condition`, `89a547f feat: Update aidlc v2`, `41c422f Remove aidlc v1` |
| `git branch -a` | `main`, `feature/update-ui-ux` (đang đứng), `remotes/origin/main` |
| `git rev-list --left-right --count main...feature/update-ui-ux` | `0 0` — nhánh feature chưa có commit riêng, trùng `main` |
| `git rev-parse HEAD` | `41c422ffd7f3b27a2f78a67eaccc43a00d13c77e` |
| `git show --stat b384da4` | Mã nguồn và test của U3 vào **cùng một commit** (42 tệp) → không phân biệt được test-trước hay test-sau |
| `git show --stat 41c422f`, `89a547f` | Hai commit gần nhất chỉ đụng workspace AI-DLC, không đụng `src/`/`tests/` |
| `git status --porcelain` | Có thay đổi đã stage đang xoá `aidlc-docs/**` — workspace đang giữa lúc chuyển v1 → v2 |
| Quét độ dài dòng / tab / `from __future__` trên `src/**/*.py` | Dòng dài nhất 112 ký tự; 0 tab; 41 tệp có `from __future__ import annotations` |
| `aidlc engine now` | `2026-11-05T16:04:25Z` (dùng cho `practices-discovery-timestamp.md`) |

## 3. Suy luận: kết luận nào đến từ đâu

| Thực hành | Kết luận trong bản nháp | Bằng chứng | Độ tin cậy |
|---|---|---|---|
| Way of Working | Một người làm, trunk `main`, mỗi Unit nghiệm thu bằng test end-to-end, tự chạy test nhanh trước commit, quyết định ghi vào record | `ideation/approval-handoff/decision-log.md` `D-23` ("dự án một người"); `code-structure.md` §1, §4; ba test `test_u{1,2,3}_end_to_end.py`; `README.md` mục "Test" | **Cao** cho phần "một người" và "mỗi Unit một test e2e"; **thấp** cho quy ước nhánh và commit message |
| Way of Working — nhánh | Có dùng nhánh feature nhưng chưa thành quy ước | `git branch -a` + `rev-list --left-right`: chỉ một nhánh, 0/0 với `main` | **Thấp** — một quan sát |
| Way of Working — commit message | Tiền tố `feat:`/`fix:` là thói quen, chưa bắt buộc | 2/6 commit có tiền tố trong `git log` | **Thấp** |
| Walking Skeleton | Chưa có quy ước; nhưng thực tế mỗi Unit là một lát cắt chạy được | `README.md` mục "Kiến trúc" (U1/U2/U3); ba test e2e; `.aidlc/scopes/aidlc-feature.md` `skeleton: on` | **Trung bình** cho hiện trạng, **không** cho quy ước |
| Testing Posture — loại/khối lượng test | Unit + integration + data-quality; 25 mô-đun, 47 hàm, 6 `slow` | `code-quality-assessment.md` §3.1; `pytest.ini`; đếm trực tiếp trong `tests/` | **Cao** |
| Testing Posture — methodology | **Không xác lập được**; tạm dùng `test-after` theo mặc định `org.md` | `git show --stat b384da4`: mã + test cùng commit | **Không** — câu hỏi phỏng vấn |
| Testing Posture — coverage | Không có ngưỡng | `pytest.ini` không có `--cov-fail-under`; `technology-stack.md` §5; `.coverage` bị gitignore | **Cao** cho hiện trạng, **không** cho ý định |
| Testing Posture — CI gate | Không có, gate là chạy tay | `technology-stack.md` §5; không có `.github/workflows` | **Cao** |
| Deployment | Không có môi trường; "phát hành" = chạy từ mã nguồn local; cổng = QualityGate + KpiReconciler; vận hành theo runbook | `architecture.md` §4; `README.md`; `config.yaml`; `code-quality-assessment.md` §5 (`docs/runbook.md` 9 tình huống) | **Cao** |
| Code Style — hình thức | 4 dấu cách, không tab, ≤112 ký tự, `from __future__ import annotations` ở 41 tệp | quét tĩnh `src/**/*.py` | **Cao** |
| Code Style — đặt tên & mẫu | `snake_case`/`PascalCase`/`UPPER_SNAKE`; `dim_`/`fact_`/`agg_`; cờ khẳng định; ID check theo nhóm; `AtomicWriter`; lỗi theo tầng; SQL tham số hoá | `code-structure.md` §3.1–3.2; `code-quality-assessment.md` §1 | **Cao** |
| Code Style — cổng tự động | Không có formatter/linter/type-checker | `code-quality-assessment.md` §4; `technology-stack.md` §5 | **Cao** cho hiện trạng |
| Ràng buộc cứng | 14 `ALWAYS` + 8 `NEVER` trong `discovered-rules.md` (12 + 8 từ bằng chứng, thêm 2 `ALWAYS` từ phỏng vấn Q3/Q4) | `AGENTS.md` dòng 7/15/16/17/35–37/40/45/46; `README.md`; `.gitignore`; `pytest.ini`; các test cụ thể; `scope-document.md` `TC-05`/`TC-06`; `practices-discovery-questions.md` Q3, Q4 | **Cao** — mỗi quy tắc nêu đường dẫn nguồn |

> **Lưu ý khi đọc bảng trên:** đây là bảng của **suy luận từ bằng chứng tĩnh**, lập trước phỏng vấn.
> Hai dòng đã bị phỏng vấn vượt qua: `Testing Posture — methodology` (nay là `tdd`, không còn `test-after`)
> và `Testing Posture — coverage` (nay có ngưỡng 80%). Cột "Độ tin cậy" vẫn đúng: nó nói bằng chứng tĩnh
> không xác lập được gì, chứ không nói thực hành cuối cùng là gì. Xem §6.

## 4. Bằng chứng đã cũ hoặc mâu thuẫn (phải nói rõ, không được lặng lẽ bỏ qua)

1. **`AGENTS.md` mục "Repo state" đã lỗi thời.** Tệp nói "Greenfield… **no application code, package
   manifest, test/lint config, CI, or git repo yet**", nhưng repo có 6 commit, 55 tệp `src/`, 25 mô-đun
   test, `requirements.txt`, `pytest.ini`. Phần "Environment (verified)" cũng nói **chưa có** `duckdb`,
   `pyarrow` trong khi `requirements.txt` ghim `duckdb==2.0.0`, `pyarrow==26.0.0` và
   `warehouse/olist.duckdb` đã tồn tại (`technology-stack.md` §6 mục 4 đã cảnh báo điều này).
   → Hệ quả cho bản nháp: các **chỉ thị quy ước** trong `AGENTS.md` (dataset bất biến, UTF-8, grain,
   tầng tách rời) vẫn dùng được vì chúng khớp với mã và test hiện tại; còn các **ghi chú môi trường**
   ("gói X chưa cài", "chưa có repo") thì **không** được dùng làm bằng chứng.
2. **`README.md` tham chiếu chết** tới `aidlc-docs/` (mục "Tài liệu"), trong khi thư mục đó đã bị xoá ở
   commit `41c422f`. Không ảnh hưởng thực hành, nhưng là bằng chứng rằng tài liệu không được rà soát
   tự động — nên đừng coi README là nguồn đúng tuyệt đối.
3. **Nhánh `feature/update-ui-ux` trùng `main`** (0/0) trong khi workspace có thay đổi đã stage (xoá
   `aidlc-docs/**`). Trạng thái git đang dở dang: không thể dùng nó để suy ra "commit sạch trước khi
   chuyển nhánh".
4. **Không có tác giả thứ hai trong lịch sử** → mọi kết luận về "review" chỉ có thể là tự soát.

## 5. Còn bỏ ngỏ cho buổi phỏng vấn

Những điểm dưới đây **không** kết luận được từ bằng chứng và trở thành câu hỏi (bước 4). Mỗi câu nêu
luôn ứng viên mặc định để người trả lời chỉ cần xác nhận hoặc sửa.

> **Đã tích hợp (bước 5):** bảy câu hỏi đã được hỏi và trả lời — xem §6 để biết câu nào chốt được gì.
> Các mục 2, 4, 7, 10, 12, 13, 14, 15, 17, 18, 19 **vẫn còn mở** (chưa được hỏi), và mục 3 chỉ được
> trả lời **một phần** (Q7 chốt chuỗi xác nhận cuối mỗi đơn vị công việc, không chốt nghĩa vụ chạy test
> trước *mỗi* commit). Những mục đó vẫn là "chưa xác định", không phải đã được chốt.

### Way of Working

1. Có giữ quy ước **mỗi thay đổi một nhánh `feature/<slug>` rồi merge vào `main`** không, hay commit
   thẳng lên `main`? (ứng viên: có, vì nhánh hiện tại đang tồn tại)
2. Commit message có theo **Conventional Commits** (`feat:`, `fix:`, `chore:`) một cách bắt buộc không?
   (ứng viên: có, theo 2 commit gần nhất có tiền tố)
3. Trước khi commit, có bắt buộc chạy `pytest -m "not slow"` và ghi lại kết quả không, hay chỉ khi thấy cần?
4. Có review gì thay thế review chéo (tự đọc lại diff, chạy `--stage all` lại) trước khi coi là xong không?

### Walking Skeleton

5. Với đợt này, **Unit đầu tiên** của lát cắt mỏng là gì — lược đồ trung gian + ánh xạ (theo thứ tự phụ
   thuộc trong `scope-document.md`), hay một đường mỏng xuyên suốt (ánh xạ → một truy vấn → một ô trên tab)?
6. **Lệnh xác minh Construction** chính thức là gì? (ứng viên: `python -X utf8 -m src.pipeline run --stage all`
   rồi `python -X utf8 -m pytest -m "not slow"`)
7. Có muốn checkpoint lát cắt mỏng (dừng lại cho người xem) hay đi tiếp tự động?

### Testing Posture

8. **Methodology thật**: test-after (mặc định đang ghi) / tdd / bdd / atdd / custom? Bằng chứng không trả lời được.
9. Có đặt **ngưỡng độ phủ** không (ví dụ 80% dòng như mặc định scope `feature`), hay giữ "không ngưỡng"
   và dựa vào test hồi quy dữ liệu?
10. Có sửa **`TD-09`** (bộ test nhanh phụ thuộc `warehouse/` + `data/marts/`) trong đợt này để test nhanh
    xanh trên máy sạch không, hay chấp nhận tiếp?
11. Có bắt buộc unit test cho mỗi mô-đun mới (ví dụ lớp chọn nguồn, lớp viết lại truy vấn, lớp ghép bản ghi)
    hay đủ nếu có một test tích hợp chạy dữ liệu thật?
12. Có thêm **CI cục bộ** (script/pre-commit chạy `pytest -m "not slow"`) trong đợt này không?

### Deployment

13. Có cần **tag/CHANGELOG** cho mốc nộp hay commit hash là đủ?
14. Có cần một **lệnh kiểm thử khói chính thức** sau mỗi lần chạy (ví dụ `reconcile` + `list_views` + mở
    dashboard) không?
15. Đợt nâng cấp có chạy trong **worktree/môi trường thứ hai** không? Nếu có, phải chốt việc chạy lại
    `integrate` vì view DuckDB chứa đường dẫn tuyệt đối.

### Code Style

16. Có thêm **`ruff` + `black` + kiểm tra kiểu** (`mypy`) trong đợt này không, hay giữ quy ước + soát tay?
17. Có giữ mức **112 ký tự** làm giới hạn dòng chính thức (không có config nào đang khai) không?
18. Có giữ quy ước **docstring một dòng**, hay nâng thành docstring tham số cho các mô-đun mới?
19. Gói mới cho ghép bản ghi mờ (nếu cần) có được chấp nhận thêm vào `requirements.txt` không — tức có
    phá vỡ ràng buộc "thư viện mã nguồn mở nhỏ, chạy local" (`TC-03`, `TC-04`) không?

## 6. Quyết định từ buổi phỏng vấn (bước 5)

Nguồn: `practices-discovery-questions.md`, bảy câu hỏi kỹ thuật đã được trả lời và xác nhận lại bằng
mục "Consolidated Summary Confirmation". Đây là nguồn **quyết định**, không phải suy luận — nó thắng
mọi chỗ bản nháp suy đoán khác.

| Câu | Trả lời | Chốt được gì | Đã ghi vào |
|---|---|---|---|
| Q1 — nhịp viết test | **B. TDD** | `Methodology: tdd` thay cho `test-after` mặc định của `org.md`; thứ tự là test-trước-rồi-code cho từng lớp chạy được | `team-practices.md` § Testing Posture (`Methodology`, `Ordering`) |
| Q2 — nhánh làm việc | **C. Tiếp tục `feature/update-ui-ux`** | Đợt nâng cấp chạy trên nhánh hiện có; **không** tạo nhánh mới mỗi đơn vị công việc, **không** commit thẳng `main`. Đây là thực hành, không phải ràng buộc cứng | `team-practices.md` § Way of Working |
| Q3 — ngưỡng phủ test | **C. 80%** | Có ngưỡng phủ tối thiểu 80% dòng trên `src/`; ngưỡng **không được hạ** để cho một bước pass | `team-practices.md` § Testing Posture; một `ALWAYS` trong `discovered-rules.md` |
| Q4 — công cụ kiểm tra mã | **B. `ruff` (lint + format)** | `ruff` trở thành cổng bắt buộc cho cả lint và format; **không** thêm `mypy`, type hint vẫn chỉ là quy ước | `team-practices.md` § Code Style; một `ALWAYS` trong `discovered-rules.md` |
| Q5 — test cho module mới | **A. Mọi module mới đều phải có test riêng** | Thắt chặt so với hiện trạng (7 mô-đun `src/` đang không có unit test trực tiếp); áp cho cả module "chỉ nối dây" | `team-practices.md` § Testing Posture |
| Q6 — lát cắt chạy được | **A. Dựng lát cắt xuyên suốt trước** | Có walking skeleton, và nội dung của nó được chốt: một thực thể lược đồ trung gian → một truy vấn viết lại → một thẻ trên tab mới | `team-practices.md` § Walking Skeleton |
| Q7 — lệnh xác nhận cuối | **C. Cả hai, theo thứ tự** | Chuỗi xác nhận end-to-end của mỗi đơn vị công việc: `pytest -m "not slow"` → `python -m src.pipeline run --stage all` → mở dashboard | `team-practices.md` § Walking Skeleton và § Deployment |

**Điều phỏng vấn không quyết định** (vì không hỏi): quy ước commit message, có sửa `TD-09` không, có
dựng CI cục bộ không, có tag/CHANGELOG cho mốc nộp không, có cần worktree cho đợt này không, giới hạn
112 ký tự có thành luật không, docstring có nâng cấp không, có thêm gói ghép mờ không, và có checkpoint
ngay sau lát cắt mỏng không. Những điểm này vẫn "chưa xác định" trong `team-practices.md` và không được
suy diễn thành thực hành đã khẳng định.

**Rủi ro cần người làm biết (không phải lý do để hạ mục tiêu).** TDD + ngưỡng phủ 80% + test riêng cho
mọi module mới là một cam kết **tham vọng** so với quỹ thời gian **1–2 tuần cho một người** đã ghi ở
`feasibility-assessment.md` (`OC-01`, `R-01`; `initiative-brief.md` dòng 17; `decision-log.md` `D-16`,
`D-31`). Ba yêu cầu này cộng lại làm tăng đáng kể khối lượng viết test trong khi khối lượng chức năng
không giảm, và người viết test cũng chính là người viết code — không có ai chạy song song. Hai hệ quả cụ
thể cần lường trước: (a) nếu phải cắt, chỗ cắt nên là **phạm vi chức năng** (theo "Ngoài phạm vi" trong
`scope-document.md`), không phải ngưỡng phủ hay nghĩa vụ test; (b) nguy cơ trượt tiến độ là thật, nên
mốc trượt phải được báo sớm thay vì lặng lẽ hạ chuẩn. Rủi ro này **được ghi để người làm quyết định**,
không phải để agent tự nới lỏng bất kỳ mục tiêu nào ở trên.

## 7. Rủi ro đã ghi nhận trước phỏng vấn (nay phần lớn đã đóng)

Đây là danh sách rủi ro lập **trước** khi có câu trả lời; giữ lại để thấy câu hỏi nào thực sự quan
trọng. Trạng thái hiện tại: rủi ro 1 và 2 **đã đóng** nhờ Q1 và Q6; rủi ro 3 **đã đóng một nửa** — đã có
ngưỡng phủ 80% (Q3) nhưng vẫn **chưa có CI**, nên chốt hồi quy tự động vẫn chưa tồn tại.

- Construction sẽ tự chọn mặc định của `org.md` (`test-after`, implement-rồi-test, không coverage floor),
  và thực hành đó sẽ được ghi vào `team.md` như thể đã được nhóm khẳng định.
- Lát cắt mỏng sẽ do agent tự chọn Unit đầu tiên; nếu chọn sai, đợt nâng cấp mất một vòng lặp.
- Không có ngưỡng phủ + không CI nghĩa là **chốt hồi quy duy nhất vẫn là 6 hàm test `slow`** — chúng chỉ
  chạy khi có `dataset/` thật và mất thời gian, nên rất dễ bị bỏ qua trước khi commit. Ngưỡng 80% nay đã
  có, nhưng **vẫn không có gì tự động chặn** một commit dưới ngưỡng hay một `ruff check` đỏ: cả hai vẫn
  là kỷ luật chạy tay cho tới khi có CI.
