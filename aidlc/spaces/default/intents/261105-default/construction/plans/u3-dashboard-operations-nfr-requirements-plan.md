# Kế hoạch NFR Requirements — U3 Dashboard & Operations

**Unit**: U3 — Dashboard & Operations
**Giai đoạn**: CONSTRUCTION - NFR Requirements (Planning)

## 1. Bối cảnh

U3 cung cấp dashboard, CLI và micro-batch trên dữ liệu U1/U2. Chạy cục bộ trên Windows, dashboard mở trên trình duyệt.

## 2. NFR đề xuất

| ID | Nhóm | Mục tiêu đề xuất |
|---|---|---|
| NFR-U3-01 | Dashboard load | Lần đầu ≤ 3 giây |
| NFR-U3-02 | Dashboard filter | Cập nhật ≤ 3 giây |
| NFR-U3-03 | CLI full run | ≤ 10 phút (U1 + U2 + overhead) |
| NFR-U3-04 | Micro-batch | ≤ 10.000 dòng/batch, xử lý ≤ 30 giây |
| NFR-U3-05 | Trình duyệt | Chrome/Edge phiên bản hiện đại |
| NFR-U3-06 | Accessibility | WCAG AA contrast, keyboard focus |
| NFR-U3-07 | Quan sát | JSON log + summary console |
| NFR-U3-08 | Tin cậy | Batch transaction; lỗi không phá mart |
| NFR-U3-09 | Bảo mật | Dashboard chỉ localhost |
| NFR-U3-10 | Bảo trì | Test dashboard/CLI/batch |

## 3. Tech stack đề xuất

| Thành phần | Lựa chọn |
|---|---|
| Dashboard | Plotly Dash |
| Chart | Plotly |
| CLI | argparse |
| Data | pandas + DuckDB |
| Test | pytest |
| Styling | CSS tokens + Dash assets |

## 4. Câu hỏi cần trả lời

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Thời gian tải dashboard
Mục tiêu lần đầu:

A) ≤ 3 giây (khuyến nghị)
B) ≤ 5 giây
C) Không đặt mục tiêu
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — Giới hạn micro-batch
Kích thước batch và thời gian xử lý:

A) ≤ 10.000 dòng/batch, ≤ 30 giây/batch (khuyến nghị)
B) ≤ 50.000 dòng/batch, ≤ 2 phút/batch
C) Không giới hạn
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — Trình duyệt hỗ trợ
Phạm vi trình duyệt:

A) Chrome/Edge phiên bản hiện đại (khuyến nghị)
B) Chrome/Edge/Firefox
C) Mọi trình duyệt hiện đại
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Accessibility
Mức hỗ trợ:

A) WCAG AA contrast + keyboard focus + reduced motion (khuyến nghị)
B) Contrast cơ bản, không kiểm tra keyboard
C) Không đặt mục tiêu
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 5 — Định dạng log
Log CLI/dashboard:

A) JSON lines + summary console (khuyến nghị)
B) Chỉ text
C) Chỉ JSON
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 5. Checklist

- [x] Đọc Functional Design U3
- [x] Đề xuất NFR và tech stack
- [x] Tạo kế hoạch và câu hỏi
- [x] Thu thập câu trả lời
- [x] Phân tích mơ hồ/mâu thuẫn
- [x] Tạo `nfr-requirements.md` + `tech-stack-decisions.md`
- [x] Cập nhật state và trình bày phê duyệt
