# Units Generation — Câu hỏi làm rõ

## Q1. [Kỹ thuật] Ranh giới đơn vị công việc chia theo cách nào?

Lưu ý: thực hành đã chốt là dựng lát cắt mỏng xuyên suốt trước (một thực thể → một truy vấn → một thẻ), nên đơn vị đầu tiên phải chạy được end-to-end.

- A. Theo lát cắt: đơn vị đầu là lát cắt mỏng xuyên suốt, các đơn vị sau theo từng nhóm chủ đề
- B. Theo component: mỗi component trong `components.md` là một đơn vị (khoảng 6 đơn vị)
- C. Gộp ba đơn vị lớn: (lược đồ + truy vấn), (ghép bản ghi + chọn nguồn), (giao diện + lớp ngữ nghĩa)
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q2. [Kỹ thuật] Muốn bao nhiêu đơn vị công việc?

Nhiều đơn vị hơn thì mỗi lần bàn giao nhỏ hơn nhưng tổng công sức phối hợp tăng.

- A. Thô: 3–4 đơn vị
- B. Vừa: 5–6 đơn vị
- C. Mịn: 8 đơn vị trở lên
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q3. [Kỹ thuật] Các đơn vị không phụ thuộc nhau có được làm song song không?

Đây là lựa chọn về cách xếp lịch, không phải về nội dung công việc.

- A. Có, cho phép làm song song các đơn vị độc lập
- B. Không, làm tuần tự từng đơn vị cho dễ theo dõi
- C. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q4. [Kỹ thuật] Mô hình triển khai của lần nâng cấp?

Hệ hiện tại chạy trên một máy, một lệnh pipeline và một app dashboard.

- A. Một khối duy nhất: mọi đơn vị nằm trong cùng repo, chạy chung một tiến trình dashboard + pipeline
- B. Tách thư viện và giao diện: các đơn vị logic là thư viện, chỉ giao diện là thứ chạy được
- C. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Ranh giới đơn vị: theo component, mỗi component một đơn vị.
- Số lượng: 5–6 đơn vị.
- Làm tuần tự, không chạy song song các đơn vị độc lập.
- Mô hình triển khai: một khối duy nhất trong cùng repo, chung một tiến trình.

Đề xuất kèm theo: sáu đơn vị, trong đó đơn vị đầu là lát cắt mỏng xuyên suốt (một thực thể → một truy vấn → một thẻ) để khớp thực hành đã chốt, năm đơn vị sau đi sâu từng phần.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct

