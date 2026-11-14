# Câu hỏi — Performance Validation

Không có câu hỏi nào để hỏi bạn.

## Vì sao

Stage này thường hỏi về mẫu tải dự kiến, phân vị độ trễ mục tiêu (p50/p95/p99), lưu lượng cần chịu, và điểm nghẽn nghi ngờ. Cả bốn câu đều cần một hệ thống có lưu lượng. Hệ thống này chạy theo lệnh, một người dùng, một tiến trình — nên cả bốn đã có câu trả lời duy nhất có thể đúng, và mốc đã được chốt từ trước ở `performance-requirements.md` của U1 và U3.

## Consolidated Summary Confirmation

- Stage này không có câu hỏi, nên không có câu trả lời để tóm tắt.
- Không có load test thật vì không có tải. Thay bằng năm phép đo: lặp lại để kiểm tất định, dò quy mô theo số tháng, dò quy mô theo số dòng, thời gian từng phép, thời gian dựng tab.
- Tất cả mốc thời gian dư **ít nhất hai bậc độ lớn**: tầng `stats` 3,5 s so với 300 s; mỗi phép 79–245 ms so với 60 s; dựng tab ~1 ms so với 1 s.
- Ba mốc từng bị `Deferred` ở `build-and-test` — NFR1.2, NFR1.4, NFR1.6 — nay **đã đo được**. Chỉ NFR1.5 ở lại dạng giả định vì `dataset/` bất biến và chỉ có một cỡ.
- Bốn mốc chỉ có **đo thủ công**, không có test canh: NFR1.2 (từng phép), NFR1.4, NFR1.6, NFR5.5. Ghi rõ thay vì đánh "đạt" cho xong.
- Điểm nghẽn lớn nhất không phải thuật toán mà là **nạp thư viện**: ~40% của 3,7 s là chi phí cố định của tiến trình Python.

- Looks correct
- Request changes

[Answer]: Looks correct
