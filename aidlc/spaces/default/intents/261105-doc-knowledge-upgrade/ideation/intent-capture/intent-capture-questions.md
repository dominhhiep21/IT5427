# Intent Capture — Câu hỏi làm rõ

## Sources

- [desc] Initial description: "tôi muốn nâng cấp giao diện và hệ thống hiện tại cho việc áp dụng các kiến thức trong @doc\\"
- [scope] Workflow-selected scope: `feature`.

## Q1. [Sản phẩm] Vấn đề lớn nhất mà lần nâng cấp này phải giải quyết

Hệ hiện tại đã có pipeline (ingest → clean → integrate → analyze) và dashboard 3 tab chạy được; bạn muốn "áp dụng kiến thức trong `doc/`". Câu hỏi này quyết định trọng tâm của cả lần nâng cấp.

- A. Hệ hiện tại mới ghép dữ liệu theo khóa cứng, chưa có lớp lược đồ trung gian / ánh xạ / truy vấn thống nhất để thể hiện đúng lý thuyết tích hợp dữ liệu
- B. Người xem (giảng viên, hội đồng) chưa thấy được các khái niệm tích hợp dữ liệu trong sản phẩm — hiện chỉ thấy dashboard báo cáo
- C. Cả hai: cần cả lớp tích hợp đúng lý thuyết lẫn giao diện thể hiện được nó
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Q2. [Kỹ thuật] Những chủ đề nào trong `doc/` cần thể hiện rõ trong lần nâng cấp này? (chọn tất cả nếu áp dụng)

Đây là các nhóm nội dung trong slide bài giảng (`2_SchemaAlignment.pdf`, `3_RecordLinkage_ER.pdf`, `4_QueryProcessing.pdf`, `5_SourcesSelection.pdf`, `2_mediationquery.pdf`). Chọn đúng nhóm để phạm vi không bị dàn trải.

- A. Đồng nhất lược đồ và lược đồ trung gian (schema alignment, mediated schema, GAV/LAV/GLAV)
- B. Ghép bản ghi / nhận dạng thực thể (record linkage, entity resolution, blocking, độ tương đồng)
- C. Xử lý và viết lại truy vấn (query processing, query rewriting/unfolding, tối ưu)
- D. Chọn nguồn dữ liệu (source selection, khả năng truy cập nguồn, chi phí)
- E. Tất cả A–D
- X. Other (please specify)

[Answer]: E

## Q3. [Sản phẩm] "Nâng cấp giao diện" cụ thể là gì?

Bạn nói muốn nâng cấp giao diện; câu hỏi này tách "thêm năng lực mới" khỏi "làm đẹp lại giao diện đang có".

- A. Thêm màn hình/tab mới cho các năng lực tích hợp (xem nguồn dữ liệu, ánh xạ lược đồ, kết quả ghép bản ghi, chạy truy vấn)
- B. Làm lại UI/UX hiện có (bố cục, màu sắc, biểu đồ) cho dễ đọc và chuyên nghiệp hơn, vẫn giữ 3 tab
- C. Cả hai: vừa thêm màn hình tích hợp vừa nâng chất lượng giao diện hiện có
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Q4. [Sản phẩm] Ai là người dùng chính của giao diện sau nâng cấp?

Người dùng chính quyết định mức độ chi tiết kỹ thuật được phơi ra trên giao diện.

- A. Giảng viên/hội đồng chấm đồ án — cần thấy bằng chứng áp dụng lý thuyết
- B. Chính bạn — công cụ khai thác và kiểm tra dữ liệu hằng ngày
- C. Nhà phân tích dữ liệu/đồng nghiệp không rành kỹ thuật — cần thao tác đơn giản
- D. Not identified (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q5. [Sản phẩm] Thành công của lần nâng cấp được đo bằng gì?

KPI baseline hiện tại: doanh thu delivered 15.419.773,75 BRL, 96.478 đơn delivered, AOV 159,83 BRL, tỷ lệ giao trễ 8,11%.

- A. Demo được đầy đủ các khái niệm trong `doc/` trên dữ liệu Olist thật, có số liệu đối chiếu
- B. Dashboard trả lời câu hỏi nghiệp vụ nhanh hơn hiện tại (ít thao tác hơn, thêm bộ lọc/tương tác)
- C. Không hồi quy: KPI baseline giữ nguyên, toàn bộ test hiện có vẫn xanh
- D. Cả A, B và C
- X. Other (please specify)

[Answer]: D

## Q6. [Sản phẩm] Vì sao làm bây giờ?

Bối cảnh quyết định mức độ ưu tiên giữa "đúng lý thuyết" và "dùng được ngay".

- A. Yêu cầu của môn học/đồ án (`doc/Projects.pdf`) — cần bản thể hiện đủ nội dung lý thuyết
- B. Hệ đã chạy ổn, giờ muốn nâng chất lượng để thể hiện phần tích hợp dữ liệu đã học
- C. Cả hai
- D. Not applicable (không áp dụng)
- X. Other (please specify)

[Answer]: C

## Q7. [Sản phẩm] Ai quyết định phạm vi và thứ tự ưu tiên?

Câu hỏi này xác định ai phải đồng ý khi phạm vi thay đổi giữa đường.

- A. Bạn tự quyết toàn bộ
- B. Bạn đề xuất, giảng viên/nhóm phê duyệt
- C. Cả nhóm cùng quyết
- D. Not identified (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q8. [Sản phẩm] Lần nâng cấp đầu tiên này KHÔNG làm gì? (chọn tất cả nếu áp dụng)

Đây là biên giới sản phẩm của phiên bản đầu, không phải câu hỏi về quy trình. Ranh giới rõ giúp tránh phình phạm vi.

- A. Không thêm nguồn dữ liệu ngoài Olist + cache IBGE hiện có
- B. Không triển khai ML dự báo giao trễ
- C. Không đổi công nghệ: vẫn Python + pandas + DuckDB + Plotly Dash, không Spark/Kafka/Docker/cloud
- D. Không làm đăng nhập/phân quyền nhiều người dùng
- E. Không giới hạn — mở mọi thứ
- X. Other (please specify)

[Answer]: A

## Q9. [Kỹ thuật] Chốt lại phạm vi chủ đề cho phiên bản đầu

Hai câu trả lời trước có lúc lệch nhau (câu 2 từng chỉ chọn một nhóm, câu 5 chọn "demo đầy đủ"); câu hỏi này chốt cách hiểu cuối cùng. Hiện câu 2 và câu 5 đã cùng chỉ về cả bốn nhóm.

- A. Chỉ làm nhóm đồng nhất lược đồ & lược đồ trung gian (GAV/LAV/GLAV); các nhóm còn lại để sau
- B. Nhóm đồng nhất lược đồ là chính, nhưng vẫn demo mức tối thiểu cả ghép bản ghi, xử lý truy vấn và chọn nguồn dữ liệu
- C. Làm cả 4 nhóm chủ đề ngang nhau (như phương án E của câu 2)
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Vấn đề: cần cả lớp tích hợp đúng lý thuyết lẫn giao diện thể hiện được nó.
- Chủ đề: cả 4 nhóm — đồng nhất lược đồ & lược đồ trung gian, ghép bản ghi/nhận dạng thực thể, xử lý & viết lại truy vấn, chọn nguồn dữ liệu.
- Giao diện: vừa thêm màn hình tích hợp, vừa nâng chất lượng giao diện hiện có.
- Người dùng chính: giảng viên/hội đồng chấm đồ án.
- Đo thành công: demo được các khái niệm trên dữ liệu thật + dashboard trả lời câu hỏi nghiệp vụ nhanh hơn + không hồi quy KPI baseline và test hiện có.
- Vì sao bây giờ: vừa do yêu cầu môn học/đồ án, vừa do muốn nâng chất lượng thể hiện phần đã học.
- Người quyết định: bạn tự quyết toàn bộ.
- Biên giới phiên bản đầu: không thêm nguồn dữ liệu ngoài Olist + cache IBGE hiện có.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct

## Assumption Confirmation

Giả định đang mở trong tài liệu:

- [assumption] Kênh giao tiếp và nhịp báo cáo với giảng viên/hội đồng chưa được xác định.

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A. Accept assumptions
