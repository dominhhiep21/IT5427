# Build and Test Summary — intent `261111-model-feature-improvemen`

## 1. Kết luận

**Đạt.** Ba đơn vị đã đóng và duyệt; toàn bộ 723 test xanh trên dữ liệu thật; phủ 92,71% so với cổng 80%; `ruff` sạch; chuỗi xác nhận bốn bước xanh (`exit 0`).

| Đơn vị | Checkpoint | Bằng chứng |
|---|---|---|
| U1 `u1-mart-and-baseline` | verified + approved | 559 test, phủ 92,48% |
| U2 `u2-features-and-models` | verified + approved | 637 test, phủ 92,57% |
| U3 `u3-prediction-ui` | verified + approved | 723 test, phủ 92,71% |

## 2. Yêu cầu → kết quả

| Yêu cầu | Kết quả |
|---|---|
| AUC ≥ 0,70 **và** vượt baseline đo lại | **chưa đạt mốc 0,70**: AUC **0,6482** (trước 0,5133), vượt baseline `customer_state` **0,5297**, đạt mốc sàn 0,55. Cờ `auc_below_target = true` vẫn đúng và được hiển thị |
| Mô hình ở grain dòng hàng | 110.195 dòng / 96.476 đơn / 8.713 trễ / 2 đơn loại |
| 14 đặc trưng, không rò rỉ | `validate_features` + test; `order_approved_at`/`order_delivered_carrier_date` chỉ vào dạng số ngày |
| Báo cáo v3, tệp mô hình | `REPORT_VERSION = 3`, 11 trường, 9 khoá; `data/models/logistic.pkl` nạp lại khớp |
| Mục Dự đoán trong dashboard | 4 mục, 10 callback, 6 trạng thái, ba đóng góp log-odds |
| Mốc sàn trong CI | test `slow` trên báo cáo thật, xanh |
| Không hạ cổng phủ, không thêm phụ thuộc, không sửa `dataset/` | đúng |

## 3. Điều đáng nói thẳng

1. **Mục tiêu AUC 0,70 không đạt.** Đặc trưng mới cải thiện rõ (+0,135 AUC, từ 0,5133 lên 0,6482, vượt baseline) nhưng chưa chạm 0,70. Không có điều chỉnh nào để "cho đẹp số": ngưỡng cảnh báo vẫn chọn theo F1 trên tập kiểm tra, cờ dưới mốc vẫn bật.
2. **Hai deviation đã ghi, không che:** (D-1) trạng thái "có kết quả chưa có ngưỡng" của FR3.2 không dựng được dưới C2; (D-2) con số "10 output" của FR3 = 9 Output KPI + 1 Output mới.
3. **Ca nhạy tải** trong `test_linkage_score.py` từng đỏ 69,6 s > 60 s khi máy bận 59%; chạy riêng 11 s. Không nới ngưỡng.

## 4. Còn mở trước khi đóng intent

| Việc | Ở đâu |
|---|---|
| Ghi ngoại lệ mốc sàn vào `project.md` **`## Corrections`** (dẫn nguyên văn luật NEVER, lý do NFR5) | nghi thức learnings |
| Ghi hai ngân sách 300 s / 240 s và con số danh sách format hiện tại (50) vào `team.md` | nghi thức learnings |
| Commit nhánh `feature/analysis-and-models` | quyết định của người làm |

## 5. Rủi ro đã biết, không chặn

| Rủi ro | Mức |
|---|---|
| Bộ nhanh chưa hermetic (`TD-09`, có từ trước) | Cao |
| Ghi tệp mô hình không nguyên tử | Thấp |
| Bảy Minor của vòng soát Code Generation U3 | Thấp |
