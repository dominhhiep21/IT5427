# NFR Requirements — u2-mediated-schema

Các ngưỡng phi chức năng của dự án đã chốt ở bước Requirements (NFR1–NFR6) và đã dùng cho U1, U4.
Dưới đây chỉ hỏi ba điểm còn mở ở mức đơn vị `u2-mediated-schema` (bộ nạp và kiểm lược đồ trung gian —
thư viện thuần, không sinh SQL, không hiển thị gì).

## Q1. [Kỹ thuật] Nạp và kiểm lược đồ phải xong trong bao lâu?

`u2-mediated-schema` chỉ đọc tệp YAML và **tiêu đề** của các tệp CSV nguồn, không đọc dữ liệu, nên nhanh
hơn nhiều so với một truy vấn. NFR1 chung là dưới 2 giây mỗi tương tác.

- A. Giữ ngưỡng chung 2 giây, không đặt ngưỡng riêng cho đơn vị này
- B. Đặt 500 ms cho một lần nạp + kiểm đầy đủ (chỉ đọc tiêu đề, không đọc dữ liệu)
- C. Không đặt ngưỡng đo được cho đơn vị này
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q2. [Vận hành] Bộ nạp có tự ghi nhật ký không?

Pipeline hiện ghi JSON Lines (`logs/<run_id>.jsonl`), mỗi sự kiện có `timestamp`, `level`, `run_id`,
`stage`, `event`. `u2-mediated-schema` là thư viện được U3/U5/U6 gọi trong cùng tiến trình, nên có hai
cách: tự ghi, hoặc trả kết quả để bên gọi ghi.

- A. Đơn vị này không tự ghi; bên gọi (pipeline hoặc tab) ghi sự kiện nạp lược đồ
- B. Đơn vị này tự ghi một sự kiện `schema_loaded` (số thực thể, số trường, thời lượng) sau mỗi lần nạp
- C. Tự ghi, và ghi thêm sự kiện lỗi `schema_error` khi ném `SchemaError` hoặc `ConfigurationError`
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q3. [Kỹ thuật] Thiếu tệp CSV nguồn thì ném lỗi gì?

Tệp khai báo lược đồ thiếu đã được chốt là `ConfigurationError`. Khác với trường hợp đó, một bảng nguồn
được khai trong lược đồ nhưng **không có tệp CSV** trong `dataset/` thì chưa được quy định — mà đơn vị
này phải mở tiêu đề tệp đó để kiểm cột.

- A. `ConfigurationError` — thiếu tệp dữ liệu là lỗi cấu hình/môi trường, giống trường hợp thiếu tệp lược đồ
- B. `SchemaError` — lược đồ trỏ tới một bảng không tồn tại, coi là lỗi khai báo
- C. Trả view ở trạng thái "một phần" (kênh `partial`) nêu bảng thiếu, giống cách xử lý thiếu thực thể
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A
