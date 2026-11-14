# Requirements — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `../intent-capture/intent-statement.md`, `../scope-definition/scope-document.md`, `../scope-definition/intent-backlog.md`, `../rough-mockups/{wireframes,user-flow}.md`, `../feasibility/{feasibility-assessment,constraint-register,raid-log}.md`, `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/{business-overview,architecture,code-structure}.md`, `../practices-discovery/team-practices.md`.

## Intent analysis

Mục tiêu không phải "thêm một mô hình" mà là **sửa một mô hình đang sai hướng**: AUC 0,5133 hiện tại thấp hơn baseline một đặc trưng (0,5333), tức 10 đặc trưng thêm vào đang làm hại. Đợt này đổi ba thứ cùng lúc — khung dự đoán (lúc bàn giao), đơn vị dự đoán (dòng hàng), và bộ đặc trưng — rồi chứng minh bằng số đo. Thêm vào đó là một bề mặt dùng được: vùng nhập liệu dự đoán trong tab thứ năm, chạy từ mô hình đã lưu.

Hai thứ **không** đổi: danh sách cột cấm (chỉ nới đúng hai cột mốc, ở dạng số ngày) và hợp đồng dữ liệu (5 KPI, 9 bảng nguồn, **9** bảng mart, 11 view).

---

## Functional requirements

### FR1 — Mở đường dữ liệu cho khung bàn giao

| ID | Yêu cầu | Nguồn |
|---|---|---|
| **FR1** | Mart phải phơi ra các cột mà khung dự đoán mới cần, **chỉ bằng cách thêm cột**: `order_approved_at` và `order_delivered_carrier_date` vào `v_fact_orders`, `seller_state` vào `v_fact_order_items`. | scope U1; feasibility F1 |
| **FR1.1** | Số dòng của mọi bảng mart và view **không đổi** sau khi thêm cột: **9** bảng mart, 11 view, 96.478 đơn đã giao. Đối chiếu với `EXPECTED` trong `src/integrate/validate.py` (9 dòng): **9 là số đúng**. `constraint-register.md` TC-03 và `scope-document.md` (mục "Ngoài phạm vi", Tiêu chí xong điều kiện 6) đang viết **11** và phải sửa thành 9 trong cùng thay đổi. | `constraint-register` TC-03; `validate.py` |
| **FR1.2** | Phải có một truy vấn quần thể ở **grain dòng hàng**: đơn `delivered` **và** có `order_delivered_carrier_date`, trả về 110.195 dòng hàng / 96.476 đơn / 8.713 dòng trễ; số dòng bị lọc vì thiếu carrier date (**2**) phải nằm trong báo cáo tại `model.counts.excluded_missing_carrier` (xem FR2.5). | feasibility (đo 2026-11-11); scope Q3 |
| **FR1.3** | Phải **đo lại baseline** `customer_state` trong đúng khung và đơn vị mới, ghi vào `model.baseline_auc` của báo cáo **trước** khi so với mô hình mới. | Q21 = A |
| **FR1.4** | Baseline quần thể của khung mới **thay** bộ số 96.478 đơn / 7.826 đơn trễ. Bộ số đó đang được khai là chuẩn ở **năm** nơi: `src/analytics/model.py` (`EXPECTED_DELIVERED`/`EXPECTED_LATE` và docstring dòng 21-23), `tests/unit/test_analytics_model.py:95`, `tests/integration/test_u2_model_end_to_end.py:62,70,75`, `README.md:63`, và `team.md` `## Way of Working` (dòng 52). Bộ số mới phải được đo và ghi: số dòng quần thể, số dòng trễ, mốc chia. **Thời điểm:** việc thay số được làm trong **thay đổi đưa khung grain dòng hàng vào sử dụng** (U2), **không phải U1** — vì `delivered_population` ném lỗi khi số dòng khác hằng số, còn `TRAINING_FRAME_SQL` vẫn gộp về grain đơn cho tới U2; đổi số ở U1 sẽ làm đỏ `test_analytics_model.py` và `test_u2_model_end_to_end.py` trước khi khung mới tồn tại. | R-13; R-18 |

### FR2 — Đặc trưng, mô hình, lưu trữ

| ID | Yêu cầu | Nguồn |
|---|---|---|
| **FR2** | Mô hình triển khai phải dựng đặc trưng từ khung bàn giao ở grain dòng hàng, và phải **giải thích được từng dự đoán** bằng hệ số của chính nó. | wireframes Q4 = A |
| **FR2.1** | Đặc trưng được phép dùng `order_approved_at` và `order_delivered_carrier_date` **chỉ ở dạng số ngày dẫn xuất** (đặt→duyệt, duyệt→bàn giao), không dùng giá trị ngày thô; mọi cột còn lại trong `FORBIDDEN_COLUMNS` vẫn bị cấm. **Lệnh cấm chỉ áp cho ma trận đặc trưng** (đúng phạm vi `validate_features`): việc **lọc quần thể** theo sự tồn tại của `order_delivered_carrier_date` là **được phép** và không được đưa cột đó vào đặc trưng. | `constraint-register` **SC-01**; Q17 = C; R-19 |
| **FR2.2** | Chia tập theo **`order_id`**: không đơn nào xuất hiện ở cả tập huấn luyện và tập kiểm tra. Mốc cắt 2018-04-01 trên **ngày đặt hàng**; đơn rơi đúng ngày cắt thuộc tập kiểm tra. | Q11 = A; feasibility Q4 |
| **FR2.3** | Huấn luyện **hồi quy logistic** làm mô hình triển khai, và huấn luyện `HistGradientBoosting` trên **cùng** bộ đặc trưng, cùng mốc cắt, cùng quần thể, **chỉ để báo cáo** AUC của nó. Cả hai dùng **`random_state` cố định** (hằng `RANDOM_STATE` hiện có, giá trị 42) để `auc_tree` tái lập được giữa hai lần chạy. | Q2 = C (market) → Q4 = A (mockups); R-08 |
| **FR2.4** | Lưu mô hình triển khai vào `data/models/` bằng **`pickle` của thư viện chuẩn** kèm một tệp JSON mô tả danh sách đặc trưng và phiên bản thư viện. Tệp mô hình phải mang **cả bộ ước lượng và trạng thái tiền xử lý đã khớp trên tập huấn luyện** — danh sách phạm trù one-hot (`_categories`) và tham số chuẩn hoá (`StandardScaler`) — hoặc một đối tượng gộp cả hai; khối dự đoán **chỉ** dùng trạng thái đã lưu đó, **không** khớp lại trên dữ liệu lúc dự đoán. Tệp này **không** được commit và chỉ được sinh bởi `run --stage stats`. | Q3 = A (practices); `model.py:182-200`; R-17 |
| **FR2.5** | `analysis.json` lên **phiên bản 3**. Khối `model` mang: `auc` (logistic), `auc_tree`, `baseline_auc`, `beats_baseline` (boolean), `split`, `threshold`, `precision`, `recall`, và `counts` gồm `cohort_rows`, `cohort_orders`, `late_rows`, `excluded_missing_carrier`, `auc_below_target`. **Mọi chỉ số (`auc`, `precision`, `recall`, `threshold`) tính trên đơn vị được chấm điểm là dòng hàng**; nhãn của mỗi dòng hàng kế thừa từ đơn chứa nó (A-02), nên phải ghi rõ đơn vị này cạnh từng con số trong báo cáo. **Ngưỡng cắt dự đoán được ghi tại `model.threshold`** và khối dự đoán đọc đúng trường đó — không có nguồn thứ hai. Đọc tệp phiên bản 2 phải trả trạng thái lỗi có thông điệp, **không** được ném. | requirements Q1 = A; R-03; R-16; R-20 |
| **FR2.6** | `counts.auc_below_target` tính theo **mốc 0,70** áp cho mô hình logistic triển khai; nếu chỉ mô hình cây đạt 0,70 thì cờ vẫn là `true`. | intent-statement; wireframes |
| **FR2.7** | **Mô hình triển khai phải vượt baseline đo lại**: `model.auc > model.baseline_auc` trên **cùng** quần thể, **cùng** mốc cắt và **cùng** cách chia. Phép so được kiểm bằng một test **`slow` chạy trên báo cáo thật** do `run --stage stats` sinh ra (không dùng fixture, vì fixture làm phép so luôn xanh); `model.beats_baseline` phải bằng đúng kết quả của phép so đó. | `intent-statement` Success Metrics; `scope-document` Tiêu chí xong #2; R-01 |
| **FR2.8** | Quyết định **giữ hay hạ mốc 0,70** phải được ghi vào record ngay tại Build and Test khi biết AUC, kèm lý do; không được để mốc tự trôi và không được hạ mốc mà không ghi. | `intent-statement` (Q15 = D, Q19 = A) |

### FR3 — Giao diện dự đoán

| ID | Yêu cầu | Nguồn |
|---|---|---|
| **FR3** | Tab "Kết quả phân tích" có thêm **mục thứ tư** "Dự đoán" (`html.H3`, cùng cấp ba mục hiện có), đọc tiếp sau mục "Mô hình"; không thêm tab, không thêm thẻ tóm tắt. Hình dạng bề mặt **đổi** và phải cập nhật test trong cùng thay đổi: **10 callback** (thêm 1 cho biểu mẫu dự đoán), **10 output**, **4 mục** của tab (thay vì 3). Các test phải sửa: `tests/unit/test_dashboard_smoke.py` (`len(app.callback_map) == 10`, `len(outputs) == 10`), `tests/unit/test_dashboard_analysis_tab.py` (bốn mục, đúng thứ tự), `tests/integration/test_u3_end_to_end.py` (10 callback, 5 tab). Hai chỗ **còn khẳng định tab không có ô nhập** và phải sửa cùng thay đổi: `TEXTS["model_caption"]` trong `src/dashboard/analysis_tab.py` ("Chỉ đọc: … không chọn lại được") và `README.md` mục Dashboard (dòng mô tả khối mô hình chỉ đọc). | wireframes Q1 = A; team.md `## Testing Posture`; R-04 |
| **FR3.1** | Biểu mẫu có **bảy ô**: bang người bán, bang người mua, ngày đặt hàng, giá món hàng, số ngày đặt→duyệt, số ngày duyệt→bàn giao, số lượng món. Bốn trường còn lại lấy mặc định, **sửa được**, và **hiện rõ** trên màn hình với đúng các giá trị: `payment_type = credit_card`, `payment_installments = 1`, `has_items = true`, `has_payment = true`. Không có ô cho `freight_value` — nó không phải đặc trưng. | wireframes Q2 = A; R-07 |
| **FR3.2** | Khối có **sáu** trạng thái: không có khối (báo cáo `rong`/`loi`), chưa dự đoán, đang tính, có kết quả có ngưỡng, có kết quả **chưa có ngưỡng** (`mot-phan`), và mô hình chưa sẵn. Trạng thái "mô hình chưa sẵn" phải hiện **một câu hướng dẫn cụ thể** — nêu lệnh `python -X utf8 -m src.pipeline run --stage stats` và đường dẫn `data/models/` — chứ không chỉ "không sập"; và có một test khẳng định câu đó xuất hiện khi tệp mô hình vắng. | wireframes; user-flow; R-14 |
| **FR3.3** | Kết quả gồm: xác suất, so với ngưỡng trong báo cáo, một câu kết luận nói về **dòng hàng**, và **ba** đóng góp lớn nhất tính bằng **log-odds** sau khi gộp mọi cột one-hot của cùng một trường về một dòng; nhãn "Ba đóng góp lớn nhất (log-odds, không phải tổng)" là bắt buộc. | wireframes Q3 = B |
| **FR3.4** | Cùng một đầu vào cho **cùng một** xác suất: qua nhiều lần bấm, qua hai lần chạy dashboard, và sau khi khởi động lại. | Q13 = C, Q14 = A |
| **FR3.5** | Không thêm token màu mới; hai kết quả phân biệt bằng chữ. Khối **không** tự đặt `aria-live` — vùng `RESULT_BODY_ID` của tab là nơi duy nhất thông báo kết quả. | NFR5 của đợt trước; wireframes |

### NFR

| ID | Yêu cầu | Ngưỡng | Kiểm bằng |
|---|---|---|---|
| **NFR1** | Tầng `stats` (đo lại baseline + hai mô hình + ghi tệp) trên dữ liệu thật. Ngân sách này **thay**: hằng `STAGE_BUDGET_SECONDS = 900` trong `tests/integration/test_u2_model_end_to_end.py`, **và cả hai** con số 900 s trong `team.md` `## Deployment` (ngân sách tầng **và** ngân sách riêng bước mô hình) — phải sửa cả ba chỗ trong cùng thay đổi | **< 300 s** | test `slow` đo đồng hồ |
| **NFR2** | Riêng bước huấn luyện hai mô hình ở grain dòng hàng, **nằm trong** ngân sách 300 s của NFR1. Ngân sách này **thay** hằng `TRAIN_BUDGET_SECONDS = 900` trong cùng test đó | **< 240 s** | test `slow` đo đồng hồ |
| **NFR3** | Độ phủ test: tuân theo **cổng phủ duy nhất đã có** — `pytest --cov=src --cov-fail-under=80` trong `ci.yml` và `## Testing Posture` của `team.md`. Không khai lại con số ở đây, không hạ ngưỡng | theo cổng đó | chính bước CI đó |
| **NFR4** | Không hồi quy dữ liệu: 5 KPI baseline, 9 bảng nguồn, 9 bảng mart, 11 view | khớp tuyệt đối | `KpiReconciler`, `StarSchemaValidator` |
| **NFR5** | **Mốc sàn** chặn mô hình thoái hoá: một test **`slow` trên báo cáo thật** khẳng định `model.auc` **≥ max(`MODEL_AUC_FLOOR`, `model.baseline_auc`)** — nghĩa là mốc sàn **không bao giờ thấp hơn baseline đo lại**, nên hai cổng không thể cho hai kết luận trái nhau; `MODEL_AUC_FLOOR` khởi đầu **0,55** và phải được nâng nếu baseline vượt nó | đỏ khi dưới mốc sàn hoặc dưới baseline | test `slow` trên `data/reports/analysis.json` do **bước 3** của chuỗi xác nhận sinh ra |
| **NFR6** | Tiếp cận: mọi vùng có nhãn, không `tabIndex` dương, chữ < 16px dùng `--text-2` (tương phản ≥ 4,5:1) | 100% vùng của khối mới | test đơn vị duyệt cây + `test_analysis_tab_contrast` |

**Ghi chú bắt buộc cho NFR5 và FR2.7 — thay đổi thực hành có chủ đích.** Hai yêu cầu này biến một chỉ số chất lượng thành **kỳ vọng của test**, đúng điều `team-practices.md` (`## Testing Posture`, mục "Test của lớp mô hình khẳng định hành vi, không khẳng định một con số mục tiêu") và quy tắc `project.md` ngày 2026-11-12 đang cấm. Đây là **quyết định thay đổi thực hành** (Q2 = A của stage này và FR2.7 do R-01 sinh ra), và phải được ghi lại qua ritual learnings để `project.md` không còn câu trái ngược.

Cả hai test **chạy trên báo cáo thật** (`data/reports/analysis.json` do `run --stage stats` sinh ra trong chuỗi xác nhận) và mang marker `slow`, **không** dựng fixture — một fixture sẽ làm cả hai phép kiểm luôn xanh, đúng thất bại mà FR2.7 sinh ra để chặn. Vì chúng là `slow`, chúng không kéo `TD-09` vào bộ nhanh.

---

## Constraints

Bộ mã cục bộ dùng tiền tố **`RQ-`** để không đụng `constraint-register.md` (đang dùng `TC-`, `OC-`, `RC-`, `SC-`).

| Mã | Ràng buộc | Nguồn |
|---|---|---|
| RQ-01 | Không thêm phụ thuộc mới; mọi thư viện phải có trong `requirements.txt` (12 gói). `pickle` là ngoại lệ vì thuộc thư viện chuẩn. | `constraint-register` TC-01; project.md |
| RQ-02 | `dataset/` bất biến; dữ liệu dẫn xuất vào `data/`, `warehouse/`, `logs/`, `inbox/`. | `constraint-register` TC-02 |
| RQ-03 | Hợp đồng dữ liệu: 5 KPI, 9 bảng nguồn, 9 bảng mart, 11 view — thêm **cột** thì được, đổi **dòng** hoặc **grain** thì không. | `constraint-register` TC-03 |
| RQ-04 | Không thêm lệnh con CLI; mọi thứ đi qua `run --stage` (`STAGES` có 5 tên). | project.md `## Mandated` ("NEVER thêm lệnh con CLI…") |
| RQ-05 | Mọi lệnh Python chạy UTF-8. | `constraint-register` TC-08 |
| RQ-06 | Tệp nguồn mới phải vào danh sách `ruff format --check` (`ci.yml:35`) cùng lúc; không thêm `per-file-ignores`. | `constraint-register` TC-07 |
| RQ-07 | `pickle.dump`/`load` là I/O nên **không** đặt trong `model.py`; chỗ đặt do Functional Design chốt, giữ hướng phụ thuộc `service`/`report`/`stages`. | team.md `## Code Style` |

## Assumptions

| Mã | Giả định | Nếu sai thì sao |
|---|---|---|
| A-01 | Baseline `customer_state` đo lại trong khung mới **thấp hơn** mốc 0,70, để việc cải thiện có ý nghĩa | nếu baseline ≥ 0,70 thì mục tiêu của đợt phải xét lại |
| A-02 | Nhãn trễ là thuộc tính của **đơn** và không đổi theo dòng hàng | nếu có nhãn cấp dòng hàng thì quy tắc chia tập phải xét lại |
| A-03 | `HistGradientBoosting` chạy được trên Python 3.13/Windows với `scikit-learn==1.6.1` | quay về chỉ dùng logistic |
| A-04 | `data/models/` không tồn tại là trạng thái **bình thường** trên máy mới clone, không phải lỗi | nếu bị coi là lỗi, giao diện sẽ chặn người dùng vô cớ |

## Out of scope

| Điều không làm | Nguồn |
|---|---|
| Thuật toán ngoài `scikit-learn` (`xgboost`, `lightgbm`, mạng nơ-ron) | scope-document |
| API dự đoán (endpoint gọi từ ngoài) | scope-document |
| Đụng bốn tab còn lại của dashboard | scope-document |
| Sửa `dataset/`, chỉnh tay tệp trung gian | project.md |
| Đổi 5 KPI baseline, số dòng 9 bảng nguồn, 9 bảng mart, 11 view | RQ-03 |
| Hiển thị AUC của mô hình cây trên tab | wireframes |
| SHAP hay thư viện giải thích mới | wireframes |
| Tối ưu CI; SLO; dashboard giám sát | scope-document |

## Open questions

| Mã | Câu hỏi | Chuyển tới |
|---|---|---|
| OQ-1 | Danh sách đặc trưng **cuối cùng** (bảy ô nhập là lõi chắc chắn; phần còn lại chờ U2) | Domain Design / Functional Design |
| OQ-3 | `--stage all` có nên chạy luôn `stats` (TD-11) hay giữ hai bước như hiện tại | Delivery Planning |
| OQ-4 | Cách xử lý khi chỉ 2 dòng hàng thiếu carrier date trên một bộ dữ liệu khác (ở đây là 2/110.197) | Functional Design |
