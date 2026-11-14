# Performance Validation — NFR Matrix

Đối chiếu **ngưỡng đã cam kết** với **số đo thật** trên máy phát triển của đợt này (Windows, Python 3.13).

| ID | Hạng mục | Ngưỡng | Đo được | Kết luận | Đo bằng |
|---|---|---|---|---|---|
| NFR1 | Tầng `stats` trên dữ liệu thật | < 300 s | **~28–30 s** cho toàn bộ `stats` trong test end-to-end | **đạt**, dư ~10× | `test_u2_model_end_to_end.py::STAGE_BUDGET_SECONDS` |
| NFR2 | Riêng bước huấn luyện hai mô hình | < 240 s | **~24 s** | **đạt**, dư ~10× | `TRAIN_BUDGET_SECONDS` |
| PR3.1 | `score_item` một dòng hàng | < 200 ms | **10,49 ms** (max 11,7) | **đạt**, dư ~19× | `test_u3_prediction_section.py -k budget` |
| PR3.2 | `load_model` | < 2 s | **0,33 ms** | **đạt**, dư rất lớn | cùng tệp |
| PR3.3 | `build_prediction_body` | < 300 ms | **~2 ms** | **đạt** | cùng tệp |
| PR3.4 | Mở tab không chậm quá +20% | +20% | **chưa đo chính thức** — đo tay một lần, không lưu số | **chưa kết luận** | đo tay |
| NFR3 | Phủ dòng `src/` | ≥ 80% | **92,71%** | **đạt** | `pytest --cov` |
| NFR5 | Mốc sàn | `auc ≥ max(0,55; baseline)` | **0,6482 ≥ 0,55** | **đạt** | `test_u3_floor_end_to_end.py` |
| — | Bộ nhanh | không có ngưỡng | 23–25 s cho 708 test | tham khảo | `pytest -m "not slow"` |
| — | Toàn bộ + phủ | không có ngưỡng | **424 s** cho 723 test | tham khảo | chuỗi xác nhận |

## Điều phải nói rõ

1. **PR3.4 chưa có số.** Ngưỡng "+20% thời gian mở tab" là đo tay và tôi đã không lưu một cặp số trước/sau. Đây là khoảng trống thật, không phải "đạt". Cách đóng: đo `render_analysis` trên cây trước/sau thay đổi bằng một lần chạy `time.perf_counter()`; nếu ai cần con số, đó là việc 10 phút.
2. **Ngưỡng thời gian là ngưỡng bắt thoái hoá**, không phải mục tiêu — dư địa 10–6.000× để không đỏ vì runner CI chậm.
3. **Không có ngưỡng nào bị nới** trong đợt này; ba ngưỡng PR3.1–PR3.3 mới được đặt lần đầu.
4. **Mục tiêu AUC 0,70 không thuộc bảng này** — nó được ghi ra và hiển thị (0,6482), không phải cổng; mốc sàn 0,55 mới là cổng.

## Nguồn

Ngưỡng lấy từ `../../construction/u3-prediction-ui/nfr-requirements/performance-requirements.md` và `../../construction/u3-prediction-ui/nfr-design/performance-design.md`; cách hiển thị tín hiệu lấy từ `../observability-setup/dashboards.md`; ngân sách lô thuộc U2 (`nfr-requirements` của `u2-features-and-models`).
