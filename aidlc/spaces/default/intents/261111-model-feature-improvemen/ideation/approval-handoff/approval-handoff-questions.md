# Câu hỏi — Approval & Handoff

## Q1. Xác nhận mục tiêu và phạm vi trước khi chuyển sang Construction

Đợt này: cứu mô hình khỏi trạng thái thua baseline một cột (0,5133 so với 0,5333), bằng cách đổi khung dự đoán sang lúc bàn giao, đơn vị sang dòng hàng, và thêm giao diện dự đoán. Ba đơn vị U1 → U2 → U3, ba Bolt.

- A. Đồng ý, giữ nguyên
- B. Đồng ý nhưng muốn siết phạm vi (nêu ở phần trả lời)
- C. Chưa đồng ý — có chỗ cần sửa
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Chấp nhận hai rủi ro không thể loại bỏ

| Rủi ro | Nội dung |
|---|---|
| **R-01** | Khung bàn giao có thể **không** đạt AUC 0,70 dù đủ 110.195 dòng mẫu. Khi đó kết luận là "không đạt", ghi vào record, và bạn quyết định ở Build and Test. |
| **R-08** | Chia tập theo **ngày đặt hàng** trong khi dự đoán tại thời điểm bàn giao làm yếu tính "ngoài thời gian" của phép chia. Không phải rò rỉ nhãn, nhưng là sai lệch phải biết. |

- A. Chấp nhận cả hai, đã hiểu hệ quả
- B. Chấp nhận R-01, muốn sửa R-08 (chia theo ngày bàn giao) — đổi lại mất so sánh với 64.322/32.156 của đợt trước
- C. Chưa chấp nhận — cần bàn thêm
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q3. Cam kết nguồn lực cho Construction

Đợt này cần khoảng **4–7 tuần** ở nhịp 5–10 giờ/tuần, chia ba Bolt.

- A. Giữ nguyên: 5–10 giờ/tuần, ba Bolt
- B. Giữ ba Bolt nhưng nguồn lực khác (nêu ở phần trả lời)
- C. Đổi số Bolt (nêu ở phần trả lời)
- D. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Ba câu đã trả lời. Bản tóm tắt để bạn xác nhận trước khi chuyển sang Construction:

- **Mục tiêu và phạm vi** [Q1 = A]: giữ nguyên — ba đơn vị U1 → U2 → U3, ba Bolt.
- **Hai rủi ro chấp nhận** [Q2 = A]: **R-01** (khung mới có thể không đạt AUC 0,70 dù đủ 110.195 dòng mẫu) và **R-08** (chia tập theo ngày đặt trong khi dự đoán lúc bàn giao — yếu tính ngoài thời gian, nhưng giữ được so sánh với đợt trước).
- **Nguồn lực** [Q3 = A]: 5–10 giờ/tuần, ba Bolt, ước lượng 4–7 tuần.
- **`initiative-brief.md`**: một trang gồm vấn đề, ba thay đổi, số đo khả thi, rủi ro hàng đầu, phạm vi trong/ngoài, hình dạng giao diện, khuyến nghị **GO** kèm điều kiện.
- **`decision-log.md`**: 28 quyết định, trong đó **ba lần đảo** được ghi lại chứ không viết đè (D-13 → D-14 thuật toán; mốc 0,70 từ "không hạ" về "chưa chốt"; biên phạm vi từ "không loại trừ gì" về ba dòng cụ thể).
- **`verification/phase-check-ideation.md`**: **PASS** — intent/scope/backlog nhất quán, mọi mục có nền khả thi, ràng buộc đã phản ánh vào thiết kế; hai điểm đã biết được ghi rõ là không chặn.

- Looks correct
- Request changes

[Answer]: Looks correct
