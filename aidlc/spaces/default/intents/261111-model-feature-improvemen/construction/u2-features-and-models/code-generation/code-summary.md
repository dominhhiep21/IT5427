# Code Summary — u2-features-and-models

## Đã làm gì

Chuyển khung huấn luyện sang **grain dòng hàng**, mở đặc trưng lên **14 cột**, dựng **hai mô hình**, nâng báo cáo lên **phiên bản 3**, lưu mô hình bằng `pickle`, và thêm hàm chấm điểm một dòng.

| Tệp | Thay đổi |
|---|---|
| `src/config.py`, `config.yaml` | thêm `models_dir` (`data/models`) vào `AppConfig`, `load_config`, vòng tạo thư mục |
| `src/analytics/service.py` | `TRAINING_FRAME_SQL` viết lại: grain dòng hàng, join `v_fact_order_items`, hai cột ngày bằng `date_diff`, bốn bộ đếm từ **một** câu lệnh (CTE `excluded` + `CROSS JOIN`); `training_frame()` trả `(frame, counts)`, kiểm duy nhất trên khoá ghép |
| `src/analytics/model.py` | `FEATURES` 11 → **14** (6 phân loại + 6 số + 2 cờ), `FORBIDDEN_COLUMNS` thêm `order_approved_at` (11 mục), `EXPECTED_*` = 110.195/8.713, thêm `MODEL_AUC_FLOOR`, `UNIT_LABEL`, `beats_floor`, `score_item` (+ `PredictionOutcome`, `PredictionContribution`, `_serve_features`); `split_frame` chia **theo `order_id`** (có nhánh dự phòng khi khung không có `order_id`); `train_from_frame` đo baseline + `HistGradientBoosting` cho `auc_tree` |
| `src/analytics/report.py` | `REPORT_VERSION = 3`; `ModelBlock` **11 trường**; `_model_block` đọc đủ và đòi **9 khoá** `counts` (thiếu ⇒ `loi`); thêm `_boolean`; thêm **`assemble_report`** |
| `src/analytics/statistics.py` | `build_analysis_report` dựng báo cáo **qua `assemble_report`** (ADR-008) |
| `src/analytics/persistence.py` | **mới**: `FittedModel`, `save_model`, `load_model`, `fit_persistable`, `fit_from_config`; `pickle` + metadata JSON |
| `src/pipeline/stages.py` | nhánh `stats` gọi `save_model(fit_from_config(...))` sau khi ghi báo cáo |
| `tests/unit/*` | **8 tệp mới** (78 test): training frame, features, split, threshold, baseline/floor, report v3, persistence, score_item; sửa 5 test grain đơn và 2 test hình dạng |
| `tests/integration/test_u2_model_end_to_end.py` | viết lại: 110.195/96.476/8.713/2, 14 đặc trưng, chia theo `order_id`, `beats_baseline`, `auc_tree` tất định, nạp lại tệp mô hình; ngân sách **300 s** tầng / **240 s** bước mô hình |
| `.github/workflows/ci.yml`, `tests/unit/test_ci_config.py` | thêm 1 tệp nguồn + 8 tệp test mới vào **cả hai** danh sách khai tay |
| `README.md` | phiên bản báo cáo **3**, grain dòng hàng 110.195/96.476/8.713/2, **14** đặc trưng, `data/models/` |

## Vá sau ba vòng soát

| Phát hiện | Cách sửa |
|---|---|
| Critical: `_serve_features` sai `item_total` và `customer_region` | `item_total = item_price × item_count`; `customer_region` lấy từ `FittedModel.state_regions` (đi trọn `fit_persistable` → `save_model` → `load_model` → `score_item`) |
| Critical: `state_regions` khai mà không dùng | truyền vào `FittedModel`, ghi/đọc trong payload, `fit_from_config` dẫn xuất từ quần thể; có test vòng ghi-đọc-và-chấm |
| Major: nhập sai kiểu/ngoài miền vẫn chấm im lặng | `_numeric_input`/`_state_code` kiểm miền và **nêu tên trường**: giá ≥ 0, số món ≥ 1, số ngày trong [0, 365], trả góp ≥ 1, mã bang hai chữ cái |
| Major: `README.md` nói "không lưu tệp mô hình" | đã sửa lại đúng C2b; `README.md` vào `source-manifest.json` |
| Major: `validate_features` không kiểm thứ tự | so nguyên bộ 14 tên với `FEATURES`; có test danh sách đảo ngược |
| Major: `assemble_report` chưa phải đường duy nhất | `stages.py` gọi `assemble_report`; `replace(...)` đã bỏ |
| Major: `fit_persistable` bỏ qua `train_classifier` | không hội tụ nay thành `ModelError`; khối `set_params` vô nghĩa đã xoá |
| Minor: hai bộ đếm không có cổng | `validate_cohort_counts` kiểm cả **bốn** bộ đếm (110.195/96.476/8.713/2), gọi ở `train_model` và `fit_from_config`; có 6 test |

## Bốn chặng, bốn điểm dừng (theo yêu cầu)

| Chặng | Bằng chứng đỏ → xanh | Đo trên dữ liệu thật |
|---|---|---|
| **A — nền dữ liệu** | 8 test mới đỏ 8/8 → **8 passed** | 110.195 dòng / 96.476 đơn / 8.713 trễ / 2 loại; khoá ghép duy nhất; `order_id` không duy nhất |
| **B — đặc trưng, chia tập** | 20 test mới đỏ → **20 passed** | 14 cột khớp hợp đồng; train 73.443 / test 36.752, giao `order_id` rỗng; ma trận 91 cột |
| **C — baseline, báo cáo, lưu** | 22 test mới đỏ → **22 passed** | `baseline_auc` = **0,5297**; baseline **thấp hơn** sàn 0,55 |
| **D — chấm điểm, ngân sách, e2e** | 8 test mới đỏ → **8 passed** | test `slow` **1 passed in 28,10 s** (ngân sách 240 s) |

## Kiểm tra đã chạy

```
python -X utf8 -m pytest -m "not slow" -q                → 623 passed, 14 deselected
python -X utf8 -m pytest -m slow tests/integration/test_u2_model_end_to_end.py -q → 1 passed in 28.10s
python -X utf8 -m ruff check .                           → All checks passed
python -X utf8 -m ruff format --check <16 tệp>           → 16 files already formatted
```

## Quyết định trong lúc thi công

1. **Hai cột ngày theo độ phân giải ngày.** Mart không có `order_purchase_timestamp`; dùng `date_key` cho `approval_days` và ngày của `order_approved_at` cho `handling_days`. Sai số dưới một ngày, đã ghi trong thiết kế.
2. **`feature_names` là danh sách đã mở rộng** (91 cột) và phép so ở chỗ chấm điểm so **toàn bộ danh sách**, không so số cột — đúng điểm chệch đã ghi ở NFR Design.
3. **`split_frame` có nhánh dự phòng** khi khung không có `order_id`, để baseline một đặc trưng của U1 vẫn dùng được. Không có nhánh này thì 6 test của U1 đỏ.
4. **`fit_from_config` nằm ở `persistence.py`**, không ở `model.py`, để giữ I/O ngoài mô-đun suy luận (ADR-001/008).
5. **Mốc sàn 0,55 cao hơn baseline 0,5297** — nghĩa là mốc sàn hiện **là mức chất lượng đặt trước**, không thuần là cổng chống thoái hoá. Đây là điều phải ghi ở cổng learnings, cùng việc sửa `project.md` `## Forbidden`.

## Điều chưa làm

- **Chưa sửa `project.md`** và **chưa ghi hai ngân sách vào `team.md`** — cả hai đi qua **nghi thức learnings ở cổng**, không sửa tay (CP2.3).
- `README.md` **đã** cập nhật (phiên bản 3, 14 đặc trưng, grain dòng hàng, `data/models/`).
- **Chưa commit** — quyết định của người làm.
