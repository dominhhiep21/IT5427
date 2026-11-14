# Mockups — Tab kết quả (độ trung thực trung bình)

Kế thừa `../../ideation/rough-mockups/wireframes.md` và bổ sung phần chi tiết theo `refined-mockups-questions.md`. Nguồn yêu cầu: `../requirements-analysis/requirements.md` (FR4.1–FR4.3), `../user-stories/stories.md` (US4).

## Bố cục

```
┌──────────────────────────────────────────────────────────────────────┐
│  Tab: Tổng quan · Danh mục · Giao vận · Tích hợp · Phân tích (chọn)  │
├──────────────────────────────────────────────────────────────────────┤
│  (A) Dải tóm tắt — 4 ô, mỗi ô: nhãn nhỏ, số lớn, ghi chú 12px        │
│      [Tỉ lệ trễ + KTC] [AUC] [Ngưỡng cảnh báo] [Số đơn kiểm tra]     │
├──────────────────────────────────────────────────────────────────────┤
│  (B) Khối "Kiểm định thống kê" — tiêu đề h2, bảng 5 nhóm             │
│      Bảng: Phép kiểm định | Ước lượng | KTC 95% | p | Diễn giải      │
│      Dưới bảng: dòng ghi chú mức ý nghĩa và cỡ mẫu từng nhóm          │
├──────────────────────────────────────────────────────────────────────┤
│  (C) Khối "Mô hình đơn trễ" — tiêu đề h2                             │
│      Hàng trên: bộ chọn ngưỡng cảnh báo (0,10 → 0,90, bước 0,05)      │
│      Hàng giữa: 4 ô chỉ số theo ngưỡng đang chọn                     │
│      Hàng dưới: bảng phân bố dự đoán (số đơn bị gắn cờ / không)      │
└──────────────────────────────────────────────────────────────────────┘
```

Mỗi nhóm kết quả là một khối riêng có tiêu đề và bảng bên trong. [Q1] Bộ lọc ngưỡng chỉ áp cho khối (C). [Q2]

## Khối lượng hiển thị

- Dải tóm tắt: 4 ô, cùng kích thước, số dùng chữ số đều bề rộng.
- Bảng thống kê: 5 dòng dữ liệu, không phân trang.
- Bảng mô hình: 2 dòng (có cờ / không cờ), cộng dòng tổng.

## Điểm khác biệt so với bản phác thảo

- Thêm bộ chọn ngưỡng trong khối mô hình. [Q2]
- Dải tóm tắt đổi ô thứ ba thành ngưỡng cảnh báo đang chọn, để khớp với bộ lọc.
- Khối mô hình có thêm bảng phân bố, không chỉ bốn chỉ số.
