# Scalability Design — u1-statistics

Nguồn: `../nfr-requirements/scalability-requirements.md`, `../functional-design/entities.md`.

## Quyết định

| # | Quyết định | Phục vụ | Vì sao |
|---|---|---|---|
| SCD-1 | Không phân vùng, không chia lô: một lần đọc, một lần tính | NFR1.5 | Ở cỡ dữ liệu hiện tại và cả 5 lần cỡ đó, dữ liệu vẫn vừa bộ nhớ; chia lô thêm mã mà không thêm khả năng |
| SCD-2 | Mọi bảng tổng hợp bị chặn số nhóm bởi số bang và số tháng | NFR1.7 | Giữ đúng grain ở mỗi bước; số nhóm không phụ thuộc số dòng |
| SCD-3 | Bộ nhớ tỉ lệ với số **nhóm**, không với số dòng thô | NFR1.6 | Hệ quả trực tiếp của SCD-2 khi phép gộp nằm trong SQL |
| SCD-4 | Một tiến trình, một luồng | NFR1.5 | Không có trạng thái dùng chung, nên mở rộng theo chiều ngang là chạy nhiều tiến trình độc lập, không phải sửa mã |

## Ngưỡng

| Đại lượng | Biên trên | Khi vượt |
|---|---|---|
| Số bang | 27 | Không vượt được với dữ liệu Brazil; nếu vượt, cột bang đã bị ghép sai |
| Số tháng | khoảng 36 | Dải 2016-09…2018-10 là 26; vượt 36 nghĩa là dữ liệu đã đổi kỳ |
| Số vùng | 5 | Vượt nghĩa là `dim_customer.region` đã đổi cách mã hoá |

## Giả định thay vì mốc đo

NFR1.5 (dữ liệu gấp 5 lần vẫn giữ mốc thời gian) là **giả định**, không phải mốc đã đo: `dataset/` bất biến và chỉ có một cỡ. Cùng loại, NFR1.6 được kiểm bằng một bản sao dữ liệu dựng trong bộ nhớ nhân đôi, không bằng dữ liệu thật. Ghi rõ để lần đọc sau không nhầm hai điều này là đã được chứng minh.

## Điều không làm

- Không dựng chỉ mục hay bảng trung gian cho riêng tầng `stats`: mart đã là bản tổng hợp, thêm một tầng nữa là thêm một chỗ để lệch.
- Không đặt giới hạn thời gian chạy cứng trong mã: ngân sách là mốc nghiệm thu, không phải một `timeout` sẽ giết lần chạy giữa chừng và để lại tệp dở.
