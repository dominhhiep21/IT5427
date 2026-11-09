# Rough Mockups — Câu hỏi làm rõ

## Q1. [Sản phẩm] Tab "Tích hợp" nên tổ chức thế nào?

Đây là màn hình mới duy nhất của lần nâng cấp, nên cách tổ chức quyết định toàn bộ phần giao diện còn lại.

- A. Một trang cuộn dọc gồm bốn khối, mỗi nhóm chủ đề một khối
- B. Trong tab có bốn tab con, mỗi nhóm một tab con
- C. Một màn hình tổng quan bốn nhóm, bấm vào thì mở trang chi tiết
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Q2. [Sản phẩm] Luồng chính khi người xem mở tab này là gì?

Luồng chính quyết định thứ tự thông tin và điểm bấm đầu tiên trên màn hình.

- A. Chọn nhóm chủ đề, rồi xem kết quả của nhóm đó
- B. Chạy một truy vấn mẫu, rồi xem ánh xạ và kế hoạch viết lại của truy vấn đó
- C. Xem tổng quan trạng thái bốn nhóm trước, rồi đi sâu vào nhóm cần xem
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Q3. [Thiết kế] Có quy ước giao diện nào phải theo không?

Ảnh hưởng tới việc giữ hay đổi phong cách hiện có của dashboard.

- A. Giữ phong cách ba tab hiện có (Plotly Dash, nhãn tiếng Việt, cùng bảng màu)
- B. Làm mới hoàn toàn phong cách cho tab mới, không cần đồng bộ
- C. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A - Nhưng giao diện hiện tại vẫn xấu, có thể dùng thêm thư viện nào nữa không, có thể dùng https://ui.shadcn.com/

## Q4. [Thiết kế] Cần hỗ trợ kích thước màn hình nào?

Bối cảnh sử dụng chính là trình bày trước hội đồng trên máy chiếu hoặc laptop.

- A. Chỉ desktop/laptop (từ 1024px trở lên)
- B. Desktop và tablet
- C. Cả điện thoại
- D. Not applicable (không áp dụng)
- X. Other (please specify)

[Answer]: A

## Q5. [Thiết kế] Mức tiếp cận (accessibility) mong muốn?

Mức càng cao thì càng tốn thời gian ở giai đoạn Construction.

- A. Cơ bản: thao tác được bằng bàn phím, tương phản đủ đọc, không phụ thuộc màu
- B. Đầy đủ WCAG 2.1 AA (tiêu điểm rõ, nhãn ARIA, thứ tự tab hợp lý)
- C. Không đặt yêu cầu riêng
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q6. [Sản phẩm] Trên giao diện có hiển thị thuật ngữ lý thuyết không?

Ví dụ "GAV/LAV", "blocking", "query rewriting" — hữu ích cho việc chấm nhưng có thể làm rối người xem.

- A. Có, kèm một dòng giải thích ngắn bên cạnh
- B. Có, chỉ hiện thuật ngữ, không giải thích
- C. Không, dùng ngôn ngữ nghiệp vụ thuần
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q7. [Thiết kế] Dùng thư viện giao diện nào để làm giao diện bớt "xấu"?

Bạn hỏi có dùng được shadcn/ui không. shadcn/ui là bộ component React + Tailwind, không cắm thẳng vào app Plotly Dash (Python) được — muốn dùng phải dựng toolchain Node và đóng gói thành Dash component, vượt ràng buộc "không đổi công nghệ lớn" và quỹ 1–2 tuần. Hai lựa chọn dưới đây cài bằng pip, chạy local, vẫn là Dash.

- A. Giữ Dash thuần, chỉ chỉnh CSS và bố cục bằng tay
- B. Dash Mantine Components (`dmc`) — bộ component hiện đại gần phong cách shadcn, cài bằng pip
- C. dash-bootstrap-components (`dbc`) — Bootstrap có sẵn, quen thuộc, cài bằng pip
- D. Dùng shadcn/ui thật (cần React + Node + đóng gói component) — không khuyến nghị vì phá ràng buộc công nghệ
- X. Other (please specify)

[Answer]: B

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Tab "Tích hợp": một màn hình tổng quan bốn nhóm, bấm vào thì mở trang chi tiết.
- Luồng chính: xem tổng quan trạng thái bốn nhóm trước, rồi đi sâu vào nhóm cần xem.
- Phong cách: giữ phong cách hiện có (Dash, nhãn tiếng Việt), nâng cấp bằng Dash Mantine Components (dmc).
- Kích thước màn hình: chỉ desktop/laptop.
- Tiếp cận: đầy đủ WCAG 2.1 AA.
- Thuật ngữ: hiển thị thuật ngữ lý thuyết, không kèm giải thích.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
