# Build and Test Summary

Nguồn: `build-instructions.md`, `test-results.md`, `cross-unit-traceability.md`, `integration-test-instructions.md`, `performance-test-instructions.md`, `security-test-instructions.md`.

## Kết luận

**Ba đơn vị xanh trên cùng một lần chạy.** Không có hồi quy, không ngưỡng nào bị nới, không test nào bị bỏ qua bằng marker.

| Hạng mục | Kết quả |
|---|---|
| Test toàn bộ | **537 passed**, exit 0, 281,85 s |
| Test nhanh | **525 passed**, 12 deselected |
| Độ phủ `src/` | **92,45%** (cổng 80% nguyên vẹn) |
| `ruff check .` | All checks passed |
| `ruff format --check` | clean trên mọi tệp đã chạm |
| Chuỗi `--stage all` → `--stage stats` | success, báo cáo `day-du` |
| Không hồi quy KPI | 5 baseline, 9 bảng nguồn, 11 mart, 11 view giữ nguyên |

## Ba đơn vị

| Đơn vị | Giao được gì | Test riêng |
|---|---|---|
| u1-statistics | `report.py`, `statistics.py`, tầng `stats`, 3 phương thức đọc mới trong `service.py` | `test_analytics_report.py`, `test_analytics_statistics.py`, `test_pipeline_stages.py`, `test_u1_stats_end_to_end.py` |
| u2-model | `model.py`, ghim `scikit-learn==1.6.1` | `test_analytics_model.py`, `test_u2_model_end_to_end.py` |
| u3-display | `analysis_tab.py`, tab thứ năm, khối CSS phạm vi | `test_dashboard_analysis_tab.py`, `test_analysis_tab_contrast.py`, `test_u3_end_to_end.py` |

## Điều chưa đạt, ghi rõ

- **AUC 0,5133**, dưới mốc 0,70. Không giấu: `counts.auc_below_target = true` và tab hiện "không đạt mốc 0,70". Đợt cải thiện đặc trưng đã ghi trong nhật ký record, mục tiêu ≥ 0,70.
- **NFR1.2, NFR1.4, NFR1.6** chưa có phép đo — đánh `Deferred`, không đánh `OK`.
- **NFR1.5** là giả định không kiểm được: `dataset/` bất biến, chỉ một cỡ dữ liệu.
- **`TD-09`** vẫn mở: bộ nhanh cần `warehouse/` và `data/marts/` sinh ra.

## Bài học của đợt

Hai vòng kiểm liên tiếp của U3 bắt cùng một lỗi: tuyên bố NFR5.1 đạt trong khi chưa có gì đo. Khi viết `test_analysis_tab_contrast.py`, nó chỉ ra ngay chỗ thứ hai bị bỏ sót — huy hiệu `chua-chay`/`rong`, đúng hai trạng thái người dùng thấy nhiều nhất.

Đó là lý do `test-results.md` ghi con số chứ không ghi lời khen: một bảng "đạt hết" không có phép đo đứng sau là bảng sai.
