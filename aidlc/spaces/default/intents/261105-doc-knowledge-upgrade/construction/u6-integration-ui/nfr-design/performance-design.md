# Performance Design — u6-integration-ui

Nguồn: `nfr-requirements/performance-requirements.md` (NFR1.1–NFR1.4), `nfr-design/security-design.md` (ADR-U6-S1), `functional-design/functional-spec.md` (W1–W7).

## 1. Chiến lược giữ ngân sách 2 giây

| Việc | Ngân sách | Cách giữ |
|---|---|---|
| Mở tab lần đầu | < 2 giây | Layout chỉ dựng khung; callback `load_overview` đọc C5/C6/C7 một lần rồi giữ trong state (ADR-U6-S1) |
| Đổi màn hình, đổi thực thể | < 2 giây | Chỉ vẽ lại từ dữ liệu đã có trong bộ nhớ tiến trình; không gọi lại hợp đồng |
| Chạy một truy vấn mẫu | < 2 giây | **Tính cả phần nạp CSV**: `run_template` nạp CSV mỗi lần chạy (không đệm), nên ngân sách của tab là tổng `load_ms + elapsed_ms + vẽ`; số thật của ba mẫu ghi ở Build and Test, và nếu vượt 2 giây thì đó là phát hiện để sửa cách nạp, không phải để nới ngưỡng |
| Đề xuất nguồn | < 2 giây | U5 trả trong bộ nhớ, không I/O ngoài |

## 2. Quy tắc

- Không gọi hợp đồng nào ngoài callback (ADR-U6-S1).
- Dữ liệu mỗi màn hình được giữ trong state của tab; quay lại tổng quan không tải lại.
- Trong lúc chạy, nút ở trạng thái chờ và vùng kết quả hiện khung tải; không vẽ lại toàn trang.
- Bảng lớn (bảng cặp) chỉ vẽ số dòng tối đa mà C5 đã cắt sẵn (U4 giới hạn 10.000 cặp); giao diện không cắt thêm để không giấu dữ liệu.

## 3. Đo

`time.perf_counter` quanh từng callback trong test dashboard; số thật của lần chạy trên dữ liệu Olist ghi vào `code-summary.md` ở Build and Test. Vượt ngân sách là ghi nhận, không phải lỗi chặn (đồng bộ BR3.8 của U3).

## 4. Không áp dụng

Không có yêu cầu thông lượng, tải đồng thời hay bộ nhớ đệm phân tán: dashboard chạy local, một người dùng.
