<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-11-08 [unit u1-thin-slice] - Revision 2: NFR5.5 nghĩa là con số trên thẻ phải khớp một phép tính độc lập từ `dataset/`, sai lệch 0. Tôi viết phép tính đó bằng pandas thuần trong test, không import `src.integration`, để một lỗi trong bộ nạp hoặc truy vấn không thể tự che mình; test mang marker `slow` vì đọc dữ liệu thật.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-11-06T14:05:00Z [unit u1-thin-slice] — "Đầy đủ" trong bảng trạng thái của `functional-spec.md` được đọc cùng BR1.8: đủ 12 tháng **và** không thiếu trạng thái nào. Trên dữ liệu Olist hiện tại thẻ vì vậy luôn ở "Một phần" (cửa sổ 12 tháng không có đơn `approved`) — đó là trạng thái đúng, không phải lỗi; có test riêng chốt định nghĩa này.
- 2026-11-06T14:05:00Z [unit u1-thin-slice] — "kết quả lần trước" giữ ở cấp **tiến trình** thay vì `dcc.Store`, vì tab mới chỉ có một `Output` và giữ hình dạng dashboard ở 10 output là yêu cầu của NFR5.3.
- Cập nhật 2026-11-09: hình dạng đích là **4 tab, 8 callback, 4 thẻ + 1 vùng**.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-11-06T14:05:00Z [unit u1-thin-slice] — `src/integration/schema.py` phụ thuộc `src/ingest/schemas.py` (danh sách chín bảng nguồn), trái ghi chú "gói mới chỉ phụ thuộc `common`". Lý do: ADR-U1-S2 lớp 1 buộc danh sách bảng lấy từ nguồn sự thật duy nhất; chép lại chín tên sẽ vi phạm luật "một sự thật một chỗ".
- 2026-11-06T14:05:00Z [unit u1-thin-slice] — CI chạy `ruff check .` toàn repo nhưng `ruff format --check` trên phạm vi hẹp; 35 tệp cũ chưa qua `ruff format` và `team.md` cấm một lần format toàn repo lẫn vào thay đổi chức năng. Tài liệu `cicd-pipeline.md` đã được sửa cho khớp lệnh thật.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-11-06T14:20:00Z [unit u1-thin-slice] — ba vòng sửa sau review (R-01…R-08 rồi ba phát hiện mới) đều là sửa văn bản/nhãn và một chỗ cô lập lỗi ghi nhật ký; không mở lại thiết kế. Đổi lại, bản được review lần cuối không còn trùng khít bản trên đĩa — người duyệt cần biết điều này.
- 2026-11-06T14:20:00Z [unit u1-thin-slice] — thêm `assets/style.css` cho tab mới thay vì để thẻ không có CSS: NFR4.2/NFR4.3 (viền tiêu điểm 3:1, chữ 4,5:1) chỉ kiểm được khi có luật CSS thật.

## Open questions
- 2026-11-08 [unit u1-thin-slice] - `render_integration_card` đã bị tab "Tích hợp" của U6 thay khỏi cây giao diện, nên con số của lát cắt hiện không hiện ở đâu cho người xem. Cổng NFR5.5 vẫn đo đúng đường dữ liệu đó, nhưng cần người quyết ở Build and Test: nối lại thẻ vào tab U6, hay bỏ hẳn thẻ cũ và coi lát cắt là bằng chứng kỹ thuật.
- Đã quyết 2026-11-09: C9 có `result_region_ids: [don-theo-thang]`, U6 dựng vùng trong thân tab — số của lát cắt **hiện trên giao diện**.
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-11-06T14:20:00Z [unit u1-thin-slice] — tag `v0.1.0` đặt trên `main` sau merge (theo `cicd-pipeline.md` §3) hay trên nhánh làm việc trước khi merge? Cần người chốt ở mốc nộp.
- 2026-11-06T14:20:00Z [unit u1-thin-slice] — kiểm bằng mắt trên trình duyệt (bước 3 trong chuỗi xác nhận của `team.md`) chưa làm; cần người mở `python -X utf8 -m src.dashboard` và xem tab "Tích hợp".
