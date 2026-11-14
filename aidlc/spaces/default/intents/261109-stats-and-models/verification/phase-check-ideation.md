# Phase Check — Ideation sang Inception

Kiểm tra tính nhất quán giữa ý định, phạm vi và danh sách công việc trước khi chuyển giai đoạn.

## 1. Ý định → Phạm vi

| Hạng mục trong `scope-document.md` | Có căn cứ trong `intent-statement.md`? | Ghi chú |
|---|---|---|
| S-01 khoảng tin cậy và so sánh hai tỉ lệ | Có | Nằm trong bốn nhóm kiểm định của mục tiêu |
| S-02 tương quan kèm khoảng tin cậy | Có | Cùng nhóm |
| S-03 mô hình phân loại đơn trễ | Có | Mục tiêu thứ hai của ý định |
| S-04 so sánh nhóm hoặc phân phối | Có | Cùng nhóm, mức "nên có" |
| S-05 phân rã mùa vụ | Có | Cùng nhóm, mức "nên có" |
| S-06 lệnh CLI ghi báo cáo | Có | Điều kiện "kết quả đến được cả hai nơi" |
| S-07 tab mới trên dashboard | Có | Cùng điều kiện |

## 2. Phạm vi → Danh sách công việc

| Hạng mục | Đơn vị trong `intent-backlog.md` | Trạng thái |
|---|---|---|
| S-01 | B-01 | Đã có |
| S-02 | B-02 | Đã có |
| S-03 | B-04 | Đã có |
| S-04 | B-06 | Đã có |
| S-05 | B-07 | Đã có |
| S-06 | B-03 | Đã có |
| S-07 | B-05 | Đã có |

## 3. Căn cứ khả thi

- B-01 đến B-03 và B-05 dựa trên hạ tầng có sẵn; rủi ro thấp theo `feasibility-assessment.md`. [Q1]
- B-04 dựa trên hai thư viện cài được và dữ liệu có nhãn; rủi ro trung bình đã ghi trong RAID. [Q2]
- B-06 và B-07 dùng cùng khung kiểm định, nên chi phí biên thấp. [Q3]

## 4. Kết luận

Không phát hiện mâu thuẫn giữa ý định, phạm vi và danh sách công việc. Mọi hạng mục trong phạm vi đều có căn cứ khả thi. Giai đoạn Ideation đủ điều kiện bàn giao. [Q4]
