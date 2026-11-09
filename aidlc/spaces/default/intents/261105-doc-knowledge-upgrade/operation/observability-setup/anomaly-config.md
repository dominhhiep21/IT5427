# Anomaly Config

## 1. Không có phát hiện bất thường tự động

Phát hiện bất thường cần dữ liệu theo thời gian và một mô hình nền. Hệ này chạy khi có người bấm, không có chuỗi thời gian đều đặn để học nền.

## 2. Ba bất thường có thể nhận ra bằng luật đơn giản

| Bất thường | Dấu hiệu | Luật |
|---|---|---|
| Dữ liệu nguồn bị thay | Số dòng nạp khác 99.441, hoặc số bản ghi bị loại tăng vọt | `rows_in != 99441` hoặc `rows_dropped > 1%` |
| Kết quả ghép lệch | `correct_rate` tụt mạnh so với 0,5301 đã đo | lệch quá 10% tương đối |
| Truy vấn chậm bất thường | `integration.query.slow` xuất hiện liên tiếp | ≥ 3 lần trong một lần chạy |

## 3. Vì sao không tự động hoá ba luật này

- Luật thứ nhất và thứ ba đã có trong nhật ký; thêm mã kiểm sẽ tạo cổng thứ hai cho cùng một sự thật.
- Luật thứ hai phụ thuộc chất lượng dữ liệu nguồn — nếu dữ liệu đổi thật thì `correct_rate` đổi là đúng, không phải bất thường. Tự động báo sẽ tạo cảnh báo giả.

## 4. Cách kiểm khi nghi ngờ

```powershell
.venv\Scripts\python.exe -X utf8 -m pytest tests/data_quality/test_real_dataset.py -m slow -q
```

Bộ test này khẳng định các hằng số dị thường đã biết trên dữ liệu thật (19.015 mã bưu chính sau gộp, 610 sản phẩm thiếu danh mục, 8.427 outlier giá). Nếu nó đỏ, dữ liệu nguồn đã đổi — đó là thông tin, không phải lỗi.

## 5. Không làm

Không thêm mô hình học máy cho phát hiện bất thường: cần dữ liệu lịch sử mà đợt này không có, và mục tiêu của sản phẩm không phải giám sát.
