# Decision Log — Giai đoạn Ideation

Mỗi dòng là một quyết định đã chốt, kèm nguồn để tra lại. Số thứ tự theo thời điểm.

| Mã | Quyết định | Lý do | Nguồn |
|---|---|---|---|
| D-01 | Làm cả kiểm định thống kê và mô hình dự báo, thống kê trước | Đề bài yêu cầu thống kê và khuyến khích ML; thống kê cho kết quả thấy được sớm hơn | [Q1] |
| D-02 | Không so sánh với thị trường thương mại; chỉ so sánh công cụ mã nguồn mở | Đây là bài tập môn học, không có thị trường | [Q2] |
| D-03 | Dùng `scipy` hoặc `statsmodels` cho kiểm định | Không tự viết công thức dễ sai | [Q3] |
| D-04 | Dùng `scikit-learn` cho mô hình | Chuẩn cho phân loại, chia dữ liệu, đo AUC | [Q4] |
| D-05 | Người dùng mục tiêu là nhóm nhỏ 2-5 người dùng chung máy | Ảnh hưởng tới cách hiển thị và lưu kết quả | [Q5] |
| D-06 | Không có ràng buộc pháp lý bổ sung | Dữ liệu công khai, không có định danh thật | [Q6] |
| D-07 | Phần mới gồm lệnh CLI và phần hiển thị trên dashboard hiện có | Người dùng cần đọc lại kết quả, không chỉ nhìn màn hình | [Q7] |
| D-08 | Không giới hạn thời gian chạy | Kết quả đúng quan trọng hơn tốc độ | [Q8] |
| D-09 | Huấn luyện trên toàn bộ 2016-2018 | Giữ đúng dữ liệu hiện có, không cắt tuỳ tiện | [Q9] |
| D-10 | Chia dữ liệu theo thời gian | Phản ánh cách mô hình được dùng, tránh nhìn thấy tương lai | [Q10] |
| D-11 | Mốc trong vòng 1 tuần | Ràng buộc thật của đợt | [Q11] |
| D-12 | Phạm vi tối thiểu: cả bốn nhóm kiểm định và một mô hình | Dưới mức này không đủ đáp ứng đề bài | [Q12] |
| D-13 | Thứ tự: kiểm định, rồi mô hình, rồi hiển thị | Phần trước tạo nền và cho kết quả sớm | [Q13] |
| D-14 | Kết quả hiện ở một tab mới trên dashboard | Tách khỏi ba tab báo cáo hiện có | [Q14] |
| D-15 | Ngoài phạm vi: không real-time, không sửa `dataset/` | Giữ đợt trong một tuần | [Q15] |
| D-16 | Bỏ qua Team Formation | Dự án một người, không có nhóm để lập kế hoạch | [Q16] |
| D-17 | Tab mới có hai mục, tóm tắt trên cùng, dùng token sẵn có, chỉ desktop ≥1280px, có trạng thái rỗng và lỗi | Theo câu trả lời phác thảo | [Q17] |
| D-18 | Đi tiếp sang Inception | Các bên đồng ý, rủi ro đã ghi nhận | [Q18] |
