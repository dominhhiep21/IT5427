# Wireframes — Tab "Phân tích" (độ trung thực thấp)

Bối cảnh: `../scope-definition/scope-document.md` (S-06 lệnh CLI, S-07 tab mới), `../scope-definition/intent-backlog.md` (B-03, B-05), `../intent-capture/intent-statement.md`.

Tab mới có hai mục chính, đọc từ báo cáo JSON do lệnh CLI ghi ra. [Q1] Thứ tự trên màn hình: dải tóm tắt, rồi kiểm định thống kê, rồi mô hình. [Q2][Q3]

## Màn hình 1 — Tab "Phân tích"

```
┌──────────────────────────────────────────────────────────────────────┐
│ OLIST / BẢNG ĐIỀU HÀNH                          Cập nhật 09/11/2026   │
├──────────────────────────────────────────────────────────────────────┤
│ [ Tổng quan ] [ Danh mục ] [ Giao vận ] [ Tích hợp ] [ Phân tích ]   │
├──────────────────────────────────────────────────────────────────────┤
│  (1) DẢI TÓM TẮT                                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐         │
│  │ Tỉ lệ trễ  │ │ KTC 95%    │ │ AUC mô hình│ │ Ngưỡng     │         │
│  │ 8,11%      │ │ 7,94–8,29  │ │ 0,78       │ │ 0,35       │         │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘         │
├──────────────────────────────────────────────────────────────────────┤
│  (2) KIỂM ĐỊNH THỐNG KÊ                                              │
│  Bảng: Phép kiểm định | Ước lượng | Khoảng tin cậy | p | Diễn giải   │
│  ─ Tỉ lệ giao trễ toàn kỳ                                             │
│  ─ So sánh hai bang cao nhất và thấp nhất                             │
│  ─ Tương quan giá hàng và phí vận chuyển                              │
│  ─ So sánh nhóm hoặc phân phối (nếu có)                               │
│  ─ Phân rã mùa vụ chuỗi doanh thu (nếu có)                            │
├──────────────────────────────────────────────────────────────────────┤
│  (3) MÔ HÌNH DỰ BÁO ĐƠN TRỄ                                          │
│  Chỉ số: AUC | Precision | Recall | Số đơn kiểm tra | Ngưỡng cảnh báo │
│  Ghi chú: cách chia theo thời gian, giai đoạn huấn luyện và kiểm tra   │
└──────────────────────────────────────────────────────────────────────┘
```

### Ghi chú tiếp cận cho màn hình 1

- Tiêu đề trang là `h1`; ba khối là `h2` theo đúng thứ tự (1)(2)(3), không nhảy cấp.
- Vùng chính là `main`; thanh tab là `nav` có nhãn "Các tab báo cáo".
- Điểm vào bàn phím: phím Tab đầu tiên rơi vào thanh tab, sau đó tới từng dòng bảng theo thứ tự đọc.
- Con số trong bảng dùng chữ số đều bề rộng để so sánh theo cột.
- Màu không phải tín hiệu duy nhất: mức "đạt/không đạt" của AUC ghi bằng chữ bên cạnh con số.

## Màn hình 2 — Trạng thái rỗng

```
┌──────────────────────────────────────────────────────────────────────┐
│  Tab "Phân tích"                                                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ○  Chưa có báo cáo phân tích                                       │
│                                                                      │
│   Chạy lệnh dưới đây để sinh báo cáo, rồi tải lại trang:             │
│   python -X utf8 -m src.pipeline stats                               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

Ghi chú tiếp cận: khối trạng thái là `role="status"`, có `h2` là "Chưa có báo cáo phân tích"; lệnh nằm trong `code` để trình đọc màn hình đọc nguyên văn.

## Màn hình 3 — Trạng thái lỗi

```
┌──────────────────────────────────────────────────────────────────────┐
│  Tab "Phân tích"                                                     │
├──────────────────────────────────────────────────────────────────────┤
│   ⚠  Không đọc được báo cáo phân tích                                │
│   Tệp báo cáo có nhưng thiếu trường bắt buộc hoặc sai định dạng.     │
│   Đường dẫn: data/reports/analysis.json                              │
└──────────────────────────────────────────────────────────────────────┘
```

Ghi chú tiếp cận: khối lỗi là `role="alert"`, chữ màu đất nung kèm biểu tượng và câu chữ, không dựa vào màu.

## Kích thước và hệ thống

- Chỉ thiết kế cho desktop từ 1280px trở lên. [Q5]
- Dùng token và thành phần có sẵn trong `assets/style.css`, không tạo bộ thành phần mới. [Q4]
- Mức tiếp cận ngang các tab hiện có: bàn phím, tương phản, nhãn cho trình đọc màn hình. [Q6]
- Có cả trạng thái rỗng và trạng thái lỗi. [Q7]
