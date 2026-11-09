# Reliability Requirements — u1-thin-slice

Nguồn: `inception/requirements-analysis/requirements.md` (NFR5, NFR6), `construction/u1-thin-slice/functional-design/rules.md`.

| Mã | Yêu cầu | Cách đáp ứng |
|---|---|---|
| NFR5.1 | Sau thay đổi, `quality` chế độ `full` và `KpiReconciler` phải xanh | Đơn vị chỉ đọc dữ liệu nguồn, không ghi vào `data/marts` hay `warehouse/`; lệnh xác nhận chạy lại toàn bộ test |
| NFR5.2 | 5 KPI baseline lệch 0 và số dòng 11 view không đổi | Không có thao tác ghi nào chạm các bảng đó trong đơn vị này |
| NFR5.3 | Cập nhật test hình dạng dashboard trong cùng thay đổi khi chạm dashboard | Đơn vị này thêm tab "Tích hợp" khai đủ **bốn `card_ids`** cộng **một vùng kết quả `don-theo-thang`** (`result_region_ids` theo C9), và vùng cần **một callback riêng** cho nút "Chạy truy vấn", nên hình dạng đích là **4 tab, 8 callback, 4 thẻ + 1 vùng**; các test khẳng định hình dạng phải cập nhật ngay trong thay đổi này |
| NFR6.1 | Chạy local, không cần mạng | Không có lời gọi mạng nào trong đơn vị này |
| NFR6.2 | Mọi lệnh Python chạy UTF-8 | Mọi lệnh trong tài liệu và trong test dùng `python -X utf8` |

## Yêu cầu chịu lỗi

| Mã | Yêu cầu | Cách đáp ứng |
|---|---|---|
| RL-U1-1 | Thiếu tệp nguồn thì báo lỗi rõ, không hiện bảng rỗng | `ConfigurationError` khi tệp lược đồ/CSV nguồn thiếu **hoặc khi tệp cấu hình tab thiếu `result_region_ids`**; `SchemaError` khi nội dung khai báo sai — đúng C1. Vùng hiện trạng thái lỗi kèm câu và nút thử lại |
| RL-U1-2 | Bản ghi hỏng không làm hỏng cả lô | BR1.1, BR1.2: loại và đếm, lô vẫn nạp tiếp |
| RL-U1-3 | Chưa có dữ liệu thì phân biệt với có dữ liệu bằng 0 | BR1.8: trạng thái rỗng riêng |
| RL-U1-4 | Lỗi truy vấn không làm mất kết quả lần trước | Kết quả cũ được giữ và ghi rõ "kết quả lần trước"; số liệu vẫn phải khớp NFR5.5 |
