# Team-Level Rules

> This team's affirmed practices and corrections. Loaded after `org.md` as
> strict-additive guidance; contradictions with broader policy are rejected.
> Populated by the practices-discovery affirmation gate. Edit at the gate,
> not directly.

## Way of Working

- **Một người làm, một người quyết định.** Chúng tôi không có review chéo, không có người phê duyệt thứ
  hai, không có quy ước "mỗi thay đổi một nhánh". Cổng tự động duy nhất là CI. Lịch sử git có **14
  commit** trên một dòng công việc; lần hợp nhất duy nhất vẫn là gộp cả nhánh nâng cấp vào `main`
  (`9ed73e2 chore: hợp nhất nhánh nâng cấp tích hợp và giao diện vào main`). Không có nhánh ngắn hạn nào
  được hợp nhất qua pull request có review. (`git log --oneline -15`.)
- **Nhưng lịch sử git không còn mô tả mã đang chạy, và chúng tôi làm việc theo đĩa.** Cây làm việc của
  `feature/analysis-and-models` đang mang **thay đổi chưa commit**: ba tệp nguồn mới của tầng suy luận
  (`src/analytics/statistics.py`, `model.py`, `report.py`), tab thứ năm (`src/dashboard/analysis_tab.py`)
  và **chín mô-đun test mới** đều đang ở trạng thái *untracked*; nhiều tệp khác (kể cả `ci.yml`,
  `requirements.txt`, `src/pipeline/stages.py`, `README.md`) đang *modified*. Commit đầu chuỗi
  (`ea77bdf`) là một commit **lưu trữ hồ sơ**, không phải commit của tầng đó. Vì vậy: **commit hash
  không mô tả mã được quét**, và khi cần biết "hệ thống đang làm gì" chúng tôi đọc đĩa, không đọc
  `git log`. Hệ quả thực hành: một lớp mới chỉ được coi là của đội khi nó đã vào commit — trước đó nó
  vẫn có thể biến mất cùng cây làm việc.
- **Chúng tôi làm việc trên một nhánh dài hơi của đợt, không phải trên `main`.** Hiện tại là
  `feature/analysis-and-models`, đi trước `main` **1 commit** (`git rev-list --count`). Trunk vẫn là
  `main`; nhánh đợt chỉ để gom thay đổi rồi hợp nhất một lần — không phải nhánh cho từng đơn vị công việc.
- **Mở nhánh là một việc hai bước: tạo nhánh, rồi thêm nhánh đó vào danh sách trigger của CI.** Việc này
  **đã làm xong** cho đợt trước: `.github/workflows/ci.yml:5-13` nay khai **ba** nhánh — `main`,
  `feature/update-ui-ux`, `feature/analysis-and-models` — ở **cả** `push` và `pull_request`. Chúng tôi
  không chấp nhận "đợt này không có cổng tự động": một nhánh không có trong danh sách trigger là một
  nhánh làm việc không có ai kiểm. Vì danh sách khai tay, đợt sau mở nhánh mới thì vẫn phải sửa cả hai
  danh sách **cùng lúc** với việc đặt tên nhánh.
- **Thông điệp commit theo Conventional Commits là thói quen đã thành nếp, chưa thành luật.**
  11 trong 14 commit có tiền tố (`feat:`, `fix:`, `chore:`); ba commit cũ (`first commit`,
  `Update plan U3`, `Remove aidlc v1`) thì không. Chúng tôi giữ ở mức khuyến khích, không chặn commit vì
  thiếu tiền tố.
- **Một đơn vị công việc chỉ xong khi test end-to-end của nó xanh trên dữ liệu thật.** Nay có **năm**
  test tích hợp mang marker `slow` chạy toàn pipeline từ `dataset/`:
  `tests/integration/test_u1_end_to_end.py`, `test_u2_end_to_end.py`, `test_u3_end_to_end.py`,
  `test_u1_stats_end_to_end.py`, `test_u2_model_end_to_end.py`, cộng `tests/data_quality/test_real_dataset.py`
  khẳng định dị thường trên CSV thật. Đây là thực hành mạnh nhất mà bằng chứng xác lập được, và là chỗ
  phải gánh nhiều nhất khi đổi khung dự đoán — xem `## Walking Skeleton`.
- **Trước khi commit chúng tôi chạy bộ nhanh, sau khi push CI chạy phần còn lại.** Cục bộ:
  `python -X utf8 -m pytest -m "not slow"`. Trên CI (`ci.yml`, 9 bước): cài phụ thuộc → `ruff check .`
  và `ruff format --check` (danh sách khai tay, `ci.yml:35`) → `run --stage all` (`:40`) →
  `run --stage stats` (`:45`) → bộ nhanh (`:48`) → `pytest --cov=src --cov-fail-under=80` (`:53`) →
  smoke nạp `config/integration-sources.yaml` (`:58`). `README.md` mục "CI" nay khớp với workflow — chỗ
  trôi tài liệu của đợt trước **đã đóng**.
- **Không hồi quy là điều kiện, không phải mong muốn.** 5 KPI baseline (doanh thu delivered
  15.419.773,75 BRL; 96.478 đơn delivered; AOV 159,83 BRL; 7.826 đơn trễ; 8,11% tỷ lệ trễ), số dòng của
  **9** bảng nguồn, số dòng **9** bảng mart, **11** view DuckDB và baseline quần thể mô hình
  (96.478 đơn / 7.826 đơn trễ, mốc chia `2018-04-01`) là hợp đồng cứng, được `KpiReconciler`,
  `StarSchemaValidator` và test tích hợp khẳng định lại. Chỉ số mô hình (AUC 0,5133; precision 0,0866;
  recall 0,2645; ngưỡng 0,40) **không** thuộc baseline đó — chúng chỉ được ghi ra và hiển thị, nên đây
  đúng là vùng đợt này được phép dịch chuyển, miễn là **đo lại** trong đúng khung và đơn vị mới.
- **Quyết định được ghi thành văn bản trong workspace AI-DLC**, không chỉ trong đầu: mỗi intent có record
  riêng dưới `aidlc/spaces/default/intents/<YYMMDD>-<label>/` (state, decision log, câu hỏi, artifact
  theo tầng). Nay có ba record song song (`261105-default` đã lưu trữ, `261109-stats-and-models`,
  `261111-model-feature-improvemen`).
- **Thứ tự thi công theo phụ thuộc dữ liệu, không theo mức độ hấp dẫn của giao diện.** Đợt trước đã chốt
  và đã đi đúng thứ tự đó: thống kê (cho kết quả thấy được sớm nhất) → mô hình (cần dựng đặc trưng và
  kiểm rò rỉ) → hiển thị (khi báo cáo đã có hình dạng ổn định). Đợt này đi tiếp trên cùng lớp, và
  `code-quality-assessment.md` §7.3 xác nhận thứ tự đó vẫn đúng: phải **đo lại baseline** trước khi
  huấn luyện mô hình mới, không có mốc so thì mọi con số sau đều vô nghĩa. Hội thoại đợt này **xác nhận
  lại** đúng thứ tự đó (Q2 = A: làm trọn từng Bolt, không dựng lát cắt mỏng) — chi tiết ở
  `## Walking Skeleton`.
- **Phạm vi do một người chốt và ghi lại trước khi làm.** Mỗi hạng mục có mức (Bắt buộc / Nên có) và danh
  sách "Ngoài phạm vi"; mở rộng ra ngoài danh sách đó là thay đổi phạm vi, phải chốt lại chứ không tự
  quyết trong lúc code. Đợt này ba hạng mục U1/U2/U3 đã được ghi trong
  `ideation/scope-definition/scope-document.md`; `code-quality-assessment.md` §7.2 liệt kê chính xác
  từng điểm chạm mã của ba hạng mục đó.
- **Đổi hình dạng bề mặt là đổi hợp đồng, và hợp đồng được khẳng định bằng test.** Hình dạng hiện tại:
  **5 tab, 9 callback, 9 output, 11 view, 3 lệnh con CLI, 4 thẻ tóm tắt và 3 mục của tab phân tích**.
  Thêm/bớt bất kỳ thứ nào trong số đó là thay đổi có chủ đích phải sửa test **trong cùng thay đổi** — chi
  tiết ở `## Testing Posture`.

## Walking Skeleton

- **Câu trả lời hiện hành của đợt này: KHÔNG dựng lát cắt mỏng chạy xuyên suốt trước** (hỏi lại và trả
  lời lại ở đợt này — Q2 = A; đợt trước cũng vậy, Q2 = B của lần đó). Chúng tôi làm trọn vẹn từng phần
  theo thứ tự đã chốt — **thống kê → mô hình → hiển thị** — nghĩa là phần mô hình chỉ bắt đầu khi phần
  thống kê xong theo định nghĩa "xong" của nó, và phần hiển thị chỉ bắt đầu khi báo cáo mô hình đã có
  hình dạng ổn định.
- **Bằng chứng mới cho thấy cái giá của lựa chọn đó, cụ thể hơn lúc nó được chốt.** Toàn bộ tầng suy luận
  (3 tệp nguồn, 1 tab, 9 mô-đun test, ~2.900 dòng mã và test) hiện **chỉ tồn tại trong cây làm việc chưa
  commit**. Không có mốc nghiệm thu trung gian nào trên đĩa có thể chỉ vào; nếu cây làm việc mất, tầng
  đó mất theo. Đây không phải lý do để đổi câu trả lời — nó là **dữ kiện đã được đưa vào câu hỏi Q2 của
  đợt này** khi hỏi lại cùng câu đó cho ba hạng mục U1/U2/U3; người làm đã trả lời sau khi biết dữ kiện
  này (xem mục dưới).
- **Cái giá chúng tôi đã chấp nhận, và cách bù — vẫn giữ nguyên hiệu lực.** Không có lát cắt mỏng nghĩa
  là rủi ro khớp nối bị dồn về cuối (khi nối báo cáo thống kê vào một tab của dashboard). Chúng tôi bù
  bằng ba thứ: (a) mỗi phần phải có test end-to-end riêng chạy trên dữ liệu thật **ngay khi phần đó
  xong** — đợt trước đã làm đúng: `test_u1_stats_end_to_end.py` và `test_u2_model_end_to_end.py` ra đời
  cùng tầng của chúng; (b) tầng thống kê vào chuỗi xác nhận của mọi đơn vị công việc (`## Deployment`);
  (c) vùng hiển thị được làm bằng thay đổi nhỏ ngay sau phần mô hình, không gộp vào một lần nối lớn.
- **Chuỗi xác nhận end-to-end của một đơn vị công việc** được khai **một chỗ duy nhất** ở
  `## Deployment` (bốn bước, có tầng `stats`). Mục này không nhắc lại để khỏi lệch — nguyên tắc "một sự
  thật khai một nơi" của repo áp cho cả artifact lẫn mã.
- **Điều việc bỏ lát cắt mỏng không hứa:** nó không thay bộ test `slow`, không miễn việc giữ 5 KPI, số
  dòng 9 bảng mart và 11 view khớp baseline, không miễn cổng phủ 80%, và không miễn test end-to-end cho
  từng phần.
- **Xung đột với scope vẫn còn nguyên và phải nêu rõ.** Scope đang chạy (`feature`) khai `skeleton: on`
  (`.aidlc/scopes/aidlc-feature.md`). Câu trả lời "không dựng lát cắt mỏng" **đi ngược cờ đó**. Bản ghi
  này giữ nguyên văn câu trả lời của người làm và **không tự sửa scope**; việc xử lý thuộc về
  delivery-planning (đừng giả định có Unit skeleton) và cổng vào Construction (chọn chế độ
  `construction_policy` cho khớp), hoặc một lần chỉnh scope có chủ đích. Cho tới khi một trong hai việc
  đó xảy ra, đây là điểm lệch đã biết giữa practice và scope.
- **Ba hạng mục của đợt phụ thuộc dữ liệu lẫn nhau, và điều đó đã được cân khi chốt:** U1 phải đo lại
  baseline trước, U2 cần mart mang mốc bàn giao mà U1 thêm vào, U3 cần khối mô hình đã ổn định — nên phần
  đầu tiên phải sửa mart, tức chạm tầng dùng chung, và làm trọn vẹn từng phần ở đây đắt hơn đợt trước.
  Cái giá đó đã được nêu rõ trong câu hỏi và người làm **vẫn chọn tuần tự** (Q2 = A), nên nó là chi phí
  đã nhận, không phải rủi ro chưa biết. Phần bù vẫn là ba thứ ở trên: test end-to-end riêng ngay khi từng
  phần xong, tầng `stats` nằm trong chuỗi xác nhận, và vùng hiển thị làm bằng thay đổi nhỏ sau phần mô hình.
- **Có dừng lại cho người xem giữa các phần hay đi tiếp tự động** vẫn là quyết định của
  `construction_policy` trong scope, không phải một cổng chúng tôi tự đặt thêm.

## Testing Posture

- **Methodology**: tdd
- **Ordering**: Với mỗi lớp chạy được của một phần, chúng tôi viết test trước cho hành vi mong muốn và chạy nó để thấy đỏ, rồi mới viết mã cho tới khi test đó xanh, rồi mới chuyển sang lớp kế tiếp — và chỉ chuyển sang phần kế tiếp khi phần đang làm đã có test end-to-end riêng xanh trên dữ liệu thật và toàn bộ bộ nhanh vẫn xanh.
- **Methodology evidence**: git **không** đưa ra được bằng chứng thứ tự, và nay càng ít hơn trước — mã nguồn cùng test của U3 vào **cùng một commit** (`b384da4 feat: Add U3 feature` chứa cả `src/**` và
  `tests/**`), còn toàn bộ tầng thống kê/mô hình/tab phân tích và chín mô-đun test của nó hiện **chưa
  được commit** nên không có mốc thời gian nào để so. Giá trị `tdd` **kế thừa** từ lần phỏng vấn trước
  (Q3 = A của đợt đó: giữ TDD cho cả phần mô hình, dù phần đó khó viết test trước hơn) và **đã được xác
  nhận lại cho đợt này** (Q1 = A) sau khi nêu rõ rằng kết quả AUC chỉ biết sau khi chạy; nó thay cho mặc
  định `test-after` của `org.md`. Người làm cũng nêu rõ **cách** giữ TDD ở lớp mô hình: test viết trước
  khẳng định **hành vi** (cỡ mẫu, chia tập theo `order_id`, không rò rỉ), chứ không khẳng định một giá
  trị AUC mục tiêu.
- **Test của lớp mô hình khẳng định hành vi, không khẳng định một con số mục tiêu.** Cụ thể: cỡ mẫu huấn
  luyện/kiểm định, việc chia tập theo **`order_id`** (không tách dòng hàng của cùng một đơn sang hai bên),
  và việc không có cột nào trong `FORBIDDEN_COLUMNS` lọt vào ma trận đặc trưng. Chỉ số chất lượng (AUC,
  precision, recall, ngưỡng) **được ghi ra và hiển thị**, không được biến thành giá trị kỳ vọng của một
  test viết trước — nếu không, test sẽ đỏ vì mô hình "chưa đủ giỏi" chứ không phải vì mã sai, và người
  làm sẽ bị đẩy vào việc chỉnh ngưỡng cho test xanh. (Q1 = A; xem `## Way of Working` — chỉ số mô hình
  không thuộc baseline hợp đồng.)
- **Ngưỡng phủ 80% đã được cưỡng chế trong CI, trên toàn bộ bộ test** (Q6 = A của đợt trước).
  `ci.yml:53` chạy `python -X utf8 -m pytest --cov=src --cov-fail-under=80` cho **cả** bộ nhanh và bộ
  `slow`, vì bảy mô-đun `src/` chỉ có phần phủ đến từ bộ `slow`. Chúng tôi không hạ ngưỡng và không tách
  cổng sang bộ nhanh để cho một bước pass. `README.md` mục "CI" nay nói đúng điều này (chỗ trôi tài liệu
  của đợt trước đã đóng); `tests/unit/test_ci_config.py` canh "cổng phủ không bị hạ" — thêm bước CI mới
  thì phải **giữ** cổng đó.
- **Mọi mô-đun mới đều phải có test riêng**, kể cả mô-đun "chỉ nối dây". Khoảng trống còn lại là nợ đã
  biết, không phải mẫu để noi theo: năm phương thức KPI cũ của `src/analytics/service.py`
  (`kpi_summary`, `revenue_by_period`, `revenue_by_dimension`, `top_entities`, `delivery_kpis`),
  `src/integrate/validate.py`, `reconcile.py`, `catalog.py`, `connections.py`, `src/pipeline/micro_batch.py`
  (nhánh lỗi), và đường `--stage all` (`run_all`). **Bốn** phương thức đọc mới phục vụ tầng `stats` thì
  **đã** có test thật trên DuckDB tạm — đó là mẫu đúng. `src/analytics/service.py` lại là chỗ đợt này sẽ
  mở rộng (khung huấn luyện ở grain dòng hàng), nên mô-đun mới **không** được lặp lại khoảng trống đó.
- **Khối lượng hiện tại** (đo lại trên đĩa ngày 2026-11-11): **74** tệp Python trong `src/` (**11.333**
  dòng), **54** tệp trong `tests/` (**49** mô-đun `test_*` với **499** hàm test, **12** hàm `slow`,
  **10.086** dòng). Bộ test nay bằng **0,89 lần** khối lượng `src/`; bảy mô-đun test lớn nhất chiếm 48%
  số dòng test (lớn nhất `test_integration_tab.py` 983 dòng). Dưới TDD + yêu cầu test cho mọi mô-đun mới
  + không có lát cắt mỏng, khối lượng này còn tăng.
- **Bộ nhanh và bộ chậm tách bằng marker**, không tách bằng thư mục: `-m "not slow"` là bộ nhanh,
  `-m slow` là bộ cần dữ liệu thật/sinh ra (`pytest.ini`: `testpaths = tests`, marker `slow`,
  `addopts = -ra`).
- **Bộ nhanh chưa hermetic** (`TD-09`, mức Cao): **năm** test trong `tests/unit/test_dashboard_smoke.py`
  và `tests/unit/test_cli.py::test_main_analyze_stage` gọi `load_config()` của repo nên cần
  `warehouse/olist.duckdb` và `data/marts/` — hai thư mục bị `.gitignore`. CI che lỗ hổng này bằng cách
  chạy `run --stage all` **và** `run --stage stats` trước bước test; trên máy mới clone bộ "nhanh" vẫn
  đỏ. Điều **đáng noi theo**: năm mô-đun test mới của đợt trước (`test_analytics_report/statistics/model`,
  `test_dashboard_analysis_tab`, `test_pipeline_stages`) tự dựng mart và tệp báo cáo trong `tmp_path`
  nên **không** dính `TD-09`; test mới của đợt này phải theo đúng mẫu đó.
- **Test là chốt hồi quy dữ liệu, không chỉ chốt mã.** Mọi thay đổi cleaning/ghép bản ghi có chủ đích phải
  cập nhật đồng thời `src/quality/allowlist.py`, `src/integrate/reconcile.py`, `README.md` và test tích
  hợp; nếu không, `quality` chế độ `full` và `KpiReconciler` sẽ đỏ. Việc này áp **ngay** cho đợt này:
  thêm **cột** vào mart thì an toàn (không đổi số dòng), nhưng đổi **lọc** hay đổi **grain** thì không.
- **Test áp đặt cả hình dạng giao diện và CLI.** Hiện có **5 tab, 9 callback, 9 output, 11 view, 3 lệnh
  con CLI**, cộng **4 thẻ tóm tắt** và **3 mục** của tab phân tích. Các chốt tương ứng:
  `tests/unit/test_dashboard_smoke.py` (5 tab/9 callback/9 output), `tests/integration/test_u3_end_to_end.py`
  (9 callback, 5 tab), `tests/unit/test_integration_tab.py` (6 callback của riêng tab "Tích hợp"),
  `tests/integration/test_u2_end_to_end.py` (`len(views) == 11`), `tests/unit/test_pipeline_stages.py`
  (5 tên tầng, `choices` khớp `STAGES | {"all"}`, **3** lệnh con),
  `tests/unit/test_dashboard_analysis_tab.py` (4 thẻ đúng thứ tự; khối mô hình **không** có ô nhập).
  Hai điều đáng nhớ: (a) phép đếm lệnh con **đã chuyển** khỏi `tests/unit/test_cli.py` sang
  `test_pipeline_stages.py`; (b) ràng buộc "khối mô hình không có ô nhập" (`TD-23`) **mâu thuẫn trực
  tiếp** với hạng mục U3 của đợt này — nó là thay đổi có chủ đích phải sửa cả ba nơi: câu chữ
  `TEXTS["model_caption"]`, test `test_model_block_offers_no_input_control`, và `README.md` mục Dashboard.
- **`STAGES` nay đã có test riêng** (`tests/unit/test_pipeline_stages.py`, 261 dòng): 5 tên tầng,
  `choices` của CLI khớp `STAGES | {"all"}`, tầng `stats` chạy thật trên mart 730 dòng dựng bằng SQL.
  Đây là chỗ đã đóng khoảng trống mà bản ghi trước ghi là "chưa có test riêng".
- **`ruff` là cổng lint + format.** `ruff check .` chạy toàn repo; `ruff format --check` chỉ chạy trên
  **danh sách khai tay 34 mục** trong `ci.yml:35` (`TD-20`), nên tệp nguồn mới **phải** được thêm vào
  danh sách đó cùng lúc với việc tạo tệp. `tests/unit/test_ci_config.py:14-29` canh 14 tệp của đợt vừa
  rồi — tiến bộ thật, nhưng danh sách kỳ vọng vẫn khai tay nên đợt sau vẫn phải tự thêm. Mã cũ chưa sạch
  ruff được dọn theo từng tệp khi có người sửa tới.
- **Không có kiểm tra kiểu tĩnh.** `mypy`/`pyright` không có trong `requirements.txt` và không có trong
  CI; type hint vẫn giữ theo quy ước hiện có nhưng không phải cổng. Đây là quyết định đã chốt, không
  phải thiếu sót.
- **Scope `feature` áp thêm sàn phủ 80% và yêu cầu chạy trong CI trước khi hợp nhất** — trùng với thực
  hành đã có, không mâu thuẫn.

## Guard Policy

<!-- Affirmed by the team. Mode: strict, relaxed, or off. Strict here holds for every intent, whatever one person asks in chat; relaxed or off here applies to every intent whose policy came from its scope, unless project.md or the person sets another; changing this line changes it. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

- **Chưa có môi trường triển khai.** Không staging, không production, không Docker/cloud, không scheduler,
  không dịch vụ ngoài nào ngoài API IBGE công khai (có cache và fallback). Vì vậy mặc định "deploy on
  merge" của `org.md` **không áp dụng**; chúng tôi không có bước build hay đóng gói phát hành.
- **CI là cổng tự động thật, chạy trên GitHub Actions.** `.github/workflows/ci.yml`: `windows-2022` (ghim
  image, không dùng `windows-latest`), Python 3.13, cache pip, **9 bước** — checkout → setup-python →
  cài phụ thuộc → lint/format → `run --stage all` → `run --stage stats` → bộ nhanh → cổng phủ 80% →
  smoke nạp cấu hình nguồn; trigger `push` **và** `pull_request` vào **ba** nhánh `main`,
  `feature/update-ui-ux`, `feature/analysis-and-models` (`ci.yml:5-13`). Chưa có bước deploy nào trong
  workflow — đúng với mô hình chạy từ mã nguồn.
- **"Phát hành" của chúng tôi = chạy từ mã nguồn trên máy local, sau khi CI xanh**, theo chuỗi xác nhận
  **bốn bước**, đúng thứ tự, dừng ngay khi một bước đỏ, không bước nào được bỏ qua vì "lần trước vẫn chạy
  được" (phỏng vấn Q4 = A, Q5 = B):
  1. `python -X utf8 -m pytest -m "not slow"` — bộ test nhanh phải xanh trước;
  2. `python -X utf8 -m src.pipeline run --stage all` — pipeline chạy hết các tầng trên dữ liệu thật, qua
     `QualityGate` và `KpiReconciler`;
  3. `python -X utf8 -m src.pipeline run --stage stats` — sinh lại `data/reports/analysis.json` (cả khối
     `stats` lẫn khối `model`) **và ghi tệp mô hình vào `data/models/`** trên dữ liệu thật, rồi kiểm báo
     cáo khớp những gì dashboard sẽ đọc;
  4. mở dashboard — xem kết quả bằng mắt, vì hình dạng giao diện là một phần của "chạy đúng".

  Bước 3 đứng **trước** bước 4 chứ không phải sau: mở dashboard khi báo cáo chưa được sinh lại — hoặc khi
  **tệp mô hình chưa tồn tại** — là xem một màn hình có thể đang đọc báo cáo cũ hay hiện trạng thái "chưa
  có mô hình". Trên **máy mới clone**, bước 3 là bắt buộc trước khi vùng dự đoán của tab phân tích dùng
  được, vì tệp mô hình không được commit (xem mục dưới). Đợt này thêm bề mặt dự đoán nên chuỗi này có nguy
  cơ phải dài thêm một bước; nếu có, sửa **ở đúng mục này** và ở `README.md`, không khai lại chỗ khác.
- **Hình dạng lệnh: thống kê và mô hình là một tầng của `run --stage`, không phải lệnh con riêng**
  (phỏng vấn Q5 = B). `STAGES` có **5** tên (`ingest`, `clean`, `integrate`, `analyze`, `stats`) trong
  `src/pipeline/stages.py:24`; CLI vẫn **3** lệnh con (`run`, `micro-batch`, `replay`) và `--stage` nhận
  **6** giá trị (`STAGES` + `all`). Chỗ lệch phải sửa khi có dịp: `_run_all` ghi **6** `StageResult`
  (`quality`, `linkage` không nằm trong `STAGES`) và **không** chạy `stats` (`TD-11`) — nên `--stage all`
  không sinh báo cáo phân tích, và CI phản ánh điều đó bằng hai bước riêng. Đợt này chạm `stages.py` nên
  đây là dịp rẻ nhất để chốt `stats` có nằm trong `all` hay không.
- **Hai lệnh riêng cho hai nửa hệ thống, không có bước build:** pipeline (có tầng `stats`) và
  `python -X utf8 -m src.dashboard` (bind `127.0.0.1:8050`, cấu hình trong `config.yaml`).
- **Phiên bản = commit hash, cộng một mốc CHANGELOG.** Không có git tag; `CHANGELOG.md` nay ghi **bốn**
  mốc `v0.1.0` (2026-11-06) → `v0.2.0` (stats), `v0.3.0` (model), `v0.4.0` (tab phân tích) theo ba nhóm
  **Thêm / Sửa / Nội bộ**, viết cho người đọc. Đợt này thêm bề mặt mới (khung dự đoán, đặc trưng, vùng
  nhập liệu, và tệp mô hình ở `data/models/`) nên CHANGELOG phải có mốc tiếp theo; đánh số tag vẫn chưa
  được đặt thành luật.
- **Tệp mô hình sống ở `data/models/`, sinh bằng `pickle` của thư viện chuẩn — và nó KHÔNG được commit.**
  Đợt này chốt cách lưu mô hình (Q3 = A): ghi vào `data/models/` bằng `pickle` (thư viện chuẩn, **không**
  thêm phụ thuộc nào — không `joblib`), đọc lại bằng chính nó. Ba hệ quả phải nói rõ, vì chúng đổi định
  nghĩa "phát hành" ở trên:
  1. `data/` nằm trong `.gitignore`, nên **tệp mô hình không vào git** và không phải artifact phát hành;
     nó là sản phẩm sinh ra, đúng như `data/marts/` và `data/reports/`.
  2. Tệp đó **chỉ được sinh bởi `python -X utf8 -m src.pipeline run --stage stats`** — cùng bước sinh báo
     cáo. Không có lệnh riêng, không có bước build.
  3. **Một máy mới clone không có mô hình nào cho tới khi chạy bước 3**, nên vùng dự đoán của tab phân
     tích phải chịu được trạng thái "chưa có tệp mô hình" (hiện trạng thái rỗng/khởi tạo, không sập) và
     `README.md` mục "Lưu ý" phải nói đúng điều này.

  Về kỹ thuật, việc lưu vẫn là thay đổi **cấu hình + tài liệu** (`AppConfig` thêm thư mục mô hình,
  `.gitignore` không phải sửa vì `data/` đã bị chặn) chứ không phải một dòng `dump`; `TD-25` vì thế hẹp
  lại còn phần cấu hình và tài liệu. Về giới hạn: `pickle` gắn với phiên bản thư viện đã sinh ra nó —
  tệp mô hình của máy này **không** phải định dạng trao đổi giữa các máy; máy khác sinh lại tệp của mình.
  Không đổi định nghĩa "phát hành" theo hướng artifact: "phát hành" vẫn là **chạy từ mã nguồn**, chỉ thêm
  ràng buộc rằng bước 3 sinh ra tệp mô hình mà vùng dự đoán cần.
- **Cổng kiểm tra sau khi chạy đóng vai trò "kiểm tra khói":** `QualityGate` (21 check cấu trúc; chế độ
  `full` thêm 9 check số dòng và 10 dị thường allowlist) và `KpiReconciler` (5 KPI với dung sai riêng).
  Pipeline chỉ được coi là chạy đúng khi hai cổng này xanh. Báo cáo phân tích **không thay** hai cổng
  này, và việc bước 3 xanh cũng không cho phép bỏ qua bước 2.
- **Vận hành đã biết trước, phải tuân khi chạy lại** (`docs/runbook.md`): đóng dashboard trước khi chạy
  `integrate` (khoá `warehouse/olist.duckdb`); view DuckDB chứa **đường dẫn tuyệt đối** vào Parquet nên
  chuyển thư mục repo hoặc dùng worktree khác phải chạy lại `integrate`; mọi lệnh Python phải chạy UTF-8.
- **Dữ liệu vào là bất biến, không có môi trường thứ hai:** `dataset/` chỉ đọc; `data/`, `warehouse/`,
  `logs/`, `inbox/` là sản phẩm sinh ra và bị `.gitignore` — `data/models/` nằm trong số đó. "Triển khai
  lại từ đầu" = xoá bốn thư mục sinh ra, chạy `--stage all`, rồi `--stage stats` để có báo cáo **và** tệp
  mô hình; thiếu bước cuối thì vùng dự đoán không có gì để đọc.
- **Ngân sách thời gian đã thành test**, nên nó là một phần của hợp đồng phát hành: 300 s cho tầng
  `stats`, 900 s cho tầng và 900 s cho riêng bước mô hình. Mô hình thứ hai và khung grain dòng hàng
  (≈112.650 dòng thay vì 96.478) sẽ đẩy thời gian lên — phải đo lại và sửa ngân sách **có chủ đích**,
  không nới ngầm.

- Ngân sách thời gian đã chốt cho tầng `stats` là **300 s** cho cả tầng và **240 s** cho riêng bước huấn luyện hai mô hình (thay hai con số 900 s cũ); vượt ngân sách thì phải đo lại và sửa ngân sách **có chủ đích**, không nới ngầm. (learned 2026-11-14) <!-- cid:261111-model-feature-improvemen:feedback-optimization:e08956f9d1149e5246e665239c99bbd21cf6c707ee53bf092cfabc512db59ecc -->

## Code Style

- **Ngôn ngữ và môi trường:** Python 3.13, Windows 10/11, chạy từ `.venv` tạo bằng
  `python -m venv --system-site-packages`. Mọi lệnh Python chạy UTF-8 (`-X utf8` hoặc `PYTHONUTF8=1`) vì
  đường dẫn có ký tự tiếng Việt và dữ liệu có ký tự Bồ Đào Nha. Chuỗi hiển thị cho người dùng bằng **tiếng
  Việt**, dữ liệu gốc giữ **tiếng Bồ Đào Nha**, số hiển thị theo định dạng Brazil (`1.234,56`, `R$`, `%`)
  trong `src/dashboard/formatting.py` (`format_percent` **không** nhân 100, người gọi tự nhân).
- **`ruff` là một cấu hình duy nhất cho cả lint và format** (`ruff.toml`): `line-length = 112`,
  `target-version = "py313"`, `select = ["E4", "E7", "E9", "F"]` — bắt lỗi thật, không đụng kiểu chữ;
  `extend-exclude` 8 mục (`assets`, `data`, `dataset`, `doc`, `inbox`, `logs`, `warehouse`, `.venv`);
  **năm** `per-file-ignores` là nợ cũ có ghi chú: bốn `F401` (`src/integrate/connections.py`,
  `src/integrate/pipeline.py`, `src/pipeline/micro_batch.py`, `src/quality/gate.py`) và một `E402`
  (`tests/conftest.py`, vì tệp đó chèn `sys.path` trước khi import). Mã mới **không** được thêm ngoại lệ
  "chỉ lần này". Ghi chú: chín `# noqa` (`BLE001`, `ANN001`) đang tồn tại với mã **không** nằm trong
  `select` nên hiện không tác dụng (`TD-27`) — chúng là nhiễu, không phải tiền lệ để mở rộng.
- **Hình thức tệp:** 4 dấu cách, không tab; dòng tối đa 112 ký tự (nay do `ruff format` bảo đảm, không
  soát tay); **59 trong 74** tệp `src/` mở đầu bằng `from __future__ import annotations` và dùng type hint
  hiện đại (`list[str]`, `dict[str, pd.DataFrame]`, `Path | None`) — bốn mô-đun mới của đợt trước đều theo
  đúng quy ước này.
- **Đặt tên:** mô-đun/hàm `snake_case`, lớp `PascalCase`, hằng `UPPER_SNAKE`; tiền tố bảng đích `dim_`,
  `fact_`, `agg_`; cột cờ là mệnh đề khẳng định (`is_delivered`, `is_late`, `has_items`, `has_payment`,
  `has_review`, `category_missing`, `translation_missing`, `price_outlier`, `multiple_reviews_per_order`,
  `auc_below_target`, `is_sparse_period`); ID check chất lượng theo nhóm (`U-` unique, `F-` foreign key,
  `D-` miền giá trị, `R-` số dòng, `A-` dị thường, `C-` count star schema, `J-` join, `L-` logic).
  Lớp tích hợp dùng định danh **tiếng Việt không dấu** cho thực thể/trường (`don_hang`, `ma_don`,
  `trang_thai`) và id kebab-case tiếng Việt cho thành phần giao diện (`tich-hop`, `luoc-do-trung-gian`,
  `don-theo-thang`, `phan-tich`, `tom-tat`, `thong-ke`, `mo-hinh`, `ti-le-tre`, `so-don`, `so-bo-qua`,
  `auc`); trạng thái giao diện là token đóng (`rong`, `chua-chay`, `dang-tai`, `day-du`, `mot-phan`,
  `loi`). Tên hằng suy luận cũng phải có nghĩa, không literal rải rác: `SPLIT_DATE`, `TARGET`,
  `AUC_TARGET`, `THRESHOLD_METHOD`, `THRESHOLD_GRID`, `EXPECTED_DELIVERED`, `EXPECTED_LATE`,
  `MODEL_DIGITS`, `RANDOM_STATE`, `MAX_ITER`, `REPORT_VERSION`, `STATUS_*`, `MIN_*`, `SEASONAL_PERIOD`.
- **Mẫu lặp lại chúng tôi giữ:** hàm làm sạch thuần theo bảng `clean_<table>(df, ...) -> DataFrame`, luôn
  `out = df.copy()` trước khi sửa và **gắn cờ thay vì lọc dòng**; builder/validator không giữ trạng thái
  (`build_*`/`validate`/`reconcile`), tiêm `config` qua tham số (không dùng DI container); **mô-đun suy
  luận là tập hàm thuần trên `DataFrame`** — `statistics.py` và `model.py` không mở kết nối, không đọc
  tệp, không giữ trạng thái, mọi I/O nằm ở `service.py` (đọc DuckDB) và `report.py` (ghi/đọc tệp), và
  `stages.py` là nơi **duy nhất** ghép ba mô-đun đó — nên việc `pickle.dump`/`pickle.load` tệp mô hình
  (Q3 = A, `data/models/`) cũng là I/O và **không** được đặt trong `model.py`; chỗ đặt cụ thể do
  Functional Design chốt, miễn giữ đúng hướng phụ thuộc đó; ghi tệp qua `AtomicWriter` (temp → đọc lại
  kiểm số dòng → `os.replace`), riêng báo cáo phân tích có thêm lớp **parse lại và kiểm cấu trúc** trước khi thay
  tệp; báo cáo = dataclass → JSON UTF-8 (`ensure_ascii=False`, indent 2), với `to_dict()` tường minh khi
  cần kiểm soát thứ tự/độ chính xác của số; nhật ký JSONL mỗi lần chạy một `run_id`
  (`<UTC>%Y%m%dT%H%M%S>-<8 hex>`), mọi sự kiện có `timestamp`, `level`, `run_id`, `stage`, `event`, và
  `prune_logs` giữ 10 tệp gần nhất; **hàm dựng giao diện là hàm thuần trả cây Dash**, test bằng cách
  duyệt cây và đọc `props` chứ không mở trình duyệt.
- **Lỗi theo tầng, bắt ở biên:** cây ngoại lệ **11 lớp** cùng gốc `PipelineError` — `SchemaError`,
  `QualityGateError`, `ExternalSourceError`, `ConfigurationError`, `QueryExecutionError`,
  `KpiMismatchError`, `NoSourceAvailableError`, `LinkageResultError`, cộng `ModelError` và `ReportError`
  của đợt trước. Bắt ở `cli.main`, `stages.run_stage`, `process_inbox`, `tab.py`,
  `analysis_tab.render_analysis`; các tầng trong ném tiếp; CLI trả mã thoát 1. Không nuốt lỗi thành
  "không có dữ liệu" (`TD-08` là nợ, không phải mẫu).
- **Chú thích:** docstring một dòng ở đầu mô-đun/hàm; **không** docstring mô tả tham số/trả về; giải thích
  dài đặt ngoài mã (`README.md`, `docs/data-dictionary.md`, `docs/runbook.md`, `docs/3v.md`,
  `CHANGELOG.md`). Dẫn **ID yêu cầu** trong docstring/chú thích (`BR1.1`–`BR3.10`, `TS-2`…`TS-9`,
  `NFR1.x`/`NFR3.x`/`NFR4.2`/`NFR5.x`, `PD-1`/`PD-2`, `SEC-2`/`SEC-5`, `SD-1`/`SD-1b`) là quy ước đã có —
  hữu ích, nhưng phụ thuộc tài liệu ngoài repo (record AI-DLC). `src/` hiện có **0** `TODO`/`FIXME`/`HACK`
  — chúng tôi không mang ghi chú nợ dang dở trong mã.
- **Hướng phụ thuộc là quy ước:** `config`/`common` ở gốc, rồi
  `ingest → clean → quality → integrate → analytics → dashboard`; `external` chỉ được `integrate` dùng;
  `integration` và `linkage` là mặt cắt ngang được `dashboard`/`pipeline` gọi; `pipeline` là điểm ghép nối.
  Trong gói `analytics`, hướng là `service ← statistics`, `service ← model`, `report ← statistics`,
  `report ← model` — `report.py` **không** import `service`/`statistics`/`model` nên không có vòng.
  Mô-đun mới của đợt này **đọc mart/DuckDB hiện có** qua `AnalyticsService` thay vì định nghĩa lại doanh
  thu hay KPI theo cách khác, và nằm cùng hướng phụ thuộc đó.
- **Ba nợ phụ thuộc đang tồn tại, là nợ chứ không phải mẫu:** `src/integrate/pipeline.py:10` import thừa
  `AnalyticsService` (miễn trừ `F401` trong `ruff.toml:27`) tạo phụ thuộc ngược chiều
  `integrate → analytics` và nay kéo cả `scipy`/`scikit-learn` vào đường phụ thuộc của gói mô hình hóa
  (`TD-06`) — xoá là rẻ; và `src/analytics/filters.py` chỉ là shim re-export `KpiFilters` (`TD-05`).
  `src/dashboard/analysis_tab.py` mượn `STATE_ICONS`/`TEXTS` của `src/integration/card.py` (`TD-26`) —
  phụ thuộc chéo giao diện↔giao diện có chủ đích để đồng bộ nhãn, nhưng phải biết khi đổi `card.py`.
- **Cấu hình tập trung, bất biến:** đọc `config.yaml` một lần thành `AppConfig` (`frozen dataclass`,
  34 trường), không rải hằng số đường dẫn trong mã; `load_config` tạo sẵn thư mục đầu ra (tác dụng phụ có
  chủ đích, và là lý do test không hoàn toàn cô lập). Ba hợp đồng YAML trong `config/`
  (`mediated-schema.yaml`, `integration-tab.yaml`, `integration-sources.yaml`) là phụ thuộc cứng của
  runtime và không có trường phiên bản, nên đổi cấu trúc là breaking change ngầm.
- **Mã cũ được dọn theo từng tệp khi có người sửa tới**, không bằng một lần format toàn repo lẫn vào thay
  đổi chức năng.
## Forbidden

<!-- Team-specific forbidden patterns -->

## Mandated

<!-- Team-specific mandates -->

## Corrections

<!-- Self-learning loop appends here. -->
