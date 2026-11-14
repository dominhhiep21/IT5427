# Team Assessment

Nguồn: `../scope-definition/scope-document.md`, `../scope-definition/intent-backlog.md`, `../feasibility/feasibility-assessment.md`.

## Team là một người, và năng lực đã được khai

| Mục | Giá trị | Nguồn |
|---|---|---|
| Số người | **1** — người làm đồng thời là người quyết định, không có người phê duyệt thứ hai | `intent-statement` (Q7 = A) |
| Năng lực khai | **5–10 giờ/tuần** | Q1 = B |
| Sáng kiến cạnh tranh cùng nguồn lực | không có sáng kiến nào khác được nêu | `intent-statement` (Q16 = A) |
| Cỡ Bolt | **3 Bolt**, mỗi đơn vị một Bolt | Q2 = A |

## Điều con số 5–10 giờ/tuần thực sự có nghĩa

Đây là ràng buộc mạnh nhất của đợt, mạnh hơn mọi ràng buộc kỹ thuật trong `constraint-register.md`. Ở mức 5 giờ/tuần, một tuần chỉ đủ cho **một** trong ba việc lớn: dựng lại mart và đo baseline, hoặc viết đặc trưng và huấn luyện hai mô hình, hoặc làm giao diện dự đoán.

Hệ quả trực tiếp: ba Bolt không phải là lựa chọn thẩm mỹ, mà là cách duy nhất để mỗi tuần có một kết quả kiểm được.

## Ước lượng, và mức tin cậy của nó

| Đơn vị | Ước lượng thô | Cơ sở |
|---|---|---|
| U1 — nới mart + baseline | 1–2 tuần | thêm 3 cột vào 2 view, cập nhật validator và test, đo một phép AUC |
| U2 — đặc trưng + hai mô hình + lưu | 2–3 tuần | phần lớn nhất: dựng đặc trưng, hai mô hình, cơ chế lưu/nạp mới, test chống rò rỉ |
| U3 — giao diện + mốc sàn | 1–2 tuần | một vùng nhập liệu trong tab có sẵn, một phép kiểm lặp lại, một cổng CI |
| **Tổng** | **4–7 tuần** ở 5–10 giờ/tuần | — |

Đây là **ước lượng**, không phải cam kết: nó dựa trên khối lượng đã thấy ở đợt trước, không dựa trên một phép đo nào của đợt này. Ghi rõ để không ai đọc bảng này thành lịch.

## Ràng buộc về người, không về kỹ thuật

| Ràng buộc | Hệ quả |
|---|---|
| Không có review chéo | mọi lỗi phải do test hoặc do người soát AI bắt; đây là rủi ro đã ghi từ đợt trước |
| Không có ai trực | sự cố phát hiện và sửa bởi chính người chạy |
| Người làm cũng là người duyệt | không có cổng ngoài CI và các cổng của AI-DLC |

## Điều bảng này không nói

Nó không nói người làm yếu hay thiếu kỹ năng nào — không có dữ liệu để khẳng định điều đó, và bịa ra một "khoảng trống kỹ năng" cho đủ bảng là đúng loại bịa mà ideation guardrail cấm. Nó chỉ nói **năng lực thời gian** là giới hạn thật, và mọi kế hoạch phải vừa với nó.
