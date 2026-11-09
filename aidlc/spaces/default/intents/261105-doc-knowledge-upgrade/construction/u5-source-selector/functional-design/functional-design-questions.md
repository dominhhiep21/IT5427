# Functional Design Questions — u5-source-selector

Đơn vị U5 mô tả từng nguồn ứng viên và chọn nguồn cho một truy vấn, kèm lý do chọn/loại bằng chữ.
Câu hỏi dưới đây chỉ hỏi những chỗ mà yêu cầu (`FR4.1`–`FR4.3`), câu chuyện (`US4.1`, `US4.2`) và
hợp đồng (`C2`, `C3`, `C7`) chưa chốt. Trả lời bằng cách điền sau mỗi `[Answer]:`.

## Q1. [Kiến trúc sư] Danh sách nguồn ứng viên gồm những nguồn nào?

Giả định A3 trong `requirements.md` nói "hai nguồn hiện có đủ để minh hoạ; nguồn thứ ba chỉ là ứng viên mô phỏng". Câu trả lời quyết định số dòng của bảng nguồn trên màn hình.

- A. Ba nguồn: Olist (CSV trong `dataset/`), cache IBGE cục bộ, và một nguồn mô phỏng thứ ba
- B. Hai nguồn: Olist và cache IBGE, không có nguồn mô phỏng
- C. Bốn nguồn: Olist, cache IBGE, và hai nguồn mô phỏng
- D. Nhiều hơn bốn nguồn, tôi sẽ liệt kê trong câu trả lời
- X. Other (please specify)

[Answer]: A

## Q2. [Kiến trúc sư] Nguồn mô phỏng (nếu có) mô tả khả năng đáp ứng thế nào?

Nguồn mô phỏng tồn tại để chứng minh luật loại nguồn: nó phải thiếu một cái gì đó, nếu không thì luôn thắng hoặc luôn thua vô nghĩa.

- A. "Nguồn đối tác (mô phỏng)": có bảng đơn hàng tổng hợp, **không** có danh mục sản phẩm, chi phí 1, độ trễ 50 ms
- B. "Nguồn đối tác (mô phỏng)": có đủ ba bảng nhưng dữ liệu cũ (chỉ đến 2017), chi phí 2, độ trễ 300 ms
- C. "Nguồn đối tác (mô phỏng)": không có dữ liệu thật (`has_data = false`), chỉ để minh hoạ trạng thái "không có dữ liệu"
- X. Other (please specify)

[Answer]:A

## Q3. [Kiến trúc sư] Khi nhiều nguồn cùng đủ trường cho một truy vấn, xếp hạng theo thứ tự nào?

Đây là luật chính của `US4.2`. `C7` cố định `cost_level` (1..5, càng nhỏ càng rẻ) và `latency_ms`; câu trả lời quyết định nguồn nào được chọn khi hoà.

- A. Đủ trường trước → chi phí thấp hơn → độ trễ thấp hơn → tên nguồn theo bảng chữ cái (thứ tự ổn định, không phụ thuộc thứ tự khai báo)
- B. Đủ trường trước → độ trễ thấp hơn → chi phí thấp hơn → tên nguồn theo bảng chữ cái
- C. Chỉ so chi phí thấp nhất, bỏ qua độ trễ
- X. Other (please specify)

[Answer]: A

## Q4. [Kiến trúc sư] Một truy vấn có thể được chọn nhiều nguồn không?

`C3` khai `selected_sources` là danh sách, nên hợp đồng cho phép nhiều hơn một. Nhưng chọn nhiều nguồn nghĩa là truy vấn phải ghép dữ liệu từ nhiều nguồn — việc mà U3 chưa làm.

- A. Đúng một nguồn cho mỗi truy vấn; danh sách chỉ có một phần tử, các nguồn còn lại vào `rejected_sources` kèm lý do
- B. Nhiều nguồn khi một nguồn không phủ đủ bảng, chọn bộ phủ tối thiểu
- X. Other (please specify)

[Answer]: A

## Q5. [Chủ sản phẩm] Khi không nguồn nào đủ trường, thông báo cho người xem nêu gì?

`US4.2` / `AC4.2.2` yêu cầu "hiện thông báo nêu trường còn thiếu và không chọn nguồn nào". Câu trả lời quyết định nội dung chữ trên màn hình.

- A. Nêu danh sách trường còn thiếu, và với mỗi nguồn gần nhất là nguồn nào thiếu trường gì
- B. Chỉ nêu câu "Không nguồn nào đủ trường cho truy vấn này" và danh sách trường thiếu
- X. Other (please specify)

[Answer]: A

## Q6. [Kiến trúc sư] Hồ sơ nguồn lấy từ đâu?

`FR4.1` nói hệ thống mô tả mỗi nguồn bằng khả năng đáp ứng, chi phí, độ trễ. Có hai cách hiện thực, ảnh hưởng tới nơi phải sửa khi thêm nguồn.

- A. Tệp cấu hình tĩnh (ví dụ `config/integration-sources.yaml`), đối chiếu với danh mục trường `C2` để biết nguồn phủ trường nào
- B. Suy hoàn toàn từ `MediatedFieldCatalogue` (`C2`) cộng chi phí/độ trễ khai trong cùng tệp lược đồ trung gian
- X. Other (please specify)

[Answer]: A

## Q7. [Chủ sản phẩm] Cột "khả năng đáp ứng" trên bảng nguồn hiển thị dạng gì?

`C7` khai `coverage: str` — một chuỗi. Câu trả lời quyết định nội dung chuỗi đó.

- A. Câu ngắn tiếng Việt mô tả phủ được gì (ví dụ "Đủ ba bảng: đơn hàng, mặt hàng, sản phẩm")
- B. Danh sách mã trường "entity.field" mà nguồn phủ được
- C. Cả hai: câu ngắn, và danh sách mã trường ở dòng phụ
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

- `has_data` của mỗi nguồn là cờ cấu hình, không phải phép dò tệp lúc chạy: nguồn mô phỏng không được phép phát sinh lệnh gọi mạng (`FR4.3`).
- Cache IBGE là nguồn thật nhưng chỉ phủ bảng địa lý; lý do loại nó cho ba truy vấn mẫu sẽ là "không có trường cần đọc", không phải "không có dữ liệu".
- Không có câu hỏi nào về giao diện: bảng nguồn, nút "Đề xuất nguồn" và bốn trạng thái hiển thị thuộc `u6-integration-ui`; U5 chỉ trả payload `C7` và kết quả chọn nguồn.
