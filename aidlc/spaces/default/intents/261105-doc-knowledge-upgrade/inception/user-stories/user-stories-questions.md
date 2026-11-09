# User Stories — Kế hoạch câu chuyện và câu hỏi

## Đánh giá: có cần user story không

**Có.** Lần nâng cấp có bề mặt người dùng mới (tab "Tích hợp" với bốn màn hình chi tiết) và các hành vi cần kiểm chứng bằng tiêu chí chấp nhận (chạy truy vấn, xem cặp ghép, xem bảng nguồn). Yêu cầu dạng `FR`/`NFR` đã đủ để thiết kế, nhưng câu chuyện giúp chốt hành vi từng màn hình và là đầu vào cho kiểm thử.

## Kế hoạch

- **Persona**: hai persona — người chấm (giảng viên/hội đồng) và người vận hành (chủ dự án). Chi tiết chờ câu trả lời Q1.
- **Định dạng**: `As a [persona], I want [goal], so that [benefit]`, mã `US{nhóm}.{số}`; tiêu chí chấp nhận `Given/When/Then`, mã `AC{nhóm}.{số}.{số}`.
- **Ưu tiên**: MoSCoW theo phạm vi đã chốt — bốn nhóm chủ đề và tab mới là Must; lớp ngữ nghĩa là Should.
- **Cách chia**: chờ câu trả lời Q3.
- **Độ chi tiết**: chờ câu trả lời Q2.
- **Truy vết**: mỗi `FR`/`NFR` phải trỏ tới ít nhất một câu chuyện trong `traceability.json`; yêu cầu không có câu chuyện sẽ ghi `GAP` hoặc `Deferred` kèm lý do.

## Q1. [Sản phẩm] Cần những persona nào?

Persona quyết định cách viết câu chuyện và mức chi tiết kỹ thuật được phơi ra.

- A. Chỉ một persona: người chấm (giảng viên/hội đồng)
- B. Hai persona: người chấm và người vận hành (chủ dự án)
- C. Ba persona: người chấm, người vận hành, và nhà phân tích dữ liệu tương lai
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q2. [Sản phẩm] Mỗi câu chuyện nên chi tiết tới đâu?

Mức chi tiết quyết định số câu chuyện và khối lượng tiêu chí chấp nhận phải viết.

- A. Vừa: mỗi nhóm chủ đề 2–3 câu chuyện, gộp các bước nhỏ (khoảng 12–15 câu chuyện)
- B. Mịn: mỗi yêu cầu chức năng một câu chuyện (khoảng 30 câu chuyện)
- C. Thô: chỉ câu chuyện cho lát cắt mảnh và tab mới (khoảng 6–8 câu chuyện)
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q3. [Kỹ thuật] Chia nhóm câu chuyện theo cách nào?

Cách chia quyết định thứ tự đọc tài liệu và cách gắn mã `US`.

- A. Theo nhóm chủ đề: lược đồ trung gian, viết lại truy vấn, ghép bản ghi, chọn nguồn, giao diện
- B. Theo persona: mọi câu chuyện của người chấm trước, của người vận hành sau
- C. Theo luồng người dùng: mở tab → xem tổng quan → đi sâu từng nhóm → quay lại
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Hai persona: người chấm (giảng viên/hội đồng) và người vận hành (chủ dự án).
- Độ chi tiết vừa: mỗi nhóm chủ đề 2–3 câu chuyện, gộp các bước nhỏ, khoảng 12–15 câu chuyện.
- Chia nhóm theo nhóm chủ đề: lược đồ trung gian, viết lại truy vấn, ghép bản ghi, chọn nguồn, giao diện.
- Ưu tiên MoSCoW theo phạm vi đã chốt: bốn nhóm và tab mới là Must, lớp ngữ nghĩa là Should.
- Mỗi `FR`/`NFR` phải trỏ tới ít nhất một câu chuyện, hoặc ghi `GAP`/`Deferred` kèm lý do.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
