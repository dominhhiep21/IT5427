# Bolt Plan — Nâng cấp tích hợp dữ liệu Olist

Một **Bolt** là một lượt xây trọn vẹn trên một phần công việc, kết thúc bằng thứ chạy được. Sáu Bolt, mỗi Bolt một đơn vị công việc, theo thứ tự phụ thuộc. Bolt 1 là **lát cắt mỏng** — bản chạy xuyên suốt nhỏ nhất chứng minh các mảnh khớp nhau.

Tham chiếu: `unit-of-work.md`, `unit-of-work-dependency.md`, `contract-summary.md`, `requirements.md`, `stories.md`.

## Bolt 1 — `u1-thin-slice` (lát cắt mỏng)

| Trường | Nội dung |
|---|---|
| Đơn vị | U1 |
| Là lát cắt mỏng | Có |
| Định nghĩa hoàn thành | Một thực thể `don_hang` khai báo được; một truy vấn "số đơn delivered theo tháng" viết lại được và chạy trên nguồn; tab "Tích hợp" có một thẻ hiển thị số liệu đó; lệnh xác nhận của dự án xanh |
| Giả thuyết tự tin | Nếu lát cắt này chạy, thì ba mảnh (lược đồ → truy vấn → giao diện) khớp nhau thật, và mọi phần mở rộng sau chỉ là thêm chứ không phải sửa kiến trúc |
| Bản demo | Mở dashboard → tab "Tích hợp" → một thẻ có số đơn delivered theo tháng |
| Chứng minh phần nào của kiến trúc | Đường dây `MediatedSchema → QueryRewriter → IntegrationUI`, hợp đồng C1, C4, C8, C9 |

## Bolt 2 — `u2-mediated-schema`

| Trường | Nội dung |
|---|---|
| Đơn vị | U2 |
| Định nghĩa hoàn thành | Ba thực thể có ánh xạ đầy đủ; bộ nạp kiểm tra mọi cột nguồn tồn tại trong CSV thật; tệp khai báo mở rộng từ tệp U1 đã bàn giao |
| Giả thuyết tự tin | Nếu ánh xạ ba thực thể đều qua kiểm tra cột nguồn, thì phần mediation đã đủ nền cho hai truy vấn còn lại mà không phải sửa cấu trúc |
| Bản demo | Màn hình lược đồ trung gian hiện ba thực thể và bảng ánh xạ của từng thực thể |
| Ghi chú | Mở rộng C8, không đổi tên thực thể đã có |

## Bolt 3 — `u5-source-selector`

| Trường | Nội dung |
|---|---|
| Đơn vị | U5 |
| Định nghĩa hoàn thành | Hồ sơ nguồn cho bốn ứng viên; luật chọn nguồn cho một truy vấn; lý do chọn/loại bằng tiếng Việt; nguồn mô phỏng không gọi mạng |
| Giả thuyết tự tin | Nếu luật chọn nguồn cho kết quả hợp lý trên hai nguồn thật, thì tiêu chí "khả năng truy cập" đã đủ để trình bày mà không cần thêm nguồn |
| Bản demo | Màn hình chọn nguồn: bảng bốn nguồn, cột "Được chọn" và lý do |
| Ghi chú | Đứng trước Bolt 4 vì U3 cần nguồn đã chọn |

## Bolt 4 — `u3-query-rewriter`

| Trường | Nội dung |
|---|---|
| Đơn vị | U3 |
| Định nghĩa hoàn thành | Ba truy vấn mẫu có nhãn tiếng Việt; kế hoạch viết lại từng bước; SQL nguồn; kết quả khớp `src/analytics` sai lệch 0; định nghĩa KPI dùng chung và `src/analytics` đọc từ đó |
| Giả thuyết tự tin | Nếu ba truy vấn viết lại khớp đúng số liệu cũ, thì cơ chế mediation không làm đổi ngữ nghĩa — đây là bằng chứng mạnh nhất cho phần lý thuyết được chấm |
| Bản demo | Chọn một truy vấn → xem hai khối mã, kế hoạch, bảng kết quả, và số đối chiếu KPI |
| Ghi chú | Bolt rủi ro nhất về mặt kỹ thuật; đứng sau U5 để có nguồn |

## Bolt 5 — `u4-record-linkage`

| Trường | Nội dung |
|---|---|
| Đơn vị | U4 |
| Định nghĩa hoàn thành | Ghép khách hàng và người bán; ngưỡng 0,85; cặp Ghép/Xem lại; cặp bị bỏ qua kèm lý do; tỉ lệ ghép đúng so với `customer_unique_id`/`seller_id`; kết quả ghi tệp ở tầng pipeline |
| Giả thuyết tự tin | Nếu kết quả ghép trên dữ liệu thật có tỉ lệ đúng hợp lý ở ngưỡng 0,85, thì thuật toán đủ tốt để trình bày; nếu không, cần đổi khoá chặn hoặc trường so khớp |
| Bản demo | Màn hình ghép bản ghi: số liệu tóm tắt, bảng cặp, dòng "Bỏ qua" |
| Ghi chú | Độc lập với U2–U3, nên có thể làm sớm nếu Bolt 4 bị kẹt |

## Bolt 6 — `u6-integration-ui`

| Trường | Nội dung |
|---|---|
| Đơn vị | U6 |
| Định nghĩa hoàn thành | Tab "Tích hợp" đủ bốn thẻ và bốn màn hình chi tiết; bốn trạng thái; WCAG 2.1 AA; ba tab cũ không đổi; test hình dạng dashboard cập nhật |
| Giả thuyết tự tin | Nếu một người chấm mở tab và đi hết bốn nhóm trong vài phút mà không cần giải thích, thì giao diện đã đạt mục tiêu "thấy được lý thuyết đang chạy" |
| Bản demo | Toàn bộ tab, đi từ tổng quan vào từng nhóm và quay lại |
| Ghi chú | Chốt sau cùng vì cần dữ liệu từ cả năm đơn vị |

## Điều kiện dừng

- Hết 1–2 tuần trước khi xong Bolt 5: giữ Bolt 1–4, ghi rõ Bolt 5–6 còn lại.
- Bolt 4 không khớp số liệu sau khi đã thử hai lần: dừng, xem lại lược đồ trung gian thay vì tiếp tục Bolt 5–6.
