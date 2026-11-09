# Business Rules — u1-thin-slice

```yaml
rules:
  - id: BR1.1
    statement: Mỗi đơn hàng phải có mã đơn duy nhất
    category: validation
    applies_to: DonHang
    trigger: khi nạp dữ liệu nguồn vào thực thể
    logic: IF hai bản ghi cùng ma_don THEN loại bản ghi lặp (giữ bản ghi đầu) và đếm vào số bản ghi hỏng
    violation: bản ghi lặp bị loại; lô vẫn nạp tiếp; số bản ghi bị loại được báo lại
    source: FR1.2
  - id: BR1.2
    statement: Đơn hàng phải có ngày đặt và trạng thái hợp lệ
    category: validation
    applies_to: DonHang
    trigger: khi nạp dữ liệu nguồn
    logic: >
      IF ngay_dat rỗng, không đọc được, hoặc ở tương lai so với thời điểm chạy
      THEN loại bản ghi và đếm vào số bản ghi hỏng.
      IF trang_thai không thuộc tám giá trị đã định THEN loại bản ghi và đếm.
    violation: bản ghi bị loại; không làm hỏng cả lô
    source: FR1.2
  - id: BR1.3
    statement: Mọi trường trung gian phải ánh xạ tới cột nguồn có thật trước khi nạp
    category: validation
    applies_to: DonHang và ánh xạ của nó
    trigger: khi nạp lược đồ, trước khi đọc dữ liệu
    logic: >
      IF một trường có ánh xạ mà cột nguồn không tồn tại trong bảng nguồn tương ứng
      THEN dừng và báo SchemaError nêu tên trường và tên cột.
      IF trường được đánh dấu "chưa nạp trong lát cắt" THEN bỏ qua khi nạp nhưng vẫn kiểm cột nguồn của nó.
    violation: SchemaError, dừng nạp
    source: FR1.2
  - id: BR1.4
    statement: Truy vấn đếm đơn phải nêu rõ trạng thái đang đếm
    category: policy
    applies_to: Truy vấn số đơn theo tháng
    trigger: khi chạy truy vấn
    logic: >
      IF truy vấn không nhóm theo trang_thai (hoặc không nêu trang_thai ở một mệnh đề lọc)
      THEN từ chối chạy. Truy vấn của lát cắt nhóm theo trang_thai, không lọc — vẫn đúng quy tắc.
    violation: trả lỗi nêu truy vấn thiếu điều kiện trạng thái
    source: FR2.1
  - id: BR1.5
    statement: Kết quả đếm phải tách theo từng cặp (tháng, trạng thái)
    category: calculation
    applies_to: Truy vấn số đơn theo tháng
    trigger: khi tính kết quả
    logic: IF nhiều trạng thái cùng xuất hiện trong một tháng THEN trả về một dòng cho mỗi cặp (tháng, trạng thái), không gộp ngầm
    violation: không có — quy tắc tính bắt buộc
    source: FR2.2
  - id: BR1.6
    statement: Truy vấn phải được viết lại thành câu chạy trên bảng nguồn trước khi thực thi
    category: policy
    applies_to: Truy vấn số đơn theo tháng
    trigger: khi chạy truy vấn
    logic: IF chưa có kế hoạch viết lại THEN từ chối thực thi
    violation: trả lỗi nêu truy vấn chưa được viết lại
    source: FR2.2
  - id: BR1.7
    statement: Vùng số liệu chỉ hiển thị 12 tháng gần nhất tính từ tháng mới nhất có dữ liệu, mỗi dòng là một cặp (tháng, trạng thái)
    category: calculation
    applies_to: Vùng số liệu của lát cắt trong tab Tích hợp
    trigger: khi dựng vùng số liệu
    logic: >
      IF có hơn 12 tháng dữ liệu THEN chỉ lấy 12 tháng gần nhất.
      IF có ít hơn THEN hiển thị đủ số tháng có và ghi rõ là thiếu tháng.
      Mỗi tháng hiện một dòng cho mỗi trạng thái có mặt (BR1.5) và một dòng tổng của tháng.
    violation: không có — quy tắc hiển thị
    source: FR5.2
  - id: BR1.8
    statement: Vùng số liệu của lát cắt trong tab phải phân biệt chưa chạy, rỗng, một phần và đầy đủ, và không hiển thị 0 thay cho dữ liệu thiếu
    category: policy
    applies_to: Vùng số liệu của lát cắt trong tab Tích hợp
    trigger: khi dựng vùng số liệu
    logic: >
      IF chưa chạy truy vấn lần nào THEN trạng thái chưa chạy kèm nút "Chạy truy vấn" (đường dữ liệu là DuckDB
      in-memory đọc `dataset/`, nên chạy pipeline không sinh ra số liệu cho vùng — xem TS-U1-2).
      IF truy vấn đã chạy nhưng không có dòng nào THEN trạng thái rỗng với câu riêng "Truy vấn chạy xong
      nhưng không có đơn nào", không hiện 0.
      IF có kết quả và cửa sổ 12 tháng thiếu tháng THEN trạng thái một phần, nêu tên tháng thiếu.
      IF có kết quả và đủ 12 tháng, mỗi tháng có ít nhất một dòng THEN trạng thái đầy đủ.
      Việc một tháng không có đủ tám trạng thái KHÔNG làm vùng thành "một phần": dữ liệu Olist không có
      tháng nào đủ tám trạng thái, nên quy tắc ấy sẽ khiến "đầy đủ" không bao giờ đạt.
      Không trạng thái nào hiển thị 0 cho phần thiếu.
    violation: không được hiện 0 cho dữ liệu thiếu
    source: FR5.5
```

## Tóm tắt quy tắc

| Mã | Loại | Nội dung ngắn |
|---|---|---|
| BR1.1 | Kiểm tra | Mã đơn duy nhất; bản lặp bị loại và đếm |
| BR1.2 | Kiểm tra | Ngày đặt và trạng thái hợp lệ |
| BR1.3 | Kiểm tra | Mọi ánh xạ phải trỏ tới cột nguồn có thật |
| BR1.4 | Chính sách | Truy vấn phải nêu trạng thái |
| BR1.5 | Tính toán | Tách kết quả theo cặp (tháng, trạng thái) |
| BR1.6 | Chính sách | Phải viết lại trước khi chạy |
| BR1.7 | Tính toán | Vùng số liệu chỉ lấy 12 tháng gần nhất; mỗi dòng là một cặp (tháng, trạng thái) |
| BR1.8 | Chính sách | Bốn trạng thái chưa chạy / rỗng / một phần / đầy đủ; "đầy đủ" chỉ đòi đủ 12 tháng có dữ liệu, không đòi đủ tám trạng thái mỗi tháng |
