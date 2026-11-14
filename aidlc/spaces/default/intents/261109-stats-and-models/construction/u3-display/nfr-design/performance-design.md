# Performance Design — u3-display

Nguồn: `../nfr-requirements/performance-requirements.md` (NFR5.1–NFR5.6), `../functional-design/functional-spec.md`, `../nfr-design/logical-components.md`.

## Quyết định

| # | Quyết định | Phục vụ | Vì sao |
|---|---|---|---|
| PDU-1 | Đọc tệp **một lần** ở đầu callback, giữ `ReportView` trong biến cục bộ rồi dựng toàn bộ nội dung từ đó | NFR5.5, NFR5.6 | Mỗi lần đọc thêm vừa tốn thời gian vừa có thể thấy hai ảnh khác nhau của tệp nếu nó bị ghi lại giữa chừng |
| PDU-2 | Không dựng lại thành phần đã có; chỉ dựng nội dung của tab | NFR5.5 | Dash dựng lại theo `children`, không theo toàn trang |
| PDU-3 | Định dạng số một lượt khi dựng, không định dạng lại trong vòng lặp hiển thị | NFR5.5 | Định dạng là chi phí nhỏ nhưng lặp lại trên mọi ô |
| PDU-4 | Không giữ trạng thái giữa các lần mở tab | NFR5.6 | Tab luôn đọc ảnh mới nhất của tệp; một bộ nhớ đệm sẽ làm người dùng thấy số cũ mà không biết |

## Ngân sách

| Bước | Ngân sách |
|---|---|
| `read_report` trên tệp vài chục KB | ≤ 100 ms |
| Dựng bảy thành phần | ≤ 900 ms |
| **Tổng từ lúc bấm tới lúc thấy nội dung** | **≤ 1 s** (NFR5.5) |

## Điều không làm

- **Không cache `ReportView`.** Tệp nhỏ, đọc lại rẻ; một bộ nhớ đệm chỉ tạo thêm một trạng thái phải làm mới và một cách để hiển thị số cũ.
- **Không đặt `timeout` cứng trong mã.** Ngân sách là mốc nghiệm thu đo trong test, không phải một giới hạn sẽ cắt nội dung giữa chừng.
- **Không đặt ngưỡng thời gian làm cổng CI.** Máy CI khác máy phát triển; một cổng thời gian ở đây sẽ đỏ vì lý do không liên quan tới thay đổi.
