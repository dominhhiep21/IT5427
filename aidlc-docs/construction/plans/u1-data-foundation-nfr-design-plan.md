# Kế hoạch NFR Design — U1 Data Foundation

**Unit**: U1 — Data Foundation
**Giai đoạn**: CONSTRUCTION - NFR Design (Planning)

## 1. Mục tiêu

Chuyển NFR U1 thành pattern và logical component cụ thể:

- Ghi atomic, fail-fast, idempotent.
- Log JSON có run_id.
- Xử lý geolocation vectorized, kiểm soát bộ nhớ.
- Test bằng fixture tổng hợp + integration test.
- Đo hiệu năng/bộ nhớ có bằng chứng.

## 2. Pattern đề xuất

| NFR | Pattern | Cách áp dụng |
|---|---|---|
| NFR-U1-01 hiệu năng | Vectorized groupby | Gộp geolocation bằng pandas, không loop |
| NFR-U1-02 bộ nhớ | In-memory + đo peak | `tracemalloc`, log peak |
| NFR-U1-03 tin cậy | Atomic write + fail-fast | Tệp tạm cùng thư mục, `os.replace` |
| NFR-U1-04 quan sát | Structured logging | JSON lines + console summary |
| NFR-U1-05 tái lập | Deterministic sort + hash | Sort trước dedupe/mode; SHA-256 |
| NFR-U1-06 bảo mật | Local-only | Không HTTP client trong U1 |
| NFR-U1-07 bảo trì | Fixture + integration test | Synthetic cho unit, real CSV cho integration |
| NFR-U1-09 mở rộng | Quality mode | `full` vs `incremental` |

## 3. Logical component đề xuất

- `RunContext` + `JsonLogger`.
- `AtomicWriter` — ghi Parquet/JSON an toàn.
- `SchemaValidator` — kiểm tra cột/kiểu.
- `GeoAggregator` — dedupe, bbox, median, mode.
- `QualityGate` — checks + allowlist + mode.
- `ReportWriter` — ingest/cleaning/quality/reconciliation.
- `MemoryProbe` — đo peak allocation.
- `TestFixtures` — bảng nhỏ tổng hợp + dữ liệu thật đánh dấu slow.

## 4. Câu hỏi cần trả lời

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Đơn vị ghi atomic
Ghi cleaned Parquet an toàn theo cách nào?

A) Từng tệp: ghi `.tmp` cùng thư mục rồi `os.replace` (khuyến nghị)
B) Ghi cả thư mục tạm rồi thay thế cả thư mục
C) Ghi trực tiếp, không atomic
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — Giữ lại tệp tạm khi lỗi
Nếu pipeline fail giữa chừng:

A) Giữ thư mục tạm để debug, log đường dẫn (khuyến nghị)
B) Xóa toàn bộ tệp tạm
C) Chuyển tệp tạm vào `data/failed/{run_id}/`
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — Chiến lược test
Cách tổ chức dữ liệu test:

A) Fixture tổng hợp cho unit test + integration test với CSV thật, đánh dấu `slow` (khuyến nghị)
B) Dùng CSV thật cho mọi test
C) Chỉ fixture tổng hợp, không test với dữ liệu thật
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Đo bộ nhớ
Cách đo peak memory:

A) `tracemalloc` (stdlib) + log peak; không thêm dependency (khuyến nghị)
B) Dùng `psutil` để đo RSS thực
C) Không đo tự động, chỉ quan sát thủ công
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 5 — Pattern gộp geolocation
Cách xử lý 1.000.163 dòng geolocation:

A) Vectorized groupby/median/mode trong một pass (khuyến nghị)
B) Chia chunk 200.000 dòng để giảm peak memory
C) Vòng lặp Python theo từng zip
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 5. Checklist

- [x] Đọc NFR Requirements U1
- [x] Đề xuất pattern và logical component
- [x] Tạo kế hoạch và câu hỏi
- [x] Thu thập câu trả lời
- [x] Phân tích mơ hồ/mâu thuẫn
- [x] Tạo `nfr-design-patterns.md` + `logical-components.md`
- [x] Cập nhật state và trình bày phê duyệt
