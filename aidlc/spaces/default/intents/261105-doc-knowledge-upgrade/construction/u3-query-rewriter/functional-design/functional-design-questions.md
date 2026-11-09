# Functional Design Questions — u3-query-rewriter

Đơn vị U3 viết lại ba truy vấn mẫu từ lược đồ trung gian thành SQL chạy được trên nguồn, hiển thị kế hoạch từng bước, và đối chiếu kết quả với định nghĩa KPI dùng chung. Câu hỏi dưới đây chỉ hỏi những chỗ mà yêu cầu (`FR2.1`–`FR2.5`, `FR6.1`), câu chuyện (`US2.1`–`US2.3`, `US6.2`) và hợp đồng (`C1`, `C3`, `C4`) chưa chốt. Trả lời bằng cách điền sau mỗi `[Answer]:`.

## Q1. [Chủ sản phẩm] Ba truy vấn mẫu lấy số liệu theo định nghĩa doanh thu nào?

`AGENTS.md` và `project.md` bắt buộc mọi KPI doanh thu phải nêu rõ định nghĩa. `src/analytics` hiện dùng `price + freight_value` của đơn `delivered`.

- A. Dùng đúng `price + freight_value` của đơn `delivered`, như `src/analytics` đang làm
- B. Dùng `payment_value` của đơn `delivered`
- C. Mỗi truy vấn một định nghĩa, ghi rõ trên màn hình
- X. Other (please specify)

[Answer]: A

## Q2. [Kiến trúc sư] Sinh SQL nguồn bằng cách nào?

Đây là quyết định lớn nhất của đơn vị: nó quyết định hình dạng kế hoạch viết lại và cách kiểm.

- A. Mẫu SQL khai tay cho từng truy vấn + hàm điền tham số; kế hoạch từng bước là dữ liệu mô tả cùng mẫu đó
- B. Sinh SQL động từ kế hoạch từng bước (thực thể → bảng → điều kiện join)
- X. Other (please specify)

[Answer]: A

## Q3. [Kiến trúc sư] Đối chiếu KPI (FR2.5) đo bằng cách nào?

Yêu cầu: kết quả cả ba truy vấn khớp **chính xác** số liệu `src/analytics` trả về cho cùng định nghĩa KPI (sai lệch 0 về số dòng và giá trị tiền tệ).

- A. Gọi lại dịch vụ của `src/analytics` ngay trong lúc chạy rồi so giá trị
- B. So với giá trị tham chiếu đã ghi sẵn (baseline) trong định nghĩa KPI
- C. Cả hai: so baseline khi chạy thường, so trực tiếp trong test
- X. Other (please specify)

[Answer]: A

## Q4. [Kiến trúc sư] Khi U5 không chọn được nguồn cho một truy vấn thì U3 làm gì?

`C3` ném `NoSourceAvailableError` khi không nguồn nào đủ trường.

- A. Trả lỗi đó nguyên vẹn cho giao diện, không chạy truy vấn
- B. Chạy trên nguồn Olist mặc định và ghi rõ là đã bỏ qua bước chọn nguồn
- X. Other (please specify)

[Answer]: A

## Q5. [Chủ sản phẩm] Ngưỡng "dưới 2 giây" của NFR1 đo trên cái gì?

- A. Thời gian chạy SQL trên DuckDB, đo bằng đồng hồ quanh lời gọi, trả trong `C4.elapsed_ms`
- B. Thời gian của cả lượt bao gồm chọn nguồn + sinh SQL + chạy
- X. Other (please specify)

[Answer]: A

## Q6. [Kiến trúc sư] Định nghĩa KPI dùng chung (FR6.1) đặt ở đâu?

- A. Mô-đun mới `src/analytics/kpis.py` (hoặc tương đương) là nguồn duy nhất; `src/dashboard` và lớp truy vấn mới đọc từ đó
- B. Mở rộng `src/common/types.py` đang có `KpiFilters`
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

- Ba truy vấn mẫu đã chốt ở `FR2.1`: doanh thu theo danh mục, doanh thu theo tháng, tỷ lệ giao trễ theo bang. Ba `query_id` tương ứng đã có trong `config/integration-sources.yaml` của U5 (`doanh_thu_theo_danh_muc`, `doanh_thu_theo_thang`, `ty_le_giao_tre_theo_bang`), nên U3 phải dùng đúng ba mã này.
- Truy vấn "tỷ lệ giao trễ theo bang" cần trường `don_hang.bang_giao` — đã có trong lược đồ trung gian từ U2.
- Không có câu hỏi nào về giao diện: tab, thẻ và bốn trạng thái hiển thị thuộc `u6-integration-ui`.
