# Kế hoạch NFR Requirements — U2 Integration & Analytics

**Unit**: U2 — Integration & Analytics
**Giai đoạn**: CONSTRUCTION - NFR Requirements (Planning)

## 1. Bối cảnh

U2 đọc cleaned Parquet, gọi IBGE, xây star schema, ghi mart Parquet, tạo DuckDB catalog và pre-aggregate. Chạy cục bộ trên Windows; dashboard U3 sẽ đọc DuckDB.

## 2. NFR đề xuất

| ID | Nhóm | Mục tiêu đề xuất |
|---|---|---|
| NFR-U2-01 | Hiệu năng integrate | Toàn bộ U2 ≤ 3 phút |
| NFR-U2-02 | Hiệu năng analytics | Query KPI phổ biến ≤ 1 giây |
| NFR-U2-03 | Bộ nhớ | Tiến trình ≤ 2 GB; DuckDB memory limit 1 GB |
| NFR-U2-04 | IBGE | Timeout + retry có giới hạn; cache bền |
| NFR-U2-05 | Đồng thời | Dashboard read-only; mart ghi atomic |
| NFR-U2-06 | Tin cậy | Fail-fast; không ghi đè mart khi lỗi |
| NFR-U2-07 | Tái lập | KPI baseline khớp; cache có hash |
| NFR-U2-08 | Quan sát | Log IBGE, row counts, KPI reconciliation |
| NFR-U2-09 | Bảo mật | Chỉ gọi IBGE; không gửi dữ liệu Olist |
| NFR-U2-10 | Bảo trì | Test star schema + KPI |

## 3. Tech stack đề xuất

| Thành phần | Lựa chọn |
|---|---|
| Xử lý | pandas 2.2.3 |
| Lưu trữ | Parquet Snappy |
| Catalog/query | DuckDB (pin khi cài) |
| HTTP | `urllib.request` stdlib hoặc `requests` |
| Test | pytest |

## 4. Câu hỏi cần trả lời

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Ngân sách hiệu năng U2
Thời gian tối đa cho integrate toàn bộ U2?

A) ≤ 3 phút (khuyến nghị)
B) ≤ 5 phút
C) Không đặt mục tiêu cứng
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — Giới hạn bộ nhớ DuckDB
Đặt `memory_limit` cho DuckDB:

A) 1 GB (khuyến nghị)
B) 2 GB
C) Không giới hạn
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — Chính sách gọi IBGE
Khi gọi API IBGE:

A) Timeout 10 giây, retry 2 lần, sau đó fail (khuyến nghị)
B) Timeout 30 giây, không retry
C) Fail ngay nếu lỗi mạng
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Độ trễ query analytics
Mục tiêu cho một query KPI phổ biến:

A) ≤ 1 giây (khuyến nghị)
B) ≤ 3 giây
C) Không đặt mục tiêu
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 5 — Đồng thời dashboard và rebuild
Khi pipeline đang ghi mart:

A) Dashboard dùng kết nối DuckDB read-only; mart ghi atomic (khuyến nghị)
B) Dừng dashboard trong lúc rebuild
C) Ghi mart versioned theo run_id, dashboard chọn bản mới nhất
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 5. Checklist

- [x] Đọc Functional Design U2
- [x] Đề xuất NFR và tech stack
- [x] Tạo kế hoạch và câu hỏi
- [x] Thu thập câu trả lời
- [x] Phân tích mơ hồ/mâu thuẫn
- [x] Tạo `nfr-requirements.md` + `tech-stack-decisions.md`
- [x] Cập nhật state và trình bày phê duyệt
