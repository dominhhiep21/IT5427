# Bằng chứng — Practices Discovery, đợt `261111-model-feature-improvemen`

> Ghi lại **cái gì đã đọc, cái gì đã đo lại, cái gì chỉ suy ra**, và **cái gì lần quét mới bác bỏ** trong
> bản ghi thực hành hiện hành (`aidlc/spaces/default/memory/team.md`). §5 ghi ba quyết định người làm đã
> chốt ngày 2026-11-12; §6 liệt kê những điểm hội thoại **còn** phải chốt — bản nháp không tự quyết chúng.
>
> Ngày đo: 2026-11-11. Ngày chốt ba quyết định: 2026-11-12. Nhánh: `feature/analysis-and-models`.

## 1. Nguồn đã đọc

| Nguồn | Lấy được gì | Mức tin cậy |
|---|---|---|
| `codekb/.../code-structure.md` | Danh mục tệp, số dòng từng tệp, phân loại, quy ước đặt tên, hướng phụ thuộc, điểm vào | Đọc toàn văn; **các con số tổng đã đo lại độc lập** (§2) |
| `codekb/.../technology-stack.md` | 12 gói ghim + lý do, nền tảng, định dạng lưu trữ, 9 callback, rủi ro công nghệ | Đọc toàn văn; đối chiếu `requirements.txt` và `ci.yml` |
| `codekb/.../dependencies.md` | Phụ thuộc ngoài theo mô-đun, đồ thị gói, **bảng "cùng một sự thật khai ở nhiều nơi"**, chi phí thêm bảng/cột/tab | Đọc toàn văn |
| `codekb/.../code-quality-assessment.md` | Sổ nợ `TD-01`…`TD-27`, §7 chạm mã của U1/U2/U3, §7.1 danh sách test khẳng định hình dạng, §8 khuyến nghị | Đọc toàn văn; đây là nguồn chính cho mục "điều hội thoại phải chốt" |
| `codekb/.../architecture.md` | Phong cách kiến trúc, bảng phương án đã loại, luồng dữ liệu, 11 quyết định, §7 cơ hội cải thiện | Đọc toàn văn |
| `codekb/.../business-overview.md` | 5 KPI baseline, chỉ số mô hình (AUC 0,5133…), ranh giới nghiệp vụ, 3V, thuật ngữ | Đọc toàn văn |
| `aidlc/spaces/default/memory/team.md` | Năm mục thực hành hiện hành — **đối tượng được cập nhật** | Đọc toàn văn |
| `aidlc/spaces/default/memory/project.md` | 15 `NEVER` + 20 `ALWAYS` đã chốt ở hai đợt trước, kèm nguồn | Đọc toàn văn |
| `.github/workflows/ci.yml` | 9 bước, 3 nhánh trigger (cả `push` và `pull_request`), danh sách `ruff format --check` **34 mục**, vị trí `run --stage all`:40, `stats`:45, bộ nhanh:48, cổng phủ:53, smoke:58 | Đọc trực tiếp; đếm mục format **đã đo lại** (§2) |
| `pytest.ini` | `testpaths = tests`, marker `slow`, `addopts = -ra` | Đọc trực tiếp |
| `ruff.toml` | `line-length = 112`, `target-version = "py313"`, `select = ["E4","E7","E9","F"]`, 8 `extend-exclude`, **5** `per-file-ignores` (4×`F401` + 1×`E402`) | Đọc trực tiếp |
| `requirements.txt` | **12** gói ghim + chú thích lý do; ghi chú riêng rằng `numpy` **không** ghim | Đọc trực tiếp |
| `README.md` | Mục "CI" (9 bước, ba nhánh, cổng phủ trên toàn bộ), mục "Test", mục "Lưu ý" (mô hình không lưu ra đĩa) | Đọc trực tiếp phần liên quan |
| `git log --oneline -15` | **14** commit; đầu chuỗi `ea77bdf chore: lưu trữ hồ sơ 261105-default`; một lần hợp nhất `9ed73e2`; 3 commit không tiền tố | Chạy trực tiếp |
| `git status --short --branch` | Nhánh `feature/analysis-and-models`; **21 tệp modified + 21 mục untracked** | Chạy trực tiếp |
| `git rev-list --count main..feature/analysis-and-models` | `1` — nhánh đi trước `main` đúng 1 commit | Chạy trực tiếp |

## 2. Số liệu đã đo lại độc lập (không chỉ tin CodeKB)

| Phép đo | Kết quả | Lệnh |
|---|---|---|
| Tệp Python trong `src/` | **74** | `pathlib.Path('src').rglob('*.py')` |
| Dòng trong `src/` | **11.333** | cộng `splitlines()` |
| Tệp trong `tests/` | **54** (**49** mô-đun `test_*`) | `rglob('*.py')` |
| Hàm test | **499** | `^def (test_\w+)` |
| Dấu `mark.slow` | **12** | `mark\.slow` |
| Dòng trong `tests/` | **10.086** | cộng `splitlines()` |
| `from __future__ import annotations` trong `src/` | **59 / 74** tệp | tìm chuỗi |
| `TODO`/`FIXME`/`HACK` trong `src/` | **0** | regex `\b(TODO\|FIXME\|HACK)\b` |
| Mục trong `ruff format --check` | **34** | đọc `ci.yml` bằng PyYAML, tách dòng lệnh |
| Nhánh trigger | **3** ở **cả** `push` và `pull_request` | đọc `ci.yml` bằng PyYAML |
| `STAGES` | **5** tên: `ingest`, `clean`, `integrate`, `analyze`, `stats` | đọc `src/pipeline/stages.py:24` |
| Lệnh con CLI | **3**: `run`, `micro-batch`, `replay` | đọc `src/pipeline/cli.py:21,29,32` |
| Tab của dashboard | **5**: `overview`, `category`, `delivery`, `<integration>`, `phan-tich` | đọc `src/dashboard/app.py:321-413` |
| Output của callback báo cáo | **9** | đọc `src/dashboard/app.py:452-460` |
| Tab phân tích | 4 thẻ, 3 mục | đọc `src/dashboard/analysis_tab.py:30,45,47` |

Không đo lại được bằng lệnh (chỉ đọc mã, và môi trường toàn cục không có `duckdb` nên không import được
`src.pipeline.stages`): **9 callback tổng** và **11 view**. Hai con số này lấy từ `code-structure.md` và từ
việc đếm khai báo `@app.callback` trong `app.py` (2 + 6 của `src/integration/tab.py` + 1 của
`analysis_tab.py`) — khớp nhau.

## 3. Thực tế git — điều không được bỏ qua

Cây làm việc **không sạch**, và đây không phải chi tiết vặt:

- **Chưa commit nhưng có thật trên đĩa:** `src/analytics/statistics.py`, `src/analytics/model.py`,
  `src/analytics/report.py`, `src/dashboard/analysis_tab.py` (untracked) và **chín** mô-đun test mới
  (`test_analytics_statistics.py`, `test_analytics_model.py`, `test_analytics_report.py`,
  `test_dashboard_analysis_tab.py`, `test_analysis_tab_contrast.py`, `test_pipeline_stages.py`,
  `test_ci_config.py`, `test_u1_stats_end_to_end.py`, `test_u2_model_end_to_end.py`).
- **Đã sửa nhưng chưa commit:** `ci.yml`, `requirements.txt`, `README.md`, `CHANGELOG.md`, `assets/style.css`,
  `src/analytics/service.py`, `src/dashboard/app.py`, `src/pipeline/cli.py`, `src/pipeline/stages.py`,
  `tests/integration/test_u3_end_to_end.py`, `tests/unit/test_dashboard_smoke.py`, cùng toàn bộ artifact
  CodeKB và `memory/{team,project}.md`.
- **HEAD là `ea77bdf`, một commit lưu trữ hồ sơ** — không phải commit của tầng thống kê/mô hình.

**Hệ quả cho mọi artifact của đợt này:** commit hash `ea77bdf` **không** mô tả mã đã được quét. Tầng
`stats`/`model`/tab phân tích — tức phần lớn nội dung CodeKB vừa cập nhật — chỉ tồn tại trong cây làm việc.
Một người clone repo ở `ea77bdf` sẽ **không** thấy `src/analytics/model.py`, và bộ test "nhanh" ở đó cũng
không có 499 hàm test. Vì vậy trong `team-practices.md` mục `## Way of Working` có thêm một thực hành
tương ứng: đọc đĩa, không đọc `git log`, khi cần biết hệ thống đang làm gì; và một lớp mới chỉ được coi là
của đội khi đã vào commit.

Ghi chú phụ: `git log --oneline -15` trả về **14** dòng (repo chỉ có 14 commit), nên con số "14 commit"
trong bản ghi cũ vẫn đúng — nó không phải chỗ phải sửa. Chỗ phải sửa là **cách diễn giải** con số đó.

## 4. Lần quét mới đã bác bỏ / thay đổi gì so với bản ghi trước

Đây là danh sách **các khẳng định trong `memory/team.md` đã bị sửa**, kèm bằng chứng.

| # | Khẳng định cũ | Hiện trạng theo bằng chứng mới | Nguồn |
|---|---|---|---|
| 1 | "70 tệp Python trong `src/` (9.444 dòng)" | **74 tệp / 11.333 dòng** | đo lại (§2) |
| 2 | "40 mô-đun test với **353** hàm test (9 hàm `slow`), 7.358 dòng test — 78% khối lượng `src/`" | **49 mô-đun / 499 hàm / 12 `slow` / 10.086 dòng — 0,89 lần** `src/`; 54 tệp test | đo lại (§2) |
| 3 | "**4 tab, 8 callback**, 9 output, 11 view" | **5 tab, 9 callback**, 9 output, 11 view; thêm **4 thẻ** + **3 mục** của tab phân tích | `app.py:321-413,452-460`; `analysis_tab.py:30,45,47`; `code-quality-assessment.md` §7.1 |
| 4 | "`STAGES` có 4 tên trong khi một báo cáo ghi 6" | `STAGES` có **5** tên; `_run_all` ghi **6** `StageResult` và **không** chạy `stats` | `stages.py:24`; `TD-11` |
| 5 | "danh sách tầng (`STAGES`) hiện **không có test riêng**" | **Đã có**: `tests/unit/test_pipeline_stages.py` (261 dòng) khẳng định 5 tên, `choices` khớp `STAGES \| {"all"}`, 3 lệnh con | `code-structure.md` §2.5 |
| 6 | "phép đếm 3 lệnh con nằm ở `tests/unit/test_cli.py`" | Phép đếm **đã chuyển** sang `test_pipeline_stages.py:157-161`; `test_cli.py` còn 2 ca parser + 1 ca chạy thật (21 dòng) | `code-structure.md` §2.5 |
| 7 | "`README.md` mục 'CI' đang nói ngược lại (bộ `slow` và cổng phủ không chạy trong CI)" | **Đã đóng**: README mục "CI" nay mô tả đúng 9 bước, đúng ba nhánh, đúng cổng phủ trên toàn bộ | `README.md:166-186` |
| 8 | "đợt này **bổ sung** `feature/analysis-and-models` vào cả hai danh sách trigger" | **Đã làm**: `ci.yml:5-13` có đủ ba nhánh ở cả `push` và `pull_request` | `ci.yml` |
| 9 | "danh sách `ruff format --check` khai tay trong `ci.yml:33`" | Nay ở **`ci.yml:35`**, **34 mục**; `test_ci_config.py` canh 14 tệp của đợt trước, không canh tệp đợt sau | đọc `ci.yml`; `TD-20` |
| 10 | "10 gói ghim" (một chỗ trong bản ghi cũ; chỗ khác đã ghi 10) | **12** gói, thêm `scipy` 1.15.2 và `scikit-learn` 1.6.1 kèm lý do; `numpy` vẫn **không** ghim | `requirements.txt`; `technology-stack.md` §2 |
| 11 | "55 trong 70 tệp `src/` mở đầu bằng `from __future__ import annotations`" | **59 trong 74** | đo lại (§2) |
| 12 | "`CHANGELOG.md` ghi mốc `v0.1.0` (2026-11-06)" | **Bốn** mốc `v0.1.0` → `v0.4.0` | `code-structure.md` §1; `code-quality-assessment.md` §5 |
| 13 | "khoảng trống test: `src/analytics/service.py` … `stages.py`" | Năm phương thức KPI **cũ** vẫn trống; **bốn** phương thức mới của tầng `stats` đã có test thật trên DuckDB tạm; `stages.py` có test cho `run_stage` nhưng đường `run_all` vẫn trống | `code-quality-assessment.md` §3.2 |
| 14 | "bộ nhanh chưa hermetic: 5 test dashboard + 1 ca CLI" | Vẫn đúng (`TD-09`, mức Cao) — nhưng **năm mô-đun test mới** dựng mart trong `tmp_path` nên không dính; đây là mẫu phải theo | `code-quality-assessment.md` §3.3 |
| 15 | "`ruff.toml` có bốn `per-file-ignores`" | **Năm** mục: bốn `F401` + một `E402` (`tests/conftest.py`); `extend-exclude` 8 mục | `ruff.toml:6-29` |
| 16 | Bản ghi không nhắc gì tới cây làm việc bẩn | **21 tệp modified + 21 mục untracked**, trong đó có cả bốn mô-đun nguồn của tầng suy luận (§3) | `git status` |
| 17 | Bản ghi không nhắc `TD-21`…`TD-27` | Lần quét mới thêm bảy mục nợ gắn trực tiếp với đợt này: baseline mô hình khai ở 4 nơi (`TD-21`), đặc trưng bị khoá hai lớp + cấm một cột không tồn tại (`TD-22`), tab "chỉ đọc" mâu thuẫn với vùng nhập liệu (`TD-23`), hợp đồng báo cáo cứng (`TD-24`), không có chỗ lưu mô hình (`TD-25`), phụ thuộc chéo giao diện (`TD-26`), `# noqa` không tác dụng (`TD-27`) | `code-quality-assessment.md` §6 |
| 18 | Chỉ số mô hình không được nhắc trong bản ghi thực hành | AUC **0,5133** (dưới mốc 0,70 → cờ `auc_below_target`), precision 0,0866, recall 0,2645, ngưỡng 0,40 — **không** thuộc `BASELINE`, nên là vùng đợt này được phép dịch chuyển miễn đo lại đúng khung | `business-overview.md` §4; `test_u3_end_to_end.py:116-117` |

Những gì **không** bị bác bỏ và được giữ nguyên: `tdd` (Q3 = A của đợt trước, **xác nhận lại ở đợt này**
— Q1 = A), cổng phủ 80% trên toàn bộ bộ test (Q6 = A), chuỗi xác nhận bốn bước (Q4 = A, Q5 = B), `stats`
là tầng chứ không phải lệnh con (Q5 = B), không dựng lát cắt mỏng (Q2 = A của đợt này; đợt trước Q2 = B
tương ứng), một người làm một người quyết định, Conventional Commits ở mức khuyến khích, 14 commit / một
lần hợp nhất, nhánh `feature/analysis-and-models` đi trước `main` 1 commit, không có môi trường triển
khai, không có kiểm tra kiểu tĩnh.

Một khẳng định trong danh sách trên **đã bị chính hội thoại này bác bỏ**, không phải bởi lần quét:
"mô hình không được lưu ra đĩa". Q3 = A đổi nó — tệp mô hình nay sống ở `data/models/`, sinh bằng
`pickle` của thư viện chuẩn, **không** được commit. §5 ghi lại quyết định đó, và `## Deployment` trong
`team-practices.md` đã được sửa theo.

## 5. Ba quyết định của người làm (2026-11-12)

Ba chỗ bằng chứng không tự trả lời được đã được hỏi; câu hỏi cùng đầy đủ phương án nằm ở
`practices-discovery-questions.md`. Dưới đây là điều đã chốt, điều bị loại, và hệ quả lên artifact.

| # | Câu hỏi | Chốt | Phương án bị loại | Hệ quả |
|---|---|---|---|---|
| Q1 | Giữ TDD cho đợt này không | **A** — giữ TDD cho mọi lớp, kể cả phần mô hình; test viết trước khẳng định **hành vi** (cỡ mẫu, chia tập theo `order_id`, không rò rỉ), **không** khẳng định một AUC mục tiêu | B (test-after riêng cho phần mô hình); C (`custom`) | `## Testing Posture`: `Methodology` giữ `tdd`, thêm một bullet về **loại khẳng định** của test lớp mô hình; quy tắc "không đặt AUC làm kỳ vọng" vào `discovered-rules.md` |
| Q2 | Có dựng lát cắt mỏng trước không | **A** — không dựng; làm trọn từng Bolt như đợt trước, thứ tự thống kê → mô hình → hiển thị | B (nới mart → một đặc trưng → logistic thô → vùng nhập liệu trống rồi mới làm thật) | `## Walking Skeleton`: câu trả lời của đợt này thay chỗ "bản nháp không tự chọn"; **điểm lệch với `skeleton: on` giữ nguyên**, không được giải quyết ngầm |
| Q3 | Lưu mô hình bằng gì | **A** — `data/models/` + **`pickle` của thư viện chuẩn**, không thêm phụ thuộc; tệp **không** commit, mỗi máy sinh lại bằng `run --stage stats` | B (`joblib`, phải ghim thêm gói); C (thư mục được commit); D (hoãn sang Functional Design) | `## Deployment`: mục "mô hình không được lưu ra đĩa" bị **thay**; `TD-25` hẹp lại còn cấu hình + tài liệu; chuỗi xác nhận bước 3 nay sinh **cả** tệp mô hình; quy tắc "không commit tệp mô hình" vào `discovered-rules.md` |

**Vì sao Q1 = A vẫn là TDD dù AUC chỉ biết sau khi chạy.** Test viết trước ở lớp mô hình không nhắm vào
chất lượng mô hình mà nhắm vào **tính đúng của khung**: cỡ mẫu, cách chia tập theo `order_id`, và việc
không cột rò rỉ nào lọt vào ma trận đặc trưng. Chất lượng (AUC 0,5133; precision 0,0866; recall 0,2645;
ngưỡng 0,40) vẫn được **ghi ra và hiển thị** — nó thuộc báo cáo, không thuộc cổng; đây cũng là lý do
`business-overview.md` §4 xếp chỉ số mô hình ngoài `BASELINE`.

**Vì sao Q2 = A vẫn giữ nguyên điểm lệch.** Người làm đã được nêu rõ ba hạng mục U1/U2/U3 phụ thuộc dữ
liệu lẫn nhau và hạng mục đầu phải sửa mart dùng chung — tức cái giá của việc không có lát cắt mỏng đã
tăng so với đợt trước — và **vẫn** chọn A. Quyết định đó thuộc về người làm; scope `feature` vẫn khai
`skeleton: on`, nên điểm lệch tiếp tục được ghi ở `## Walking Skeleton` cho tới khi delivery-planning chọn
chế độ Construction cho khớp, hoặc có một lần chỉnh scope có chủ đích.

**Vì sao Q3 = A đổi định nghĩa "phát hành" mà không biến tệp mô hình thành artifact.** `data/models/` nằm
dưới `data/` — bị `.gitignore` chặn, cùng chỗ với `data/marts/` và `data/reports/` — nên tệp mô hình là
sản phẩm sinh ra, **không** phải thứ được phát hành: "phát hành" vẫn là chạy từ mã nguồn. Cái mới là một
ràng buộc vận hành: máy mới clone **phải** chạy `run --stage stats` trước khi vùng dự đoán dùng được, và
vùng đó phải chịu được trạng thái "chưa có tệp mô hình" thay vì sập. Thêm một giới hạn phải nói: `pickle`
gắn với phiên bản thư viện đã sinh ra nó, nên tệp **không** phải định dạng trao đổi giữa các máy — máy
khác sinh lại tệp của mình.

## 6. Điều hội thoại còn phải chốt (bản nháp không tự quyết)

1. **Hình dạng của tab phân tích.** `TD-23`: tab đang được khai "chỉ đọc" ở ba nơi (câu chữ
   `TEXTS["model_caption"]`, test `test_model_block_offers_no_input_control`, `README.md:101-105`), trong
   khi U3 cần **vùng nhập liệu dự đoán**. Cần chốt: đặt vùng nhập liệu trong tab này (và sửa cả ba nơi
   trong cùng thay đổi) hay ở một tab khác. Số callback/output sẽ đổi theo, kéo theo ba test đếm.
2. **Chỗ chứa số liệu mô hình mới.** `TD-24`: `analysis.json` đang `version: 2` với `ModelBlock` đúng
   **7 trường**, `_model_block` **từ chối** tệp thiếu trường. Thêm số của estimator thứ hai vào túi
   `counts` (nhanh, không kiểu) hay tăng `REPORT_VERSION` lên 3 (đúng, nhưng ba test + tab phải theo).
3. **Baseline mới đo ở đâu và ai chịu trách nhiệm.** `TD-21`: baseline quần thể mô hình đang là chỗ khai
   thứ tư của 96.478/7.826. Đổi khung dự đoán và đơn vị dự đoán (sang grain dòng hàng, ≈112.650 dòng) thì
   bộ ba số (số dòng, số nhãn dương, mốc cắt) phải mới và phải được **đo lại** — cần chốt nó sống ở đâu,
   không sửa `reconcile.BASELINE`.
4. **Định nghĩa cột cấm sau khi đổi khung.** `order_delivered_carrier_date` hiện nằm trong
   `FORBIDDEN_COLUMNS` **và** không tồn tại trong mart. Nếu mốc bàn giao thành **mốc quan sát** thì cột đó
   phải rời danh sách cấm và các cột "sau bàn giao" mới là cấm. Đây là quyết định về **định nghĩa rò rỉ**,
   không phải chi tiết kỹ thuật — cần người làm chốt trước khi code.
5. **`stats` có nằm trong `--stage all` hay không.** `TD-11`; đợt này chạm `stages.py` nên đây là dịp rẻ
   nhất. Hiện `STAGES` nói có, `_run_all` nói không, và chuỗi xác nhận bốn bước đang dựa vào việc gọi
   `stats` riêng.
6. **Thời gian và ngân sách.** Ngân sách 300 s / 900 s / 900 s **đã là test**. Thêm estimator thứ hai và
   đổi sang grain dòng hàng sẽ đẩy thời gian lên; cần chốt nới ngân sách **có chủ đích** hay giữ nguyên
   và chấp nhận bộ `slow` đỏ trước khi tối ưu.
7. **Nhánh của đợt.** Đợt trước dùng `feature/analysis-and-models`; đợt này tiếp tục trên nhánh đó hay mở
   nhánh mới? Nếu mở nhánh mới thì quy tắc hai bước (thêm vào **cả** hai danh sách trigger) áp ngay.

Ba mục đã đóng ở đây (`tdd`, lát cắt mỏng, lưu mô hình) không còn là câu hỏi mở, nhưng chúng **không**
đóng các câu hỏi kỹ thuật mà chúng kéo theo: Q3 = A đã chốt *chỗ lưu và cách lưu*, còn `AppConfig` thêm
trường nào, ai ghi/đọc tệp, và vùng dự đoán hiển thị gì khi chưa có tệp vẫn thuộc Functional Design. Q1 = A
đã chốt *cách giữ TDD*, nhưng việc chọn estimator thứ hai và đặt ngưỡng vẫn chưa được chốt ở đâu — mục 2
dưới đây chỉ nói **số liệu của estimator đó sống ở đâu**, không nói chọn nó thế nào.

## 7. Điều bản nháp này **không** làm

- Không sửa `aidlc/spaces/default/memory/team.md` hay `memory/project.md` — việc ghi vào memory là bước
  riêng sau cổng xác nhận.
- Không tự trả lời ba câu hỏi: chúng đã được **hỏi người làm** và câu trả lời được ghi ở §5, không suy ra
  từ git hay từ code.
- Không sửa mã, `README.md` hay `.gitignore` để thực thi Q3 = A — artifact này chỉ ghi quyết định; việc
  thêm thư mục mô hình vào `AppConfig`, đặt chỗ `pickle.dump`/`pickle.load`, và viết lại mục "Lưu ý" của
  `README.md` thuộc các bước sau.
- Không sửa hay đề xuất sửa scope (`skeleton: on`); xung đột được **nêu** ở `## Walking Skeleton`, không
  được giải quyết.
- Không tự thêm quy tắc nào không có nguồn kiểm được trong repo.
- Không chạy test hay build (môi trường toàn cục thiếu `duckdb`); mọi số liệu ở đây là **đo tĩnh trên đĩa**
  hoặc đọc từ CodeKB, và được ghi rõ nguồn ở từng dòng.
