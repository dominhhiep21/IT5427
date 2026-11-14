# Constraint Register — Ràng buộc của đợt

Các ràng buộc dưới đây giới hạn cách làm; chúng không phải yêu cầu chức năng. Bối cảnh: `../intent-capture/intent-statement.md` và `../market-research/build-vs-buy.md`.

## Kỹ thuật

| Mã | Ràng buộc | Loại | Ảnh hưởng | Nguồn |
|---|---|---|---|---|
| TC-01 | Python 3.13 trên Windows, chạy từ `.venv` của repo | Môi trường | Thư viện phải hỗ trợ 3.13 và có bánh sẵn cho Windows | [Q2] |
| TC-02 | Mọi phụ thuộc mới phải ghim phiên bản trong `requirements.txt` và ghi lý do | Quy ước dự án | Hai thư viện mới phải được thêm cùng lúc với mã dùng chúng | [Q1] |
| TC-03 | View DuckDB chứa đường dẫn tuyệt đối vào Parquet | Môi trường | Phần đọc kết quả phải chạy sau `integrate`, không được giả định vị trí tệp | [Q4] |
| TC-04 | Không có môi trường thứ hai: staging, production, cloud đều không có | Triển khai | "Phát hành" là chạy lại từ mã nguồn trên máy | [Q7] |
| TC-05 | `dataset/` là dữ liệu gốc, chỉ đọc | Dữ liệu | Mọi dữ liệu dẫn xuất phải ghi ra `data/` hoặc `warehouse/` | [Q4] |
| TC-06 | Thời gian chạy không bị giới hạn, miễn kết quả đúng | Hiệu năng | Có thể huấn luyện lại toàn bộ thay vì tối ưu phức tạp | [Q3] |

## Dữ liệu

| Mã | Ràng buộc | Ảnh hưởng | Nguồn |
|---|---|---|---|
| DC-01 | Năm 2016 chỉ có 329 đơn | Giai đoạn 2016 không đại diện; không dùng để đánh giá mô hình | [Q4] |
| DC-02 | Chỉ khoảng 8,11% đơn đã giao là trễ | Phải dùng chỉ số phù hợp lớp mất cân bằng | [Q5] |
| DC-03 | Chia dữ liệu theo thời gian | Không được chia ngẫu nhiên cho kết quả báo cáo chính | [Q5] |

## Tổ chức

| Mã | Ràng buộc | Ảnh hưởng | Nguồn |
|---|---|---|---|
| OC-01 | Mốc trong vòng 1 tuần | Phạm vi phải hẹp; mỗi phần thêm vào đều phải đáng công | [Q6] |
| OC-02 | Không có trở ngại bên ngoài | Không cần kế hoạch dự phòng về người hay máy | [Q7] |

## Pháp lý

| Mã | Ràng buộc | Nguồn |
|---|---|---|
| RC-01 | Không có ràng buộc pháp lý bổ sung; dữ liệu công khai, không có định danh cá nhân thật | [Q7] |
