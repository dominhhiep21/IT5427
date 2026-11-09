# Requirements Analysis — Câu hỏi làm rõ

## Q1. [Sản phẩm] Lược đồ trung gian nên phủ những thực thể nào trong lần đầu?

Danh sách này quyết định khối lượng việc của nhóm cốt lõi đầu tiên.

- A. Tám thực thể chính: đơn, mặt hàng, khách, người bán, sản phẩm, thanh toán, đánh giá, địa lý
- B. Ba thực thể đủ cho lát cắt đầu tiên (đơn, mặt hàng, sản phẩm), mở rộng sau
- C. Chỉ hai thực thể (đơn, mặt hàng)
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q2. [Kỹ thuật] Cần bao nhiêu truy vấn mẫu cho phần viết lại truy vấn?

Mỗi truy vấn mẫu là một kịch bản phải viết lại và hiển thị kế hoạch.

- A. Ba truy vấn: doanh thu theo danh mục, doanh thu theo tháng, tỷ lệ giao trễ theo bang
- B. Năm truy vấn, thêm hai truy vấn tuỳ chọn
- C. Một truy vấn duy nhất cho lát cắt đầu tiên
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q3. [Kỹ thuật] Ghép bản ghi sẽ minh hoạ trên đối tượng nào?

Ảnh hưởng tới dữ liệu mẫu và tiêu chí đánh giá của nhóm ghép bản ghi.

- A. Khách hàng (dùng `customer_unique_id` làm mốc so sánh với kết quả ghép)
- B. Người bán
- C. Cả khách hàng và người bán
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Q4. [Kỹ thuật] Ngưỡng tương đồng mặc định cho ghép bản ghi là bao nhiêu?

Ngưỡng thấp hơn cho nhiều cặp ghép hơn nhưng tăng rủi ro ghép sai.

- A. 0.85 như wireframe đang minh hoạ
- B. 0.90 (chặt hơn, ít cặp hơn)
- C. Không cố định, cho người xem tự chỉnh và mặc định 0.85
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q5. [Kỹ thuật] Chọn nguồn dữ liệu cần thể hiện điều gì trên giao diện?

Quyết định mức chi tiết của bảng nguồn trên tab mới.

- A. Bảng đầy đủ: nguồn, có dữ liệu hay không, chi phí ước tính, độ trễ, lý do chọn/loại
- B. Chỉ hiện nguồn được chọn và một dòng lý do
- C. Hiện bảng đầy đủ nhưng ẩn chi phí/độ trễ (chỉ là số mô phỏng)
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q6. [Sản phẩm] Chỉ số thành công nên có ngưỡng định lượng chưa?

Ba chỉ số hiện đang định tính; người kiểm tra ở bước đầu đã nêu điểm này.

- A. Đặt ngưỡng cụ thể: mỗi nhóm có ít nhất 1 màn hình và 1 bảng số liệu; mỗi tương tác dashboard phản hồi dưới 2 giây; 5 KPI lệch 0 so với baseline
- B. Giữ định tính, không đặt ngưỡng
- C. Chỉ đặt ngưỡng cho KPI baseline, hai chỉ số còn lại giữ định tính
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q7. [Thiết kế] Ba tab báo cáo cũ có được làm mới trong đợt này không?

Điểm này còn mở từ bước Rough Mockups và ảnh hưởng tới việc có thêm một đơn vị công việc giao diện.

- A. Có, làm mới cả ba tab trong đợt này
- B. Không, hoãn sang đợt sau; đợt này chỉ thêm tab "Tích hợp"
- C. Chỉ làm mới nếu còn thời gian sau khi xong bốn nhóm
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Lược đồ trung gian: ba thực thể trước (đơn, mặt hàng, sản phẩm), mở rộng sau.
- Truy vấn mẫu: ba — doanh thu theo danh mục, doanh thu theo tháng, tỷ lệ giao trễ theo bang.
- Ghép bản ghi: minh hoạ trên cả khách hàng và người bán.
- Ngưỡng tương đồng mặc định: 0.85.
- Bảng chọn nguồn: đầy đủ (nguồn, có dữ liệu, chi phí, độ trễ, lý do chọn/loại).
- Ngưỡng thành công: mỗi nhóm có ít nhất một màn hình và một bảng số liệu; mỗi tương tác dashboard phản hồi dưới 2 giây; 5 KPI lệch 0 so với baseline.
- Ba tab cũ: không làm mới trong đợt này, hoãn sang đợt sau.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
