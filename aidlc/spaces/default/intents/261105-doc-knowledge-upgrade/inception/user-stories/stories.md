# User Stories — Nâng cấp tích hợp dữ liệu Olist

Định dạng: `As a [persona], I want [goal], so that [benefit]`. Ưu tiên theo MoSCoW. Mã câu chuyện `US{nhóm}.{số}`, mã tiêu chí `AC{nhóm}.{số}.{số}`.

## Nhóm 1 — Lược đồ trung gian

### US1.1 — Xem ánh xạ của một thực thể (Must)

As P1 (người chấm), I want chọn một thực thể trong lược đồ trung gian và xem bảng ánh xạ của nó, so that tôi thấy dữ liệu nguồn được đưa về một lược đồ chung như thế nào.

- **AC1.1.1**: Given tab "Tích hợp" đang mở ở màn hình lược đồ trung gian, When chọn thực thể `don_hang`, Then bảng bên phải hiện mọi trường trung gian của thực thể đó kèm nguồn và kiểu.
- **AC1.1.2**: Given bảng đang hiện `don_hang`, When chọn `mat_hang` hoặc `san_pham`, Then bảng cập nhật sang trường của thực thể đó mà không tải lại trang, và trình đọc màn hình đọc lên số dòng mới.
- **AC1.1.3**: Given thực thể không có ánh xạ nào, When chọn nó, Then màn hình hiện trạng thái rỗng kèm lý do, không hiện bảng trắng.

### US1.2 — Thấy dạng ánh xạ đang dùng (Must)

As P1, I want thấy ký hiệu dạng ánh xạ (`GAV`) ngay trên màn hình ánh xạ, so that tôi đối chiếu được với bài giảng mà không phải mở tài liệu kèm theo.

- **AC1.2.1**: Given màn hình ánh xạ đang mở, When nhìn vào phần đầu bảng, Then thấy nhãn `GAV` cùng một dòng ngắn nêu nó áp cho thực thể nào.
- **AC1.2.2**: Given một trường có ánh xạ, When xem dòng đó, Then nguồn được ghi đúng dạng `<bảng nguồn>.<cột nguồn>`.

### US1.3 — Kiểm tra ánh xạ khớp dữ liệu thật (Must)

As P2 (người vận hành), I want đối chiếu ánh xạ với cột thật trong CSV nguồn, so that tôi phát hiện sớm tên cột sai trước khi nó lan xuống truy vấn.

- **AC1.3.1**: Given lược đồ trung gian đã khai, When chạy bộ test nhanh `python -X utf8 -m pytest -m "not slow"`, Then mọi cột nguồn được nêu trong ánh xạ đều tồn tại trong tệp CSV tương ứng.
- **AC1.3.2**: Given một ánh xạ trỏ tới cột không tồn tại, When chạy cùng bộ test đó, Then ít nhất một kiểm thử thất bại nêu rõ tên trường và tên cột sai.

## Nhóm 2 — Viết lại truy vấn

### US2.1 — Chạy một truy vấn mẫu (Must)

As P1, I want chọn một trong ba truy vấn mẫu và chạy nó, so that tôi thấy hệ thống trả lời được câu hỏi nghiệp vụ qua lược đồ trung gian.

- **AC2.1.1**: Given màn hình viết lại truy vấn đang mở, When chọn "Doanh thu theo danh mục" và bấm Chạy, Then màn hình hiện kết quả kèm thời gian chạy và số dòng.
- **AC2.1.2**: Given một truy vấn đang chạy, When chưa có kết quả, Then nút Chạy ở trạng thái chờ và vùng kết quả hiện khung tải, không hiện kết quả cũ như mới.
- **AC2.1.3**: Given truy vấn chạy lỗi, When lỗi xảy ra, Then thông báo nêu tên truy vấn và lỗi, cùng nút thử lại; kết quả lần trước được ghi rõ là kết quả cũ.

### US2.2 — Xem kế hoạch viết lại từng bước (Must)

As P1, I want thấy truy vấn trên lược đồ trung gian và bản viết lại xuống nguồn cạnh nhau, so that tôi kiểm chứng được cơ chế viết lại truy vấn thay vì chỉ tin vào kết quả.

- **AC2.2.1**: Given một truy vấn mẫu đã chạy, When xem kết quả, Then hai khối mã hiện song song: truy vấn trung gian và kế hoạch viết lại.
- **AC2.2.2**: Given kế hoạch viết lại, When đọc nó, Then mỗi bước nêu thực thể trung gian, bảng nguồn tương ứng và điều kiện join.
- **AC2.2.3**: Given một kết quả đã có, When bấm "Xem SQL nguồn", Then hiện câu SQL thực thi trên nguồn của lần chạy đó.

### US2.3 — Đối chiếu kết quả với KPI hiện có (Must)

As P2, I want so kết quả viết lại với số liệu `src/analytics` đang trả, so that tôi biết phần viết lại không làm đổi ngữ nghĩa.

- **AC2.3.1**: Given cả ba truy vấn mẫu đã chạy, When so với số liệu hiện có, Then số dòng và giá trị tiền tệ khớp chính xác (sai lệch 0).
- **AC2.3.2**: Given một truy vấn trả lệch so với số liệu hiện có, When chạy bộ test nhanh `python -X utf8 -m pytest -m "not slow"`, Then có kiểm thử thất bại nêu truy vấn nào lệch và lệch bao nhiêu.

## Nhóm 3 — Ghép bản ghi

### US3.1 — Xem quy mô ghép (Must)

As P1, I want thấy số cặp vượt ngưỡng và số nhóm trùng cho cả khách hàng và người bán, so that tôi đánh giá được kết quả ghép có hợp lý với dữ liệu thật.

- **AC3.1.1**: Given màn hình ghép bản ghi đang mở, When mở lần đầu, Then thấy số cặp vượt ngưỡng, số nhóm trùng và ngưỡng đang dùng (0.85).
- **AC3.1.2**: Given người xem đổi giữa khách hàng và người bán, When chọn đối tượng kia, Then số liệu tóm tắt và bảng cặp đổi theo.

### US3.2 — Xem cặp tiêu biểu (Must)

As P1, I want xem bảng cặp bản ghi tiêu biểu với điểm số và quyết định Ghép/Xem lại, so that tôi thấy thuật toán ghép làm việc trên dữ liệu thật chứ không phải minh hoạ giả.

- **AC3.2.1**: Given bảng cặp đang hiện, When đọc một dòng, Then thấy bản ghi A, bản ghi B, điểm 2 chữ số thập phân, và quyết định kèm biểu tượng.
- **AC3.2.2**: Given một cặp có điểm đúng bằng ngưỡng, When xem dòng đó, Then quyết định là `Xem lại` chứ không phải `Ghép`.
- **AC3.2.3**: Given trường hợp ghép khách hàng, When đối chiếu với `customer_unique_id`, Then tỷ lệ cặp ghép đúng được tính theo công thức "số cặp ghép có cùng `customer_unique_id` / tổng số cặp đã ghép ở ngưỡng 0.85" và hiển thị kèm mẫu số. Với người bán, mốc đúng là `seller_id` và cùng công thức đó.

### US3.3 — Biết cặp nào không chấm được (Must)

As P2, I want thấy rõ cặp nào không tính được điểm vì thiếu trường, so that tôi không tưởng nhầm là thuật toán đã xét hết.

- **AC3.3.1**: Given một bản ghi thiếu trường so khớp, When màn hình tổng hợp kết quả, Then có dòng nêu số cặp bị bỏ qua và lý do thiếu trường nào.
- **AC3.3.2**: Given không cặp nào bị bỏ qua, When xem màn hình, Then dòng đó ghi "không có" thay vì ẩn đi.

## Nhóm 4 — Chọn nguồn dữ liệu

### US4.1 — Xem bảng nguồn ứng viên (Must)

As P1, I want xem mọi nguồn ứng viên với khả năng đáp ứng, chi phí và độ trễ ước tính, so that tôi thấy tiêu chí chọn nguồn là tường minh chứ không phải mặc định.

- **AC4.1.1**: Given màn hình chọn nguồn đang mở, When xem bảng, Then mỗi dòng có tên nguồn, có dữ liệu hay không, chi phí, độ trễ, và trạng thái được chọn.
- **AC4.1.2**: Given một nguồn bị loại, When xem dòng đó, Then lý do loại được ghi bằng chữ, không chỉ bằng màu.
- **AC4.1.3**: Given bảng có nguồn mô phỏng, When xem màn hình, Then có ghi chú rằng nguồn đó chỉ là ứng viên mô phỏng và không gọi mạng.

### US4.2 — Đề xuất nguồn cho một truy vấn (Must)

As P2, I want chọn một truy vấn rồi bấm đề xuất nguồn, so that tôi kiểm tra được luật chọn nguồn cho đúng truy vấn đó.

- **AC4.2.1**: Given đã chọn một truy vấn, When bấm "Đề xuất nguồn", Then cột "Được chọn" cập nhật và kết quả được đọc lên bằng trình đọc màn hình.
- **AC4.2.2**: Given không nguồn nào đủ trường cho truy vấn, When bấm đề xuất, Then hiện thông báo nêu trường còn thiếu và không chọn nguồn nào.

## Nhóm 5 — Giao diện

### US5.1 — Mở tab và thấy bốn nhóm (Must)

As P1, I want mở tab "Tích hợp" và thấy trạng thái của cả bốn nhóm trong một màn hình, so that tôi nắm được toàn cảnh trước khi đi sâu.

- **AC5.1.1**: Given dashboard đang mở, When chọn tab "Tích hợp", Then hiện bốn thẻ, mỗi thẻ có tên nhóm, trạng thái, hai dòng số liệu và một điểm vào chi tiết.
- **AC5.1.2**: Given một nhóm hiển thị được một phần dữ liệu của mình (ví dụ có bảng ánh xạ nhưng chưa có bảng cặp ghép), When xem thẻ của nhóm đó, Then thẻ ghi trạng thái "một phần" kèm tên phần còn thiếu, ba thẻ còn lại vẫn hiển thị bình thường.
- **AC5.1.3**: Given ba tab báo cáo cũ, When chuyển sang chúng, Then số liệu và hành vi không đổi so với trước đợt nâng cấp.

### US5.2 — Đi vào chi tiết và quay lại (Must)

As P1, I want mở chi tiết một nhóm rồi quay lại tổng quan mà không mất ngữ cảnh, so that tôi xem lần lượt bốn nhóm trong một buổi trình bày.

- **AC5.2.1**: Given đang ở tổng quan, When mở thẻ "Ghép bản ghi", Then hiện màn hình chi tiết của nhóm đó.
- **AC5.2.2**: Given đang ở màn hình chi tiết, When chọn đường quay lại, Then trở về tổng quan với trạng thái như trước khi rời.
- **AC5.2.3**: Given người dùng chỉ dùng bàn phím, When đi qua lại giữa tổng quan và chi tiết, Then mọi bước đều thực hiện được, tiêu điểm luôn hiện rõ với tương phản tối thiểu 3:1 so với nền.
- **AC5.2.4**: Given mọi trạng thái hiển thị trên tab mới, When kiểm tra tương phản và tín hiệu, Then chữ thường đạt tối thiểu 4.5:1 và không trạng thái nào chỉ dùng màu để truyền đạt.

### US5.3 — Thấy trạng thái lỗi rõ ràng (Must)

As P1, I want mỗi màn hình nói rõ khi rỗng, đang tải, lỗi hay thiếu một phần, so that tôi không nhầm dữ liệu thiếu là số 0.

- **AC5.3.1**: Given một nhóm chưa có dữ liệu, When mở chi tiết nhóm đó, Then màn hình hiện trạng thái rỗng kèm hướng dẫn chạy `python -X utf8 -m src.pipeline run --stage all` trong terminal (dashboard phải đóng trước khi chạy integrate), không đặt nút chạy pipeline ngay trong dashboard.
- **AC5.3.2**: Given một lỗi khi tải dữ liệu, When màn hình hiện lỗi, Then có câu nêu việc gì hỏng, biểu tượng cảnh báo, và nút thử lại; không hiện mã lỗi thô.
- **AC5.3.3**: Given dữ liệu thiếu, When xem ô số liệu, Then hiện "không có" chứ không hiện 0.

## Phụ thuộc và lát cắt mỏng đầu tiên

- **US1.1 → US2.1 → US5.1**: chuỗi tối thiểu để tab mới hiển thị được dữ liệu thật; đây chính là **lát cắt mỏng** đã chốt trong `team-practices.md` (một thực thể → một truy vấn viết lại → một thẻ trên tab).
- **US1.3** phụ thuộc US1.1 (cần ánh xạ tồn tại trước khi đối chiếu với CSV).
- **US2.2, US2.3** phụ thuộc US2.1; **US2.3** cũng phụ thuộc US6.1 (cùng cơ chế so KPI).
- **US3.1, US3.2, US3.3** độc lập với nhóm 2 nhưng cần dữ liệu khách/người bán từ nguồn.
- **US4.1** độc lập; **US4.2** phụ thuộc US4.1 và US2.1 (cần truy vấn đã chọn).
- **US5.2, US5.3** phụ thuộc US5.1.
- **US6.1** là điều kiện đóng của mọi câu chuyện khác, không phải câu chuyện làm trước.
- **US6.2** là Should, làm sau khi các Must xanh.

## Nhóm 6 — Không hồi quy và lớp ngữ nghĩa

### US6.1 — Chạy bộ xác nhận và thấy KPI không đổi (Must)

As P2, I want chạy chuỗi xác nhận của dự án và thấy KPI cùng số dòng không đổi, so that tôi biết đợt nâng cấp không làm hỏng hệ thống đang chạy.

- **AC6.1.1**: Given mã mới đã thêm, When chạy `pytest -m "not slow"`, Then bộ nhanh xanh.
- **AC6.1.2**: Given pipeline chạy xong, When so 5 KPI và số dòng 11 view, Then khớp chính xác baseline.
- **AC6.1.3**: Given thay đổi chạm dashboard, When chạy bộ test, Then các test khẳng định hình dạng dashboard được cập nhật cùng thay đổi và xanh.

### US6.2 — Một định nghĩa KPI dùng chung (Should)

As P2, I want định nghĩa KPI nằm một chỗ và được cả dashboard lẫn lớp truy vấn dùng, so that số liệu không lệch giữa các màn hình.

- **AC6.2.1**: Given một KPI đã định nghĩa, When dashboard và lớp truy vấn cùng tính nó, Then hai kết quả khớp nhau.
- **AC6.2.2**: Given thêm KPI mới, When xem tài liệu đi kèm, Then định nghĩa doanh thu đang dùng được nêu rõ.
