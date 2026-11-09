# Practices Discovery — Câu hỏi phỏng vấn

Năm phần thực hành được suy ra từ bằng chứng trong repo; dưới đây chỉ hỏi những điểm mà mã nguồn và git không xác lập được.

## Q1. [Kỹ thuật] Bạn viết test theo nhịp nào?

Hiện repo không có dấu vết cho biết test được viết trước hay sau khi code.

- A. Viết code trước, rồi viết test cho phần vừa viết (test-after, như hiện tại)
- B. Viết test trước rồi mới viết code (TDD)
- C. Viết kịch bản hành vi trước, code sau (BDD)
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q2. [Kỹ thuật] Bạn muốn làm việc trên nhánh nào?

Git hiện chỉ có một nhánh `feature/update-ui-ux` chưa phân kỳ khỏi `main`.

- A. Làm thẳng trên `main`
- B. Nhánh ngắn hạn cho mỗi đơn vị công việc rồi gộp lại
- C. Tiếp tục dùng nhánh `feature/update-ui-ux` hiện có
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Q3. [Kỹ thuật] Có đặt ngưỡng độ phủ test tối thiểu không?

Hiện chưa có ngưỡng nào và cũng không có CI chạy test.

- A. Không đặt ngưỡng
- B. Đặt 60%
- C. Đặt 80%
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Q4. [Kỹ thuật] Có thêm công cụ kiểm tra mã tự động không?

Hiện repo không có formatter, linter hay type-checker nào.

- A. Không, giữ như hiện tại
- B. Thêm `ruff` (lint + format)
- C. Thêm `ruff` và `mypy` (kiểm tra kiểu)
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q5. [Kỹ thuật] Mỗi module mới có bắt buộc phải có test riêng không?

Ảnh hưởng trực tiếp tới khối lượng việc khi thêm bốn nhóm chức năng mới.

- A. Có, mọi module mới đều phải có test
- B. Chỉ module có logic nghiệp vụ, không cần cho module chỉ nối dây
- C. Không bắt buộc
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q6. [Kỹ thuật] Có dựng một lát cắt chạy được xuyên suốt trước không? Walking skeleton là một bản tối thiểu chạy hết đường từ đầu đến cuối, dựng trước để chứng minh các mảnh khớp với nhau trước khi làm tính năng thật.

Với lần nâng cấp này, lát cắt đó sẽ là: một thực thể trong lược đồ trung gian → một truy vấn viết lại → một thẻ hiển thị trên tab mới.

- A. Có, dựng lát cắt xuyên suốt trước rồi mới làm rộng
- B. Không, làm từng nhóm chức năng trọn vẹn rồi mới ghép
- C. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q7. [Kỹ thuật] Lệnh nào dùng để xác nhận cả hệ thống chạy đúng?

Đây sẽ là lệnh kiểm tra cuối cùng sau mỗi đơn vị công việc.

- A. `pytest -m "not slow"` (bộ test nhanh)
- B. `python -m src.pipeline run --stage all` rồi mở dashboard
- C. Cả hai, chạy test nhanh trước rồi chạy pipeline và mở dashboard
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Nhịp viết test: TDD — viết test trước rồi mới viết code.
- Nhánh làm việc: tiếp tục dùng nhánh `feature/update-ui-ux` hiện có.
- Ngưỡng phủ test tối thiểu: 80%.
- Công cụ kiểm tra mã: thêm `ruff` (lint + format).
- Mọi module mới đều phải có test riêng.
- Có dựng lát cắt chạy được xuyên suốt trước, rồi mới làm rộng.
- Lệnh xác nhận cuối: `pytest -m "not slow"` trước, rồi `python -m src.pipeline run --stage all` và mở dashboard.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
