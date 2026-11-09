# Contract Design — Câu hỏi làm rõ

## Q1. [Kỹ thuật] Các đơn vị trao đổi với nhau bằng cơ chế nào?

Hệ chạy một tiến trình duy nhất trên máy, nên có nhiều cách rẻ hơn REST.

- A. Gọi hàm Python trong cùng tiến trình, dữ liệu đi qua dataclass có kiểu
- B. REST nội bộ giữa các module (mỗi module một endpoint)
- C. Trao đổi qua tệp trung gian (JSON/Parquet) trong `data/`
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q2. [Kỹ thuật] Kết quả ghép bản ghi được bàn giao cho giao diện bằng cách nào?

Ghép toàn bộ khách hàng và người bán không thể chạy lại mỗi lần mở màn hình trong 2 giây.

- A. Ghi ra tệp trong `data/` ở tầng pipeline; giao diện đọc lại
- B. Tính lại mỗi lần mở màn hình
- C. Ghi vào bảng trong DuckDB, giao diện truy vấn
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q3. [Kỹ thuật] Chính sách thay đổi hợp đồng giữa các đơn vị?

Một người làm nên có thể nới, nhưng hợp đồng lỏng quá thì khó biết khi nào vỡ.

- A. Chỉ thêm trường; không đổi nghĩa hay xoá trường đang có
- B. Đổi thoải mái vì chỉ một người làm, miễn test xanh
- C. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q4. [Kỹ thuật] Khi một đơn vị lỗi ở biên, bên gọi xử lý thế nào?

Ảnh hưởng tới cách giao diện hiện trạng thái lỗi và cách test viết.

- A. Ném exception có kiểu rõ ràng; giao diện bắt và hiện trạng thái lỗi
- B. Trả giá trị mặc định (rỗng) và ghi log
- C. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q5. [Kỹ thuật] Chốt lại cơ chế trao đổi: REST nội bộ hay gọi hàm?

Câu 1 chọn "REST nội bộ giữa các module", nhưng ở bước Units Generation đã chốt "một khối duy nhất, chung một tiến trình", và thực hành của dự án là chạy một app dashboard cộng một lệnh pipeline. REST thật cần mỗi module một tiến trình HTTP riêng, thêm cổng và vòng đời tiến trình — điều này chưa có trong ràng buộc công nghệ.

- A. Gọi hàm Python trong cùng tiến trình, dữ liệu qua dataclass (giữ "một khối, một tiến trình")
- B. REST nội bộ thật: mỗi module một dịch vụ HTTP riêng, chấp nhận chạy nhiều tiến trình và quản lý cổng
- C. REST chỉ ở một chỗ: kết quả ghép bản ghi bàn giao qua endpoint đọc tệp; phần còn lại gọi hàm
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Cơ chế trao đổi: gọi hàm Python trong cùng tiến trình, dữ liệu qua dataclass — thay cho lựa chọn REST nội bộ ở câu 1, để giữ "một khối, một tiến trình".
- Kết quả ghép bản ghi: ghi ra tệp trong `data/` ở tầng pipeline, giao diện đọc lại.
- Chính sách hợp đồng: chỉ thêm trường; không đổi nghĩa hay xoá trường đang có.
- Lỗi ở biên: ném exception có kiểu rõ ràng; giao diện bắt và hiện trạng thái lỗi.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
