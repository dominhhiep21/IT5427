# Business Rules — u6-integration-ui

Nguồn: `functional-spec.md` (W1–W5, bản đồ màn hình), `frontend-components.md` (cây thành phần, năm trạng thái), `inception/requirements-analysis/requirements.md` (FR5.1–FR5.6, NFR1, NFR4), `inception/contract-design/contract-summary.md` (C1–C9).

Đơn vị `ui` không có thực thể nghiệp vụ riêng; các luật dưới đây là **nghĩa vụ hiển thị** mà giao diện phải giữ, mỗi luật kiểm được bằng test dashboard hoặc bằng rà giao diện.

```yaml
rules:
  - id: BR6.1
    statement: Tab mới có id cố định và không làm đổi ba tab cũ
    category: constraint
    applies_to: IntegrationTab
    trigger: khi dựng layout dashboard
    logic: >
      Tab mới dùng đúng tab_id "tich-hop" và nhãn "Tích hợp" theo C9. Ba tab cũ giữ nguyên
      nội dung, số liệu và số callback của chúng; tab mới có callback riêng với tên khác.
      Thân tab dựng **mọi** `result_region_ids` của C9 phía trên lưới thẻ và giữ chúng khi dựng
      lại thân tab; vùng không phải `card_id`.
    violation: test hình dạng dashboard đỏ
    source: FR5.1, FR5.6; C9

  - id: BR6.2
    statement: Tổng quan có đúng bốn thẻ, mỗi thẻ hai dòng số liệu và một điểm vào chi tiết
    category: constraint
    applies_to: CardGrid
    trigger: khi mở tab
    logic: >
      Bốn thẻ theo card_ids của C9. Mỗi thẻ có tiêu đề, trạng thái, đúng hai dòng số liệu và một
      nút vào màn hình chi tiết tương ứng. Không thẻ nào tự chạy truy vấn khi mở tab.
    violation: test dashboard đỏ
    source: FR5.2

  - id: BR6.3
    statement: Mỗi màn hình chi tiết có đường quay lại tổng quan và giữ trạng thái
    category: constraint
    applies_to: DetailScreen
    trigger: khi điều hướng
    logic: >
      Mọi màn hình chi tiết có nút "Quay lại tổng quan"; quay lại không tải lại dữ liệu và không
      đặt lại trạng thái đã có.
    violation: test điều hướng đỏ
    source: FR5.3

  - id: BR6.4
    statement: Mỗi màn hình hiển thị được năm trạng thái, không dùng số 0 thay dữ liệu thiếu
    category: policy
    applies_to: StateBlock
    trigger: khi dựng nội dung màn hình
    logic: >
      Năm trạng thái: rỗng, đang tải, lỗi, một phần, đủ. Trạng thái "một phần" hiển thị dữ liệu đã
      có, nêu phần thiếu và lý do bằng chữ; tuyệt đối không hiển thị số 0 cho dữ liệu thiếu.
    violation: rà giao diện + test trạng thái
    source: FR5.5

  - id: BR6.5
    statement: Không hiển thị traceback; mọi lỗi thành câu tiếng Việt kèm nút thử lại
    category: policy
    applies_to: StateBlock
    trigger: khi hợp đồng ném lỗi
    logic: >
      Bắt đủ bộ lỗi đã khai của C1–C7; dựng thông báo tiếng Việt nêu việc gì hỏng và nút thử lại.
      Không lộ thông điệp nội bộ hay traceback ra màn hình.
    violation: rà giao diện
    source: FR5.5

  - id: BR6.6
    statement: Kết quả cũ không được trình bày như kết quả mới
    category: policy
    applies_to: QueryPanel
    trigger: khi chạy lại một truy vấn
    logic: >
      Trong lúc chạy, vùng kết quả hiện khung tải và nút ở trạng thái chờ; kết quả lần trước (nếu
      còn) được ghi rõ "kết quả cũ". Lỗi khi chạy nêu tên truy vấn và lỗi, kèm nút thử lại.
    violation: test trạng thái truy vấn
    source: AC2.1.2, AC2.1.3

  - id: BR6.7
    statement: Hiển thị hai bản SQL, kế hoạch từng bước và SQL của lần chạy gần nhất
    category: constraint
    applies_to: QueryPanel
    trigger: khi có kết quả C4
    logic: >
      Vẽ song song truy vấn trung gian và SQL nguồn; mỗi bước kế hoạch nêu thực thể, bảng nguồn và
      điều kiện join; nút "Xem SQL nguồn" hiện SQL của lần chạy gần nhất mà không chạy lại.
    violation: test hiển thị đỏ
    source: FR2.2, FR2.3, FR2.4; AC2.2.1–AC2.2.3

  - id: BR6.8
    statement: Bảng nguồn và bảng ghép hiển thị đúng dữ kiện hợp đồng, lý do bằng chữ
    category: constraint
    applies_to: SourcePanel, LinkagePanel
    trigger: khi vẽ hai màn hình đó
    logic: >
      Bảng nguồn: nguồn, có dữ liệu hay không, chi phí, độ trễ, được chọn hay không, lý do; nguồn
      mô phỏng có ghi chú "nguồn mô phỏng"; không nguồn nào đủ trường thì nêu trường thiếu.
      Bảng ghép: số cặp vượt ngưỡng, số nhóm trùng, bảng cặp với điểm 2 chữ số và quyết định, và
      dòng "Bỏ qua" kèm lý do.
    violation: test hiển thị đỏ
    source: FR3.3, FR3.4, FR4.2; AC3.3.2, AC4.1.1, AC4.1.3, AC4.2.2

  - id: BR6.9
    statement: Tab mới đạt WCAG 2.1 AA và giữ ngân sách 2 giây mỗi tương tác
    category: policy
    applies_to: IntegrationTab
    trigger: khi tương tác
    logic: >
      Thao tác hoàn toàn bằng bàn phím, tiêu điểm thấy rõ, tương phản ≥ 4,5:1 cho chữ thường, không
      dùng màu làm tín hiệu duy nhất. Mỗi tương tác (đổi thẻ, đổi thực thể, chạy mẫu, đề xuất nguồn)
      trả kết quả dưới 2 giây trên máy local; thao tác chậm hiện trạng thái chờ thay vì treo.
    violation: rà tiếp cận + đo thời gian
    source: NFR1, NFR4

  - id: BR6.10
    statement: Màn hình lược đồ hiển thị danh sách thực thể, bảng ánh xạ ba cột và nhãn GAV
    category: constraint
    applies_to: SchemaPanel
    trigger: khi mở màn hình lược đồ
    logic: >
      Danh sách thực thể từ C6; bảng ánh xạ của thực thể đang chọn có ba cột: tên trường trung gian,
      nguồn dạng `<bảng>.<cột>`, kiểu dữ liệu. Nhãn `GAV` hiện trên bảng, không kèm đoạn giải thích
      dài. Chưa có dữ liệu thì trạng thái rỗng kèm câu giải thích; thiếu trường thì trạng thái một
      phần nêu tên thực thể thiếu.
    violation: test màn hình lược đồ đỏ
    source: FR1.3, FR1.4; AC1.1.1–AC1.2.2

  - id: BR6.11
    statement: Màn hình ghép bản ghi hiển thị ngưỡng, số liệu, bảng cặp và dòng "Bỏ qua"
    category: constraint
    applies_to: LinkagePanel
    trigger: khi mở màn hình ghép bản ghi
    logic: >
      Hiện ngưỡng 0,85, số cặp vượt ngưỡng, số nhóm trùng, tỉ lệ ghép đúng kèm mẫu số; bảng cặp với
      điểm 2 chữ số và quyết định Ghép/Xem lại; chuyển được giữa khách hàng và người bán. Dòng "Bỏ
      qua" luôn có mặt: có cặp thì liệt kê kèm lý do, không có thì ghi "Không có cặp bị bỏ qua".
      Người bán không có khoá mốc thì tỉ lệ đúng hiện "Không đo được" kèm lý do, không hiện 0.
      Tệp kết quả chưa có là trạng thái rỗng kèm hướng dẫn chạy pipeline, không phải lỗi.
    violation: test màn hình ghép đỏ
    source: FR3.2, FR3.3, FR3.4; AC3.1.2, AC3.2.3, AC3.3.2

  - id: BR6.13
    statement: Màu và chữ của tab theo bộ token shadcn/ui, đọc từ biến CSS, font tự lưu
    category: policy
    applies_to: IntegrationTab
    trigger: khi dựng và khi đổi giao diện
    logic: >
      Mọi màu của tab mới đọc từ biến CSS khai một lần trong `assets/style.css` theo bảng token
      shadcn/ui (nền, chữ, viền, chữ phụ, nút chính, bán kính 0,625rem), có cả bảng tối. Chữ dùng
      `Geist` tự lưu trong `assets/fonts/` và khai `@font-face`; không tải font qua mạng (NFR6).
      Không viết mã màu rời trong mã Python. Tương phản giữ mức NFR4 (≥ 4,5:1 cho chữ thường).
    violation: rà giao diện + rà mã: không có mã màu rời, không có URL font
    source: NFR4, NFR6; yêu cầu của người làm 2026-11-08

  - id: BR6.12
    statement: Màn hình truy vấn hiển thị danh sách định nghĩa KPI kèm định nghĩa doanh thu
    category: constraint
    applies_to: QueryPanel
    trigger: khi có kết quả C4
    logic: >
      Dưới bảng kết quả, hiển thị mỗi mục trong `kpi_definitions` với tên, công thức và
      `revenue_definition` (nêu rõ doanh thu = price + freight_value của đơn delivered). Đây là
      bề mặt giao diện của AC6.2.2 và là câu trả lời cho câu hỏi mở của C4 ("hiển thị hay chỉ dùng
      trong test"): hiển thị.
    violation: test hiển thị định nghĩa KPI đỏ
    source: FR6.1, FR6.2; AC6.2.1, AC6.2.2

```

## Tóm tắt luật

| Mã | Luật | Nguồn |
|---|---|---|
| BR6.1 | Tab mới id cố định, ba tab cũ không đổi | FR5.1, FR5.6, C9 |
| BR6.2 | Bốn thẻ, hai dòng số liệu, một điểm vào | FR5.2 |
| BR6.3 | Đường quay lại, giữ trạng thái | FR5.3 |
| BR6.4 | Năm trạng thái, không số 0 giả | FR5.5 |
| BR6.5 | Không traceback, lỗi bằng chữ | FR5.5 |
| BR6.6 | Kết quả cũ không giả làm mới | AC2.1.2, AC2.1.3 |
| BR6.7 | Hai bản SQL + kế hoạch + SQL gần nhất | FR2.2–FR2.4 |
| BR6.8 | Bảng nguồn và bảng ghép đúng hợp đồng | FR3.3, FR3.4, FR4.2 |
| BR6.9 | WCAG AA + dưới 2 giây | NFR1, NFR4 |
| BR6.10 | Lược đồ: ba cột ánh xạ + nhãn GAV | FR1.3, FR1.4 |
| BR6.11 | Ghép bản ghi: ngưỡng, số liệu, bảng cặp, dòng "Bỏ qua" | FR3.2–FR3.4 |
