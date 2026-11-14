# Cross-Unit Traceability — intent `261111-model-feature-improvemen`

Đối chiếu ba đơn vị với 29 tiêu chí nghiệm thu của US2.1–US2.5, US3.1–US3.2 và 6 NFR. Nguồn mỗi dòng là `traceability.json` của đơn vị tương ứng (U1: `construction/u1-mart-and-baseline/`, U2: `.../u2-features-and-models/`, U3: `.../u3-prediction-ui/`).

## 1. Phân công

| Nhóm AC | Đơn vị giao | Bằng chứng |
|---|---|---|
| AC1.1.1–AC1.3.2 (mart, baseline, bất biến số dòng) | **U1** | test mart + `test_u1_mart_columns_end_to_end.py` |
| AC2.2.1, AC2.3.1, AC2.3.3, AC2.4.1–AC2.4.6, AC2.5.3 (chấm điểm, tất định, chia tập) | **U2** | `test_analytics_score_item.py`, `test_u2_model_end_to_end.py` |
| AC2.1.1–AC2.1.6, AC2.2.2–AC2.2.3, AC2.3.2, AC2.5.1–AC2.5.6, AC3.1.1–AC3.1.3, AC3.2.1–AC3.2.2 | **U3** | `test_u3_prediction_section.py`, `test_dashboard_analysis_tab.py`, `test_u3_floor_end_to_end.py` |

## 2. Bảng quyết định chéo

| AC | U1 | U2 | U3 | Ghi chú |
|---|---|---|---|---|
| AC2.4.3 (nạp trạng thái đã lưu) | — | giao | N/A | U3 chỉ gọi `load_model` |
| AC2.4.4 (chia tập theo `order_id`) | — | giao | N/A | |
| AC2.4.5 (không cột cấm) | — | giao | N/A | |
| AC2.4.6 (`auc_tree` tất định) | — | giao | N/A | |
| AC2.5.3 ("kết quả chưa có ngưỡng") | — | — | **N/A** | không dựng được dưới C2 — deviation D-1, đã ghi trong `functional-spec.md` §0 |
| AC2.1.3, AC3.2.x (bề mặt, cổng) | — | — | giao | |

## 3. NFR

| NFR | Giao cho | Bằng chứng |
|---|---|---|
| NFR1 (300 s tầng `stats`) | U2 | `test_u2_model_end_to_end.py::STAGE_BUDGET_SECONDS` |
| NFR2 (240 s bước huấn luyện) | U2 | `TRAIN_BUDGET_SECONDS` |
| NFR3 (cổng phủ 80% trong CI) | U2 + U3 | `ci.yml` bước phủ; `test_ci_config.py` canh "không bị hạ" |
| NFR4 (không hồi quy dữ liệu) | U1 | `KpiReconciler`, `StarSchemaValidator` |
| NFR5 (mốc sàn) | U2 (hàm) + U3 (test) | `beats_floor` + `test_u3_floor_end_to_end.py` |
| NFR6 (tiếp cận) | U3 | test duyệt cây + `test_analysis_tab_contrast.py` |

## 4. Khoảng hở và xử lý

| Khoảng hở | Xử lý |
|---|---|
| AC2.5.3 không thoả được | đánh `N/A` **có lý do** trong `traceability.json` của U3; nêu ở cổng duyệt |
| `PR3.1`–`PR3.4` (ngân sách tương tác) | PR3.1–PR3.3 có test; PR3.4 là đo tay (đúng thiết kế) |
| Không có AC nào không có đơn vị nhận | kiểm bằng ba sensor `traceability`, tất cả `pass` |
