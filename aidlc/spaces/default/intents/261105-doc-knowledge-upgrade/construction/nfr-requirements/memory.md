<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-11-07T08:20:25Z [unit u2-mediated-schema] Ba câu hỏi mở đã được trả lời hết, không có mâu thuẫn: Q1 = A (giữ ngưỡng NFR1 2 giây, không đặt ngưỡng riêng cho đơn vị), Q2 = A (đơn vị không tự ghi nhật ký; bên gọi ghi), Q3 = A (thiếu tệp CSV nguồn là ConfigurationError, không phải SchemaError).
- 2026-11-07T08:20:25Z [unit u2-mediated-schema] Lệch giữa mã U1 đang có và functional-spec, ghi lại cho bước sinh mã: (1) load_schema trong src/integration/schema.py chưa kiểm tiêu đề các tệp CSV nguồn như Workflow 1 bước 4; (2) cờ loaded đang bị đòi bắt buộc là bool trong khi đặc tả nói mặc định true khi vắng mặt; (3) chưa có kênh partial cho thực thể thiếu. Cả ba đã thành TS-U2-3, TS-U2-7, TS-U2-4 trong tech-stack-decisions.md.
- 2026-11-07T08:20:25Z [unit u2-mediated-schema] Đơn vị kiểu library nên engine chỉ yêu cầu security-requirements, tech-stack-decisions và traceability; các chỉ tiêu NFR1/2/3/5/6 được chốt trong tech-stack-decisions.md §3 thay vì tệp performance/reliability/observability riêng, và NFR4 ghi N/A vì đơn vị không hiển thị gì.
