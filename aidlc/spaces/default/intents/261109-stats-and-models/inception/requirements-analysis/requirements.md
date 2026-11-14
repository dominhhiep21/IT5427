# Requirements — Kiểm định thống kê và mô hình dự báo

Nguồn: `../../ideation/intent-capture/intent-statement.md`, `../../ideation/scope-definition/scope-document.md`, `../../ideation/scope-definition/intent-backlog.md`, `../../inception/practices-discovery/team-practices.md`, và các câu trả lời Q1–Q6 trong `requirements-analysis-questions.md`.

## Functional Requirements

### FR1 — Kiểm định thống kê

| Mã | Yêu cầu | Tiêu chí đạt | Nguồn |
|---|---|---|---|
| FR1.1 | Báo cáo tỉ lệ giao trễ toàn kỳ kèm khoảng tin cậy Wilson 95% và cỡ mẫu | Với dữ liệu thật cho ra tỉ lệ 8,11% và khoảng tin cậy chứa giá trị đó, có ghi số đơn trễ và số đơn đã giao | [Q1] |
| FR1.2 | So sánh hai tỉ lệ trễ giữa hai bang bằng kiểm định z gộp, kèm khoảng tin cậy cho hiệu | Chỉ so sánh bang có tối thiểu 100 đơn đã giao; kết quả gồm hiệu, z, p, khoảng tin cậy, kết luận có ý nghĩa hay không | [Q1] |
| FR1.3 | Tương quan Pearson giữa giá hàng và phí vận chuyển, kèm khoảng tin cậy Fisher 95% | Trả về r, n, khoảng tin cậy; n bằng số dòng hàng hợp lệ | [Q1] |
| FR1.4 | So sánh nhóm hoặc kiểm định phân phối cho một cặp biến có ý nghĩa | Có nêu điều kiện áp dụng và bậc tự do; từ chối chạy khi mẫu không đủ điều kiện | [Q1] |
| FR1.5 | Phân rã mùa vụ chuỗi doanh thu theo tháng thành ba thành phần | Trả về chuỗi xu hướng, mùa vụ và phần dư theo từng tháng của giai đoạn có dữ liệu | [Q1] |

### FR2 — Mô hình phân loại đơn trễ

| Mã | Yêu cầu | Tiêu chí đạt | Nguồn |
|---|---|---|---|
| FR2.1 | Dựng đặc trưng chỉ từ thông tin biết trước thời điểm giao hàng | Danh sách đặc trưng không chứa ngày giao thực tế, số ngày giao, hay cờ trễ; có test khẳng định điều này | [Q3] |
| FR2.2 | Chia dữ liệu theo thời gian, huấn luyện trên giai đoạn sớm và kiểm tra trên giai đoạn muộn | Có ghi rõ mốc chia; không rò rỉ dữ liệu tương lai vào tập huấn luyện | [Q3] |
| FR2.3 | Báo cáo AUC trên tập kiểm tra, đạt tối thiểu 0,70 | Con số AUC có trong báo cáo, kèm cỡ mẫu từng tập | [Q3] |
| FR2.4 | Chọn ngưỡng cảnh báo từ đường cong precision/recall và báo cáo cả hai chỉ số ở ngưỡng đó | Báo cáo ghi ngưỡng, precision, recall và cách chọn | [Q3] |

### FR3 — Báo cáo kết quả

| Mã | Yêu cầu | Tiêu chí đạt | Nguồn |
|---|---|---|---|
| FR3.1 | Ghi một tệp JSON chứa cả phần thống kê và phần mô hình | Tệp có thời điểm sinh, mức ý nghĩa, độ tin cậy, và hai khối kết quả | [Q2] |
| FR3.2 | Ghi tệp qua `AtomicWriter`, không ghi đè trực tiếp | Có kiểm tra số dòng sau khi ghi như các báo cáo hiện có | [Q2] |

### FR4 — Tab kết quả trên dashboard

| Mã | Yêu cầu | Tiêu chí đạt | Nguồn |
|---|---|---|---|
| FR4.1 | Thêm một tab mới có hai mục: thống kê và mô hình; dải tóm tắt nằm trên cùng | Mở tab thấy dải tóm tắt trước, rồi tới hai mục theo thứ tự | [Q6] |
| FR4.2 | Hiện trạng thái rỗng khi chưa có báo cáo và trạng thái lỗi khi báo cáo hỏng | Hai trạng thái có câu chữ riêng; trạng thái rỗng nêu câu lệnh cần chạy | [Q6] |
| FR4.3 | Dùng token và thành phần sẵn có trong `assets/style.css`, chỉ thiết kế cho màn hình từ 1280px | Không thêm bộ thành phần mới; không vỡ bố cục ở 1280px | [Q6] |

### FR5 — Nối vào vận hành hiện có

| Mã | Yêu cầu | Tiêu chí đạt | Nguồn |
|---|---|---|---|
| FR5.1 | Thêm tầng `stats` vào chuỗi `run --stage`, không thêm lệnh con CLI | `python -m src.pipeline run --stage stats` chạy được; số lệnh con của CLI vẫn là 3 | [Q4] |
| FR5.2 | Thêm nhánh đang làm vào cả hai danh sách trigger của CI | `ci.yml` có nhánh trong `on.push.branches` và `on.pull_request.branches` | [Q4] |
| FR5.3 | Cập nhật README mục CI, mục Test và CHANGELOG trong cùng thay đổi | README khớp `ci.yml`; CHANGELOG có mốc mới | [Q4] |

## Non-Functional Requirements

| Mã | Yêu cầu | Tiêu chí đạt | Nguồn |
|---|---|---|---|
| NFR1 | Thời gian chạy | Phần kiểm định dưới 5 phút; huấn luyện mô hình dưới 15 phút trên máy phát triển | [Q4] |
| NFR2 | Độ phủ test | `pytest --cov=src --cov-fail-under=80` xanh trên toàn bộ bộ test | [Q5] |
| NFR3 | Không hồi quy | 5 KPI baseline, số dòng 9 bảng nguồn và 11 view giữ nguyên; `quality` chế độ `full` và `KpiReconciler` xanh | [Q5] |
| NFR4 | Chất lượng mã | `ruff check .` và `ruff format --check` sạch; không thêm ngoại lệ mới; tệp mới được thêm vào danh sách trong `ci.yml` | [Q5] |
| NFR5 | Tiếp cận | Bàn phím đi được toàn tab mới; tương phản đạt như các tab hiện có; mỗi vùng có nhãn cho trình đọc màn hình | [Q6] |

## Assumptions & Open Questions

- Có thể tách ngưỡng cảnh báo khỏi 0,5 mà không đổi cách đánh giá AUC. [Q3]
- Dữ liệu 2016 quá ít đơn nên không dùng để đánh giá mô hình. [Q3]
