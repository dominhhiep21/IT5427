# Phase Check — Ideation → Inception

Nguồn: `../approval-handoff/{initiative-brief,decision-log}.md`, `../intent-capture/intent-statement.md`, `../scope-definition/{scope-document,intent-backlog}.md`, `../feasibility/{feasibility-assessment,constraint-register,raid-log}.md`, `../rough-mockups/wireframes.md`.

## Kết luận

**PASS**, với hai điểm đã biết được ghi lại thay vì bị bỏ qua.

## 1. Intent → Scope → Backlog nhất quán

| Kiểm | Cách kiểm | Kết quả |
|---|---|---|
| Mỗi mục trong scope có gốc từ intent | đối chiếu ba mục U1–U3 với bốn mục tiêu của `intent-statement` | **khớp** — AUC, giao diện dự đoán, không hồi quy, cổng chống thoái hoá |
| Mỗi mục trong backlog truy vết được về một mục tiêu | bảng "Truy vết về mục tiêu" của `intent-backlog` | **khớp**, bốn dòng phủ bốn mục tiêu |
| Không có hạng mục nào trong backlog mà scope không khai | đọc `scope-document` mục "Trong phạm vi" | **khớp** — ba đơn vị, không thừa |
| Không có mục tiêu nào không có đơn vị phụ trách | đọc bảng truy vết | **khớp** |

## 2. Mọi mục phạm vi có nền khả thi

| Đơn vị | Nền khả thi | Bằng chứng |
|---|---|---|
| U1 — nới mart + baseline | mart thiếu cột nhưng dữ liệu có trong cleaned; quần thể 110.195 dòng | `feasibility-assessment` F1, bảng số đo |
| U2 — đặc trưng + mô hình + lưu | 2.970 người bán, 8.713 dòng trễ; hai mô hình đều có sẵn trong `scikit-learn` đã ghim | `feasibility-assessment` F3, F4 |
| U3 — giao diện + mốc sàn | tab có sẵn ba mục, bốn thẻ; thêm một mục là thay đổi cục bộ | `wireframes`, `user-flow` |

## 3. Ràng buộc đã được phản ánh vào thiết kế

| Ràng buộc | Có mặt ở đâu trong thiết kế |
|---|---|
| Không thêm phụ thuộc | `build-vs-buy` (B4 dùng lớp có sẵn), `wireframes` (không SHAP) |
| Hợp đồng 5 KPI / 9 bảng / 11 view | `feasibility-assessment` (chỉ thêm cột, không đổi số dòng) |
| Tiếp cận: nhãn vùng, `tabIndex`, tương phản, không token mới | `wireframes` bảng "Ràng buộc tiếp cận", bảng "Nguyên tắc rút ra" |
| Chia tập theo `order_id` | `intent-statement` bảng ranh giới, `feasibility-assessment` F2 |

## 4. Hai điểm đã biết, không chặn

| # | Điểm | Vì sao vẫn PASS |
|---|---|---|
| 1 | **Mốc AUC ≥ 0,70 chưa có bằng chứng đạt được** với khung mới | đường đi đã định nghĩa: đo baseline trước, quyết định tại Build and Test, ghi kết quả dù đạt hay không. Đây là rủi ro đã chấp nhận ở cổng (D-27), không phải lỗ hổng kế hoạch |
| 2 | **R-08** chia tập theo ngày đặt hàng trong khi dự đoán lúc bàn giao | sai lệch đã ghi thành rủi ro có mã, có lý do chọn, và có đường đổi nếu cần |

## 5. Điều phase check này không kiểm

Nó không kiểm nội dung kỹ thuật của thiết kế — việc đó thuộc Domain Design và Contract Design. Nó chỉ kiểm **tính nhất quán giữa các artifact Ideation** và **mọi mục phạm vi có nền khả thi**.

## Ủy quyền chuyển pha

Ideation đủ điều kiện chuyển sang Inception. Ba tài liệu mang sang: `initiative-brief.md` (một trang cho người đọc), `decision-log.md` (28 quyết định, gồm ba lần đảo), `raid-log.md` (rủi ro còn sống).
