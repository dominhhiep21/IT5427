# Domain Design — Câu hỏi làm rõ

## Q1. [Kỹ thuật] Bốn nhóm chủ đề nên là bốn component riêng hay một khối?

Đây là quyết định ranh giới lớn nhất của bước này: nó quyết định số thư mục, số file và cách kiểm thử.

- A. Bốn component độc lập trong một package mới (ví dụ `src/integration/`), mỗi nhóm một thư mục
- B. Một component `Integration` duy nhất, bên trong chia bốn module con
- C. Mỗi nhóm nằm rải ở package sẵn có gần nhất (lược đồ → `ingest`, truy vấn → `analytics`, ghép → `clean`, chọn nguồn → `pipeline`)
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q2. [Kỹ thuật] Lược đồ trung gian được khai báo bằng gì?

Ảnh hưởng tới cách kiểm tra ánh xạ và cách người chấm đọc được nó.

- A. Tệp khai báo dữ liệu (YAML/JSON) đọc lúc chạy, tách khỏi mã
- B. Khai báo bằng mã Python (dataclass/hằng số), có kiểu
- C. Bảng trong DuckDB, truy vấn được như dữ liệu
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q3. [Kỹ thuật] Lớp ngữ nghĩa KPI đặt ở đâu?

Hiện KPI được định nghĩa trong `src/analytics` và dashboard đọc lại; câu hỏi này chốt có tách ra không.

- A. Tách một module định nghĩa KPI dùng chung; `analytics` và dashboard đều đọc từ đó
- B. Giữ nguyên KPI trong `src/analytics`, chỉ thêm lớp mỏng cho truy vấn mới
- C. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q4. [Thiết kế] Mã giao diện của tab "Tích hợp" đặt ở đâu?

Ảnh hưởng tới việc có phải sửa `src/dashboard/app.py` hiện có hay không.

- A. Package riêng cho tab mới (ví dụ `src/dashboard/integration/`), `app.py` chỉ gọi vào
- B. Thêm trực tiếp vào `src/dashboard/app.py` và các tệp hiện có
- C. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Bốn nhóm chủ đề là bốn component độc lập trong một package mới `src/integration/`.
- Lược đồ trung gian khai báo bằng tệp YAML/JSON đọc lúc chạy, tách khỏi mã.
- Lớp ngữ nghĩa KPI tách thành module dùng chung; `analytics` và dashboard cùng đọc.
- Mã giao diện tab "Tích hợp" thêm trực tiếp vào `src/dashboard/app.py` và các tệp hiện có, không tách package riêng.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
