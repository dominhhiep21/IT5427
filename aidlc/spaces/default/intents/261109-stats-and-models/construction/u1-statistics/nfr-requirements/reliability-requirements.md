# Reliability Requirements — u1-statistics

Nguồn: `../functional-design/functional-spec.md`, `../functional-design/rules.md`, `../../../inception/requirements-analysis/requirements.md` (NFR2, NFR3), `../../../inception/contract-design/contract-summary.md` (C1, C2).

Tệp này chỉ mang những yêu cầu **thật sự phi chức năng**. Hành vi đúng/sai của hàm đọc, của bước ghi tệp và của nhánh bỏ qua kiểm định đã là quy tắc chức năng (`BR1.6`, `BR1.9`, `BR1.10`, `BR1.11`) và được kiểm bằng test đơn vị ở `rules.md`; chép chúng vào đây rồi gán một mã NFR mới là gán sai nguồn gốc.

| Mã | Yêu cầu | Mốc | Cách kiểm |
|---|---|---|---|
| NFR3.1 | Không hồi quy 5 KPI baseline | doanh thu 15.419.773,75 BRL; 96.478 đơn delivered; AOV 159,83 BRL; 7.826 đơn trễ; tỉ lệ trễ 8,11% | `KpiReconciler` |
| NFR3.2 | Không hồi quy hình dạng dữ liệu | 9 bảng nguồn, 11 bảng mart, 11 view giữ nguyên số dòng và tên | `StarSchemaValidator` |
| NFR3.3 | Không hồi quy chất lượng dữ liệu | `quality` chế độ `full` xanh | Lần chạy `--stage all` |
| NFR3.4 | Chạy lại cho cùng kết quả | hai lần chạy liên tiếp trên cùng dữ liệu cho nội dung giống nhau, **bỏ qua `generated_at`** ở hai khối vì trường đó cố ý khác nhau giữa hai lần chạy | Test `slow` so hai tệp sau khi loại `generated_at` |
| NFR2.1 | Độ phủ test | `pytest --cov=src --cov-fail-under=80` xanh trên **toàn bộ** bộ test, đúng như CI đang chạy | Cổng phủ trong chuỗi xác nhận và trong CI; mã mới không được làm giảm con số này |

## Ràng buộc kế thừa từ thiết kế chức năng

Không mang mã `NFRx.y` vì gốc của chúng là quy tắc chức năng, không phải yêu cầu phi chức năng:

| Mã | Ràng buộc | Nguồn |
|---|---|---|
| REL-1 | Đọc báo cáo không ném ngoại lệ; năm nhánh trạng thái đều trả `ReportView` — kiểm bằng sáu tệp mẫu: không tồn tại, không parse được, sai phiên bản, thiếu trường bắt buộc, sai kiểu trường, và đủ hai khối | BR1.9, BR1.10 |
| REL-2 | Ghi báo cáo không để lại tệp dở hay tệp tạm | BR1.11 |
| REL-3 | Một kiểm định hỏng điều kiện không kéo cả tầng xuống | BR1.6 |
| REL-4 | Không nở dòng ở mọi bước ghép; grain được nêu trước mỗi lần merge | quy tắc dự án về grain |

## Điều không đặt

Không có mốc sẵn sàng hay khôi phục sau sự cố: đơn vị chạy theo lệnh, không có dịch vụ thường trực. Đặt SLA cho một tiến trình chạy 5 phút là mốc rỗng.
