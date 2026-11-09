<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-11-06T15:05:00Z [unit u4-record-linkage] — bản đầu của thiết kế ghép bản ghi chỉ dùng địa lý. Đo trên dữ liệu thật: 806.705 cặp ứng viên (chặn 5 chữ số), 805.778 cặp đạt 1,00, nhưng chỉ 3.631 cặp cùng `customer_unique_id` → tỉ lệ đúng 0,45% so với 84,2% mà màn hình D hứa.
- 2026-11-06T15:10:00Z [unit u4-record-linkage] — người làm chọn hướng "đổi tín hiệu ghép": thêm bằng chứng hành vi mua (Jaccard tập `product_id`) bên cạnh địa lý. Điểm mới = 0,40 × địa lý + 0,60 × mua, ngưỡng 0,85 giữ nguyên.
- 2026-11-06T15:10:00Z [unit u4-record-linkage] — `partial` của C5 **không** dùng cho việc cắt danh sách: nó có nghĩa "một đối tượng chưa có kết quả". Việc cắt được khai bằng `summary.pairs_total` + `summary.pairs_truncated`.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-11-06T15:10:00Z [unit u4-record-linkage] — vòng review thứ hai vẫn NOT-READY (2 phát hiện cũ còn mở + 6 phát hiện mới) và đã hết lượt review. Thay vì sửa tiếp trong im lặng, tôi hỏi người làm và họ chọn đổi tín hiệu ghép; thiết kế được viết lại theo hướng đó **sau** khi hết lượt review, nên bản trên đĩa mới hơn bản mà review đã đọc.
- 2026-11-06T15:10:00Z [unit u4-record-linkage] — chặn theo đủ 5 chữ số là hằng số trong mã, không phải tham số cấu hình: 3 chữ số cho 14,8 triệu cặp, 4 chữ số cho 2,55 triệu, đều không chạy được trên máy local.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-11-06T15:10:00Z [unit u4-record-linkage] — trọng số 0,60 cho hành vi mua, 0,40 cho địa lý: địa lý đã bị chặn theo mã bưu chính nên khả năng phân biệt còn lại thấp; đổi lại, cặp thiếu đơn hàng sẽ bị bỏ qua nhiều hơn.
- 2026-11-06T15:10:00Z [unit u4-record-linkage] — trần 10.000 cặp thay vì 50.000: mỗi cặp mang thêm ba chỉ số bằng chứng, nên tệp phình nhanh; con số đầy đủ vẫn nằm trong `summary`.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-11-06T15:10:00Z [unit u4-record-linkage] — **cần chốt ở cấp yêu cầu**: FR3, AC3.2.3 (con số 84,2%) và màn hình D trong mockups phải được sửa theo hướng mới; đơn vị này không tự sửa artifact inception.
- 2026-11-06T15:10:00Z [unit u4-record-linkage] — người bán không có khoá mốc: `correct_rate` trả null kèm lý do, AC3.2.3 vế người bán đánh dấu Deferred.
- 2026-11-06T15:10:00Z [unit u4-record-linkage] — giả thuyết A2 (tập sản phẩm phân biệt tốt hơn địa lý) **chưa được đo**; phải kiểm bằng số ở Build and Test trước khi tin con số tỉ lệ đúng.
- 2026-11-08T02:40:00Z [unit u5-source-selector] — người làm trả lời cả bảy câu đều chọn A. Hệ quả cần nhớ: ba nguồn (một nguồn mô phỏng thiếu danh mục sản phẩm), xếp hạng theo chi phí rồi độ trễ rồi tên, chọn đúng một nguồn, hồ sơ nằm trong tệp cấu hình tĩnh, cột khả năng đáp ứng là câu tiếng Việt.
- 2026-11-08T02:40:00Z [unit u5-source-selector] — **AC4.1.1 đánh `Deferred` sang `u6-integration-ui`, không đánh `OK`**: nó là tiêu chí hiển thị bảng nguồn, và R-02 của vòng review U2 vừa bắt đúng lỗi đánh `OK` cho yêu cầu giao diện. U5 chỉ cấp đủ năm dữ kiện qua C7.
