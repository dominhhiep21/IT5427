# Đánh giá User Stories

## Quyết định: Execute

## Lý do

- Lần nâng cấp có bề mặt người dùng mới (tab "Tích hợp" với màn hình tổng quan và bốn màn hình chi tiết) nên hành vi cần được mô tả ở mức người dùng, không chỉ ở mức yêu cầu kỹ thuật.
- Có hai persona với nhu cầu khác nhau (người chấm cần thấy quá trình, người vận hành cần kiểm tra được) nên câu chuyện giúp tách rõ hai loại hành vi.
- Các hành vi có tính "kiểm chứng được hay không" (chạy truy vấn, đối chiếu KPI, xem cặp ghép) cần tiêu chí Given/When/Then để viết test theo TDD.
- Đây không phải refactor thuần, không phải bugfix, không phải thay đổi hạ tầng — ba trường hợp sẽ khiến bước này bị bỏ qua.

## Các yếu tố đã xét

| Yếu tố | Kết luận |
|---|---|
| Loại dự án | Nâng cấp có bề mặt người dùng, brownfield |
| Số persona | 2 — người chấm và người vận hành |
| Độ phức tạp nghiệp vụ | Trung bình: bốn nhóm chủ đề, mỗi nhóm một hành vi chính |
| Phối hợp nhiều người | Không — một người làm, nên câu chuyện chủ yếu phục vụ kiểm thử và trình bày |
| Mức độ sẵn có của yêu cầu | Cao: 36 ID `FR`/`NFR` đã có từ bước Requirements Analysis |

## Khu vực câu chuyện đem lại giá trị nhất

1. **Nhóm 2 — viết lại truy vấn**: nhóm được làm sâu nhất, cần tiêu chí đối chiếu số liệu rõ ràng.
2. **Nhóm 5 — giao diện**: nơi hành vi người dùng dày nhất (trạng thái, điều hướng, bàn phím).
3. **Nhóm 6 — không hồi quy**: chốt điều kiện "không làm hỏng hệ thống đang chạy" thành câu chuyện có tiêu chí đo được.

## Ghi chú

- Tổng 16 câu chuyện, 42 tiêu chí chấp nhận (đếm theo mã `AC`), 31 ID yêu cầu con được truy vết, chia theo nhóm chủ đề theo quyết định của người dùng.
- Không có câu chuyện nào thuộc "Won't Have": các mục ngoài phạm vi đã bị loại từ bước yêu cầu, không cần câu chuyện để đánh dấu.
