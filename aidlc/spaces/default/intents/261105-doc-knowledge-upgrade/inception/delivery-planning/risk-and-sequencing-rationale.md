# Risk & Sequencing Rationale — Nâng cấp tích hợp dữ liệu Olist

Một **Bolt** là một lượt xây trọn vẹn trên một phần công việc, kết thúc bằng thứ chạy được. Tài liệu này giải thích vì sao sáu Bolt được xếp theo thứ tự hiện tại.

## Mô hình chấm điểm

**Không dùng mô hình chấm điểm chính thức** (người đặt yêu cầu chọn phương án phán đoán). Lý do: sáu đơn vị đã có thứ tự phụ thuộc rõ trong `unit-of-work-dependency.md`, và chấm điểm chỉ có ý nghĩa khi có nhiều đường đi kinh tế khác nhau — ở đây gần như chỉ có một đường hợp lệ.

## Cách xếp thứ tự: lát cắt mỏng trước

Hai lựa chọn hợp lệ khác đã cân nhắc:

| Cách | Ưu | Nhược | Kết luận |
|---|---|---|---|
| Lát cắt mỏng trước | Chứng minh ba mảnh khớp nhau sớm nhất; rủi ro kiến trúc lộ ra ở Bolt 1 chứ không phải Bolt 5 | Bolt 1 phải chạm ba đơn vị, không phải một | **Chọn** |
| Rủi ro nhất trước (viết lại truy vấn) | Làm sớm phần khó nhất | Phải dựng lược đồ và nguồn trước đã, nên không thể đứng đầu DAG | Loại |
| Giá trị thấy được trước (ghép bản ghi) | Dễ trình diễn | Không chứng minh được đường mediation — phần được chấm nặng nhất | Loại |

Lát cắt mỏng thắng vì nó vừa đúng thực hành đã chốt, vừa là cách rẻ nhất để phát hiện sớm nếu kiến trúc sai.

## Ràng buộc DAG đã tôn trọng

Thứ tự Bolt 1 → 2 → 3 → 4 → 5 → 6 tôn trọng mọi cạnh phụ thuộc:

- U2 cần U1 (C8) → Bolt 2 sau Bolt 1.
- U5 cần U2 (C2) → Bolt 3 sau Bolt 2.
- U3 cần U2 và U5 (C1, C3) → Bolt 4 sau Bolt 3.
- U4 độc lập → Bolt 5 có thể đổi chỗ với Bolt 3 hoặc 4 mà không vi phạm DAG.
- U6 cần cả năm đơn vị (C4–C7, C9) → Bolt 6 cuối.

Không có chỗ nào đi ngược DAG.

## Rủi ro và cách xử lý

| Rủi ro | Ảnh hưởng | Ứng phó trong kế hoạch |
|---|---|---|
| Thời gian 1–2 tuần không đủ (điều lo nhất của người đặt yêu cầu) | Cao | Điều kiện dừng ghi trong `bolt-plan.md`: hết thời gian trước Bolt 5 thì giữ Bolt 1–4 và ghi rõ phần còn lại |
| Bolt 4 không khớp số liệu cũ | Cao | Dừng sau hai lần thử, xem lại lược đồ thay vì làm tiếp Bolt 5–6 |
| Ghép bản ghi cho kết quả kém ở ngưỡng 0,85 | Trung bình | Bolt 5 đứng độc lập nên có thể đổi chỗ; nếu kém thì đổi khoá chặn hoặc trường so khớp, không đổi ngưỡng (ngưỡng đã chốt) |
| Lát cắt mỏng phải mở rộng lược đồ ngoài một thực thể | Trung bình | Truy vấn của Bolt 1 đã chọn loại chỉ đọc bảng đơn để tránh phải mở rộng |
| Tab mới làm đỏ test hình dạng dashboard | Thấp | Bolt 6 cập nhật test trong cùng thay đổi, theo thực hành đã chốt |

## Ghi chú về thứ tự không theo giá trị

Bolt 3 (chọn nguồn) không phải phần được chấm nặng nhất nhưng đứng trước Bolt 4 vì U3 cần nguồn đã chọn. Đây là ràng buộc kỹ thuật, không phải ưu tiên giá trị — đã ghi để người đọc không hiểu nhầm.
