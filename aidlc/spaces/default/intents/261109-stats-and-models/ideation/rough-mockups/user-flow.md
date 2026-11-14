# User Flow — Từ mở dashboard tới đọc kết quả

Bối cảnh: `../scope-definition/scope-document.md` (thứ tự kiểm định trước, mô hình sau, hiển thị cuối), `wireframes.md` (ba màn hình).

## Luồng chính

```
Mở dashboard
   │
   ├─→ Bấm tab "Phân tích"
   │      │
   │      ├─ Có báo cáo hợp lệ ─→ Dải tóm tắt (tỉ lệ trễ, KTC, AUC, ngưỡng)
   │      │        │
   │      │        ├─→ Đọc bảng kiểm định thống kê (5 nhóm phép kiểm định)
   │      │        └─→ Đọc khối mô hình (AUC, precision, recall, ngưỡng)
   │      │
   │      ├─ Chưa có báo cáo ─→ Trạng thái rỗng + câu lệnh cần chạy
   │      │        │
   │      │        └─→ Chạy `python -X utf8 -m src.pipeline stats`, tải lại trang
   │      │
   │      └─ Báo cáo hỏng ─→ Trạng thái lỗi + đường dẫn tệp
   │
   └─→ Quay lại tab khác mà không mất trạng thái đã chọn
```

## Điểm quyết định

| Điểm | Điều kiện | Nhánh |
|---|---|---|
| D1 | Tệp báo cáo có tồn tại không | Không: trạng thái rỗng [Q7] |
| D2 | Tệp có đủ trường bắt buộc không | Không: trạng thái lỗi [Q7] |
| D3 | Có kết quả cho cả phần thống kê và phần mô hình không | Thiếu một phần: hiện phần có, ghi rõ phần thiếu |

## Đường phục hồi

- Từ trạng thái rỗng: chạy lệnh, tải lại trang, quay về luồng chính.
- Từ trạng thái lỗi: chạy lại lệnh để ghi đè báo cáo, rồi tải lại.
- Nếu báo cáo chỉ có phần thống kê: vẫn đọc được phần đó, phần mô hình ghi rõ "chưa có".

## Không nằm trong luồng này

- Không có đăng nhập, không có phân quyền. [Q6]
- Không có thao tác sửa số liệu trên giao diện; mọi thứ đọc từ tệp báo cáo. [Q4]
