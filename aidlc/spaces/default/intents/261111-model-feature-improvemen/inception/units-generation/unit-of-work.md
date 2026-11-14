# Units of Work — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `../domain-design/{components,decisions}.md`, `../requirements-analysis/requirements.md`, `../user-stories/stories.md`, `../units-generation/units-generation-questions.md` (Q1 = A, Q2 = A, Q3 = A).

Ba đơn vị, một đường phụ thuộc thẳng. Mỗi đơn vị là một lát cắt **chạy được và kiểm được trên dữ liệu thật** của riêng nó, không phải một tầng giấy.

## Unit summary

| Unit ID | Directory | Name | Kind | Complexity | Deployment |
|---|---|---|---|---|---|
| U1 | `u1-mart-and-baseline` | Nới mart và đo baseline | `library` | M | shared (một tiến trình) |
| U2 | `u2-features-and-models` | Đặc trưng, hai mô hình, lưu mô hình | `library` | L | shared |
| U3 | `u3-prediction-ui` | Mục Dự đoán và mốc sàn CI | `ui` | L | embedded (gắn vào dashboard) |

`kind` chọn theo Q1 = A. Không đơn vị nào là `service`: repo không có tiến trình riêng cho tầng mô hình — `run --stage stats` là một nhánh của cùng CLI.

---

## U1 — `u1-mart-and-baseline`

**Mô tả.** Mở rộng mart đúng ba cột mà tầng mô hình cần, đo lại quần thể ở grain dòng hàng, và giao **hàm** đo baseline một đặc trưng. Đơn vị này không đổi số dòng của bất kỳ bảng nào.

**Sở hữu và giao:**
- Ba cột mart: `order_approved_at` và `order_delivered_carrier_date` vào `v_fact_orders`, `seller_state` vào `v_fact_order_items` — tất cả **thêm cột**, không đổi lọc, không đổi grain.
- Hàm thuần đo baseline một đặc trưng (`customer_state`) trên một `DataFrame` + mốc chia, trả AUC. Hàm này **chưa** được nối vào `analysis.json` — việc nối thuộc U2 (Q2 = A, FR1.4).
- Bảo đảm bất biến số dòng của 9 bảng mart và 11 view sau khi thêm cột.

**Ranh giới.** U1 **không** sở hữu `TrainingFrame` (khung vẫn ở grain đơn) và **không** sở hữu `CohortCounts`: cả bốn bộ đếm — kể cả `cohort_rows = 110.195` — chỉ đếm được khi truy vấn đã ở grain dòng hàng, mà đổi grain đó là việc của U2 theo `FR1.4`. U1 không sở hữu đặc trưng, không sở hữu báo cáo, không sở hữu giao diện.

**Điều kiện xong:**
- 9 bảng mart và 11 view **giữ nguyên số dòng**; `StarSchemaValidator` và 5 KPI baseline (`KpiReconciler`) xanh.
- Hàm đo baseline chạy được trên khung **order-grain hiện có** trên dữ liệu thật và trả AUC trong (0,1); đây là kiểm hàm, **không** phải kiểm quần thể mới — quần thể 110.195 dòng hàng thuộc U2.
- Test end-to-end riêng của U1 (`slow`) xanh trên `dataset/`.
- `ruff check .` và `ruff format --check` sạch, tệp mới đã thêm vào danh sách khai tay của `ci.yml`.

**Rủi ro chính.** Đây là đơn vị **duy nhất chạm tầng dùng chung** (mart). Một lỗi grain ở đây làm đỏ cả 5 KPI và toàn bộ test tích hợp cũ, nên phần bù là chạy `--stage all` + `--stage stats` trên dữ liệu thật ngay trong đơn vị này.

**Ghi chú thi công:** `seller_state` phải lấy từ `olist_sellers_dataset.csv` (qua `dim_sellers`), không suy từ địa chỉ khách. Hai cột mốc chỉ được dùng ở dạng **số ngày dẫn xuất**, không đưa giá trị ngày thô vào đặc trưng — việc chặn thuộc U2 nhưng cột thì do U1 mở.

---

## U2 — `u2-features-and-models`

**Mô tả.** Chuyển khung huấn luyện sang grain dòng hàng, dựng đặc trưng có kiểm, huấn luyện hai mô hình, chọn ngưỡng, so với baseline, lưu mô hình, và ghi `analysis.json` phiên bản 3.

**Sở hữu và giao:**
- `TrainingFrame` ở grain **dòng hàng** (một dòng mỗi cặp đơn × món), lọc `delivered` + có carrier date; 19 cột như `components.md`.
- `CohortCounts` ở `AnalyticsService`: cùng **một** truy vấn trả khung và bốn bộ đếm — `cohort_rows` 110.195, `cohort_orders` 96.476, `late_rows` 8.713, `excluded_missing_carrier` 2. Đây là chỗ **duy nhất** sinh ra `excluded_missing_carrier` (FR1.2): đếm trước khi lọc, không lọc rồi đếm lại, không có truy vấn thứ hai.
- `FEATURES` + `FORBIDDEN_COLUMNS` + `validate_features`; hai cột mốc **chỉ** vào dưới dạng `approval_days` / `handling_days`.
- Chia tập theo `order_id`, mốc `2018-04-01` trên ngày đặt; giao tập hai bên rỗng.
- Hồi quy logistic (**mô hình triển khai**) và `HistGradientBoosting` (chỉ để báo cáo `auc_tree`), cùng đặc trưng/mốc/quần thể/`random_state`.
- Ba đóng góp log-odds **gộp theo trường** (mọi cột one-hot của cùng một trường cộng lại).
- `baseline_auc` và `beats_baseline` — nối kết quả của hàm baseline do U1 giao vào hợp đồng.
- `counts` đủ **chín** mục — bốn khoá v2 (`flagged`, `not_flagged`, `total`, `threshold_method`), `auc_below_target` do `ModelModule` tính, và bốn bộ đếm quần thể — **không** để giao diện tự so.
- `ModelPersistence`: ghi `data/models/` bằng `pickle` + JSON mô tả đặc trưng và phiên bản thư viện; đọc lại trả đúng trạng thái tiền xử lý đã khớp.
- `analysis.json` **v3**: 11 trường khối `model` (7 trường cũ giữ nguyên + `unit`, `auc_tree`, `baseline_auc`, `beats_baseline`), đọc tệp v2 trả `loi` có thông điệp.
- **Ranh giới I/O theo ADR-008**: `collect_stats` và `build_analysis_report` không còn là entry point của `statistics.py`; `train_model` không còn tự dựng `AnalyticsService`; `ReportContract.assemble_report` là entry point duy nhất dựng `AnalysisReport` và giữ khối `model` cũ. `PipelineStages` là nơi lấy dữ liệu, gọi hàm thuần, và giao `assemble_report`.
- **Hằng số ngưỡng**: `MODEL_AUC_FLOOR` (NFR5, khởi đầu 0,55) đặt trong `src/analytics/model.py`, cạnh `AUC_TARGET` — U2 sở hữu tệp đó nên U2 khai hằng số này. U3 **không** sửa `model.py`; U3 chỉ `import` hằng số để test mốc sàn. Cùng với `AUC_TARGET`, đây là hai hằng số duy nhất của ngưỡng mô hình.
- **Hàm so mốc sàn** (R-06): một hàm thuần `(auc, baseline_auc, floor) -> bool` đặt trong `ModelModule`, để nhánh đỏ kiểm được bằng test đơn vị mà không dựng báo cáo giả.

**Ranh giới.** Không sửa mart (U1 đã xong), không dựng giao diện, không tự đọc DuckDB trong mô-đun thuần — `PipelineStages` lấy dữ liệu rồi truyền vào (ADR-008).

**Điều kiện xong:**
- `--stage stats` trên dữ liệu thật sinh báo cáo v3 + tệp mô hình; `auc`, `auc_tree`, `baseline_auc`, `beats_baseline` đều có mặt và `beats_baseline` khớp phép so.
- `counts` trên dữ liệu thật ra đúng 110.195 / 96.476 / 8.713 / 2, và `auc_below_target` bằng `auc < AUC_TARGET`.
- Bộ số baseline mới được thay ở **cả năm nơi** (`model.py`, `test_analytics_model.py`, `test_u2_model_end_to_end.py`, `README.md`, `team.md`) — FR1.4.
- **ADR-008 đã thực thi xong**: `grep` không còn `collect_stats(`/`build_analysis_report(`/`train_model(` là entry point công khai trong `statistics.py`/`model.py`, `stages.py` gọi `assemble_report`, và **không** còn chỗ nào thứ hai dựng `AnalysisReport`; test cũ đã đổi sang đường mới.
- `MODEL_AUC_FLOOR` có mặt trong `model.py` cạnh `AUC_TARGET`, và hàm thuần so mốc sàn có test đơn vị cho cả hai nhánh.
- Ba khai báo ngân sách thời gian được cập nhật **cùng thay đổi** theo số đo mới: `STAGE_BUDGET_SECONDS` và `TRAIN_BUDGET_SECONDS` trong `tests/integration/test_u2_model_end_to_end.py`, cùng hai con số ngân sách trong `team.md` (NFR1, NFR2). Không nới ngầm.
- Không cột nào trong `FORBIDDEN_COLUMNS` lọt vào ma trận; tách `order_id` hai bên rỗng.
- Chạy `--stage stats` hai lần cho `auc_tree` giống nhau.
- Test end-to-end riêng của U2 (`slow`) xanh.

**Rủi ro chính.** Đổi grain là thay đổi chạm nhiều nơi nhất trong repo: năm khai báo baseline, `TRAINING_FRAME_SQL`, và ngân sách thời gian 300 s. Phần bù: đo lại thời gian và sửa ngân sách **có chủ đích**, không nới ngầm.

**Ghi chú thi công:** `pickle` là thư viện chuẩn nên không thêm phụ thuộc; tệp mô hình **không** được commit (`data/` đã bị `.gitignore`). Tệp model của máy này không phải định dạng trao đổi — máy khác sinh lại.

---

## U3 — `u3-prediction-ui`

**Mô tả.** Thêm mục thứ tư "Dự đoán" vào tab phân tích, và dựng mốc sàn AUC trong bộ test `slow`.

**Sở hữu và giao:**
- Bốn mục theo thứ tự tóm tắt → thống kê → mô hình → dự đoán; mục mới là `H3`, dùng lại `_section`/`.chart-card`, chỉ **thêm** CSS cho `fieldset`, nút, danh sách đóng góp.
- Mười một giá trị nhập dựng bằng **mười** thành phần (3 `dcc.Dropdown`, 6 `dcc.Input`, 1 `dcc.Checklist` hai mục); sáu trạng thái (`rong`, `chua-chay`, `dang-tai`, `day-du`, `mot-phan`, `loi`).
- Ba dòng đóng góp log-odds đã gộp theo trường, nhãn "Ba đóng góp lớn nhất (log-odds, không phải tổng)".
- **10 callback / 10 output** trên toàn dashboard: callback KPI đang trả **9** `Output` trong một callback (`app.py:450-465`), nên con số 10 là *một callback mới, một output mới* cộng vào 9 callback hiện có — không phải callback KPI tự nhân đôi output. Ba tệp test canh con số này, sửa trong **cùng** thay đổi: `tests/unit/test_dashboard_smoke.py` (`len(app.callback_map) == 10`, `len(outputs) == 10`), `tests/unit/test_dashboard_analysis_tab.py` (bốn mục, đúng thứ tự), `tests/integration/test_u3_end_to_end.py` (10 callback, 5 tab). Đúng ba tệp — không phải năm.
- Khối kết quả là **con** của `RESULT_BODY_ID`, không đặt `aria-live` thứ hai.
- `TEXTS["model_caption"]` và `README.md` mục Dashboard: bỏ câu khẳng định tab chỉ đọc.
- Mốc sàn: hàm thuần `(auc, baseline_auc, floor) -> bool` của U2 có test đơn vị cho **cả hai nhánh**; test `slow` chỉ khẳng định **nhánh xanh trên tệp báo cáo thật** do `--stage stats` sinh — không dựng báo cáo tổng hợp, vì NFR5 cấm fixture.

**Ranh giới.** Không huấn luyện, không đọc DuckDB, không tính lại chỉ số; chỉ đọc báo cáo và gọi hàm chấm điểm của U2.

**Điều kiện xong:**
- Ba tệp test hình dạng ở trên được sửa **cùng thay đổi** và xanh: 10 callback, 10 output, bốn mục đúng thứ tự, 5 tab.
- Sáu trạng thái đều dựng được không cần dữ liệu thật (dựng báo cáo trong `tmp_path`), tab không sập khi thiếu `data/models/`, và câu hướng dẫn chứa đúng `python -X utf8 -m src.pipeline run --stage stats` + `data/models/`.
- Không chạm `src/analytics/model.py`; hằng số `MODEL_AUC_FLOOR` chỉ được `import`.
- Tương phản chữ dưới 16px đạt ≥ 4,5:1 bằng token có sẵn (`--text-2`), không thêm token màu.
- Mốc sàn: hàm thuần `(auc, baseline_auc, floor) -> bool` của U2 có test đơn vị cho **cả hai nhánh** (đỏ và xanh); test `slow` chỉ khẳng định **nhánh xanh trên tệp báo cáo thật** do `--stage stats` sinh — không dựng báo cáo tổng hợp, vì NFR5 cấm fixture.

**Rủi ro chính.** Hình dạng bề mặt là hợp đồng: 10 callback/10 output là con số được test canh ở **ba** tệp (tên ở trên), cộng hai câu văn (`TEXTS["model_caption"]`, `README.md`). Phần bù: sửa test trong cùng thay đổi, không sửa sau.

**Ghi chú thi công:** `AC2.5.6` đã hạ xuống "spinner của `dcc.Loading` là đủ" (ADR-005) — không có output thứ mười một, nút không bị khoá khi đang tính.

---

## Điều các đơn vị này không làm

- Không thêm lệnh con CLI; `run --stage stats` vẫn là đường duy nhất sinh báo cáo và tệp mô hình.
- Không sửa `--stage all` để chạy `stats` (TD-11, ngoài phạm vi).
- Không xoá `TD-06` (`integrate → analytics`) hay `TD-26` (tab → `integration/card.py`).
- Không thêm phụ thuộc ngoài `requirements.txt`; không đụng `dataset/`.
