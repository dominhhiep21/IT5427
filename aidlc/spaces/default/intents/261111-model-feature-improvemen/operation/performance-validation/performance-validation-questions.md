# Performance Validation — Câu hỏi

Stage này không có lựa chọn cần bạn quyết định. Bản tóm tắt để bạn xác nhận:

## Consolidated Summary Confirmation

- **Không có load test** — hệ thống là một tiến trình localhost cho một người; đo bằng ngân sách lô và ngân sách tương tác thay vì VU/p95.
- **Bảy ngưỡng đạt:** `stats` ~28–30 s / 300 s; huấn luyện ~24 s / 240 s; `score_item` 10,49 ms / 200 ms; `load_model` 0,33 ms / 2 s; dựng khối ~2 ms / 300 ms; phủ 92,71% / 80%; mốc sàn 0,6482 ≥ 0,55.
- **Một ngưỡng chưa kết luận:** PR3.4 (+20% thời gian mở tab) chưa có cặp số trước/sau — ghi là khoảng trống thật, không phải "đạt".
- **Một ca bất thường đã giải thích:** `test_linkage_score` đỏ 69,6 s khi máy bận 59%, chạy riêng 11,11 s — không nới ngưỡng.
- **Không ngưỡng nào bị nới** trong đợt này; mục tiêu AUC 0,70 vẫn được ghi ra và hiển thị, không phải cổng.

Does this all look correct?

[Answer]: Looks correct
