# SLO Report

Kỳ báo cáo: đợt nâng cấp 2026-11-05 → 2026-11-09.

## 1. Ba cam kết và kết quả

| Mã | Cam kết | Ngưỡng | Kết quả | Đạt? |
|---|---|---|---|---|
| SLO-1 | Số trên vùng `don-theo-thang` khớp phép tính độc lập từ `dataset/` | 0 sai lệch | 0 sai lệch (2 test `slow`) | đạt |
| SLO-2 | 5 KPI baseline không đổi sau thay đổi | 0 lệch | lệch 0 trong mọi lần chạy pipeline của đợt | đạt |
| SLO-3 | 11 view tồn tại, số dòng 9 bảng mart không đổi | khớp baseline | khớp | đạt |

## 2. Ngân sách lỗi

Đã dùng: **0**. Không có lần nào số liệu sai lọt qua cổng trong đợt này.

Ghi chú quan trọng: điều đó **không** chứng minh hệ không có lỗi — nó chỉ nói cổng hiện có chưa bắt được lỗi nào. Một cổng yếu cũng cho 0.

## 3. Sự cố trong kỳ

| Ngày | Mức | Sự cố | Ảnh hưởng SLO |
|---|---|---|---|
| 2026-11-08 | P1 | Vùng số liệu mất khỏi giao diện khi U6 dựng lại tab | không (số liệu vẫn đúng, chỉ không hiển thị) |
| 2026-11-09 | P2 | Plan U5 bị engine từ chối vì `contract_sha256` lệch | không |

Cả hai đã đóng, mỗi cái kèm một biện pháp khoá lại.

## 4. Điều báo cáo này không nói

- Không có số liệu theo thời gian: hệ không chạy nền, không có chuỗi thời gian.
- Không có tỉ lệ tuân thủ theo tuần/tháng: chỉ một kỳ.
- Không có SLO về độ trễ: ngưỡng 2 giây thuộc NFR1 và đã có test riêng.
