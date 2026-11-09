# NFR Design Patterns — U3 Dashboard & Operations

## 1. Server-Side Callback + Aggregate Pattern

- Dash callback chạy server-side; nhận filter, gọi `AnalyticsService`.
- Chart ưu tiên `agg_sales_daily` / `agg_delivery_daily`; chỉ dùng fact view khi cần drill-down.
- Không tính lại toàn bộ fact trong callback.
- **NFR**: U3-01, U3-02.

## 2. Filter State Pattern

- `dcc.Store(id="filters")` giữ filter khi chuyển tab.
- Mỗi tab đọc cùng store; thay đổi filter phát signal cập nhật tất cả.
- Không reset khi đổi tab.
- **NFR**: U3-02.

## 3. Formatting + Accessibility Pattern

- Hàm thuần: `format_brl`, `format_date`, `format_number`.
- CSS tokens trong `assets/style.css`.
- Contrast AA; focus ring rõ; `@media (prefers-reduced-motion: reduce)` tắt animation.
- **NFR**: U3-05, U3-06.

## 4. Error Boundary Pattern

- Callback bọc try/except.
- Lỗi dữ liệu → banner tiếng Việt + nút “Thử lại”.
- Empty → thông điệp hướng dẫn đổi filter.
- Không hiển thị traceback.
- **NFR**: U3-06, U3-08.

## 5. CLI Stage Runner Pattern

- argparse subcommands: `run`, `micro-batch`, `replay`.
- `StageRunner` gọi U1/U2 theo thứ tự.
- Mỗi stage trả `StageResult`; tổng hợp `RunSummary`.
- Exit code 0/1.
- **NFR**: U3-03, U3-07.

## 6. Transactional Batch Pattern

1. Copy `data/cleaned` → `run.temp_dir/cleaned`.
2. Clean batch, upsert vào bản tạm.
3. Quality gate trên bản tạm.
4. Promote từng tệp bằng `os.replace`.
5. Chạy U2 integrate full rebuild.
6. Lỗi → không promote; giữ bản cũ.
- **NFR**: U3-04, U3-08.

## 7. Manifest Idempotency Pattern

- Manifest JSON: batch_id, table, sha256, status, processed_at.
- Hash success → skip.
- Hash mới → xử lý.
- Ghi manifest atomic.
- **NFR**: U3-04, U3-08.

## 8. Natural-Key Upsert Pattern

- Đọc existing cleaned + batch mới.
- Xóa existing rows có key trong batch.
- Append batch rows.
- Sort theo key để deterministic.
- Ghi atomic.
- **NFR**: U3-04.

## 9. Replay Generation Pattern

- Lấy cleaned orders theo tháng.
- Mỗi tháng → `inbox/replay/{YYYY-MM}/`.
- Ghi `orders.csv`, `order_items.csv`, `payments.csv`, `reviews.csv` (subset theo order_id).
- Xử lý tuần tự qua micro-batch.
- **NFR**: U3-04.

## 10. Structured Logging Pattern

- JSON lines: timestamp, level, run_id, command, stage, rows, duration, status.
- Console summary ngắn.
- Không log dữ liệu từng dòng.
- **NFR**: U3-07.

## 11. Localhost Security Pattern

- `app.run(host="127.0.0.1", port=8050)`.
- Không auth; không expose LAN.
- Không upload dữ liệu.
- **NFR**: U3-09.

## 12. Pattern → NFR mapping

| Pattern | NFR |
|---|---|
| Server-side callback + agg | U3-01, U3-02 |
| Filter store | U3-02 |
| Formatting/accessibility | U3-05, U3-06 |
| Error boundary | U3-06, U3-08 |
| Stage runner | U3-03, U3-07 |
| Transactional batch | U3-04, U3-08 |
| Manifest idempotency | U3-04, U3-08 |
| Natural-key upsert | U3-04 |
| Replay generation | U3-04 |
| JSON logging | U3-07 |
| Localhost | U3-09 |
