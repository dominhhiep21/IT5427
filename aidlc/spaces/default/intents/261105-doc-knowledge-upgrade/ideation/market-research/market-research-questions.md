# Market Research — Câu hỏi làm rõ

## Q1. [Sản phẩm] So sánh với nhóm giải pháp nào?

Lần nâng cấp này là một đồ án học tập, nhưng vẫn có lựa chọn "tự làm hay dùng công cụ có sẵn". Chọn nhóm đối chiếu để phần phân tích có ích cho các bước thiết kế sau.

- A. Công cụ mã nguồn mở: dbt, Airbyte, Trino/Presto, Splink, DuckDB
- B. Nền tảng thương mại: Denodo, Informatica, Talend, Fivetran
- C. Cả hai nhóm
- D. Not applicable (không cần so sánh)
- X. Other (please specify)

[Answer]: C

## Q2. [Kỹ thuật] Đứng giữa "tự xây" và "dùng công cụ có sẵn", bạn nghiêng về đâu?

Đây là quyết định build-vs-buy chính của lần nâng cấp, ảnh hưởng trực tiếp tới khối lượng code ở giai đoạn Construction.

- A. Tự xây toàn bộ phần lõi để thể hiện rõ lý thuyết (ánh xạ, ghép bản ghi, viết lại truy vấn, chọn nguồn)
- B. Tự xây phần lõi, chỉ dùng thư viện cho phần phụ (ví dụ thư viện so khớp chuỗi)
- C. Dùng công cụ có sẵn, chỉ viết lớp trình diễn trên dashboard
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q3. [Sản phẩm] Xu hướng nào cần phản ánh trong sản phẩm?

Chọn những xu hướng bạn muốn sản phẩm thể hiện, để phần "market trends" không lan man.

- A. Semantic layer / lớp ngữ nghĩa dùng chung cho nhiều công cụ
- B. Lakehouse và xử lý tại chỗ (DuckDB, Parquet)
- C. Data contracts và lineage (truy vết nguồn gốc dữ liệu)
- D. Không cần — chỉ cần đủ lý thuyết trong `doc/`
- E. Not applicable (không áp dụng)
- X. Other (please specify)

[Answer]: A

## Q4. [Kỹ thuật] Ràng buộc về giấy phép và chi phí?

Ràng buộc này quyết định danh sách công cụ được phép xuất hiện trong phần so sánh và trong thiết kế.

- A. Chỉ dùng thư viện/công cụ mã nguồn mở, miễn phí
- B. Được nêu bản thương mại để so sánh, nhưng không dùng thật
- C. Không quan tâm
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q5. [Sản phẩm] Có sản phẩm hay tiêu chí cụ thể nào bắt buộc phải đối chiếu không?

Ví dụ giảng viên yêu cầu so sánh với một công cụ nhất định, hoặc đề bài có danh sách tiêu chí chấm.

- A. Không có yêu cầu bắt buộc
- B. Có — mình sẽ ghi rõ trong Other
- C. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Đối chiếu với cả hai nhóm: công cụ mã nguồn mở và nền tảng thương mại.
- Hướng build-vs-buy: tự xây phần lõi, chỉ dùng thư viện cho phần phụ.
- Xu hướng đưa vào sản phẩm: semantic layer / lớp ngữ nghĩa dùng chung.
- Ràng buộc: chỉ dùng công cụ/thư viện mã nguồn mở, miễn phí.
- Không có sản phẩm hay tiêu chí đối chiếu nào bắt buộc từ giảng viên/đề bài.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
