# Requirements — Nâng cấp tích hợp dữ liệu Olist

Nguồn: `ideation/intent-capture/intent-statement.md`, `ideation/scope-definition/scope-document.md`, `inception/practices-discovery/team-practices.md`, và các artifact CodeKB của repo (`business-overview.md`, `architecture.md`, `code-structure.md`).

## Intent analysis

Mục tiêu không phải thêm tính năng kinh doanh mới, mà là **làm cho bốn nhóm lý thuyết tích hợp dữ liệu trở nên quan sát được trên hệ thống thật**: người xem (giảng viên/hội đồng) phải thấy được lược đồ trung gian, quá trình viết lại truy vấn, các cặp bản ghi được ghép, và lý do chọn nguồn — không chỉ thấy báo cáo cuối. Hệ hiện tại đã có pipeline và dashboard ổn định; phần lớn giá trị nằm ở việc **phơi ra** những gì đang bị ẩn, chứ không phải ở hạ tầng mới.

## Functional requirements

### FR1 — Lược đồ trung gian và ánh xạ

- **FR1.1** Hệ thống khai báo một lược đồ trung gian cho ba thực thể: `don_hang`, `mat_hang`, `san_pham`. Các thực thể còn lại được thêm ở đợt sau.
- **FR1.2** Mỗi trường của lược đồ trung gian có ánh xạ tường minh tới cột nguồn trong 9 CSV, kèm kiểu dữ liệu và tên nguồn.
- **FR1.3** Giao diện hiển thị danh sách thực thể và bảng ánh xạ của thực thể đang chọn, gồm tên trường trung gian, nguồn và kiểu.
- **FR1.4** Bảng ánh xạ hiển thị dạng ánh xạ đang dùng — giá trị cố định `GAV` — ngay trên màn hình, không kèm đoạn giải thích dài.
- **FR1.5** Phần ghép bản ghi (FR3) đọc trực tiếp hai bảng nguồn `olist_customers_dataset` và `olist_sellers_dataset`, không đi qua lược đồ trung gian; nối vào lược đồ trung gian là việc của đợt sau, khi hai thực thể khách và người bán được thêm.

### FR2 — Viết lại truy vấn

- **FR2.1** Hệ thống có đúng ba truy vấn mẫu: doanh thu theo danh mục, doanh thu theo tháng, tỷ lệ giao trễ theo bang.
- **FR2.2** Với mỗi truy vấn mẫu, hệ thống viết lại truy vấn trên lược đồ trung gian thành SQL chạy được trên nguồn, và hiển thị cả hai bản cạnh nhau.
- **FR2.3** Màn hình hiển thị kế hoạch viết lại từng bước (thực thể → bảng nguồn → điều kiện join), thời gian chạy và số dòng trả về.
- **FR2.4** Người dùng xem được SQL nguồn của lần chạy gần nhất bằng một hành động riêng.
- **FR2.5** Kết quả của cả ba truy vấn mẫu phải khớp chính xác số liệu mà `src/analytics` đang trả về cho cùng định nghĩa KPI (sai lệch 0 về số dòng và giá trị tiền tệ), để chứng minh phần viết lại không làm đổi ngữ nghĩa.

### FR3 — Ghép bản ghi

- **FR3.1** Hệ thống thực hiện ghép bản ghi cho cả khách hàng và người bán: khoá chặn là tiền tố mã bưu chính (`zip_code_prefix`) lấy từ bảng khách/người bán; trường so khớp là `customer_city`/`seller_city` chuẩn hoá (bỏ dấu, chữ thường) và `customer_zip_code_prefix`/`seller_zip_code_prefix`; độ tương đồng là tỉ lệ khớp ký tự chuẩn hoá trên hai trường đó; mốc đúng để đo là `customer_unique_id` (khách) và `seller_id` (người bán).
- **FR3.2** Ngưỡng tương đồng cố định là 0.85 trong đợt này; màn hình hiển thị ngưỡng đang dùng nhưng không cho chỉnh trong đợt này.
- **FR3.3** Màn hình hiển thị số cặp vượt ngưỡng, số nhóm trùng, và bảng cặp tiêu biểu với điểm số và quyết định `Ghép` hoặc `Xem lại`.
- **FR3.4** Khi một nguồn thiếu trường dùng để so khớp, màn hình ghi rõ cặp nào không chấm được điểm thay vì bỏ qua im lặng.

### FR4 — Chọn nguồn dữ liệu

- **FR4.1** Hệ thống mô tả mỗi nguồn bằng khả năng đáp ứng truy vấn, chi phí ước tính và độ trễ ước tính.
- **FR4.2** Màn hình hiển thị bảng đầy đủ các nguồn ứng viên: nguồn, có dữ liệu hay không, chi phí, độ trễ, được chọn hay không, và lý do chọn/loại.
- **FR4.3** Mọi nguồn ngoài Olist và cache IBGE chỉ là ứng viên mô phỏng; hệ thống không thực hiện lệnh gọi mạng nào.

### FR5 — Giao diện tab "Tích hợp"

- **FR5.1** Dashboard có thêm một tab "Tích hợp" bên cạnh ba tab hiện có.
- **FR5.2** Tab mở ra màn hình tổng quan gồm bốn thẻ, mỗi thẻ là một nhóm chủ đề với trạng thái, hai dòng số liệu và một điểm vào xem chi tiết.
- **FR5.3** Mỗi thẻ dẫn tới màn hình chi tiết của nhóm tương ứng, có đường quay lại tổng quan.
- **FR5.4** Giao diện mới dùng Dash Mantine Components; nhãn hiển thị bằng tiếng Việt.
- **FR5.5** Mỗi màn hình có đủ bốn trạng thái: rỗng, đang tải, lỗi, và một phần — trong đó "một phần" nghĩa là màn hình hiển thị dữ liệu đã có, ghi rõ phần nào thiếu và vì sao, và không hiển thị số 0 thay cho dữ liệu thiếu.
- **FR5.6** Ba tab báo cáo cũ giữ nguyên hành vi và số liệu.

### FR6 — Lớp ngữ nghĩa KPI

- **FR6.1** Định nghĩa KPI được khai báo một lần và dùng chung cho dashboard lẫn lớp truy vấn mới.
- **FR6.2** Khi thêm KPI hoặc truy vấn mới, định nghĩa doanh thu đang dùng được nêu rõ trong tài liệu đi kèm.

## Non-functional requirements

- **NFR1 — Hiệu năng tương tác**: mỗi tương tác trên dashboard (đổi thẻ, đổi thực thể, chỉnh ngưỡng, chạy truy vấn mẫu) trả kết quả trong **dưới 2 giây** trên máy local với dữ liệu Olist hiện có.
- **NFR2 — Độ phủ kiểm thử**: mã mới trong `src/` giữ độ phủ dòng **≥ 80%**, đo bằng `pytest --cov=src`; mọi module mới có test riêng.
- **NFR3 — Chất lượng mã**: `ruff check` và `ruff format --check` sạch trên mã mới; không thêm `mypy` trong đợt này.
- **NFR4 — Tiếp cận**: tab mới đạt **WCAG 2.1 AA** — thao tác được hoàn toàn bằng bàn phím, tiêu điểm thấy rõ, tương phản ≥ 4.5:1 cho chữ thường, không dùng màu làm tín hiệu duy nhất.
- **NFR5 — Đúng đắn dữ liệu**: sau mọi thay đổi, `quality full` và `KpiReconciler` phải xanh; **5 KPI baseline lệch 0** so với giá trị hiện tại, và **11 view hiện có giữ nguyên số dòng**. Dữ liệu riêng của tab mới được sinh vào view/tệp mới và đếm riêng, không làm thay đổi 11 view cũ.
- **NFR6 — Khả chạy tại chỗ**: toàn bộ hệ thống chạy trên một máy, không cần mạng, không cần dịch vụ ngoài; mọi lệnh Python chạy UTF-8.

## Constraints

- **C1**: `dataset/` là dữ liệu bất biến; mọi đầu ra ghi vào `data/`, `warehouse/`, `logs/`, `inbox/`.
- **C2**: Công nghệ giữ nguyên — Python 3.13, pandas, DuckDB, Plotly Dash; chỉ thêm thư viện Python mã nguồn mở nhỏ, ghim trong `requirements.txt`.
- **C3**: Không dùng công cụ thương mại trong sản phẩm; nhóm thương mại chỉ xuất hiện trong tài liệu so sánh.
- **C4**: Thời gian khoảng 1–2 tuần cho một người.
- **C5**: Không thêm nguồn dữ liệu ngoài Olist và cache IBGE.
- **C6**: Nhánh làm việc `feature/update-ui-ux`; trunk vẫn là `main`.

## Assumptions

- **A1**: Ba thực thể (`don_hang`, `mat_hang`, `san_pham`) đủ để chứng minh lược đồ trung gian và làm nền cho ba truy vấn mẫu.
- **A2**: Ngưỡng 0.85 cho kết quả ghép vừa đủ để minh hoạ mà không tạo quá nhiều cặp sai.
- **A3**: Hai nguồn hiện có đủ để minh hoạ chọn nguồn dữ liệu; nguồn thứ ba chỉ là ứng viên mô phỏng.
- **A4**: Cache IBGE cục bộ đủ dùng; không cần gọi API IBGE trong đợt này.

## Out of scope

- **OS1**: Làm mới ba tab báo cáo cũ (hoãn sang đợt sau).
- **OS2**: Thêm thực thể thứ tư trở đi vào lược đồ trung gian.
- **OS3**: ML dự báo giao trễ.
- **OS4**: Nguồn dữ liệu mới ngoài Olist và cache IBGE.
- **OS5**: Đăng nhập, phân quyền, nhiều người dùng.
- **OS6**: Trình tối ưu truy vấn tổng quát; chỉ ba truy vấn mẫu đã chốt.
- **OS7**: Đổi công nghệ lớn (Spark, Kafka, Docker, cloud) hoặc thêm `mypy`.

## Open questions

- **OQ1**: Có sửa `TD-09` (bộ test nhanh phụ thuộc `warehouse/olist.duckdb` và `data/marts/`) trong đợt này không? Hiện chưa quyết; nếu không sửa, bộ test nhanh chỉ xanh trên máy đã chạy `python -m src.pipeline run --stage all` ít nhất một lần.
- **OQ2**: Có cần tag hay CHANGELOG cho mốc nộp không? Hiện dùng commit hash làm mốc.
- **OQ3**: Giới hạn 112 ký tự mỗi dòng có thành luật trong cấu hình `ruff` không?
