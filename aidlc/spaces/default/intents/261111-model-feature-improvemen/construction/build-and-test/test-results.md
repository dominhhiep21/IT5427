# Test Results — intent `261111-model-feature-improvemen`

Số đo lấy từ lượt xác nhận cuối của Bolt 3 (`bolt checkpoint --action verify`, exit 0, 2026-11-13) và các lượt chạy trong từng đơn vị.

## 1. Tổng hợp

| Bộ | Số test | Kết quả | Thời gian |
|---|---|---|---|
| Bộ nhanh (`-m "not slow"`) | 708 | **708 passed, 15 deselected** | 25,2 s |
| Bộ `slow` | 15 | 15 passed (trong lượt toàn bộ) | ~7 phút |
| Toàn bộ + cổng phủ | 723 | **723 passed** | 424 s |
| Phủ dòng `src/` | — | **92,71%** (cổng 80%) | — |

`ruff check .` → All checks passed. `ruff format --check` trên danh sách 50 mục của `ci.yml` → 50 files already formatted.

## 2. Theo đơn vị

| Đơn vị | Test mới | Trọng tâm | Bằng chứng |
|---|---|---|---|
| **U1** `u1-mart-and-baseline` | 20 đơn vị + 2 `slow` | ba cột mart không đổi số dòng; baseline một đặc trưng | `test_integrate_facts_columns.py`, `test_integrate_seller_state.py`, `test_analytics_baseline.py`, `test_u1_mart_columns_end_to_end.py` |
| **U2** `u2-features-and-models` | 78 đơn vị + 1 `slow` | grain dòng hàng, 14 đặc trưng, hai mô hình, báo cáo v3, `pickle`, `score_item` | `test_analytics_{training_frame,features,split,threshold,baseline_block,report_v3,persistence,score_item}.py`, `test_u2_model_end_to_end.py` |
| **U3** `u3-prediction-ui` | 74 đơn vị + 1 `slow` | bốn mục, sáu trạng thái, 10 callback, ba đóng góp, cổng mốc sàn | `test_u3_prediction_section.py`, `test_dashboard_{analysis_tab,smoke}.py`, `test_analysis_tab_contrast.py`, `test_u3_end_to_end.py`, `test_u3_floor_end_to_end.py` |

## 3. Tiêu chí nghiệm thu then chốt

| Điều kiện | Kết quả |
|---|---|
| 5 KPI baseline, 9 bảng mart, 11 view không đổi | xanh trong `--stage all` (`KpiReconciler`, `StarSchemaValidator`) |
| Quần thể mô hình 110.195 / 96.476 / 8.713 / 2 | xanh trong test `slow` U2 và trong khối `counts` của báo cáo |
| 14 đặc trưng đúng tên/thứ tự, không cột cấm | `validate_features` + test đơn vị |
| Chia tập theo `order_id`, mốc 2018-04-01 | test đơn vị + `slow` |
| Báo cáo v3: 11 trường, 9 khoá `counts` | `test_analytics_report_v3.py` |
| `score_item` tất định, ba đóng góp gộp theo trường | `test_analytics_score_item.py`, `test_u3_prediction_section.py` |
| Bề mặt: 10 callback, 9 Output KPI, 4 mục, 5 tab, 4 thẻ | `test_dashboard_smoke.py`, `test_dashboard_analysis_tab.py`, `test_u3_end_to_end.py` |
| Mốc sàn `beats_floor(auc, baseline_auc)` | `test_u3_floor_end_to_end.py` (AUC 0,6482 ≥ max(0,55; 0,5297)) |
| Cổng phủ 80% | 92,71%, không hạ ngưỡng |

## 4. Ca đỏ đã gặp và cách xử lý

| Ca | Nguyên nhân | Xử lý |
|---|---|---|
| `test_u3_end_to_end.py` ghim "0,5133" | test cũ ghim AUC của mô hình trước | sửa để đọc AUC từ báo cáo (đúng luật "không ghim AUC") |
| `test_linkage_score.py::test_scoring_two_hundred_thousand_pairs_stays_under_sixty_seconds` đỏ 69,6 s > 60 s | máy chịu tải 59% khi chạy cả bộ; chạy riêng 16 passed in 11 s | **không** nới ngưỡng; ghi nhận là ca nhạy tải, không liên quan đợt này |
| `code-generation` vòng 1–2 của U2 đỏ vì `_serve_features` sai hai đặc trưng | lỗi thiết kế đã sửa | thêm test canh |

## 5. Khoảng trống đã biết

| Khoảng trống | Mức | Ghi chú |
|---|---|---|
| Bộ nhanh chưa hermetic (`TD-09`) | Cao (có từ trước) | 5 test dashboard + 1 test CLI cần `warehouse/`; CI chạy `--stage all` trước khi test |
| `PR3.4` (mở tab +20%) là **đo tay** | Thấp | đúng thiết kế, không phải test |
| Ghi tệp mô hình **không** nguyên tử | Thấp | đã ghi trong `infrastructure-specification.md` §3; hỏng thì có câu hướng dẫn |
| Bảy Minor của vòng soát Code Generation U3 (logger ở nhánh dựng panel, `custom_spinner`, `# noqa` không tác dụng…) | Thấp | ghi trong `reviews/` của U3, không chặn |
