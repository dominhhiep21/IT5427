# Performance Requirements — u3-display

Nguồn: `../functional-design/functional-spec.md`, `../functional-design/rules.md`, `../../../inception/requirements-analysis/requirements.md` (NFR5), `../../../inception/contract-design/contract-summary.md` (C2).

Requirements Analysis giao U3 **đúng một** NFR: **NFR5** (tiếp cận). Không có NFR riêng cho hiệu năng, nên các mốc dưới đây mang mã con của NFR5 — chúng là điều kiện để NFR5 đo được, không phải một họ NFR mới.

Tab đọc một tệp JSON vài chục KB rồi dựng thành phần. Không truy vấn, không tính toán.

| Mã | Yêu cầu | Mốc | Cách kiểm |
|---|---|---|---|
| NFR5.1 | Tương phản chữ trên nền của tab mới | tối thiểu **4,5:1** cho chữ thường, 3:1 cho chữ lớn (WCAG AA), đo trên **đúng các cặp** (chữ, nền) mà tab vẽ: `--text` và `--text-2` trên `--surface`, `--surface-sunken`, `--paper` (`--text-3` không dùng cho chữ nhỏ trong tab này vì chỉ đạt 3,85:1) | Test đơn vị đọc token từ `assets/style.css`, tính tỉ lệ và khẳng định trên từng cặp đã liệt kê |

## Vì sao tab mới dùng `--text-2`, không dùng `--text-3`

`--text-3` (`#78857d`) chỉ đạt **3,85:1** trên `--surface` (3,71:1 trên `--surface-sunken`, 3,52:1 trên `--paper`) — dưới mốc 4,5:1. Đó lại đúng là token các thẻ hiện có dùng cho chữ 11–12px. Ba ràng buộc đá nhau: BR3.8 đòi "tương phản như tab hiện có", TSU-3 đòi dùng lại token, BR3.9 cấm thêm token mới.

Cách giải chọn: **tab mới dùng `--text-2` cho mọi chữ dưới 16px**, giữ nguyên `--text-3` cho các tab cũ. Hệ quả:

- Không hạ mốc nào, không đụng giao diện đang chạy, không thêm token.
- Tab mới sẽ **đậm hơn** các tab cũ ở chữ phụ — khác biệt có chủ đích, và là khác biệt duy nhất.
- BR3.8 phải đọc là "tương phản **ít nhất** bằng các tab hiện có", không phải "bằng đúng".
- Việc nâng `--text-3` cho toàn dashboard là một thay đổi riêng, không gộp vào đây.
| NFR5.2 | Mỗi vùng có nhãn cho trình đọc màn hình | 100% vùng nội dung mang `aria-label` hoặc heading ngữ nghĩa | Test đơn vị duyệt cây thành phần và đếm vùng thiếu nhãn |
| NFR5.3 | Đi được bằng bàn phím theo thứ tự đọc | mọi phần tử tương tác nhận focus; `tabIndex` theo thứ tự tóm tắt → thống kê → mô hình | Test đơn vị trên danh sách `tabIndex` |
| NFR5.4 | Không vỡ bố cục ở 1280px | không tràn ngang, không cắt chữ | Xem bằng mắt ở 1280px trong bước 4 của chuỗi xác nhận; ghi kết quả vào `code-summary.md` |
| NFR5.5 | Thời gian dựng tab khi bấm | dưới 1 giây trên máy phát triển | Đo bằng `time.perf_counter` quanh hàm dựng trong test đơn vị; **không** đặt làm cổng CI vì máy CI khác máy dev |
| NFR5.6 | Số lần đọc tệp mỗi callback | đúng một | Đếm bằng stub bọc `read_report` |

## Vì sao mốc hiệu năng không phải NFR riêng

`requirements.md` không đòi hiệu năng cho tab, và một tab đọc tệp cục bộ không có rủi ro hiệu năng thật. NFR5.5 và NFR5.6 được ghi lại vì chúng là điều kiện để tab dùng được, nhưng chúng **không** phải cam kết với người dùng — chúng là ghi chú thiết kế có số đo, và không được biến thành cổng chặn merge.

## Ghi chú

- NFR5.1 tính được bằng số vì màu đến từ token cố định trong `assets/style.css`; nếu tab tự đặt màu mới thì phép kiểm này mất hiệu lực — đó là lý do BR3.9 cấm thêm token.
- Không đặt mốc cho số người dùng đồng thời: dashboard bind `127.0.0.1`, một người.
