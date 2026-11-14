<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs

- 2026-11-10T06:37:00Z — chọn `skipped` là danh sách cặp `{test, reason}` thay vì dict khoá theo tên kiểm định; danh sách giữ được thứ tự phát hiện và không cần ràng buộc "mỗi khoá một lần", đổi lại bên đọc phải tự lọc theo `test` nếu cần tra cứu nhanh.
- 2026-11-10T06:37:00Z — đặt `excluded` trong từng `ComparisonResult` thay vì một danh sách bang bị loại ở cấp khối; con số đi kèm đúng phép so sánh mà nó giải thích, nhưng nhiều phép so sánh trong cùng báo cáo sẽ lặp lại cùng một giá trị nếu tập bang bị loại không đổi.
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions

- 2026-11-10T06:37:00Z — `ModelBlock` (C3) và các trường `dict` trong `StatsBlock` (C1) chưa chốt danh sách khoá; người kiểm nêu hai điểm này ở mức Major và chúng nên được chốt ở Functional Design của U2, trước khi U2 ghi khối mô hình, vì thêm trường bắt buộc sau đó sẽ buộc tăng `REPORT_VERSION` lần nữa.
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
