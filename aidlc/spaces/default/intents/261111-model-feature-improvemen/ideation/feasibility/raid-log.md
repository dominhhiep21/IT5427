# RAID Log

Nguồn: `feasibility-assessment.md`, `constraint-register.md`, `../intent-capture/intent-statement.md`, `../market-research/competitive-analysis.md`.

## Risks

| Mã | Rủi ro | Khả năng | Tác động | Ứng phó |
|---|---|---|---|---|
| **R-01** | Khung bàn giao **không** đạt AUC 0,70 dù đủ 110.195 dòng mẫu | Trung bình | Cao — mục tiêu chính của đợt không đạt | đo sớm: baseline trước, rồi mô hình đầu tiên ngay khi có đặc trưng; Q19 đã chốt ai quyết định và ở mốc nào |
| **R-02** | Mô hình mới vẫn **thua** baseline `customer_state` đo lại | Thấp–trung bình | Cao — kết luận phải là "hướng này không cứu được" | Q3 = B cho một lần thử cuối bằng mô hình cây rồi công bố kết luận |
| **R-03** | Nới mart (O1) làm lệch hợp đồng 11 view hoặc số dòng, khiến CI đỏ ở nhiều nơi | Trung bình nếu chọn O1 | Trung bình — mất thời gian, không mất dữ liệu | O2 (đọc cleaned) tránh hẳn rủi ro này; nếu chọn O1 thì thêm cột, **không** đổi số dòng |
| **R-04** | Rò rỉ qua đơn vị lồng nhau làm AUC đẹp giả | Trung bình | Cao — kết luận sai mà không ai biết | TC-04: chia theo `order_id`; test khẳng định không đơn nào ở cả hai phía |
| **R-05** | Đặc trưng dẫn xuất từ `order_approved_at`/`order_delivered_carrier_date` bị dùng quá tay thành rò rỉ | Trung bình | Cao | SC-01: chỉ số ngày, không dùng giá trị ngày thô; kiểm trong mã |
| **R-06** | Mô hình lưu ra đĩa không nạp lại cho cùng kết quả (phiên bản thư viện, thứ tự đặc trưng) | Thấp | Trung bình — giao diện dự đoán sai mà không rõ | TC-09: phép kiểm lặp lại hai lần chạy |
| **R-07** | Mốc sàn 0,55 neo vào khung cũ nên cho qua mô hình vẫn thua baseline | Cao (nếu baseline đo lại > 0,55) | Trung bình | SC-03: xem lại mốc sàn ngay sau phép đo baseline |
| **R-08** | Chia tập theo ngày **đặt hàng** trong khi dự đoán tại thời điểm **bàn giao** làm yếu tính "ngoài thời gian" của phép chia | Chắc chắn xảy ra | Thấp — không phải rò rỉ nhãn, nhưng là sai lệch phải biết | đã ghi trong `feasibility-assessment.md`; nếu cần chia chặt theo thời điểm dự đoán thì đó là thay đổi riêng |

## Assumptions

| Mã | Giả định | Nếu sai thì sao |
|---|---|---|
| **A-01** | Thông tin tuyến đường duy nhất dữ liệu này có là bang/mã bưu chính của người bán so với người mua | nếu có nguồn khác thì phải mở lại phạm vi |
| **A-02** | Nhãn trễ là của đơn và không đổi theo dòng hàng | nếu có nhãn cấp dòng hàng thì quy tắc chia tập phải xét lại |
| **A-03** | `HistGradientBoostingClassifier` trong `scikit-learn==1.6.1` chạy được trên Python 3.13/Windows | nếu không, quay về hồi quy logistic |
| **A-04** | 110.195 dòng hàng là đủ để học đặc trưng theo người bán (2.970 người bán) | nếu không, phải gộp người bán theo bang |

## Issues

| Mã | Vấn đề | Trạng thái |
|---|---|---|
| **I-01** | Mart không có `order_delivered_carrier_date`, `order_approved_at`, `seller_state` | **đã chốt**: nới mart, chỉ thêm cột, không đổi số dòng |
| **I-02** | Chưa có cơ chế lưu/nạp mô hình nào trong repo | **đã chốt**: tệp nhị phân trong `data/models/` + JSON mô tả đặc trưng và phiên bản thư viện |
| **I-03** | Hai dòng hàng đã giao thiếu carrier date (trên 110.197) | **đã chốt**: lọc khỏi quần thể, ghi rõ số bị lọc trong báo cáo |

## Dependencies

| Mã | Phụ thuộc | Vào đâu |
|---|---|---|
| **D-01** | Phép đo baseline trong khung mới phải xong **trước** khi viết bất kỳ đặc trưng nào | Q21 = A |
| **D-02** | Quần thể và mốc cắt dùng chung cho baseline, mô hình logistic và mô hình cây | phép so công bằng |
| **D-03** | Giao diện dự đoán phụ thuộc cơ chế lưu/nạp mô hình | Q12 = A, Q14 = A |
| **D-04** | Mốc sàn CI phụ thuộc giá trị baseline đo lại | SC-03 |
