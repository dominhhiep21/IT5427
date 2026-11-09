# Feasibility & Constraints — Câu hỏi làm rõ

## Q1. [Kỹ thuật] Phần nâng cấp phải ăn khớp với hệ thống nào?

Hệ hiện tại là pipeline + dashboard trong chính repo này. Câu hỏi xác định có hệ thống bên ngoài nào ràng buộc thiết kế không.

- A. Chỉ hệ thống trong repo: pipeline, `data/marts`, `warehouse/olist.duckdb`, dashboard Dash — không có hệ thống ngoài
- B. Có hệ thống ngoài phải ăn khớp — mình sẽ ghi rõ trong Other
- C. Không cần ăn khớp với gì, làm độc lập
- D. Not applicable (không áp dụng)
- X. Other (please specify)

[Answer]: A

## Q2. [Tuân thủ] Có yêu cầu quy định hoặc dữ liệu cá nhân nào không?

Ảnh hưởng tới việc có phải thêm lớp che dữ liệu, kiểm soát truy cập hay ghi log hay không.

- A. Không — dữ liệu Olist đã ẩn danh, dashboard chỉ chạy localhost
- B. Có yêu cầu của môn học (trích dẫn nguồn, liêm chính học thuật) — không phải dữ liệu cá nhân
- C. Có yêu cầu khác — mình sẽ ghi rõ trong Other
- D. Not applicable (không áp dụng)
- X. Other (please specify)

[Answer]: A

## Q3. [Kỹ thuật] Công nghệ nào được phép dùng cho phần mới?

Quyết định này khoanh vùng thư viện được thêm vào và cách viết code ở giai đoạn Construction.

- A. Giữ nguyên: Python 3.13 + pandas + DuckDB + Plotly Dash trên máy local, không Spark/Kafka/Docker/cloud
- B. Được thêm thư viện Python mã nguồn mở nhỏ (ví dụ thư viện so khớp chuỗi), vẫn chạy local
- C. Được đổi/thêm công nghệ lớn — mình sẽ ghi rõ trong Other
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q4. [Sản phẩm] Bạn có bao nhiêu thời gian cho lần nâng cấp này?

Mốc thời gian quyết định độ sâu của từng nhóm chủ đề và việc có làm hết bốn nhóm hay không.

- A. Vài ngày — cần bản chạy được sớm
- B. Khoảng 1–2 tuần
- C. Từ 1 tháng trở lên
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q5. [Sản phẩm] Có ràng buộc tổ chức nào không?

Ví dụ mốc nộp cố định, lịch bảo vệ, hoặc phần khác của đồ án phải hoàn thành trước.

- A. Không — tự làm, tự quyết tiến độ
- B. Có mốc cố định — mình sẽ ghi rõ trong Other
- C. Not applicable (không áp dụng)
- X. Other (please specify)

[Answer]: A

## Q6. [Kỹ thuật] Có cần dùng đám mây hoặc hạ tầng ngoài máy local không?

Ảnh hưởng trực tiếp tới chi phí và độ phức tạp triển khai.

- A. Không — chỉ chạy localhost như hiện tại
- B. Có — mình sẽ ghi rõ trong Other
- C. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Chỉ phải ăn khớp với hệ thống trong repo; không có hệ thống ngoài.
- Không có yêu cầu quy định hay dữ liệu cá nhân; dữ liệu đã ẩn danh, chạy localhost.
- Được thêm thư viện Python mã nguồn mở nhỏ, vẫn chạy local.
- Thời gian: khoảng 1–2 tuần.
- Không có ràng buộc tổ chức hay mốc nộp cố định.
- Không dùng đám mây hay hạ tầng ngoài máy local.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
