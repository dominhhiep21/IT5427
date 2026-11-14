<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-11-11T00:00:00Z — "drift" đọc là trôi tài liệu-vs-cấu-hình và trôi dữ liệu-sinh-ra, không phải AWS Config: dự án không có bản khai báo hạ tầng nào để so.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-11-11T00:00:00Z — không có báo cáo tuân thủ SLO vì không tồn tại SLO; thay bằng bảng mốc nghiệm thu so với thực đo, giữ nguyên chỗ đứng của AUC 0,5133.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-11-11T00:00:00Z — từ chối cả bốn đề xuất tối ưu CI dù đo được ~60 s tiết kiệm khả dĩ, vì ba trong bốn đổi một chốt đúng lấy vài giây.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-11-11T00:00:00Z — khung dự đoán "lúc đặt hàng" có phải khung đúng? Chuyển sang "lúc bàn giao cho đơn vị vận chuyển" sẽ nâng AUC nhưng làm cảnh báo muộn hơn; phải trả lời ở Ideation trước khi viết đặc trưng.
