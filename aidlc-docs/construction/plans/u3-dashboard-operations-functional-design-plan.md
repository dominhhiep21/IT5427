# Kế hoạch Functional Design — U3 Dashboard & Operations

**Unit**: U3 — Dashboard & Operations
**Story**: US-15 → US-18, US-20 → US-22 (7 story)
**Giai đoạn**: CONSTRUCTION - Functional Design (Planning)

## 1. Bối cảnh

U3 là lớp sản phẩm và vận hành:

- Dashboard Plotly Dash tiếng Việt.
- CLI orchestration, micro-batch `inbox/`, replay.
- README, data dictionary, test end-to-end.
- ML dự báo giao trễ (tùy chọn).

**Phụ thuộc**: U1 cleaned, U2 marts + DuckDB + analytics.
**Đầu ra**: dashboard chạy được, CLI một lệnh, tài liệu, test.

## 2. Phạm vi chức năng

### Dashboard
- Trang Tổng quan: KPI cards + xu hướng doanh thu.
- Trang Danh mục: doanh thu/AOV/freight share, top product.
- Trang Giao vận: tỷ lệ trễ theo bang/danh mục/tháng.
- Bộ lọc: thời gian, bang/vùng, danh mục, trạng thái.
- Nhãn tiếng Việt, tiền BRL, ngày dd/mm/yyyy.

### CLI
- `python -m src.pipeline run --stage ingest|clean|integrate|analyze|all`.
- `python -m src.pipeline micro-batch`.
- `python -m src.pipeline replay --batches N`.
- `python -m src.dashboard`.
- Log run summary.

### Micro-batch
- `inbox/*.csv` cùng schema 9 bảng.
- Manifest theo hash; idempotent.
- Upsert vào mart theo natural key.
- Tệp lỗi schema bị đánh dấu failed.

### Tài liệu
- README cài đặt/chạy.
- Data dictionary.
- Runbook lỗi thường gặp.

### ML tùy chọn
- Dự báo giao trễ bằng logistic regression/random forest.
- Không chặn MVP.

## 3. Câu hỏi cần trả lời

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Bố cục dashboard
Cách tổ chức giao diện:

A) Một trang với 3 tab: Tổng quan / Danh mục / Giao vận (khuyến nghị)
B) Nhiều trang riêng biệt
C) Một trang cuộn dọc, không tab
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — CLI parser
Thư viện CLI:

A) `argparse` stdlib (khuyến nghị)
B) Typer
C) Click
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — Micro-batch merge
Cách cập nhật mart khi nhận batch:

A) Upsert theo natural key (order_id, order_item_id, ...) (khuyến nghị)
B) Append-only, gắn cờ trùng
C) Rebuild toàn bộ mart từ raw + inbox
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Định dạng inbox
Tệp micro-batch:

A) CSV cùng schema 9 bảng nguồn (khuyến nghị)
B) JSON event
C) Parquet
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 5 — ML trong U3
Phạm vi ML:

A) Trì hoãn; hoàn tất dashboard/CLI trước (khuyến nghị)
B) Làm logistic regression dự báo giao trễ
C) Làm cả dự báo giao trễ và điểm đánh giá
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 4. Checklist

- [x] Đọc unit definition và story map
- [x] Đề xuất phạm vi dashboard/CLI/micro-batch
- [x] Tạo kế hoạch và câu hỏi
- [x] Sử dụng thêm các agent skill hiện có 
- [x] Thu thập câu trả lời
- [x] Phân tích mơ hồ/mâu thuẫn
- [x] Tạo `business-logic-model.md`, `business-rules.md`, `domain-entities.md`
- [x] Cập nhật state và trình bày phê duyệt
