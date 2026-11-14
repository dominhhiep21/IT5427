# Construction → Operation — Phase Check

Ngày: 2026-11-13. Phạm vi: intent `261111-model-feature-improvemen` (scope `feature`).

## 1. Đơn vị đã dựng và đã kiểm

| Đơn vị | Code Generation | Checkpoint | Bằng chứng |
|---|---|---|---|
| `u1-mart-and-baseline` | hoàn tất | **verified + approved** | 559 test, phủ 92,48% |
| `u2-features-and-models` | hoàn tất, 2 vòng soát | **verified + approved** | 637 test, phủ 92,57% |
| `u3-prediction-ui` | hoàn tất, 1 vòng soát | **verified + approved** | 723 test, phủ 92,71% |

## 2. Traceability

| Tệp | Sensor | Kết quả |
|---|---|---|
| `construction/u1-mart-and-baseline/code-generation/traceability.json` | `sensor-traceability` | pass — 0 gap, 0 orphan |
| `construction/u2-features-and-models/code-generation/traceability.json` | `sensor-traceability` | pass — 43 dòng phủ, 0 gap |
| `construction/u3-prediction-ui/code-generation/traceability.json` | `sensor-traceability` | pass — 29 AC + 6 NFR, 0 gap |
| `construction/build-and-test/cross-unit-traceability.md` | đọc tay | mọi AC/NFR có đơn vị nhận; AC2.5.3 là `N/A` có lý do (deviation D-1) |

## 3. Phát hiện chưa đóng

| Nguồn | Finding | Trạng thái |
|---|---|---|
| Vòng soát Code Generation U2 | 0 Critical, 0 Major còn mở (đã đóng ở vòng 2) | đóng |
| Vòng soát Code Generation U3 | 0 Critical; 1 Major (nhãn 8/14) **đã sửa** + test; 7 Minor còn mở, không chặn | Minor mở, có ghi |
| Functional/NFR/Infra của U3 | các Major đã sửa; Minor còn mở trong `reviews/` | Minor mở, có ghi |

Không có finding mức Critical hoặc Major nào chưa đóng.

## 4. Cổng CI có cưỡng chế đúng lệnh của Build and Test?

| Lệnh Build and Test ghi | Cổng CI tương ứng | Khớp |
|---|---|---|
| `ruff check .` | bước 4 | ✓ |
| `ruff format --check` (50 mục) | bước 5 | ✓ |
| `run --stage all` | bước 6 | ✓ |
| `run --stage stats` | bước 7 | ✓ |
| `pytest -m "not slow"` | bước 8 | ✓ |
| `pytest --cov=src --cov-fail-under=80` | bước 9 | ✓ |
| smoke `integration-sources.yaml` | bước 10 | ✓ |
| `beats_floor` trên báo cáo thật | nằm trong bộ `slow` của bước 9 | ✓ |

## 5. Kết luận

**PASS.** Ba đơn vị đã dựng, đã kiểm, đã duyệt; không còn finding Critical/Major; traceability của cả ba đơn vị và bảng chéo đều không có GAP ngoài một `N/A` có lý do; tám cổng CI cưỡng chế đúng các lệnh mà Build and Test đã ghi.

Điều kiện chuyển sang Operation: **đạt**, với hai nghĩa vụ còn treo thuộc về intent (không phải của CI): ghi ngoại lệ mốc sàn vào `project.md` `## Corrections`, và cập nhật `team.md` (ngân sách 300/240; danh sách format 50 mục) — cả hai qua nghi thức learnings trước khi đóng intent.
