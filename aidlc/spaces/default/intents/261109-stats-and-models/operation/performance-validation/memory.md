<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-11-11T00:00:00Z — "load test" đọc là "đo lặp lại + dò quy mô", không phải kịch bản đồng thời: hệ thống một người dùng, một tiến trình, nên kịch bản đồng thời sẽ đo tranh chấp khoá DuckDB chứ không đo hệ thống.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-11-11T00:00:00Z — đo thủ công ba mốc từng bị `Deferred` (NFR1.2, NFR1.4, NFR1.6) thay vì thêm test canh; stage này đo và ghi lại, không sinh mã.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-11-11T00:00:00Z — chấp nhận bốn mốc "đạt nhưng không có test canh" để giữ stage trong phạm vi; ghi rõ khoảng trống trong ma trận thay vì đánh đạt cho xong.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-11-11T00:00:00Z — có thêm ba test mốc rộng cho `train_model`, `seasonal_decomposition`, `price_freight_correlation` trong đợt cải thiện đặc trưng không? Nếu không, bốn mốc này tiếp tục không được canh.
