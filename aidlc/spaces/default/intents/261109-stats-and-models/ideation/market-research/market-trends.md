# Market Trends — Xu hướng kỹ thuật liên quan

Phạm vi lấy từ `../intent-capture/intent-statement.md`: thêm kiểm định thống kê và mô hình dự báo cho một pipeline dữ liệu chạy local. [Q1] Vì không có thị trường thương mại, phần này chỉ ghi những xu hướng ảnh hưởng trực tiếp tới lựa chọn kỹ thuật của đợt. [Q1]

## 1. Phân tích chạy ngay trên tệp cục bộ

Parquet cộng DuckDB đã đủ nhanh cho vài triệu dòng mà không cần cụm hay dịch vụ ngoài; dự án đang đi theo hướng này. [Q1] Hệ quả cho đợt này: kết quả kiểm định và dự báo nên ghi thành tệp trong `data/reports/`, không phụ thuộc một máy chủ nào. [Q2]

## 2. Thư viện học máy đã ổn định

`scikit-learn` vẫn là lựa chọn mặc định cho phân loại cỡ dữ liệu này; các thư viện tăng tốc như `xgboost` hay `lightgbm` chỉ có lợi khi dữ liệu lớn hơn nhiều. [Q4] Với 96.478 đơn đã giao, mô hình tuyến tính có điều chỉnh là đủ để so sánh và giải thích.

## 3. Kiểm định thống kê không cần tự viết

`scipy` và `statsmodels` đã có sẵn kiểm định, khoảng tin cậy và phân rã chuỗi thời gian; tự viết lại vừa tốn công vừa dễ sai. [Q3] Đổi lại phải ghim thêm phiên bản vào `requirements.txt`.

## 4. Tái lập là yêu cầu, không phải điểm cộng

Người dùng mục tiêu là một nhóm nhỏ dùng chung máy, nên kết quả phải chạy lại được trên máy khác bằng cùng lệnh. [Q5] Điều này đẩy các lựa chọn về phía: ghim phiên bản, ghi báo cáo ra tệp, không dùng dịch vụ ngoài.

## 5. Dữ liệu công khai, không có định danh cá nhân thật

Bộ Olist là dữ liệu công khai, đã ẩn danh; không có ràng buộc pháp lý bổ sung cho đợt này. [Q6]
