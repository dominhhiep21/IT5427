# Unit ↔ Story Map — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `unit-of-work.md`, `../user-stories/stories.md` (10 truyện), `../requirements-analysis/requirements.md`.

Mỗi dòng ứng với **một** `USx.y`. Cột `Units` nêu mọi đơn vị thi công một phần của truyện đó; cột `Directories` là tên thư mục construction tương ứng (đích mà `traceability.json` trỏ tới).

## Story map

| Story | Units | Directories | Đơn vị giao phần chính |
|---|---|---|---|
| US1.1 | U2; U1 | `u2-features-and-models`; `u1-mart-and-baseline` | U2 sinh `cohort_rows`/`cohort_orders`/`late_rows`/`excluded_missing_carrier` từ truy vấn grain dòng hàng và ghi `baseline_auc` + `counts` vào báo cáo v3; U1 giữ bất biến số dòng mart (AC1.1.3) và giao hàm đo baseline |
| US1.2 | U2 | `u2-features-and-models` | `auc` vs `baseline_auc`, `beats_baseline`, `auc_tree`, `version = 3`, nhãn `unit` |
| US1.3 | U2 | `u2-features-and-models` | `counts.auc_below_target` theo mốc hiện hành; mục ghi quyết định giữ/hạ mốc nằm trong record của Build and Test |
| US2.1 | U3 | `u3-prediction-ui` | Bốn mục, `H3`, 10 callback / 10 output, không `aria-live` riêng, câu mở đầu nói "một dòng hàng", `TEXTS["model_caption"]` + README |
| US2.2 | U3; U2 | `u3-prediction-ui`; `u2-features-and-models` | U3 dựng 11 giá trị / 10 thành phần và bốn trường mặc định sửa được, lỗi tại ô; U2 giao hàm chấm điểm một dòng |
| US2.3 | U3; U2 | `u3-prediction-ui`; `u2-features-and-models` | U2 gộp đóng góp log-odds **theo trường**; U3 hiện đúng ba dòng và nhãn "không phải tổng" |
| US2.4 | U2; U3 | `u2-features-and-models`; `u3-prediction-ui` | U2 lo tất định (cùng đầu vào → cùng xác suất), trạng thái tiền xử lý đã lưu, chia tập theo `order_id`, `FORBIDDEN_COLUMNS`, `random_state`; U3 không khớp lại trên dữ liệu lúc dự đoán |
| US2.5 | U3 | `u3-prediction-ui` | Sáu trạng thái; `rong`/`loi` không có mục Dự đoán; `mot-phan` nói "chưa có ngưỡng để so"; thiếu `data/models/` hiện đúng câu lệnh |
| US3.1 | U3; U2 | `u3-prediction-ui`; `u2-features-and-models` | U2 tính `auc_below_target`; U3 hiện "đạt/không đạt mốc" kèm giá trị mốc đang áp, không hard-code 0,70 |
| US3.2 | U3 | `u3-prediction-ui` | Test `slow` đọc báo cáo **thật**, đỏ khi `auc < max(MODEL_AUC_FLOOR, baseline_auc)` |

## Cross-cutting rows

| Việc | Đơn vị | Vì sao không thuộc một truyện |
|---|---|---|
| Thay bộ số baseline ở **năm** nơi (FR1.4) | U2 | Việc cập nhật hằng số ở nhiều tệp, không phải hành vi người dùng thấy được — `stories.md` đã ghi rõ nó ở `Deferred` |
| Sửa **ba** tệp test hình dạng khi bề mặt đổi | U3 | Là hệ quả của US2.1 nhưng chạm ba tệp test (`test_dashboard_smoke.py`, `test_dashboard_analysis_tab.py`, `test_u3_end_to_end.py`) cộng hai câu văn, không phải một tiêu chí nghiệm thu riêng |
| `ruff format --check` thêm tệp mới vào danh sách khai tay | U1, U2, U3 | Quy ước repo (`ci.yml:35`), áp cho mọi đơn vị tạo tệp nguồn mới |

## Thứ tự trong nội bộ một đơn vị

Không phải thứ tự thi công giữa các đơn vị (việc đó thuộc Delivery Planning), và cũng không phải ràng buộc của DAG. Thứ tự **bên trong** một đơn vị là chuyện của Functional Design và Code Generation; ở đây chỉ ghi những chỗ có phụ thuộc kỹ thuật thật, để không ai phải phát hiện lại:

- **U2**: đặc trưng và `validate_features` phải có trước khi huấn luyện; `ModelPersistence` phải có trước khi giao diện nạp được tệp mô hình; `assemble_report` phải có trước khi `stages.py` ghi được báo cáo v3.
- **U3**: bề mặt (bốn mục, mười thành phần, sáu trạng thái) phải có trước khi callback thứ mười nối vào; mốc sàn chỉ kiểm được sau khi U2 đã sinh báo cáo thật.
- **U1**: ba cột mart phải có trước khi `StarSchemaValidator`/KPI được chạy lại.



## Coverage verification

- **10/10 truyện được gán**, không có `GAP`.
- **Mọi đơn vị có dòng**: U1 (US1.1), U2 (US1.1, US1.2, US1.3, US2.2, US2.3, US2.4, US3.1), U3 (US2.1, US2.2, US2.3, US2.4, US2.5, US3.1, US3.2).
- **U1 không có truyện nào "của riêng nó"**, và đó là sự thật chứ không phải thiếu sót: U1 là hạ tầng dữ liệu, `stories.md` đã ghi "U1 và U2 thuần kỹ thuật… không có truyện riêng". Phần U1 chịu trách nhiệm trong US1.1 là **AC1.1.3** (9 bảng mart và 11 view giữ nguyên số dòng); `cohort_rows` và `baseline_auc` của AC1.1.1–.2 thuộc U2 vì chúng cần truy vấn grain dòng hàng.
- **Đích trong `traceability.json`** là đơn vị **chính** của từng dòng, luôn có mặt trong ô `Directories` của dòng đó.
