# Đánh giá chất lượng (Code Quality Assessment)

> Không có mã nguồn để đánh giá. Phần này đánh giá **chất lượng dữ liệu và mức độ sẵn sàng** của tài sản hiện có.

## Độ phủ kiểm thử

- **Tổng thể**: Không có (0%).
- **Unit tests**: Không có.
- **Integration tests**: Không có.
- **Data quality tests**: Không có.
- **CI/CD**: Không có.

## Chỉ số chất lượng mã nguồn

- **Linting**: Chưa cấu hình.
- **Code style**: Không áp dụng (chưa có mã).
- **Documentation**: Trung bình — có `AGENTS.md` và tài liệu AI-DLC, nhưng chưa có tài liệu pipeline/schema chính thức.
- **Version control**: Không phải git repo.

## Nợ kỹ thuật

| Mức độ | Vấn đề | Vị trí |
|---|---|---|
| Cao | Không có pipeline ingestion/cleaning/integration | Toàn workspace |
| Cao | Không có schema contract hay data dictionary chính thức | `dataset/` |
| Cao | Không có kiểm thử dữ liệu (unique, FK, reconciliation) | Toàn workspace |
| Trung bình | Không có lockfile/venv, khó tái lập môi trường | Root |
| Trung bình | Không có phân vùng/lưu trữ tối ưu; dữ liệu là CSV thô | `dataset/` |
| Thấp | Tên cột gốc sai chính tả (`lenght`) | `olist_products_dataset.csv` |
| Thấp | Không có README mô tả cách chạy | Root |

## Phát hiện chất lượng dữ liệu

| Mức độ | Phát hiện | Bằng chứng |
|---|---|---|
| Cao | Join geolocation trực tiếp làm bùng nổ số dòng | 1.000.163 dòng / 19.015 zip, trung bình 52,6 dòng/zip; join customers tạo 15.083.455 dòng |
| Cao | `customer_id` không phải định danh khách hàng thật | 99.441 `customer_id` nhưng chỉ 96.096 `customer_unique_id` |
| Trung bình | Payments và reviews là quan hệ nhiều dòng/đơn | 103.886 payment, 99.224 review; 547 đơn nhiều review (551 dòng dư) |
| Trung bình | Tổng thanh toán lệch tổng dòng hàng | 378 đơn lệch > 0,01 |
| Trung bình | Sản phẩm thiếu danh mục và thuộc tính | 610/32.951 sản phẩm |
| Trung bình | Thiếu bản dịch danh mục | `pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos` |
| Trung bình | Tọa độ ngoại lai | lat -36,6…45,1; lng -101,5…121,1 (Brazil) |
| Trung bình | Timestamp đọc dưới dạng chuỗi | Tất cả cột thời gian |
| Thấp | Đơn không có dòng hàng | 775 đơn (603 unavailable, 164 canceled) |
| Thấp | Zip không có geolocation | 278 customer zip, 7 seller zip |
| Thấp | Review thiếu nội dung | 87.656 thiếu title; 58.247 thiếu message |
| Thấp | Trùng lặp geolocation | 261.831 dòng trùng hoàn toàn |
| Thấp | Biến thể tên thành phố | Tối đa 5 cách viết/zip |

## Thống kê nghiệp vụ đáng chú ý

- Tỷ lệ giao trễ trong đơn `delivered`: **8,11%** (7.826/96.478).
- Thời gian giao trung vị: **10,2 ngày**; trung bình: **12,6 ngày**.
- Điểm đánh giá trung bình: **~4,09/5**; 57.328 lượt 5 sao, 11.424 lượt 1 sao.
- Phương thức thanh toán: credit_card 76.795; boleto 19.784; voucher 5.775; debit_card 1.529; not_defined 3.
- Tập trung địa lý: SP 41.746 đơn; RJ 12.852; MG 11.635.

## Pattern tốt

- Khóa chính rõ ràng ở hầu hết bảng.
- Referential integrity tốt: không có item/payment/review trỏ tới đơn không tồn tại; không có item trỏ tới product/seller không tồn tại.
- Có bảng từ điển danh mục riêng.
- Kích thước dữ liệu phù hợp để xử lý cục bộ bằng pandas.

## Anti-pattern

- Trộn grain trong cùng một mô hình phân tích nếu join thô.
- Dùng `customer_id` để đếm khách hàng.
- Inner join với bảng translation/geolocation làm mất dữ liệu.
- Không phân biệt doanh thu theo `payment_value` và `price + freight_value`.
