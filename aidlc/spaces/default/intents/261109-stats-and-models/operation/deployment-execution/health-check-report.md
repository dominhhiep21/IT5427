# Health Check Report

Nguồn: `deployment-log.md`, `smoke-test-results.md`, `../../construction/build-and-test/performance-test-instructions.md`, `../../construction/u3-display/nfr-requirements/performance-requirements.md`.

## Sức khoẻ của hệ thống sau triển khai

Không có dịch vụ thường trực nên không có "uptime" hay "error rate". Sức khoẻ ở đây là **ba câu hỏi sau một lần chạy**: nó chạy được không, mất bao lâu, và có gì bất thường không.

| Câu hỏi | Trả lời | Ngưỡng |
|---|---|---|
| Chạy được không? | có — bốn bước đều xanh | — |
| Tầng `stats` mất bao lâu? | ~1 giây trên dữ liệu thật | dưới 5 phút (NFR1.1) |
| Tab dựng mất bao lâu? | trung vị **1,06 ms**, max 2,97 ms trên 20 lần | dưới 1 giây (NFR5.5) |
| Bộ nhớ đỉnh? | dưới `quality.memory_fail_mb` (2048 MB) qua `MemoryProbe` | NFR1.3 |
| Có lỗi trong nhật ký không? | không có dòng `level: error` nào trong lần chạy | — |

## Trạng thái mô hình — mục duy nhất không đạt

| Chỉ số | Giá trị | Đánh giá |
|---|---|---|
| AUC | 0,5133 | **dưới mốc 0,70** |
| Ngưỡng chọn | 0,40 | đến từ lưới 19 điểm, F1 cao nhất |
| Precision | 0,0866 | trong số đơn bị gắn cờ, ~1/12 thật sự trễ |
| Recall | 0,2645 | bắt được ~1/4 đơn trễ thật |

Đây là **hạn chế đã biết của thiết kế**, không phải hệ thống hỏng: mô hình chỉ dùng thông tin có lúc đặt hàng, và nhãn trễ phụ thuộc chủ yếu vào những gì xảy ra sau đó. Đợt cải thiện đặc trưng đã ghi trong nhật ký record với mục tiêu AUC ≥ 0,70.

## Bốn mục chưa đo được

| Mục | Trạng thái |
|---|---|
| NFR1.2 (thời gian từng phép) | chưa có phép đo — `Deferred` |
| NFR1.4 (chi phí phân rã tuyến tính) | chưa có phép đo — `Deferred` |
| NFR1.6 (bộ nhớ tuyến tính) | chưa có phép đo — `Deferred` |
| NFR1.5 (dữ liệu 5×) | giả định, không kiểm được vì `dataset/` bất biến |

## Kết luận

Hệ thống khoẻ ở mọi mặt vận hành và **yếu ở đúng một mặt**: chất lượng mô hình. Không có gì trong báo cáo này bị ẩn — cả bốn mục chưa đo và một mục không đạt đều nằm trong bảng, không nằm trong ghi chú.
