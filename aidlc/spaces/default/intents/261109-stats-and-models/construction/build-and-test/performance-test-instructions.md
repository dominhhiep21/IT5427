# Performance Test Instructions

Nguồn: `../../u1-statistics/nfr-requirements/performance-requirements.md`, `../../u2-model/nfr-requirements/tech-stack-decisions.md`, `../../u3-display/nfr-requirements/performance-requirements.md`, `../../u3-display/nfr-design/performance-design.md`.

## Mốc và cách đo

| Mã | Mốc | Đo ở đâu | Trạng thái |
|---|---|---|---|
| NFR1.1 | tầng `stats` dưới 5 phút | test `slow` của U1, đồng hồ quanh lần chạy | đo được — lần chạy thật ~1 giây cho riêng `stats` |
| NFR1.2 | mỗi phép dưới 60 s | test đơn vị U1 | **chưa có** — đã đánh `Deferred` |
| NFR1.3 | đỉnh bộ nhớ dưới `quality.memory_fail_mb` | `MemoryProbe` trong test `slow` | đo được |
| NFR1.4 | chi phí phân rã tuyến tính | hai độ dài chuỗi dựng tại chỗ | **chưa có** — `Deferred` |
| NFR1.5 | dữ liệu 5× vẫn dưới 5 phút | không đo được: `dataset/` bất biến, một cỡ | **giả định**, đã ghi `N/A` |
| NFR1.6 | bộ nhớ tuyến tính | khung tổng hợp nhân đôi | **chưa có** — `Deferred` |
| NFR5.5 | tab dựng dưới 1 s | `perf_counter` trong test đơn vị | đo được — trung vị **1,06 ms**, max 2,97 ms trên 20 lần |
| NFR5.6 | đúng một `read_report` mỗi callback | stub đếm | đo được |

## Vì sao bốn mốc bị hoãn thay vì đánh đạt

Đây là điểm tôi muốn giữ rõ: `Deferred` không phải `OK`. NFR1.2, NFR1.4 và NFR1.6 chưa có phép đo nào, và NFR1.5 là giả định không thể kiểm vì chỉ có một cỡ dữ liệu. Đánh chúng `OK` sẽ là nói dối bằng bảng.

## Không đặt cổng thời gian trong CI

Máy CI khác máy phát triển. Một cổng thời gian ở đây sẽ đỏ vì lý do không liên quan tới thay đổi, và cổng đỏ thường trực là cổng bị bỏ qua. Mốc thời gian là **mốc nghiệm thu đo một lần**, ghi vào `code-summary.md`.

## Đo lại khi nào

- Sau mỗi lần đổi danh sách đặc trưng của U2 (huấn luyện lại đổi thời gian).
- Sau mỗi lần đổi truy vấn của U1.
- Khi dữ liệu vào vượt 5 lần cỡ hiện tại — lúc đó NFR1.5 phải đo thật, không suy ra.
