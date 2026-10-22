# NFR Requirements — U1 Data Foundation

## 1. Mục tiêu chất lượng

U1 phải chạy ổn định trên máy cá nhân Windows, xử lý 1.550.922 dòng, tạo output tái lập và không làm hỏng dữ liệu cũ khi lỗi.

## 2. Yêu cầu phi chức năng

### NFR-U1-01 — Hiệu năng
- **Mục tiêu**: Ingest + clean + quality gate toàn bộ ≤ **5 phút** (chạy nguội, không cache).
- **Đo**: từ lúc CLI bắt đầu stage đến khi ghi xong `quality-report.json`.
- **Điều kiện**: SSD, CPU 4 lõi, RAM ≥ 8 GB.
- **Kiểm chứng**: log `duration_seconds`; test benchmark thủ công ghi lại kết quả.
- **Nếu vượt**: tối ưu gộp geolocation (vectorized groupby) trước khi tối ưu nơi khác.

### NFR-U1-02 — Bộ nhớ
- **Mục tiêu**: Đỉnh bộ nhớ tiến trình ≤ **2 GB**; peak Python allocation ≤ 1,5 GB.
- **Chiến lược**: nạp toàn bộ vào bộ nhớ; geolocation là bảng lớn nhất (~1 triệu dòng).
- **Kiểm chứng**: theo dõi peak RSS khi chạy full batch; ghi vào run summary.
- **Giới hạn**: nếu dữ liệu tăng > 5 triệu dòng, phải chuyển sang chunk geolocation (ngoài phạm vi hiện tại).

### NFR-U1-03 — Tin cậy và toàn vẹn
- **Fail-fast**: lỗi schema/khóa/orphan dừng pipeline, CLI trả mã 1.
- **Atomic write**: ghi vào thư mục tạm cùng ổ đĩa, kiểm tra thành công rồi thay thế thư mục đích.
- **Không output dở dang**: nếu fail, cleaned/mart cũ giữ nguyên.
- **Idempotent**: chạy lại cùng input cho cùng nội dung logic.
- **Kiểm chứng**: test giả lập lỗi giữa chừng; output cũ vẫn đọc được.

### NFR-U1-04 — Quan sát
- **Log**: JSON lines ra `logs/{run_id}.jsonl`; mỗi dòng có:
  `timestamp`, `level`, `run_id`, `stage`, `table`, `rows_in`, `rows_out`, `duration_ms`, `status`, `message`.
- **Console**: summary ngắn gọn, dễ đọc.
- **Báo cáo**: `ingest-report.json`, `cleaning-report.json`, `quality-report.json`, `reconciliation.json`.
- **Kiểm chứng**: mọi stage tạo ít nhất một log entry; lỗi có stack trace hoặc mã lỗi.

### NFR-U1-05 — Tái lập
- **Dependency**: pin chính xác trong `requirements.txt`; không dùng range khi chạy.
- **Determinism**: sắp xếp ổn định trước khi gộp geolocation; không dùng random.
- **Input hash**: SHA-256 của 9 CSV được ghi lại.
- **Kiểm chứng**: chạy 2 lần trên cùng input; so sánh số dòng, checksum logic, KPI mẫu.

### NFR-U1-06 — Bảo mật và riêng tư
- **Phạm vi**: chỉ chạy cục bộ; U1 không gọi mạng.
- **Dữ liệu**: không upload dữ liệu Olist ra ngoài; không đưa dữ liệu vào log chi tiết từng dòng.
- **Secret**: không lưu credential/token trong repo.
- **Quyền**: chỉ ghi trong workspace.
- **Kiểm chứng**: không có import HTTP client trong U1; không có secret trong config.

### NFR-U1-07 — Bảo trì và kiểm thử
- **Coverage**: ≥ **70%** cho module `clean` và `quality`.
- **Test bắt buộc**:
  - join customers × geolocation trả 99.441 dòng.
  - category fallback giữ 610 sản phẩm.
  - review/payment không nhân bản item.
  - quality gate fail khi orphan/khóa trùng.
- **Kiểu**: type hints cho public function; docstring ngắn.
- **Kiểm chứng**: `pytest` pass; báo cáo coverage.

### NFR-U1-08 — Tương thích
- **OS**: Windows 10/11.
- **Python**: 3.13.x.
- **Encoding**: UTF-8; dùng `pathlib.Path`; không hardcode dấu `/`.
- **Console**: chạy với `python -X utf8` hoặc `PYTHONUTF8=1`.
- **Kiểm chứng**: chạy trên máy hiện tại; test đường dẫn có dấu tiếng Việt.

### NFR-U1-09 — Khả năng mở rộng
- **Hiện tại**: full batch 1,5 triệu dòng.
- **Tương lai**: micro-batch dùng cùng quality rules ở chế độ incremental.
- **Không** yêu cầu Spark/DuckDB trong U1.
- **Kiểm chứng**: quality gate có tham số `mode=full|incremental`.

### NFR-U1-10 — Lưu trữ
- **Định dạng**: Parquet.
- **Compression**: Snappy.
- **Partition**: không partition ở U1; một tệp/bảng.
- **Kiểm chứng**: đọc lại bằng pandas/pyarrow; số dòng khớp.

## 3. Ràng buộc và đánh đổi

| Quyết định | Đánh đổi |
|---|---|
| In-memory toàn bộ | Nhanh, đơn giản; không phù hợp dữ liệu > 5 triệu dòng |
| Snappy | Nhanh; dung lượng lớn hơn Zstandard |
| Atomic temp + replace | An toàn; cần dung lượng đĩa gấp đôi tạm thời |
| JSON lines | Dễ parse; file lớn hơn text log |
| Allowlist exact counts | Phát hiện thay đổi tốt; cần cập nhật khi dữ liệu nền thay đổi |

## 4. Tiêu chí nghiệm thu NFR

- [ ] Full batch U1 ≤ 5 phút.
- [ ] Peak RSS ≤ 2 GB.
- [ ] Fail giữa chừng không làm hỏng output cũ.
- [ ] Log JSON có đủ trường bắt buộc.
- [ ] `pytest` pass; coverage cleaning/quality ≥ 70%.
- [ ] Chạy được trên đường dẫn có ký tự tiếng Việt.
- [ ] Parquet đọc lại đúng số dòng.
