# Kế hoạch NFR Design — U3 Dashboard & Operations

**Unit**: U3 — Dashboard & Operations
**Giai đoạn**: CONSTRUCTION - NFR Design (Planning)

## 1. Mục tiêu

Chuyển NFR U3 thành pattern và logical component:

- Dashboard 3 tab, callback nhanh, filter state rõ.
- CLI orchestration có run summary.
- Micro-batch transaction, manifest, upsert.
- Replay minh họa velocity.
- Accessibility và lỗi hiển thị thân thiện.

## 2. Pattern đề xuất

| NFR | Pattern | Cách áp dụng |
|---|---|---|
| U3-01/02 hiệu năng | Server-side callback + agg | Query `agg_*`, không tính lại fact |
| U3-03 CLI | Stage runner tuần tự | `run` gọi U1/U2, summary |
| U3-04 batch | Transactional temp | copy cleaned → upsert → validate → promote |
| U3-05 browser | Progressive enhancement | Dash + CSS chuẩn |
| U3-06 accessibility | Semantic HTML + tokens | contrast, focus, reduced motion |
| U3-07 logging | JSON lines | run_id, command, stage |
| U3-08 reliability | Fail-safe batch | không promote khi lỗi |
| U3-09 security | Localhost binding | 127.0.0.1 |
| U3-10 test | Smoke + unit | Dash callback, manifest, upsert |

## 3. Logical component đề xuất

- `DashboardApp` — tạo Dash app, layout, callback.
- `LayoutBuilder` — tabs, filter bar, KPI cards, charts.
- `Formatters` — BRL/ngày/số.
- `ErrorBoundary` — empty/error state.
- `PipelineCLI` — argparse, subcommands.
- `StageRunner` — gọi U1/U2, run summary.
- `MicroBatchProcessor` — quét inbox, manifest, upsert.
- `UpsertService` — natural key merge.
- `ReplayGenerator` — tạo batch lịch sử.
- `RunSummaryWriter` — JSON log/summary.

## 4. Câu hỏi cần trả lời

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Chế độ callback dashboard
Cách xử lý callback:

A) Server-side callback (khuyến nghị)
B) Client-side callback cho filter
C) Hybrid: filter client-side, chart server-side
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — Lưu trạng thái filter
Cách giữ filter khi chuyển tab:

A) `dcc.Store` trong bộ nhớ (khuyến nghị)
B) URL query params
C) Không lưu; reset mỗi lần chuyển tab
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — Transaction micro-batch
Cách đảm bảo batch lỗi không phá dữ liệu:

A) Copy cleaned sang temp, upsert/validate rồi promote (khuyến nghị)
B) Backup file cũ rồi ghi đè
C) Ghi trực tiếp, rollback bằng Git/backup thủ công
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Sinh batch replay
Cách tạo batch lịch sử:

A) Chia cleaned orders theo tháng, ghi orders/items/payments/reviews (khuyến nghị)
B) Sinh batch ngẫu nhiên từ cleaned
C) Không làm replay; chỉ micro-batch thủ công
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 5 — Hiển thị lỗi dashboard
Cách xử lý lỗi/empty:

A) Banner tiếng Việt + nút “Thử lại” (khuyến nghị)
B) Chỉ text lỗi
C) Modal popup
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 5. Checklist

- [x] Đọc NFR Requirements U3
- [x] Đề xuất pattern và logical component
- [x] Tạo kế hoạch và câu hỏi
- [x] Thu thập câu trả lời
- [x] Phân tích mơ hồ/mâu thuẫn
- [x] Tạo `nfr-design-patterns.md` + `logical-components.md`
- [x] Cập nhật state và trình bày phê duyệt
