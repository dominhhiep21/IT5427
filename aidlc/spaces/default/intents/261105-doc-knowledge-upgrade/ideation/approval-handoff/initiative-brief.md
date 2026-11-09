# Initiative Brief — Nâng cấp tích hợp dữ liệu Olist

Tổng hợp từ các tài liệu Ideation: `intent-statement.md`, `stakeholder-map.md`, `competitive-analysis.md`, `feasibility-assessment.md`, `constraint-register.md`, `scope-document.md`, `intent-backlog.md`, `wireframes.md`, `user-flow.md`.

## 1. Ý định và vấn đề

Hệ Olist hiện có pipeline + dashboard chạy được nhưng chưa có lớp tích hợp để thể hiện lý thuyết trong `doc/`; người xem chỉ thấy dashboard báo cáo. Lần nâng cấp giải quyết cả hai: lớp tích hợp đúng lý thuyết và giao diện thể hiện được nó. Người dùng chính: giảng viên/hội đồng chấm đồ án.

## 2. Xác nhận thị trường (tóm tắt)

- Công cụ có sẵn (Trino, Denodo, Splink) làm tốt phần mediation nhưng che thuật toán — ngược với mục tiêu chứng minh hiểu lý thuyết.
- Xu hướng được giữ: lớp ngữ nghĩa dùng chung; các xu hướng khác ghi nhận, không làm.
- Quyết định build-vs-buy: tự xây phần lõi, thư viện mã nguồn mở nhỏ cho phần phụ, chỉ dùng công cụ miễn phí.

## 3. Khả thi và rủi ro

- Khả thi ở mức trung bình; ràng buộc chặt nhất là thời gian 1–2 tuần.
- Rủi ro chính: R-01 thời gian, R-02 viết lại truy vấn phình thành trình tối ưu, R-04 sửa pipeline làm hỏng KPI baseline. Cả ba đã được chấp nhận kèm ứng phó trong `raid-log.md`.
- Ràng buộc: chỉ hệ thống trong repo, chạy local, không đám mây, `dataset/` bất biến, không hồi quy KPI và test.

## 4. Biên giới phạm vi

**Trong phạm vi**: bốn nhóm chủ đề — lược đồ trung gian (sâu), viết lại truy vấn (sâu), ghép bản ghi (tối thiểu), chọn nguồn dữ liệu (tối thiểu); lớp ngữ nghĩa KPI; một tab "Tích hợp"; bộ test bảo vệ hành vi cũ.

**Ngoài phạm vi**: thêm nguồn dữ liệu, ML dự báo giao trễ, đổi công nghệ lớn, đăng nhập/phân quyền, dùng công cụ thương mại, tối ưu truy vấn tổng quát.

## 5. Hình ảnh khái niệm

Năm màn hình trong `wireframes.md`: khung ứng dụng, tổng quan bốn thẻ trạng thái, lược đồ trung gian, viết lại truy vấn, ghép bản ghi, chọn nguồn. Luồng chính: mở tab → xem tổng quan → đi sâu một nhóm → quay lại.

```
[Tổng quan 4 nhóm] --bấm thẻ--> [Chi tiết nhóm] --breadcrumb--> [Tổng quan]
```

<!-- Text fallback: từ màn hình tổng quan bốn nhóm, bấm một thẻ để mở trang chi tiết của nhóm đó, quay lại bằng breadcrumb. -->

## 6. Kế hoạch đội

Một người thực hiện, tự quyết phạm vi và tiến độ; không có nhóm, không có mob. Bước Team Formation đã được bỏ qua vì lý do này.

## 7. Thứ tự thi công

`PB-01 lược đồ trung gian → PB-02 mô tả nguồn → PB-03 chọn nguồn / PB-04 viết lại truy vấn → PB-05 ghép bản ghi → PB-06 lớp ngữ nghĩa → PB-07 tab "Tích hợp" → PB-09 làm mới ba tab`

Đường găng: `PB-01 → PB-02 → PB-04 → PB-07`.

## 8. Khuyến nghị go/no-go

**Go**, với hai điều kiện:

1. Bắt đầu bằng lược đồ trung gian và không mở rộng phạm vi cho đến khi nó chạy được trên dữ liệu thật.
2. Giữ bộ test hiện có làm mốc; mỗi nhóm mới phải có kiểm thử riêng trước khi sang nhóm sau.

## 9. Điểm còn mở

- Ba tab cũ chưa có wireframe làm mới (R-01 của bước Rough Mockups) — chưa chặn, nhưng cần chốt trước khi làm PB-09.
- Cách bấm thẻ tổng quan (R-02) và vị trí thuật ngữ trên màn hình (R-03) sẽ chốt ở bước thiết kế chi tiết.
- Chỉ số thành công vẫn ở mức định tính (theo góp ý của người kiểm tra ở bước Intent Capture).
