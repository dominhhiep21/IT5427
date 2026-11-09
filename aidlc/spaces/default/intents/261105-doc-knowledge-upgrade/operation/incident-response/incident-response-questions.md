# Incident Response — câu hỏi

Không có câu hỏi mới. Stage này chốt bốn runbook cho bốn tình huống thật, ba mức sự cố, và một ma trận leo thang **theo mức** thay vì theo người — vì dự án một người, không có ai để leo thang tới.

## Consolidated Summary Confirmation

Tóm tắt để bạn xác nhận:

1. **Bốn runbook**: pipeline đỏ (theo từng tầng), KPI lệch, số trên vùng `don-theo-thang` sai, dashboard không mở. Mỗi cái có bước kiểm, bước sửa, dấu hiệu dừng.
2. **Ba mức**: P1 = số liệu sai hoặc `dataset/` bị chạm (xử lý ngay); P2 = hệ không chạy được nhưng dữ liệu nguyên (trong ngày); P3 = chạy được nhưng có điểm xấu (khi có thời gian). Không có P4.
3. **Leo thang theo mức, không theo người**: P3→P2 khi lỗi lặp ≥ 3 lần/tuần; P2→P1 khi phát hiện số cũng sai; dừng hẳn khi nguyên nhân ngoài phạm vi (ví dụ dữ liệu nguồn đổi).
4. **Nhật ký sự cố có hai mục thật** của đợt này: vùng số liệu bị mất khi U6 dựng lại tab (P1, đã sửa + thêm 2 test), và plan U5 bị từ chối vì hash lệch (P2, sửa quy trình).
5. **Hậu kiểm bắt buộc**: mỗi P1 thêm một test khoá lại; mỗi P2 thêm một dòng vào runbook.
6. **Không có kênh thông báo, không có người trực thay**: khi vắng, hệ đứng yên — không có gì tự chạy để hỏng thêm.

Does this all look correct?

- A. Looks correct
- B. Request changes

[Answer]: Looks correct