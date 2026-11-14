# Bolt Plan — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `../units-generation/{unit-of-work,unit-of-work-dependency,unit-of-work-story-map}.md`, `../contract-design/contract-summary.md`, `../requirements-analysis/requirements.md`, `delivery-planning-questions.md` (Q1 = A, Q2 = A, Q3 = A, Q4 = A, Q5 = A).

**Bolt** ở đây là một lượt chạy xuyên các stage Construction cho một phần việc, kết thúc bằng thứ **chạy được và kiểm được trên dữ liệu thật**. Ba Bolt, mỗi Bolt một đơn vị — không gộp, không tách, vì mỗi đơn vị đã có điều kiện xong riêng.

Thứ tự `u1 → u2 → u3` là thứ tự **duy nhất** mà DAG cho phép. Kế hoạch này không chọn nó; nó giải thích vì sao đi đúng nó là đúng (xem `risk-and-sequencing-rationale.md`).

## Bolt 1 — `u1-mart-and-baseline`

| | |
|---|---|
| **Unit** | `u1-mart-and-baseline` (kind `library`) |
| **Walking skeleton** | **Không** — đợt này không dựng lát cắt mỏng (Q2 của đợt = A, ghi trong `team.md` `## Walking Skeleton` và `project.md`) |

**Definition of Done**

- Ba cột mart có mặt: `order_approved_at`, `order_delivered_carrier_date` trên `v_fact_orders`; `seller_state` trên `v_fact_order_items` — tất cả **thêm cột**, không đổi grain, không đổi lọc.
- 9 bảng mart và 11 view **giữ nguyên số dòng**; `StarSchemaValidator` xanh; 5 KPI baseline của `KpiReconciler` xanh (doanh thu delivered 15.419.773,75 BRL; 96.478 đơn; AOV 159,83; 7.826 đơn trễ; 8,11%).
- Hàm `measure_state_baseline` là hàm thuần, có test trên khung order-grain hiện có, trả AUC trong (0,1); lỗi là `ModelError`.
- Test end-to-end riêng của U1 (`slow`) xanh trên `dataset/`.
- `ruff check .` và `ruff format --check` sạch; tệp mới đã vào danh sách khai tay của `ci.yml`.

**Confidence hypothesis** — "Thêm ba cột vào mart **không** làm đổi số dòng của bất kỳ bảng nào, và 5 KPI baseline vẫn khớp đúng từng đồng." Nếu giả thuyết này sai, toàn bộ phần còn lại phải dừng: mọi con số mô hình sẽ được đo trên một mart khác với mart mà KPI mô tả.

**Demo kỳ vọng** — chạy `python -X utf8 -m src.pipeline run --stage all`, rồi mở dashboard: 5 tab vẫn đúng, 5 thẻ KPI vẫn đúng số cũ, và một truy vấn tay cho thấy ba cột mới có mặt.

---

## Bolt 2 — `u2-features-and-models`

| | |
|---|---|
| **Unit** | `u2-features-and-models` (kind `library`) |
| **Walking skeleton** | **Không** |

**Definition of Done**

- `TrainingFrame` ở grain **dòng hàng**: 110.195 dòng, 96.476 đơn, 8.713 dòng trễ, 2 dòng thiếu carrier date — cùng **một** truy vấn trả khung và bốn bộ đếm.
- `FEATURES` + `FORBIDDEN_COLUMNS` + `validate_features`; hai cột mốc chỉ vào dưới dạng `approval_days`/`handling_days`.
- Chia tập theo `order_id`, mốc `2018-04-01`; giao tập hai bên **rỗng**.
- Logistic (triển khai) + `HistGradientBoosting` (báo cáo `auc_tree`) cùng đặc trưng/mốc/quần thể/`random_state`; chạy hai lần cho cùng `auc_tree`.
- `analysis.json` **v3**: 11 trường khối `model` và `counts` **chín** khoá; `beats_baseline` khớp phép so; `auc_below_target` do `ModelModule` tính trên giá trị đã làm tròn.
- `ModelPersistence`: ghi `data/models/` bằng `pickle` + JSON metadata; `AppConfig.models_dir` + khoá `config.yaml`; nạp lại cho đúng trạng thái tiền xử lý.
- **ADR-008 thực thi**: `assemble_report` là entry point duy nhất dựng `AnalysisReport`; `collect_stats`/`build_analysis_report`/`train_model` không còn là entry point và không tự dựng `AnalyticsService`.
- Bộ số baseline mới thay ở **cả năm nơi** (FR1.4); ba khai báo ngân sách (NFR1/NFR2) cập nhật theo số đo mới.
- Test end-to-end riêng của U2 (`slow`) xanh; `--stage stats` nằm trong ngân sách 300 s.

**Confidence hypothesis** — "Mô hình triển khai **thực sự** tốt hơn baseline `customer_state` đo trong **cùng** khung: `auc > baseline_auc` trên tập kiểm tra grain dòng hàng, và ưu thế đó không phải sản phẩm của việc đổi grain." Nếu sai, cả đợt không có kết quả — và ta biết điều đó ngay ở Bolt 2, trước khi bỏ công dựng giao diện.

**Demo kỳ vọng** — `python -X utf8 -m src.pipeline run --stage stats`, rồi `jq`/đọc `data/reports/analysis.json`: thấy `version: 3`, `auc`, `auc_tree`, `baseline_auc`, `beats_baseline`, `unit`, và chín khoá `counts`.

---

## Bolt 3 — `u3-prediction-ui`

| | |
|---|---|
| **Unit** | `u3-prediction-ui` (kind `ui`) |
| **Walking skeleton** | **Không** |

**Definition of Done**

- Bốn mục trong tab theo thứ tự tóm tắt → thống kê → mô hình → dự đoán; tiêu đề mục là `H3`.
- 11 giá trị nhập dựng bằng **10** thành phần; bốn trường mặc định sửa được và hiện đúng giá trị đã chốt; lỗi hiện tại ô.
- Sáu trạng thái dựng được **không cần** dữ liệu thật; câu hướng dẫn khi thiếu mô hình chứa đúng lệnh và `data/models/`.
- Ba dòng đóng góp log-odds gộp theo trường, nhãn "Ba đóng góp lớn nhất (log-odds, không phải tổng)".
- **10 callback / 10 output**; ba tệp test hình dạng sửa cùng thay đổi; `build_dashboard_outputs` và 9 `Output` của callback KPI **không** đổi.
- Không `aria-live` thứ hai; khối kết quả là con của `RESULT_BODY_ID`; không token màu mới; tương phản chữ dưới 16px ≥ 4,5:1.
- Nhãn cứng "đơn" ở mục mô hình đổi sang đơn vị `dòng hàng`; `_auc_note` và mọi đọc mềm còn lại bị xoá.
- Mốc sàn `slow` đọc **tệp thật**, đỏ khi `auc < max(MODEL_AUC_FLOOR, baseline_auc)`; nhánh đỏ kiểm bằng hàm thuần.

**Confidence hypothesis** — "Người dùng mở tab, nhập một dòng hàng và nhận một xác suất **giải thích được** (ba đóng góp theo trường), và con số đó **không đổi** giữa hai lần bấm hay sau khi khởi động lại." Nếu sai, mô hình đúng nhưng không dùng được — và đó là lý do Bolt này tồn tại.

**Demo kỳ vọng** — `python -X utf8 -m src.dashboard`, mở tab thứ năm, nhập một dòng, thấy xác suất + ba đóng góp; tắt dashboard, bật lại, dự đoán lại, thấy cùng con số.

---

## Điều kế hoạch này không làm

- Không đổi thứ tự: DAG là chuỗi, và ba Bolt là ba lần giao hàng nối tiếp.
- Không thêm Bolt cho việc "dọn dẹp" — mã cũ dọn theo từng tệp khi có người sửa tới (`team.md` `## Code Style`).
- Không có Bolt nào chạy song song: mỗi Bolt cần Bolt trước xong để test của nó xanh.
