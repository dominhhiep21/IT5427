# User Flow — Tab "Tích hợp"

Bối cảnh: `wireframes.md`, `scope-document.md`, `intent-backlog.md`. Persona chính: giảng viên/hội đồng chấm, mở dashboard trên laptop và đi từ tổng quan vào từng nhóm.

## Luồng 1 — Xem tổng quan rồi đi sâu (luồng chính)

```
Mở dashboard
   -> Tab "Tích hợp"
   -> Màn hình tổng quan: 4 thẻ trạng thái
   -> Chọn một thẻ (bấm hoặc Enter)
   -> Màn hình chi tiết của nhóm đó
   -> "← Tích hợp" để quay lại tổng quan
```

- Điều kiện đầu: pipeline đã chạy ít nhất một lần.
- Kết thúc thành công: người xem thấy được số liệu của nhóm và quay lại không mất trạng thái tổng quan.
- Lỗi: nếu nhóm chưa có dữ liệu, màn hình chi tiết mở ở trạng thái rỗng với nút "Chạy pipeline".

## Luồng 2 — Kiểm chứng lược đồ trung gian

```
Tổng quan -> thẻ "Lược đồ trung gian"
   -> Danh sách 8 thực thể
   -> Chọn "don_hang"
   -> Bảng ánh xạ hiện 6 trường, ghi rõ nguồn từng trường
   -> (tuỳ chọn) chọn thực thể khác
```

- Kết thúc thành công: người xem đối chiếu được từng trường trung gian với bảng nguồn.

## Luồng 3 — Chạy một truy vấn mẫu và xem kế hoạch viết lại

```
Tổng quan -> thẻ "Viết lại truy vấn"
   -> Chọn truy vấn mẫu
   -> Bấm "Chạy"
   -> Nút chuyển trạng thái chờ; vùng kết quả hiện skeleton
   -> Hai khối: truy vấn trung gian và kế hoạch viết lại
   -> Xem thời gian chạy, số dòng, nút "Xem SQL nguồn"
```

- Lỗi truy vấn: thông báo ngay dưới ô chọn, nêu truy vấn và lỗi, có nút thử lại; hai khối mã giữ nội dung lần chạy trước và ghi rõ là kết quả cũ.
- Quá 5 giây: hiện dòng "Đang chạy lâu hơn bình thường" cạnh nút.

## Luồng 4 — Điều chỉnh ngưỡng ghép bản ghi

```
Tổng quan -> thẻ "Ghép bản ghi"
   -> Bảng cặp khớp mặc định (ngưỡng 0.85)
   -> Kéo thanh ngưỡng hoặc nhập số
   -> Số liệu tóm tắt và bảng cập nhật
   -> Cột "Quyết định" cho biết Ghép / Xem lại
```

- Lỗi: ngưỡng ngoài 0–1 bị chặn ngay tại ô nhập, không cho gửi.
- Trạng thái một phần: nếu một nguồn thiếu trường so khớp, bảng ghi rõ cặp nào không chấm được điểm.

## Luồng 5 — Đề xuất nguồn cho một truy vấn

```
Tổng quan -> thẻ "Chọn nguồn"
   -> Chọn truy vấn
   -> Bấm "Đề xuất nguồn"
   -> Bảng nguồn cập nhật cột "Được chọn" và lý do loại
```

- Lỗi: không nguồn nào đủ dữ liệu -> banner nêu truy vấn nào thiếu trường nào, không chọn nguồn nào.

## Luồng phụ — Quay lại ba tab cũ

```
Tab "Tích hợp" -> tab "Tổng quan" / "Danh mục" / "Giao vận"
```

- Không làm mất bộ lọc đã chọn ở tab cũ nếu có; ba tab cũ giữ nguyên hành vi.

## Đường lỗi chung

| Tình huống | Màn hình | Thông báo | Hành động phục hồi |
|---|---|---|---|
| Chưa chạy pipeline | Tổng quan | "Chưa có dữ liệu tích hợp" | Nút "Chạy pipeline" |
| Một nhóm lỗi, ba nhóm còn lại đạt | Tổng quan | Thẻ lỗi có badge đỏ + lý do | Mở chi tiết nhóm lỗi, thử lại |
| Tệp mart thiếu | Chi tiết | "Không tìm thấy dữ liệu của nhóm này" | Quay lại tổng quan |
| Truy vấn lỗi cú pháp | Viết lại truy vấn | Nêu tên truy vấn và lỗi | Chọn truy vấn khác hoặc thử lại |
| Không nguồn nào đủ dữ liệu | Chọn nguồn | Nêu trường còn thiếu | Đổi truy vấn |

## Ghi chú thiết kế luồng

- Độ sâu tối đa: dashboard → tab → chi tiết (2 lần bấm từ trang đầu), đúng giới hạn 3 lần bấm.
- Mọi màn hình chi tiết đều có đường quay lại bằng breadcrumb và bằng phím Escape không cần thiết — chỉ cần Tab tới breadcrumb.
- Không có hành động phá huỷ dữ liệu trong tab này, nên không cần hộp thoại xác nhận.
