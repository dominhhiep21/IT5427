# Rollback Runbook

Nguồn: `deployment-strategy.md`, `cd-config.md`, `docs/runbook.md`, `../../construction/build-and-test/build-instructions.md`.

## Nguyên tắc

Không có triển khai từ xa, nên không có "rollback hệ thống". Có **bốn** thứ có thể hỏng, và mỗi thứ có một cách lùi riêng. Điều quan trọng: ba trong bốn lùi được mà không mất dữ liệu, vì `dataset/` bất biến và mọi thứ khác sinh lại được.

## Bảng lùi

| Hỏng gì | Dấu hiệu | Cách lùi | Mất gì |
|---|---|---|---|
| Mã nguồn mới | chuỗi xác nhận đỏ ở bước 1 | `git revert <commit>` hoặc `git checkout <commit tốt>` rồi chạy lại bước 1 | không |
| Phụ thuộc bị nâng | bộ `slow` của U1 đỏ, số KPI lệch | sửa `requirements.txt` về bản cũ, `pip install -r requirements.txt`, chạy lại bộ `slow` | không |
| Dữ liệu dẫn xuất hỏng | bước 2 đỏ, `QualityGate` báo check hỏng | xoá `data/`, `warehouse/`, `logs/`, `inbox/` rồi `run --stage all` | không — sinh lại từ `dataset/` |
| Báo cáo hỏng hoặc sai phiên bản | tab hiện `loi` kèm thông điệp phiên bản | `run --stage stats` sinh lại | không |
| Tệp báo cáo bị sửa tay | tab hiện `loi` | `run --stage stats` ghi đè | không |

## Trình tự khi chuỗi đỏ

1. **Dừng.** Không chạy tiếp bước sau — kết quả của nó đo trên dữ liệu chưa đúng.
2. Xác định bước đỏ đầu tiên. Mỗi bước có nguyên nhân riêng, và bước sau không sửa được bước trước.
3. Lùi đúng một mục ở bảng trên.
4. Chạy lại từ bước 1 của chuỗi, không phải từ bước vừa sửa.

## Điều không lùi được

`dataset/` — nhưng nó cũng không bao giờ bị sửa, nên không cần lùi. Nếu ai đó sửa nó, cách duy nhất là lấy lại bản gốc; repo không giữ bản sao.

## Sau khi lùi

Ghi một dòng vào `CHANGELOG.md` mục **Sửa** nếu bản lùi đã từng được đưa lên nhánh chung. Không cần ghi nếu nó chưa rời máy.

## Kiểm tra khói sau khi lùi

Chạy lại đủ bốn bước. Không chấp nhận "bước 1 xanh là đủ" — bước 2 mới là chỗ `QualityGate` và `KpiReconciler` nói rằng dữ liệu còn đúng.
