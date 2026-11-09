# Code Summary — u1-thin-slice

Nguồn: kế hoạch đã được duyệt `code-generation-plan.md`, hướng dẫn test `unit-test-instructions.md`, và báo cáo build của đơn vị.

## 1. Đã dựng gì

| Lớp | Tệp | Nội dung |
|---|---|---|
| Data model | `src/integration/models.py` | `DonHang` (năm trường), `LoadResult`, `QueryRunResult` (C4 + `total_orders`, `months`, `partial`), `InvalidRecord` |
| Data model | `src/integration/schema.py` | Đọc `config/mediated-schema.yaml` bằng `yaml.safe_load`, `checked_identifier` ba lớp, trả danh sách cột cần đọc (chỉ `loaded: true`) |
| Repository | `src/integration/load.py` | `load_don_hang` với `usecols` từ lược đồ, `dtype=str`, thử lại một lần sau 100 ms, gắn cờ rồi loại bản ghi hỏng (BR1.1, BR1.2), cache cấp tiến trình khoá theo đường dẫn + mtime |
| Business logic | `src/integration/query.py` | `rewrite_plan` + `run_monthly_orders` trên DuckDB in-memory, đóng trong `finally`, kiểm điều kiện trạng thái (BR1.4) và kế hoạch viết lại (BR1.6), một dòng cho mỗi cặp (tháng, trạng thái) |
| Frontend | `src/integration/card.py` | `build_integration_card` với năm trạng thái, id lấy từ `config/integration-tab.yaml`, nhãn chữ + biểu tượng, nút nhận tiêu điểm |
| Frontend | `src/dashboard/app.py` | Tab thứ tư "Tích hợp" (bản U1: một callback `tich-hop-cap-nhat`); U6 sau đó thay phần thân tab bằng `IntegrationTab` + **sáu** callback riêng (năm của U6 + một của vùng `don-theo-thang`), tổng **8 callback**; 9 output cũ giữ nguyên |
| Hạ tầng | `config.yaml`, `src/config.py` | Hai đường dẫn cấu hình mới trong `AppConfig` |
| Hạ tầng | `src/common/logging.py`, `src/pipeline/stages.py` | `NullLogger`, `prune_logs` (giữ 10 tệp gần nhất) và lời gọi ở cuối lần chạy |
| Hạ tầng | `src/common/exceptions.py` | `QueryExecutionError` (C4 yêu cầu) |
| Hạ tầng | `requirements.txt`, `ruff.toml` | Ghim `ruff==0.17.4` kèm lý do; cấu hình ruff một chỗ ở gốc repo |
| Hạ tầng | `.github/workflows/ci.yml` | Workflow sáu bước trên `windows-2022` theo `cicd-pipeline.md` §2 (có bước chạy pipeline vì `TD-09`) |
| Tài liệu | `README.md`, `docs/runbook.md`, `CHANGELOG.md` | Mục CI; dọn nhật ký còn 10 tệp; mục `v0.1.0` |

## 2. Quyết định chính

| Quyết định | Vì sao |
|---|---|
| "Kết quả lần trước" giữ trong biến cấp tiến trình ở `card.py`, không dùng `dcc.Store` | Kế hoạch chốt callback mới chỉ có một `Output` (10 output thay vì 9), nên `dcc.Store` không có chỗ nối nếu không thêm output thứ 11 — điều đó sẽ đổi hình dạng dashboard ngoài kế hoạch. Hành vi theo ADR-U1-R2 giữ nguyên: số cũ + nhãn "kết quả lần trước" + giờ + nút thử lại |
| Trạng thái rỗng hiện cả câu hướng dẫn **và** nút "Chạy truy vấn" | Hoà giải BR1.8 (hướng dẫn chạy pipeline) với ADR-U1-R5 (nút hành động); không hiện số 0 |
| `src/integration/schema.py` import danh sách bảng nguồn từ `src/ingest/schemas.py` | ADR-U1-S2 lớp 1 buộc danh sách 9 bảng lấy từ nguồn sự thật duy nhất; chép lại 9 tên sẽ vi phạm luật "một sự thật một chỗ". Đây là **ngoại lệ có chủ đích** với ghi chú "gói mới chỉ phụ thuộc `common`" |
| `total_orders` = tổng của toàn bộ kết quả truy vấn, không phải tổng 12 tháng | Workflow 3 tách hai phép tính: "tính tổng số đơn" và "lấy 12 tháng gần nhất". Bảng có caption "12 tháng gần nhất" để không ai cộng nhầm |
| `ruff format --check` chỉ chạy trên mã của đợt này | 36 tệp cũ chưa qua `ruff format`, và `team.md` cấm "một lần format toàn repo lẫn vào thay đổi chức năng". `ruff check .` vẫn chạy toàn repo; nợ cũ khai bằng `per-file-ignores` |
| Test dọn nhật ký đặt trong `tests/unit/test_log_pruning.py` | `prune_logs` là hàm mới nên cần test riêng (NFR2.2), dù kế hoạch chỉ nói "dọn nhật ký" ở bước 8 |

## 3. Kết quả test

| Cổng | Lệnh | Kết quả |
|---|---|---|
| Bộ nhanh toàn repo | `pytest -m "not slow"` | 133 passed, 6 deselected |
| Lệnh unit-scoped của đơn vị | `pytest` 6 tệp (4 tệp lớp + `test_log_pruning.py` + `test_dashboard_smoke.py`) | 97 passed |
| Lint | `ruff check .` | sạch |
| Định dạng | `ruff format --check` trên phạm vi ở `cicd-pipeline.md` §1 | sạch (11 tệp) |
| Pipeline thật | `python -X utf8 -m src.pipeline run --stage all` | thành công; `QualityGate` và `KpiReconciler` xanh |
| Phủ gói mới | `--cov=src/integration` | 98% (card 100, models 100, query 100, load 97, schema 95) |

Số đo trên dữ liệu thật: nạp 99.441 đơn trong **686 ms** (ngân sách 2.500 ms), truy vấn **60 ms** (ngưỡng 2.000 ms), 0 bản ghi bị loại, 136 dòng kết quả, 12 tháng `2017-11 … 2018-10`, `partial = ["thiếu trạng thái approved"]`.

**Về ngưỡng phủ 80%:** lệnh xác nhận của dự án (`.venv/Scripts/python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80`) chạy **toàn bộ** bộ test — nhanh + `slow` — cho **139 passed** và **90,08%**, tức ngưỡng **đạt**. Con số 77% chỉ là phép đo tham khảo trên **bộ nhanh** và không phải cổng; phần thiếu nằm ở các mô-đun cũ mà bộ `slow` bao phủ. Gói mới của đơn vị này đạt 98%. Không hạ ngưỡng và không sửa lệnh đo.

## 4. Test viết nhưng chưa chạy

| Test | Vì sao chưa chạy |
|---|---|
| 6 hàm `@pytest.mark.slow`, gồm `tests/integration/test_u3_end_to_end.py` (đã sửa: 2 callback → 3) | Bộ `slow` cần dữ liệu thật/sinh ra và bị loại khỏi CI (Q2 = B); nó chạy ở lần xác nhận trước phát hành. Đây là lần chạy cần người, không phải cổng tự động |

Kiểm bằng mắt trên trình duyệt (bước 3 trong chuỗi xác nhận của `team.md`) chưa làm: cần người mở `python -X utf8 -m src.dashboard`. Build đã bù bằng cách gọi thẳng callback và dựng thẻ trên dữ liệu thật.

## 5. Điểm lệch kế hoạch

| # | Lệch | Ghi chú |
|---|---|---|
| 1 | Trong bước 11, một lần đổi tên hằng được ghi lại bằng lệnh Python qua shell thay vì công cụ tệp | Sai quy trình của chính bước này; kết quả đã kiểm lại (6 chỗ, test xanh). Các lần sửa khác đều qua công cụ tệp |
| 2 | `dcc.Store` không dùng; trạng thái "kết quả lần trước" nằm trong biến cấp tiến trình | Xem §2 |
| 3 | CI: `ruff check .` toàn repo, `ruff format --check` chỉ trên mã đợt này | Xem §2; khác `cicd-pipeline.md` §2 một dòng |
| 4 | `schema.py → src.ingest.schemas` | Xem §2; ngoại lệ có chủ đích với ghi chú phụ thuộc |
| 5 | Thêm `tests/unit/test_log_pruning.py` | Hàm mới cần test riêng |
| 6 | Sửa `tests/conftest.py` (ngoài danh sách "Touches" của kế hoạch) | Bắt buộc: `create_app(real_config)` ném `ConfigurationError` nếu hai đường dẫn cấu hình mới không có trong fixture |
| 7 | Cài `ruff` vào `.venv` ở bước 5 thay vì bước 18 | Để chạy được cổng lint ngay từ bước 5; việc ghim vào `requirements.txt` vẫn ở bước 18 |
| 8 | Thêm `InvalidRecord(ValueError)` | C4 không có lỗi cấp bản ghi; lỗi theo tầng cho lỗi cấp tệp/lược đồ/truy vấn vẫn giữ nguyên |

## 6. Ngoài phạm vi, đúng như kế hoạch

Không dùng `dmc`; không dựng ba thẻ tổng quan còn lại hay màn hình chi tiết (thuộc U6); không làm ghép bản ghi / chọn nguồn / lớp ngữ nghĩa (U3, U4, U5); không sửa `TD-09`; không chuyển `ibge_dir` ra khỏi `dataset/`.

## 7. Sửa sau vòng review 1

| Vấn đề | Cách sửa |
|---|---|
| Con số tiêu đề của thẻ đếm phạm vi khác bảng bên dưới mà không có nhãn | `_numbers` nay ghi rõ "Tổng toàn kỳ: …" và "… dòng của cả kỳ"; caption bảng ghi "12 tháng gần nhất · N dòng hiển thị". Hai phạm vi được gọi tên, không còn mơ hồ |
| Truy vết bỏ sót bảy yêu cầu (NFR2.1, NFR2.2, NFR3.1, NFR4.1–4.4) | Đã thêm đủ bảy dòng vào `traceability.json`, mỗi dòng trỏ tới tệp thật; NFR2.1 ghi `N/A` kèm lý do (cổng của lệnh xác nhận, không do tệp mã cưỡng chế) |
| Danh mục nhật ký thiếu hai sự kiện dọn log; tập `error_code` đóng chưa khai một lần; nhánh dự phòng trả sai | `observability-design.md` §2 nay có đủ **mười hai** sự kiện; `src/common/logging.py` khai `ERROR_CODES` + `normalise_error_code`, `JsonLogger.error` chuẩn hoá mọi mã lạ thành `unknown`, và `load._error_code` trả `unknown` thay cho `file_not_found` |
| "Đầy đủ" không bao giờ đạt trên dữ liệu thật | Định nghĩa được chốt: **Đầy đủ = đủ 12 tháng VÀ không thiếu trạng thái nào** (BR1.8 thắng dòng "Có 12 tháng dữ liệu" của bảng trạng thái). Trên dữ liệu Olist hiện tại thẻ luôn ở "Một phần" vì cửa sổ 12 tháng không có đơn `approved`; danh sách `partial` nói đúng lý do. Có test `test_full_state_requires_twelve_months_and_all_eight_statuses` |
| "Đang tải" là nhánh mã không có đường chạy | Đã nối thật: tab bọc `dcc.Loading` với `custom_spinner` dựng từ `build_integration_card(state=STATE_LOADING)`, nên trạng thái này hiện trong lúc callback chạy truy vấn |
| Ràng buộc "ngày đặt không ở tương lai" chưa cài | `DonHang.from_row` loại bản ghi với lý do `ngay_dat_tuong_lai`; có test riêng |
| Test "không xoá nhật ký hiện tại" không kiểm được điều nó tuyên bố | Test nay đặt `os.utime` cho nhật ký hiện tại thành **tệp cũ nhất**, nên chỉ quy tắc an toàn mới giữ được nó; bỏ dòng `continue` trong `prune_logs` là test đỏ |
| Cổng định dạng trong CI hẹp hơn tài liệu thiết kế | `cicd-pipeline.md` §1/§2 nay ghi đúng lệnh hẹp và lý do (35 tệp cũ chưa qua `ruff format`; `team.md` cấm một lần format toàn repo) |

## 8. Sửa sau vòng review 2

| Vấn đề | Cách sửa |
|---|---|
| Thẻ mất hẳn `html.Section` nên `className="integration-card"` và `data-state` không tới DOM; chưa có CSS nào cho tab | `build_integration_tab` và `render_integration_card` nay trả **chính thẻ** (không phải `card.children`), nên Section và `data-state` có mặt trong DOM; `assets/style.css` có khối `.integration-*` gồm bảng, số liệu, nhãn trạng thái theo token màu, viền tiêu điểm 2px, và khung skeleton |
| `JsonLogger.error` chuẩn hoá quá tay, làm `PIPELINE_ERROR`/`BATCH_ERROR` của pipeline thành `unknown` | Bỏ chuẩn hoá khỏi `JsonLogger.error`; `normalise_error_code` chỉ được gọi ở hai chỗ của đơn vị (`src/integration/load.py` và `src/integration/schema.py`), nên mã lỗi cũ của pipeline giữ nguyên |
| ADR-U1-R2 nói `dcc.Store`, mã dùng biến cấp tiến trình | Đã sửa ADR-U1-R2 trong `reliability-design.md` theo đúng cách làm và ghi lý do (chỉ một `Output`, giữ 10 output của NFR5.3) |
| Lệnh test trong tài liệu thiếu `test_log_pruning.py` | Đã thêm vào `unit-test-instructions.md` |
| `test_integration_load.py` tự khai lại `ERROR_CODES` | Nay import từ `src/common/logging.py` — một nguồn duy nhất |
| Số liệu trong tài liệu lệch nhau | §3 nay ghi đúng lần chạy cuối: 97 unit-scoped, 133 bộ nhanh, 139 + 90,08% cho lệnh xác nhận, 11 tệp định dạng |

## 9. Revision 2 — cổng đúng đắn dữ liệu (2026-11-08)

Lý do: vòng phản biện `nfr-requirements` để lại hai phát hiện Major (R-19, R-20). Bản sửa yêu cầu đã thêm **NFR5.4–NFR5.6** và chốt **TS-U1-2**. Revision này đóng chúng bằng mã và test, không chỉ bằng tài liệu.

| Việc | Tệp | Nội dung |
|---|---|---|
| Cổng đúng đắn NFR5.5 | `tests/unit/test_integration_correctness.py` (**mới**, 2 test, `@pytest.mark.slow`) | Tính lại số đơn theo `(tháng, trạng thái)` **độc lập bằng pandas** từ `dataset/olist_orders_dataset.csv` (bỏ trùng `order_id`, loại ngày rỗng/tương lai và trạng thái ngoài tám giá trị, cửa sổ 12 tháng), rồi so từng nhóm và tổng toàn kỳ với `run_monthly_orders`; lệch một đơn ở bất kỳ trạng thái nào là đỏ |
| Cổng ngữ nghĩa NFR5.6 | cùng tệp | Khẳng định SQL nêu `order_status AS trang_thai` và dùng `trang_thai` làm khoá nhóm; cửa sổ đúng 12 tháng |
| Một đường dữ liệu TS-U1-2 | `src/integration/card.py` | `empty_hint` nay là "Chưa chạy truy vấn lần nào…", bỏ chỉ dẫn `python -m src.pipeline run --stage all`; thẻ chỉ đọc số từ `run_monthly_orders` của chính lần chạy |
| Khoá hành vi đó | `tests/unit/test_integration_card.py` | Test rỗng khẳng định câu mới và **không** còn nhắc `src.pipeline`; test mới `test_render_integration_card_never_reads_the_warehouse` trỏ `duckdb_path` vào tệp không tồn tại mà thẻ vẫn ra số |
| Sổ sách | `unit-test-instructions.md`, `code-generation-plan.md` | Thêm lệnh `-m slow` cho tệp mới; ghi rõ ngoại lệ duy nhất được đọc `dataset/`; kế hoạch có bước 20–24 và bảng kết quả |

### Kết quả chạy (thay cho các con số ở §3 — chúng là lần chạy của bản trước)

| Cổng | Lệnh | Kết quả |
|---|---|---|
| Bộ nhanh | `pytest -m "not slow"` | **368 passed, 9 deselected** |
| Bộ chậm | `pytest -m slow` | **9 passed, 368 deselected** (gồm 2 test đối chiếu mới) |
| Cổng nghiệm thu | `pytest --cov=src --cov-fail-under=80` | **377 passed**, phủ **90,82%** — ngưỡng đạt |
| Lint / định dạng | `ruff check` + `ruff format --check` | sạch |

**Điều đáng nói:** cổng NFR5.5 xanh ngay ở lần chạy đầu — số trên thẻ vốn đã khớp phép tính độc lập. Nghĩa là phát hiện R-19 đúng về **thiếu cổng**, không phải về số liệu sai; từ nay mọi thay đổi bộ nạp/truy vấn đều bị test này chặn nếu làm lệch.

**Còn mở, có chủ đích:** `render_integration_card` hiện chỉ được test gọi, không còn nằm trong cây tab — tab "Tích hợp" của U6 thay nó. Hành vi của nó vẫn là đường dữ liệu mà NFR5.5 đo, nhưng nếu muốn con số của lát cắt hiện trên giao diện thật thì cần một việc riêng ở Build and Test (nối lại thẻ vào tab U6 hoặc bỏ hẳn thẻ cũ). Điều này chưa nằm trong kế hoạch đơn vị và không được tự quyết ở đây.

## 10. Sau hai vòng kiểm tra người làm yêu cầu (2026-11-08)

Người làm chọn "cho kiểm tra lại cách làm mới trước khi quyết". Hai vòng phản biện được mở bằng `--person-asked`:

| Stage | Vòng | Kết quả | Việc đã làm sau đó |
|---|---|---|---|
| `nfr-requirements` | 4 | NOT-READY — R-20 còn mở, thêm 2 Major mới | Đã sửa: BR1.8 + Workflow 3 bỏ hướng dẫn chạy pipeline; tách dải mã NFR5.4–NFR5.6 khỏi NFR5.1–NFR5.3; NFR5.3 ghi đủ bốn `card_ids` + một vùng và số hình dạng cụ thể (4 tab, **8** callback, 4 thẻ + 1 vùng — con số 8 chốt ở Revision 3); RL-U1-1 dùng `ConfigurationError` cho tệp thiếu; OB-U1-1 định nghĩa `run_id`/`stage`; SR-U1-3 buộc kiểm định danh; SR-U1-5 mô tả đúng `config.yaml`; bỏ con số "8GB"; thống nhất ngân sách lần bấm đầu 5+2 giây; `traceability.json` có đủ mảng reverse |
| `code-generation` | 3 | READY — 1 Major mới (thẻ rời đường chạy) + 6 Minor | Đã sửa các Minor trong tầm: cửa sổ 12 tháng khai lại trong test (không mượn hằng của mã đang kiểm), so sánh theo nhóm thay vì đòi bằng đúng tập tháng, `traceability.json` trỏ BR1.7/BR1.8/AC2.1.2/AC2.1.3 vào test thay vì tệp không còn nối vào tab. Major về đường chạy ghi ở §9 và `memory.md` để người quyết ở Build and Test |

Ghi chú về mã NFR: bản trước định nghĩa NFR5.1–NFR5.3 hai lần (một bộ ở `reliability-requirements.md` cho cổng chất lượng, một bộ ở `tech-stack-decisions.md` cho đúng đắn dữ liệu). Nay bộ thứ hai là **NFR5.4–NFR5.6**; mọi tham chiếu trong đơn vị đã đổi theo.

## 11. Vòng kiểm tra thứ ba (2026-11-08)

| Stage | Vòng | Kết quả | Ghi chú |
|---|---|---|---|
| `nfr-requirements` | 5 | **READY** | R-20, R-24, R-25, R-26…R-29 đã đóng; còn 1 Minor (R-17: ngân sách đường ghép) đã bổ sung sau đó |
| `code-generation` | 4 | **NOT-READY** | Bốn sửa của vòng trước đều đạt (R-16, R-17, R-18, R-19 — cổng đối chiếu nay tự đỏ khi cửa sổ hoặc nguồn đổi). **R-15 vẫn mở**: thẻ của lát cắt không còn trên đường chạy |

**R-15 là quyết định, không phải lỗi sửa được trong đơn vị này.** Tab "Tích hợp" do `src/integration/tab.py` (U6) dựng với bốn thẻ theo C9; thẻ "Số đơn theo tháng" của U1 không còn chỗ trong đó. Cổng NFR5.5 vẫn đo đúng đường dữ liệu ấy, nhưng con số không hiện cho người dùng. Hai hướng, phải chọn một và ghi vào cùng thay đổi:

1. **Nối lại số của lát cắt vào tab** — thêm một vùng kết quả trong tab U6 (không thêm `card_id`, giữ C9) và trỏ lại BR1.7/BR1.8 vào vùng đó; khi ấy phải mở lại phạm vi U6.
2. **Bỏ phần dựng thẻ của `card.py`** — giữ lại `load.py`/`query.py` (đường dữ liệu mà NFR5.5 đo) và đổi BR1.7/BR1.8/AC2.1.2/AC2.1.3 sang `N/A` kèm lý do "phần hiển thị thuộc U6".

Cả hai đều đổi phạm vi của một đơn vị đã duyệt, nên tôi không tự chọn.

## 12. Revision 3 — vùng số liệu đã vào tab (2026-11-09)

Người làm chọn hướng 1. Đã làm:

| Việc | Tệp |
|---|---|
| `result_region_ids: [don-theo-thang]` theo C9 | `config/integration-tab.yaml` |
| `TabConfig.result_region_ids`; `load_tab_config` từ chối cấu hình thiếu vùng | `src/integration/card.py` |
| Khung tab dựng vùng `don-theo-thang` phía trên lưới bốn thẻ | `src/integration/tab.py` |
| Callback thứ sáu của tab (Output vùng, Input `tich-hop-cap-nhat`) gọi `render_integration_card` | `src/integration/tab.py` |
| Đường dự phòng cấu hình hỏng cũng khai vùng | `src/dashboard/app.py` |
| Test hình dạng: **8 callback**, tab có vùng, `TabConfig` có `result_region_ids`, callback của tab = 6 | ba tệp test |

**R-15 đã đóng:** con số của lát cắt giờ hiện trong tab thật, do chính callback của nó dựng. Hình dạng dashboard là **4 tab, 8 callback, 4 thẻ + 1 vùng**.

Kết quả: `pytest -m "not slow"` → **370 passed, 9 deselected**; `ruff check` và `ruff format --check` sạch trên sáu tệp đã sửa.

### Sửa sau vòng phản biện của Revision 3

| Phát hiện | Cách sửa |
|---|---|
| Critical: `_tab_config` dự phòng dùng `callback_ids=()` nên `callback_ids[0]` ném `IndexError` đúng trong ca cấu hình hỏng mà nó phải cứu | Dự phòng nay khai `callback_ids=("tich-hop-cap-nhat",)` cùng `result_region_ids` |
| Major: `tests/integration/test_u3_end_to_end.py` còn khẳng định 7 callback | Cập nhật thành **8**, khớp hình dạng mới |
| Major: `render_integration_card` đọc cấu hình tab ngoài `try` nên `ConfigurationError` thoát khỏi ranh giới callback | Đưa vào trong `try`, `action_id` khởi tạo bằng `DEFAULT_ACTION_ID` |
| Major: vùng không có trạng thái "Chưa chạy" — `STATE_EMPTY` gánh cả hai nghĩa | Thêm `STATE_PENDING` ("chưa chạy") với nhãn và biểu tượng riêng; `STATE_EMPTY` nay chỉ nghĩa "chạy xong nhưng 0 dòng"; vùng dựng bằng `STATE_PENDING` |
| Minor: thiếu test cho `_region_ids` | Bổ sung cùng lượt kiểm cấu hình tab |





