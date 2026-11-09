# Phase Check — Ideation → Inception

Bước kiểm tra ranh giới pha, chạy ở bước Approval & Handoff. Phạm vi: tính nhất quán giữa ý định, phạm vi và backlog, và việc mọi mục phạm vi đều có cơ sở khả thi.

## 1. Ý định → Phạm vi → Backlog

| Kiểm tra | Kết quả | Ghi chú |
|---|---|---|
| Mục tiêu trong `intent-statement.md` có mặt trong `scope-document.md` | Đạt | Cả bốn nhóm chủ đề đều có dòng tương ứng |
| Mọi nhóm chủ đề trong phạm vi có mục backlog | Đạt | Bốn nhóm ánh xạ vào PB-01, PB-02/03, PB-04, PB-05 |
| Mọi mục backlog Must truy được về một nhóm chủ đề hoặc bảo vệ không hồi quy | Đạt | PB-06 là Should; PB-08 bảo vệ không hồi quy; PB-07 là giao diện |
| Biên giới ngoài phạm vi không mâu thuẫn với mục tiêu | Đạt | Không mục tiêu nào cần thêm nguồn, ML, hay công nghệ mới |
| Ràng buộc thời gian 1–2 tuần phù hợp với phạm vi | Đạt có điều kiện | Chỉ đạt nếu mỗi nhóm giữ ở một kịch bản; đã ghi ở R-01 |

## 2. Mọi mục phạm vi có cơ sở khả thi

| Mục | Cơ sở trong `feasibility-assessment.md` |
|---|---|
| Lược đồ trung gian | Khả thi cao, công sức trung bình |
| Viết lại truy vấn | Khả thi trung bình, công sức trung bình–cao, có rủi ro phình phạm vi |
| Ghép bản ghi | Khả thi cao, có dữ liệu sẵn để minh hoạ |
| Chọn nguồn dữ liệu | Khả thi cao, công sức thấp, cần mô phỏng tình huống |
| Giao diện | Khả thi cao, thêm thư viện dmc |

## 3. Nhất quán với quyết định ở các bước trước

| Cặp tài liệu | Kết quả |
|---|---|
| `intent-statement.md` ↔ `scope-document.md` | Đạt — bốn nhóm, biên giới nguồn dữ liệu, không hồi quy |
| `build-vs-buy.md` ↔ `constraint-register.md` | Đạt — chỉ công cụ mã nguồn mở, chạy local |
| `feasibility-assessment.md` ↔ `intent-backlog.md` | Đạt — nhóm khó nhất (viết lại truy vấn) được làm sâu nhưng giới hạn ở tập truy vấn mẫu |
| `wireframes.md` ↔ `scope-document.md` | Đạt một phần — một tab mới đúng phạm vi; ba tab cũ chưa có wireframe (O-01) |

## 4. Cảnh báo

- **O-01**: PB-09 "làm mới ba tab hiện có" nằm trong backlog nhưng chưa có thiết kế; nếu làm, cần thêm wireframe trước khi sinh code.
- **O-04**: ba chỉ số thành công chưa có ngưỡng đo; acceptance criteria ở bước Requirements Analysis sẽ phải đặt ngưỡng thay.
- Không có mâu thuẫn chặn chuyển pha.

## 5. Kết luận

**Đạt để chuyển sang Inception**, với hai cảnh báo O-01 và O-04 được mang theo dưới dạng điểm còn mở trong `initiative-brief.md`.

- [x] Đã kiểm tra tính nhất quán ý định → phạm vi → backlog
- [x] Đã kiểm tra cơ sở khả thi cho từng mục phạm vi
- [x] Đã ghi các cảnh báo cần theo dõi ở Inception
