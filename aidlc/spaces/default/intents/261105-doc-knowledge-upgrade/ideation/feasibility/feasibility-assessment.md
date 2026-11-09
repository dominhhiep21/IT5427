# Feasibility Assessment — Nâng cấp tích hợp dữ liệu Olist

Nguồn bối cảnh: `ideation/intent-capture/intent-statement.md` (mục tiêu, biên giới, chỉ số thành công), cùng `competitive-analysis.md`, `market-trends.md`, `build-vs-buy.md` ở bước Market Research.

## Kết luận tổng quát

**Khả thi, ở mức trung bình, với rủi ro chính là thời gian.** Bốn nhóm chủ đề đều triển khai được trên công nghệ hiện có (Python + pandas + DuckDB + Dash) mà không cần thêm hạ tầng, nhưng quỹ thời gian 1–2 tuần (Q4) là ràng buộc chặt so với khối lượng bốn nhóm cộng với việc nâng cấp giao diện.

## Đánh giá theo nhóm chủ đề

| Nhóm | Khả thi kỹ thuật | Công sức | Ghi chú |
|---|---|---|---|
| Đồng nhất lược đồ / lược đồ trung gian | Cao | Trung bình | Khai báo lược đồ trung gian + ánh xạ từ 9 CSV và cache IBGE; không cần công cụ ngoài. Là nền cho ba nhóm còn lại nên làm trước. |
| Ghép bản ghi / nhận dạng thực thể | Cao | Trung bình | Dữ liệu đã có `customer_unique_id`; phần minh hoạ tập trung vào blocking và tính điểm tương đồng, có thể dùng thư viện so khớp chuỗi (Q3 = B). |
| Xử lý / viết lại truy vấn | Trung bình | Trung bình–cao | Viết lại từ lược đồ trung gian xuống SQL DuckDB là phần khó nhất; nên giới hạn ở tập truy vấn mẫu thay vì trình tối ưu tổng quát. |
| Chọn nguồn dữ liệu | Cao | Thấp | Chỉ có Olist và cache IBGE; cần mô phỏng tình huống chọn theo khả năng truy cập/chi phí, không cần hạ tầng thật. |
| Nâng cấp giao diện | Cao | Trung bình | Dash đã có 3 tab; thêm màn hình và cải thiện bố cục trong cùng framework. |

## Yếu tố thuận lợi

- Không có hệ thống ngoài phải ăn khớp (Q1) — không phải lo hợp đồng tích hợp hay phiên bản API.
- Không có yêu cầu quy định hay dữ liệu cá nhân (Q2) — bỏ được lớp che dữ liệu, phân quyền, kiểm toán truy cập.
- Chỉ chạy localhost (Q6) — không có chi phí hạ tầng, không có rủi ro triển khai.
- Dữ liệu nhỏ (khoảng 100 nghìn đơn) nên vòng lặp thử nghiệm nhanh.

## Yếu tố bất lợi

- Quỹ thời gian 1–2 tuần cho bốn nhóm chủ đề cộng giao diện là eo hẹp; nếu không cắt được, chất lượng từng nhóm sẽ mỏng.
- Nhóm viết lại truy vấn dễ trượt sang xây một trình tối ưu — vượt xa mức "đủ để thể hiện lý thuyết".
- Không có mốc nộp cố định (Q5) vừa là thuận lợi (không bị chặn) vừa là rủi ro (dễ trượt tiến độ mà không có điểm dừng).

## Khuyến nghị

1. **Làm theo thứ tự phụ thuộc**: lược đồ trung gian trước, rồi truy vấn viết lại, rồi ghép bản ghi, rồi chọn nguồn — mỗi nhóm dựa trên lớp trước.
2. **Đặt giới hạn rõ cho từng nhóm**: mỗi nhóm chỉ cần một kịch bản chạy được trên dữ liệu thật và một màn hình hiển thị, không cần đầy đủ tính năng như công cụ thương mại.
3. **Kiểm tra không hồi quy sớm**: chạy bộ test hiện có trước khi thêm phần mới để có mốc so sánh.
4. **Nếu thời gian co lại còn vài ngày**, cắt nhóm viết lại truy vấn xuống mức một truy vấn mẫu thay vì bỏ hẳn — vì nó là phần thể hiện rõ nhất lý thuyết mediation.
