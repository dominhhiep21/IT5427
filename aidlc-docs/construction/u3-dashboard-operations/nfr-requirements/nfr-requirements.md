# NFR Requirements — U3 Dashboard & Operations

## 1. Mục tiêu chất lượng

Dashboard phải mở nhanh, dùng được bằng bàn phím, hiển thị tiếng Việt nhất quán. CLI và micro-batch phải đủ nhanh cho demo và không phá dữ liệu cũ.

## 2. Yêu cầu phi chức năng

### NFR-U3-01 — Dashboard load
- **Mục tiêu**: lần đầu mở ≤ **3 giây** (localhost, dữ liệu đã có).
- **Đo**: performance panel trình duyệt hoặc `time.perf_counter` quanh callback đầu.
- **Kiểm chứng**: ghi lại thời gian; nếu vượt, kiểm tra query/agg.

### NFR-U3-02 — Dashboard filter
- **Mục tiêu**: cập nhật KPI/chart ≤ **3 giây**.
- **Đo**: thời gian callback.
- **Kiểm chứng**: filter mặc định và filter 1 bang.

### NFR-U3-03 — CLI full run
- **Mục tiêu**: `run --stage all` ≤ **10 phút** (U1 ≤5 + U2 ≤3 + overhead).
- **Đo**: run summary duration.
- **Kiểm chứng**: chạy trên dữ liệu thật.

### NFR-U3-04 — Micro-batch
- **Mục tiêu**: ≤ **10.000 dòng/batch**; xử lý ≤ **30 giây/batch** (không tính rebuild U2 toàn bộ).
- **Đo**: `BatchResult.duration_seconds`.
- **Kiểm chứng**: batch mẫu 1k/10k dòng.

### NFR-U3-05 — Trình duyệt
- Hỗ trợ Chrome/Edge phiên bản hiện đại.
- Không yêu cầu Firefox/Safari.
- **Kiểm chứng**: manual smoke trên Chrome/Edge.

### NFR-U3-06 — Accessibility
- Contrast WCAG AA cho text/nền.
- Keyboard focus rõ ràng; tab order hợp lý.
- Tôn trọng `prefers-reduced-motion`.
- **Kiểm chứng**: kiểm tra contrast; tab qua filter/tab; CSS media query.

### NFR-U3-07 — Logging
- JSON lines + summary console.
- Trường: timestamp, level, run_id, command, stage, rows, duration, status.
- **Kiểm chứng**: log file parse được.

### NFR-U3-08 — Tin cậy batch
- Batch transaction: temp → validate → promote.
- Lỗi không làm hỏng cleaned/mart cũ.
- **Kiểm chứng**: batch lỗi schema.

### NFR-U3-09 — Bảo mật
- Dashboard chỉ `127.0.0.1`.
- Không auth/multi-user.
- Không gửi dữ liệu ra ngoài.
- **Kiểm chứng**: config host.

### NFR-U3-10 — Bảo trì và test
- Unit: format, manifest, upsert.
- Integration: CLI all, dashboard callback.
- Coverage dashboard/pipeline/micro-batch ≥ **70%**.
- **Kiểm chứng**: `pytest`.

## 3. Ràng buộc và đánh đổi

| Quyết định | Đánh đổi |
|---|---|
| Dash | Nhanh để build; ít kiểm soát layout hơn React |
| Single page 3 tab | Ít điều hướng; tab Giao vận tách biệt |
| Upsert cleaned + rebuild marts | Đúng dữ liệu; micro-batch chậm hơn nếu batch lớn |
| Localhost only | An toàn; không chia sẻ LAN |
| Không ML | Giảm dependency; US-22 để sau |

## 4. Tiêu chí nghiệm thu NFR

- [ ] Dashboard mở ≤ 3 giây.
- [ ] Filter cập nhật ≤ 3 giây.
- [ ] CLI all ≤ 10 phút.
- [ ] Batch 10k dòng ≤ 30 giây.
- [ ] Chrome/Edge smoke pass.
- [ ] Contrast AA + keyboard focus + reduced motion.
- [ ] Log JSON parse được.
- [ ] Batch lỗi không phá mart.
- [ ] `pytest` pass; coverage ≥ 70%.
