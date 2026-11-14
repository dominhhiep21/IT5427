# Bằng chứng — Practices Discovery, intent `261109-stats-and-models`

> Ghi lại cái đã đọc, cái suy ra, cái không xác lập được, cái phỏng vấn đã chốt, và cái còn chưa chắc.
> Mọi đường dẫn tính từ gốc repo, tại commit `ea77bdf88d1431de11c36e1b739972bd594063f0`
> (nhánh `feature/analysis-and-models`, đi trước `main` 1 commit).

## 1. Đã đọc trực tiếp

| Nguồn | Dùng để xác lập |
|---|---|
| `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/business-overview.md` | KPI baseline, định nghĩa doanh thu, khoảng trống thống kê/ML, 4 tab dashboard |
| `.../architecture.md` | Hướng phụ thuộc, quyết định kiến trúc, ranh giới `AnalyticsService` (chỉ đọc, không trạng thái) |
| `.../code-structure.md` | 70 tệp `src/` (9.444 dòng), 40 mô-đun test, mẫu thiết kế, quy ước đặt tên, điểm vào CLI |
| `.../technology-stack.md` | 10 gói ghim, phiên bản Python/ruff, không có thư viện thống kê/ML, cấu hình CI |
| `.../dependencies.md` | Phụ thuộc ngoài, 10 điểm phải sửa khi thêm bảng, các nơi khai trùng một sự thật dữ liệu |
| `.../code-quality-assessment.md` | `TD-01`…`TD-20`, §7.1 danh sách assert hình dạng dashboard/CLI, §7.2 hạng mục S-01…S-07 |
| `.github/workflows/ci.yml` | 8 bước CI, `windows-2022`, trigger `main` + `feature/update-ui-ux`, `ruff check .`, `ruff format --check` trên danh sách khai tay, `--cov-fail-under=80` trên toàn bộ bộ test |
| `ruff.toml` | `line-length = 112`, `target-version = "py313"`, `select = ["E4","E7","E9","F"]`, 4 `per-file-ignores` có ghi chú |
| `pytest.ini` | `testpaths = tests`, marker `slow`, `addopts = -ra` |
| `requirements.txt` | 10 gói ghim chính xác, có chú thích lý do cho `dash-mantine-components` và `ruff` |
| `README.md` | Kiến trúc, lệnh chạy, mục Test / Lint / CI / KPI baseline / Lưu ý / Tài liệu |
| `CHANGELOG.md` | Mốc `v0.1.0` (2026-11-06), ba nhóm Thêm / Sửa / Nội bộ |
| `.gitignore` | Bốn thư mục sinh ra + `.venv/` + `.coverage` bị loại khỏi version control |
| `git log --oneline -15`, `git branch -a`, `git status` | Lịch sử commit, nhánh hiện tại, nhánh trên `origin` |
| `ideation/scope-definition/scope-document.md` | Phạm vi S-01…S-07, thứ tự thi công, điều kiện "xong" |
| `.aidlc/scopes/aidlc-feature.md` | Scope đang chạy: `skeleton: on`, `guard_policy: off`, `sensors`/`learnings`/`summary_confirmation` bật |
| `aidlc/spaces/default/memory/team.md`, `project.md` | Baseline đã xác nhận ở đợt trước (năm mục + `## Mandated` / `## Forbidden`) |
| Đếm trực tiếp trên đĩa | 40 tệp `tests/**/test_*.py`, 353 hàm `def test_`, 9 marker `slow`, 70 tệp `.py` trong `src/`, 55 tệp có `from __future__ import annotations` |

Phỏng vấn đã chạy trong cùng stage này; câu hỏi và câu trả lời nằm ở
`practices-discovery-questions.md` (Q1–Q6, kèm `Consolidated Summary Confirmation` = "Looks correct").
Cả sáu câu đều được hỏi vì bằng chứng tĩnh không trả lời được, không phải vì agent cần xác nhận lại
điều đã biết.

## 2. Suy ra (không đọc trực tiếp được từ một tệp duy nhất)

- **`team.md` đã lạc hậu so với repo ở ba chỗ**, và bản nháp này cập nhật lại: (a) khối lượng test —
  `team.md` ghi "25 mô-đun, 47 hàm test", thực tế **40 mô-đun, 353 hàm, 9 `slow`**; (b) "chưa có CI" — nay
  **có** `ci.yml`; (c) "ngưỡng 80% đặt ra nhưng chưa cưỡng chế" — nay **cưỡng chế** ở `ci.yml:46`. Nguồn của
  độ lệch: `team.md` được viết ở lần quét trước, trước commit `0e68405 chore: thêm ruff, CI và cập nhật tài liệu`.
- **Hình dạng dashboard đã đổi từ 3 tab/2 callback thành 4 tab/8 callback** (vẫn 9 output, 11 view). Các
  assert tương ứng nằm ở `tests/unit/test_dashboard_smoke.py`, `tests/integration/test_u3_end_to_end.py`,
  `tests/integration/test_u2_end_to_end.py`, và có thêm `tests/unit/test_cli.py` cho 3 lệnh con CLI.
- **Conventional Commits đã thành nếp**: 11 trong 14 commit gần nhất có tiền tố `feat:` / `fix:` / `chore:`;
  ba commit cũ (`41c422f`, `43e7a26`, `2342538`) không có. Vì vậy bản nháp nâng từ "thói quen" lên "thói
  quen đã thành nếp nhưng chưa thành luật".
- **Nhánh làm việc của đợt là `feature/analysis-and-models`**, chỉ có ở local (không có
  `origin/feature/analysis-and-models`) và **không nằm trong danh sách trigger của `ci.yml`** (chỉ `main`
  và `feature/update-ui-ux`), nên push lên nhánh này không chạy CI; chỉ pull request vào `main` mới chạy.
  Đây là lý do Q1 phải hỏi, và nay đã chốt (mục 4).
- **`README.md` mục "CI" mâu thuẫn với `ci.yml`.** README nói "sáu bước" và "bộ test `slow` và cổng phủ 80%
  **không** chạy trong CI"; `ci.yml` thực tế có 8 bước và **có** chạy `pytest --cov=src --cov-fail-under=80`
  không kèm `-m`, tức là chạy cả bộ `slow`. Đây là trôi tài liệu, không phải hai chính sách khác nhau —
  và hướng đã chốt là **giữ `ci.yml`, sửa README** (Q6 = A). Trạng thái hiện tại: README **vẫn còn sai**
  trên đĩa; việc sửa nó là một thay đổi tài liệu phải làm trong đợt, không phải một quyết định còn mở.
- **Cổng phủ 80% tính trên toàn bộ bộ test là ràng buộc có lý do kỹ thuật**, được ghi ngay trong chú thích
  `ci.yml:44-45`: bảy mô-đun `src/` chỉ có phần phủ đến từ bộ `slow`, nên đặt cờ lên bộ nhanh sẽ đỏ ngay.
  Vì lý do đó, lựa chọn "chỉ tính phủ trên bộ nhanh" (Q6 = B) là lựa chọn sai về kỹ thuật chứ không phải
  một sở thích ngang giá — và người làm đã chọn A.
- **`ruff format --check` phủ một danh sách khai tay**, không phủ toàn repo (`ci.yml:33`, `README.md` mục
  "Lint và định dạng"). Hệ quả: tệp mới tạo mà quên thêm vào danh sách sẽ không được kiểm format (`TD-20`).
  Quy tắc tương ứng được ghi thành `ALWAYS` trong `discovered-rules.md`.
- **Scope `feature` khai `skeleton: on`** và áp sàn phủ 80% + chạy CI trước khi hợp nhất; phần phủ và CI
  trùng với thực hành đã có, còn `skeleton: on` **xung đột với Q2 = B** (mục 4, mục 5). Đây là chỗ duy nhất
  mà một câu trả lời của người làm đi ngược cấu hình đang chạy.
- **Đợt này chạm đúng những chỗ đã biết là mỏng**: `src/analytics/service.py` (không có unit test trực tiếp,
  chỉ được phủ bởi `test_u2_end_to_end`), hình dạng dashboard/CLI (assert số cứng), và `requirements.txt`
  (chưa có gói thống kê/ML nào). Ba điểm này ảnh hưởng trực tiếp tới `## Testing Posture` và `## Code Style`
  của artifact practices.
- **Một tầng mới trong `run --stage` không đụng con số "3 lệnh con"** mà `tests/unit/test_cli.py` khẳng
  định, nhưng **có** đụng danh sách tầng và báo cáo liệt kê tầng — đúng chỗ `TD-11` đang lệch (`STAGES` 4
  tên, báo cáo ghi 6). Vì vậy hình dạng "tầng" (Q5 = B) có một hệ quả kỹ thuật mà hình dạng "lệnh con"
  không có: phải sửa `TD-11`, không chỉ thêm một nhánh `elif` vào CLI.

## 3. Không xác lập được

- **Thứ tự test-trước hay test-sau — đã chốt, không còn mở.** Lịch sử chỉ có 14 commit; mã nguồn và test
  của U3 vào **cùng một commit** (`b384da4`), nên git không phân biệt được. Đó là lý do phải hỏi, và Q3 = A
  đã xác nhận TDD (mục 4). Giá trị `tdd` không suy ra từ git mà từ quyết định của người làm.
- **Có bảo vệ nhánh trên GitHub hay không.** Repo có remote `origin`
  (`https://github.com/dominhhiep21/IT5427.git`) và `ci.yml` có trigger `pull_request`, nhưng không có
  artifact nào trong repo cho biết required checks / branch protection. Không kết luận "CI chặn merge".
  Q1 quyết định *có* chạy CI trên nhánh đợt; nó **không** chứng minh được CI có chặn hợp nhất hay không.
- **Thời gian chạy CI thực tế.** Không có log CI trong repo; `ci.yml` chạy `--stage all` (đọc 1,55 triệu
  dòng) rồi hai lượt `pytest` (lượt hai gồm cả bộ `slow`) trên `windows-2022`, nên chi phí là đáng kể —
  nhưng không có số đo. Q6 = A giữ nguyên chi phí đó (cộng thêm bộ test của đợt), có chủ đích.
- **Có tag phát hành hay không.** `git branch`/`git log` không cho thấy tag trong 15 commit gần nhất;
  `CHANGELOG.md` có mốc `v0.1.0` nhưng không có tag tương ứng được xác nhận. Vì vậy "phiên bản = commit
  hash" vẫn giữ, cộng thêm mốc CHANGELOG.
- **`TD-09` có được sửa trong đợt này hay không.** `code-quality-assessment.md` §3.3 ghi rõ "vẫn nguyên";
  scope document không nhắc tới; phỏng vấn không hỏi. Chưa có quyết định.
- **Ai review, nếu có.** Không có bằng chứng review chéo trong repo; `D-23` của đợt trước nói dự án một
  người. Không kiểm chứng được bằng git author vì mọi commit đều trên một dòng công việc.
- **Đã có `pyproject.toml` hay chưa.** Không có; cấu hình nằm ở `ruff.toml` + `pytest.ini` +
  `requirements.txt`. Không suy ra được ý định gộp về một tệp.

## 4. Phỏng vấn đã chốt

Sáu câu hỏi, sáu câu trả lời, và `Consolidated Summary Confirmation` được người làm xác nhận "Looks
correct". Mỗi mục ghi câu trả lời và cái nó **đóng lại**.

1. **Q1 = A — Nhánh làm việc và cổng CI.** Thêm nhánh đang làm vào danh sách trigger của `ci.yml`.
   *Đóng lại:* giả định "đợt này không có CI tự động". `feature/analysis-and-models` phải được thêm vào
   **cả** `on.push.branches` và `on.pull_request.branches`, cùng lúc với việc tạo nhánh. Việc sửa `ci.yml`
   chưa được thực hiện trong stage này (stage này chỉ ghi practice); nó là một thay đổi của đợt.
2. **Q2 = B — Không dựng lát cắt mỏng trước.** Làm từng phần trọn vẹn theo thứ tự đã chốt: thống kê → mô
   hình → hiển thị. *Đóng lại:* thế đứng "dựng lát cắt mỏng trước" mà bản nháp trước ghi cho `## Walking
   Skeleton`. *Mở ra (đã ghi nhận):* xung đột với `skeleton: on` của scope — xem mục 5.
3. **Q3 = A — Giữ TDD.** Viết test trước rồi mới viết mã, **kể cả phần mô hình**, dù phần đó khó viết test
   trước hơn. *Đóng lại:* nghi vấn "có đổi sang test-sau cho phần mô hình không". `## Testing Posture` giữ
   `- **Methodology**: tdd` và `- **Ordering**` viết lại theo nhịp "từng lớp trong một phần, phần xong rồi
   mới sang phần kế tiếp".
4. **Q4 = A — Lệnh thống kê là bước thứ ba của chuỗi xác nhận**, trước khi mở dashboard. *Đóng lại:* câu
   hỏi "có thêm bước cho S-06 hay không". Chuỗi thành bốn bước: bộ nhanh → `run --stage all` →
   `run --stage stats` → mở dashboard. Bước `stats` đứng **trước** dashboard vì dashboard đọc báo cáo.
5. **Q5 = B — Hình dạng là một tầng mới của `run --stage`**, không phải lệnh con thứ tư. *Đóng lại:* lựa
   chọn giữa `python -m src.pipeline stats` và `run --stage stats`. *Hệ quả:* CLI vẫn 3 lệnh con (assert
   của `tests/unit/test_cli.py` không đổi), nhưng danh sách tầng và báo cáo liệt kê tầng phải sửa cùng lúc
   — `TD-11` (mục 2).
6. **Q6 = A — Cổng phủ giữ như CI hiện tại:** tính trên **toàn bộ** bộ test (nhanh + `slow`), chạy trong
   CI với `--cov-fail-under=80`. *Đóng lại:* mâu thuẫn `ci.yml` ↔ `README.md` (mục 2). Hướng xử lý: giữ
   `ci.yml`, **sửa README**. Không tách cổng sang bộ nhanh, không hạ ngưỡng.

## 5. Còn chưa chắc

- **Xung đột `skeleton: on` ↔ Q2 = B chưa được xử lý ở tầng cấu hình.** Artifact practices ghi trung thực
  câu trả lời (không dựng lát cắt mỏng) và **không** tự sửa scope. Còn mở: delivery-planning có chỉnh scope /
  bỏ Unit skeleton không, hay `construction_policy` ở cổng vào Construction xử lý. Cho tới lúc đó, đây là
  điểm lệch đã biết.
- **`TD-11` (danh sách tầng lệch báo cáo) chưa có thiết kế sửa.** Q5 = B chỉ chốt *hình dạng* (tầng, không
  lệnh con), không chốt cách dọn danh sách tầng đang lệch. Thuộc về functional-design / code-generation.
- **`TD-09` (bộ nhanh chưa hermetic) vẫn nguyên**, và Q6 = A không chạm tới nó: CI vẫn phải dựng dữ liệu
  trước khi test, máy mới clone vẫn đỏ ở bộ "nhanh".
- **`README.md` mục "CI" vẫn sai trên đĩa** cho tới khi có người sửa; quyết định đã có, việc sửa chưa làm.
- **`ci.yml` chưa có `feature/analysis-and-models`** cho tới khi có người sửa; quyết định Q1 đã có, việc
  sửa chưa làm.
- **Bảo vệ nhánh / required checks trên GitHub** không kiểm chứng được từ repo (mục 3), nên "CI xanh" vẫn
  chưa được chứng minh là điều kiện chặn hợp nhất.
- **Mốc CHANGELOG cho đợt này** chưa được chốt về hình thức (có tag hay không); chỉ chắc rằng phải có một
  mốc mới vì bề mặt thay đổi.
- **Vị trí mô-đun thống kê/mô hình trong cây `src/`** chưa được quyết ở stage này; chỉ chắc ràng buộc
  "đọc mart hiện có" và "mọi mô-đun mới có test riêng".

## Sources

- `[scope]` `aidlc/spaces/default/intents/261109-stats-and-models/ideation/scope-definition/scope-document.md`
  — S-01…S-07, thứ tự thi công, điều kiện "xong".
- `[memory:M1]` `aidlc/spaces/default/memory/team.md` — baseline năm mục đã xác nhận ở đợt trước.
- `[memory:M2]` `aidlc/spaces/default/memory/project.md` — `## Mandated` / `## Forbidden` hiện hành.
- `[report]` `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/` — sáu artifact reverse-engineering
  đã đọc (mục 1).
- `[repo]` `ci.yml`, `ruff.toml`, `pytest.ini`, `requirements.txt`, `README.md`, `CHANGELOG.md`,
  `.gitignore`, `git log -15`, `git branch -a`, `.aidlc/scopes/aidlc-feature.md`.
- `[ondisk]` Số đếm trực tiếp: 40 tệp test, 353 hàm test, 9 `slow`, 70 tệp `src/`, 55 tệp có
  `from __future__ import annotations`.
- `[Q1]` `practices-discovery-questions.md` — nhánh làm việc và trigger CI.
- `[Q2]` `practices-discovery-questions.md` — có dựng lát cắt mỏng trước không.
- `[Q3]` `practices-discovery-questions.md` — cách viết test của đợt.
- `[Q4]` `practices-discovery-questions.md` — vị trí lệnh thống kê trong chuỗi xác nhận.
- `[Q5]` `practices-discovery-questions.md` — hình dạng lệnh thống kê.
- `[Q6]` `practices-discovery-questions.md` — cổng phủ 80% chạy ở đâu.

## Assumptions & Open Questions

- **Giả định A1**: `team.md` đang lạc hậu ở ba điểm (khối lượng test, sự tồn tại của CI, mức cưỡng chế
  ngưỡng phủ) và bản nháp này thay bằng trạng thái thực tế tại commit `ea77bdf`. Kiểm chứng: mục 2.
- **Giả định A2**: "nhánh dài hơi của đợt" vẫn là thực hành, chỉ đổi tên nhánh và bổ sung trigger. **Đã
  được xác nhận** bởi Q1 = A (thêm nhánh vào CI, không chuyển sang trunk-based).
- **Giả định A3**: `tdd` vẫn đúng. **Đã được xác nhận** bởi Q3 = A; không còn là giả định.
- **Giả định A4**: việc sửa `ci.yml` và `README.md` theo Q1/Q6 là thay đổi của đợt này, không phải của
  stage practices-discovery; stage này chỉ ghi lại practice và bằng chứng.
- **Câu hỏi mở Q1**: nhánh làm việc và trigger CI — **đã trả lời** (Q1 = A).
- **Câu hỏi mở Q2**: cổng phủ 80% chạy ở đâu — **đã trả lời** (Q6 = A).
- **Câu hỏi mở Q3**: `tdd` còn hiệu lực không — **đã trả lời** (Q3 = A).
- **Câu hỏi mở Q4**: bước CLI thống kê trong chuỗi xác nhận — **đã trả lời** (Q4 = A, Q5 = B).
- **Câu hỏi mở Q5**: cách xử lý xung đột `skeleton: on` ↔ Q2 = B (mục 5) — **vẫn mở**.
- **Câu hỏi mở Q6**: `TD-09`, `TD-11`, mốc CHANGELOG, vị trí mô-đun mới (mục 5) — **vẫn mở**, thuộc các
  stage sau.
