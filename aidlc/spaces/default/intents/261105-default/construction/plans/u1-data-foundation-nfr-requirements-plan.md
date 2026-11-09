# Kế hoạch NFR Requirements — U1 Data Foundation

**Unit**: U1 — Data Foundation
**Giai đoạn**: CONSTRUCTION - NFR Requirements (Planning)

## 1. Bối cảnh

U1 xử lý 9 CSV, tổng 1.550.922 dòng, trong đó geolocation 1.000.163 dòng. Chạy cục bộ trên Windows, Python 3.13, pandas + PyArrow; không Spark/cloud.

NFR cần chốt để Functional Design chuyển thành code có hiệu năng, an toàn và tái lập.

## 2. NFR đề xuất

| ID | Nhóm | Mục tiêu đề xuất |
|---|---|---|
| NFR-U1-01 | Hiệu năng | Ingest + clean toàn bộ ≤ 5 phút |
| NFR-U1-02 | Bộ nhớ | Đỉnh ≤ 2 GB; geolocation xử lý theo khối nếu cần |
| NFR-U1-03 | Tin cậy | Fail-fast; ghi atomic; không để output dở dang |
| NFR-U1-04 | Quan sát | Log có run_id, stage, rows_in/out; JSON lines |
| NFR-U1-05 | Tái lập | Pin phiên bản dependency; output xác định |
| NFR-U1-06 | Bảo mật | Chỉ chạy cục bộ; không secret; không gửi dữ liệu ra ngoài |
| NFR-U1-07 | Bảo trì | Test cleaning/quality; coverage ≥ 70% |
| NFR-U1-08 | Tương thích | Windows, UTF-8, Python 3.13 |

## 3. Tech stack đề xuất

| Thành phần | Lựa chọn | Lý do |
|---|---|---|
| Runtime | Python 3.13.5 | Có sẵn |
| DataFrame | pandas 2.2.3 | Có sẵn, đủ cho 1,5 triệu dòng |
| Parquet | PyArrow | Cần cài; đọc/ghi cột |
| Config | PyYAML | Đọc `config.yaml` |
| Test | pytest | Chuẩn Python |
| Log | logging + JSON formatter | Không cần dịch vụ ngoài |
| Compression | Snappy (đề xuất) | Nhanh, đủ giảm dung lượng |

## 4. Câu hỏi cần trả lời

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Ngân sách hiệu năng U1
Thời gian tối đa cho ingest + clean toàn bộ?

A) ≤ 5 phút (khuyến nghị)
B) ≤ 10 phút (khớp ngân sách toàn pipeline)
C) Không đặt mục tiêu cứng
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — Chiến lược bộ nhớ
Cách xử lý dữ liệu trong U1?

A) Nạp toàn bộ vào bộ nhớ; đỉnh ≤ 2 GB (khuyến nghị)
B) Chỉ xử lý geolocation theo khối, các bảng khác in-memory
C) Chunk toàn bộ các bảng
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — An toàn ghi output
Khi ghi cleaned Parquet:

A) Ghi thư mục tạm rồi thay thế atomic (khuyến nghị)
B) Ghi đè trực tiếp
C) Ghi vào thư mục versioned theo run_id, giữ lịch sử
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Định dạng log
Log của pipeline:

A) JSON lines ra file + summary dễ đọc ở console (khuyến nghị)
B) Chỉ text log
C) JSON lines cho mọi output, không summary text
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 5 — Nén Parquet
Codec nén cho cleaned Parquet:

A) Snappy (nhanh, khuyến nghị)
B) Zstandard (nhỏ hơn, chậm hơn)
C) Không nén
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 5. Checklist

- [x] Đọc Functional Design U1
- [x] Xác định NFR và tech stack đề xuất
- [x] Tạo kế hoạch và câu hỏi
- [ ] Thu thập câu trả lời
- [ ] Phân tích mơ hồ/mâu thuẫn
- [ ] Tạo `nfr-requirements.md` + `tech-stack-decisions.md`
- [ ] Cập nhật state và trình bày phê duyệt
