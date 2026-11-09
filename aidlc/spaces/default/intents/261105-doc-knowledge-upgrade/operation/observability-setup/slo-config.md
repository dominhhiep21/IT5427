# SLO Config

## 1. Không có SLO theo thời gian

Không có dịch vụ chạy nền nên không có "độ khả dụng 99,9% trong 30 ngày". Hệ chỉ tồn tại khi có người mở nó.

## 2. SLO thay thế: ba cam kết kiểm được

| Mã | Cam kết | Ngưỡng | Đo bằng |
|---|---|---|---|
| SLO-1 | Số liệu trên vùng `don-theo-thang` đúng | **0 sai lệch** so với phép tính độc lập từ `dataset/` | `tests/unit/test_integration_correctness.py` (marker `slow`) |
| SLO-2 | 5 KPI baseline không đổi sau thay đổi | **0 lệch** | `KpiReconciler` trong mỗi lần chạy pipeline |
| SLO-3 | 11 view tồn tại và số dòng 9 bảng mart không đổi | khớp baseline | `test_u2_end_to_end.py` |

Ba cam kết này là loại SLO phù hợp với một pipeline dữ liệu: chúng nói về **tính đúng**, không nói về thời gian hoạt động.

## 3. Ngân sách lỗi

Không có ngân sách lỗi theo thời gian. Thay vào đó: **một sai lệch là một sự cố**. Cổng SLO-1 và SLO-2 đều dùng dung sai 0 — không có "một chút lệch thì chấp nhận".

Lý do: dữ liệu này dùng để trình bày số liệu kinh doanh; một con số sai còn tệ hơn một con số thiếu, vì nó không tự báo.

## 4. Điều không đặt

- Không SLO về độ trễ hiển thị: ngưỡng 2 giây đã nằm trong NFR1 và test, không cần thêm một lớp SLO nữa.
- Không báo cáo tuân thủ SLO theo tuần/tháng: không có bên nhận báo cáo.
