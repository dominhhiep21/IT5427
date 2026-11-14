# Feasibility Assessment — Kiểm định thống kê và mô hình dự báo

Bối cảnh lấy từ `../intent-capture/intent-statement.md` và các tài liệu `../market-research/`. Phần mới gồm một lệnh CLI và phần hiển thị trên dashboard hiện có. [Q1]

## 1. Khả thi kỹ thuật từng phần

| Phần | Đánh giá | Căn cứ |
|---|---|---|
| Kiểm định thống kê | Khả thi, rủi ro thấp | Dữ liệu đã nằm trong DuckDB; `scipy` và `statsmodels` cài được trực tiếp từ PyPI [Q2] |
| Mô hình phân loại đơn trễ | Khả thi, rủi ro trung bình | Có nhãn sẵn trên 96.478 đơn đã giao; `scikit-learn` cài được [Q2]; rủi ro nằm ở mất cân bằng lớp và rò rỉ đặc trưng |
| Hiển thị trên dashboard | Khả thi, rủi ro thấp | Dashboard đã có tab và cơ chế đọc báo cáo; chỉ thêm phần đọc kết quả [Q1] |
| Lệnh CLI mới | Khả thi, rủi ro thấp | Đã có khuôn CLI với các lệnh `run`, `micro-batch`, `replay`; thêm một lệnh cùng kiểu |

## 2. Ranh giới dữ liệu

- Huấn luyện trên toàn bộ 2016-2018 như dữ liệu hiện có. [Q4] Năm 2016 chỉ có 329 đơn, nên nếu mô hình học từ giai đoạn đó thì ảnh hưởng gần như không đáng kể, nhưng cũng không nên kỳ vọng nó giúp ích.
- Chia theo thời gian: huấn luyện trên giai đoạn sớm, kiểm tra trên giai đoạn muộn. [Q5] Cách này phản ánh đúng cách mô hình sẽ được dùng, và tránh việc mô hình nhìn thấy tương lai.

## 3. Rủi ro kỹ thuật chính

- **Mất cân bằng lớp**: chỉ khoảng 8% đơn là trễ, nên độ chính xác (accuracy) là chỉ số gây hiểu nhầm; cần AUC và precision/recall. Mức độ: trung bình.
- **Rò rỉ đặc trưng**: các cột như ngày giao thực tế chỉ có sau khi đơn xong, không được dùng làm đầu vào. Mức độ: cao nếu không kiểm.
- **Chi phí thời gian**: mốc 1 tuần [Q6] là ràng buộc thật; mỗi cổng duyệt tiêu tốn thời gian của người làm, nên cần giữ phạm vi hẹp.

## 4. Kết luận

Đợt này khả thi. Không có ràng buộc pháp lý hay hạ tầng nào cản trở [Q7]; hai thư viện mới đều cài được [Q2]; thời gian chạy không bị giới hạn [Q3]. Rủi ro còn lại thuộc về cách làm mô hình, không phải về khả năng của môi trường.
