# Business Rules — U3 Dashboard & Operations

## Nhóm A — Dashboard

### BR-U3-01 — Ba tab
- **Quy tắc**: Dashboard có đúng 3 tab: Tổng quan, Danh mục, Giao vận.
- **Lý do**: Tách câu hỏi kinh doanh theo mục đích, tránh một trang quá tải.
- **Kiểm thử**: render app, đếm tab = 3.

### BR-U3-02 — Bộ lọc toàn cục
- **Quy tắc**: Bộ lọc thời gian, bang, vùng, danh mục, trạng thái áp dụng cho cả 3 tab.
- Mặc định: toàn bộ thời gian, trạng thái `delivered`.
- Tab Giao vận chỉ tính đơn delivered, bất kể bộ lọc trạng thái.
- **Kiểm thử**: đổi filter → KPI và chart cùng cập nhật.

### BR-U3-03 — Nguồn dữ liệu
- KPI card dùng `AnalyticsService.kpi_summary`.
- Xu hướng/danh mục/vùng dùng `agg_sales_daily`.
- Giao vận dùng `agg_delivery_daily` + `AnalyticsService.delivery_kpis`.
- **Không** đọc CSV; **không** ghi dữ liệu.
- **Kiểm thử**: monkeypatch service; dashboard không mở CSV.

### BR-U3-04 — Định dạng
- Tiền: `R$ 1.234,56` (pt-BR).
- Ngày: `dd/mm/yyyy`.
- Số: dấu chấm hàng nghìn, phẩy thập phân.
- Nhãn, tiêu đề, tooltip tiếng Việt.
- **Kiểm thử**: format functions.

### BR-U3-05 — Trạng thái rỗng/lỗi
- Không có dữ liệu → “Không có dữ liệu với bộ lọc hiện tại.”
- DuckDB/Parquet lỗi → “Không đọc được dữ liệu. Kiểm tra pipeline/DuckDB.”
- Không crash trắng, không hiển thị traceback cho người dùng.
- **Kiểm thử**: filter không tồn tại; đóng DuckDB.

### BR-U3-06 — 2016 sparse
- Khi filter/kết quả có năm 2016, hiển thị badge “Dữ liệu 2016 chưa đầy đủ”.
- Không loại 2016 khỏi chart.
- **Kiểm thử**: filter 2016 → badge xuất hiện.

### BR-U3-07 — Định hướng thị giác
- Palette: ink `#0B1F1A`, paper `#F6F7F2`, mist `#DCE8E0`, ochre `#D9A441`, clay `#B5532F`.
- Heading/số lớn: Georgia; body/nhãn: Segoe UI; số nhỏ: Consolas.
- Không dùng card bo tròn đồng loạt; ưu tiên đường kẻ mảnh, khoảng trắng rộng.
- **Kiểm thử**: kiểm tra CSS tokens; screenshot thủ công.

## Nhóm B — CLI

### BR-U3-08 — Lệnh
- `python -m src.pipeline run --stage all|ingest|clean|integrate|analyze`
- `python -m src.pipeline micro-batch --inbox inbox`
- `python -m src.pipeline replay --batches N`
- `python -m src.dashboard`
- Dùng `argparse` stdlib.
- **Kiểm thử**: `--help`; từng stage.

### BR-U3-09 — Thứ tự stage
- `all` = ingest → clean → quality → integrate → analyze smoke.
- `integrate` yêu cầu cleaned tồn tại; nếu thiếu → lỗi rõ.
- `analyze` chỉ đọc, không ghi.
- **Kiểm thử**: chạy all trên dữ liệu thật.

### BR-U3-10 — Run summary
- Mỗi lệnh có `run_id`, stage, rows_in/out, duration, status.
- Log JSON lines + summary console.
- Exit code 0/1.
- **Kiểm thử**: lỗi giả lập → exit 1.

## Nhóm C — Micro-batch

### BR-U3-11 — Cấu trúc inbox
- `inbox/{batch_id}/{table}.csv`.
- Tên bảng thuộc 9 bảng nguồn.
- Không nhận file ngoài schema.
- **Kiểm thử**: batch hợp lệ/lỗi.

### BR-U3-12 — Manifest idempotency
- Manifest lưu batch_id, table, sha256, status, processed_at.
- Hash đã success → bỏ qua.
- Hash mới → xử lý.
- **Kiểm thử**: chạy 2 lần cùng batch → row count không đổi.

### BR-U3-13 — Upsert natural key
- Khóa theo bảng trong business-logic-model.
- Xóa bản ghi cũ cùng khóa trong bản tạm, thêm bản mới.
- Không tạo bản ghi trùng.
- **Kiểm thử**: batch cập nhật order_status → mart phản ánh giá trị mới.

### BR-U3-14 — Batch transaction
- Copy cleaned hiện tại sang temp.
- Upsert + quality gate trên temp.
- Chỉ promote khi pass.
- Sau promote, rebuild U2 marts.
- Lỗi → giữ cleaned/mart cũ.
- **Kiểm thử**: batch lỗi schema → mart cũ không đổi.

### BR-U3-15 — Batch lỗi
- Tệp lỗi schema bị đánh dấu `failed`, các tệp hợp lệ khác vẫn xử lý.
- Batch có ít nhất một tệp failed → batch status `partial`/`failed`.
- Không chặn batch kế tiếp.
- **Kiểm thử**: 1 tệp lỗi + 1 tệp tốt.

### BR-U3-16 — Replay
- `replay --batches N` tạo N batch lịch sử theo tháng từ cleaned orders.
- Ghi vào `inbox/replay/`, xử lý tuần tự.
- Idempotent theo hash.
- **Kiểm thử**: replay 2 batch, KPI cuối khớp batch đầy đủ.

## Nhóm D — Tài liệu và phạm vi

### BR-U3-17 — Tài liệu
- README: cài đặt, chạy, dashboard, micro-batch, troubleshooting.
- Data dictionary: dim/fact/agg.
- Runbook: IBGE, DuckDB lock, schema batch.
- 3V: volume/variety/velocity.
- **Kiểm thử**: review nội dung; lệnh trong README chạy được.

### BR-U3-18 — ML trì hoãn
- Không triển khai US-22 trong MVP.
- Không thêm dependency scikit-learn.
- Story giữ trạng thái Could.
- **Kiểm thử**: không có import ML trong `src/`.

### BR-U3-19 — Bảo mật
- Dashboard chỉ localhost.
- Không auth/multi-user.
- Không gửi dữ liệu ra ngoài.
- **Kiểm thử**: host mặc định 127.0.0.1.

### BR-U3-20 — Kiểm thử
- Unit: format, manifest, upsert.
- Integration: CLI all + dashboard callback smoke.
- Không bắt buộc browser test.
- **Kiểm thử**: `pytest` pass.
