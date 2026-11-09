# Feedback Loop

## 1. Vòng lặp hiện có

Không có telemetry tự động chảy về đâu cả. Vòng lặp thật của đợt này là:

```
reviewer / kiểm toán  →  danh sách phát hiện  →  sửa mã hoặc tài liệu  →  test mới khoá lại  →  chạy lại chuỗi xác nhận
```

Mỗi vòng như vậy để lại một test hoặc một dòng runbook. Đó là cách tri thức không bị mất khi phiên kết thúc.

## 2. Sáu phát hiện đáng đưa vào đợt sau

| # | Phát hiện | Loại | Đề xuất |
|---|---|---|---|
| 1 | `bang_giao` khai `loaded: true` nhưng bộ nạp bỏ qua bảng customers (`TD-16`) | khiếm khuyết dữ liệu | nạp thêm bảng customers (join 1:1) hoặc hạ cờ; phải chốt vì đổi hành vi `don_hang` |
| 2 | Bộ test nhanh chưa hermetic (`TD-09`) | nợ test | dựng fixture thay vì đọc `warehouse/`; xoá bước dựng pipeline khỏi CI |
| 3 | Hai bảng `agg_sales_daily`, `agg_delivery_daily` thiếu baseline số dòng | lỗ hổng cổng | thêm số dòng kỳ vọng vào test `u2_end_to_end` |
| 4 | Không có test tự động cho tương phản màu và thứ tự tiêu điểm | lỗ hổng tiếp cận | dùng công cụ đo tương phản trong CI, hoặc ít nhất chụp ảnh so sánh |
| 5 | Không có test tích hợp C5 thật (U4 sinh tệp → tab đọc) | lỗ hổng hợp đồng | thêm test `slow` chạy pipeline đầy đủ rồi đọc tệp thật |
| 6 | Bộ test không chạy callback Dash, nên **ba lỗi UI thật** (nút "Xem chi tiết" chết, màn hình tự mở, treo 12.613 dòng) chỉ lộ ra khi kiểm bằng trình duyệt | lỗ hổng kiểm chứng | thêm một lớp kiểm chạy thật trong trình duyệt (Playwright/chrome-devtools) cho tab "Tích hợp": mở tab, bấm từng thẻ, bấm "Tải lại", đọc console và khẳng định không có `ReferenceError` |

## 3. Ba phát hiện về **quy trình**, không phải mã

| # | Điều học được | Nên làm gì |
|---|---|---|
| 1 | Reviewer bắt được lỗi mà test không bắt (C9 mất vùng, C3 tiêu thụ hình thức) | giữ reviewer adversarial ở các stage thiết kế; đừng coi test xanh là đủ |
| 2 | Sửa tay khối `## Testing Contract` làm gãy hash và chặn plan | không bao giờ sửa tay khối đó; luôn dùng `testing-posture render` |
| 3 | Kiểm toán chéo tài liệu↔mã bằng subagent rẻ hơn nhiều so với để reviewer phát hiện từng cái | chạy một lượt quét trước mỗi cụm stage, không phải sau khi bị trả về |

## 4. Điều không có

- Không có kênh thu thập phản hồi người dùng: không có người dùng ngoài người làm.
- Không có dashboard phân tích hành vi: không có telemetry.
- Không có lịch chạy tự động: vòng lặp này chạy khi có người mở phiên làm việc.
