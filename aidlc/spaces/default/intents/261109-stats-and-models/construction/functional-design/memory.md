<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs

- 2026-11-10T07:12:44Z — [unit u1-statistics] giữ bốn tháng thưa cuối 2016 trên trục mùa vụ thay vì loại bỏ; loại chúng chỉ còn 22 tháng, dưới sàn một chu kỳ 12, và như vậy là mất hẳn nhóm kiểm định thứ năm mà US1.1 đòi. Cái giá là bốn tháng gần rỗng vẫn nằm trong chuỗi, nên chúng tôi để nguyên cột `observed` cho người đọc thấy thay vì làm mượt đi.
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions

- 2026-11-10T07:12:44Z — [unit u1-statistics] người kiểm chấp nhận thiết kế này nhưng còn hai điểm chưa đóng, cả hai đều là chỗ dễ vấp khi viết mã: (a) `AtomicWriter` hiện tại thay tệp ngay chứ không đọc lại, nên BR1.11 mô tả một trình tự mà lớp ghi sẵn có không làm — Code Generation phải hoặc bọc thêm bước kiểm, hoặc sửa lại quy tắc cho khớp mã thật; (b) quy tắc làm tròn 4 chữ số áp lên mọi trường số thực sẽ phá hằng đẳng thức `observed = trend + seasonal + residual`, nên phải chốt làm tròn ở mức hiển thị chứ không ở mức lưu.
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
