# Scalability Design — u1-thin-slice

Nguồn: `nfr-requirements/` (`scalability-requirements.md`, `performance-requirements.md`, `security-requirements.md`, `reliability-requirements.md`, `observability-requirements.md`, `tech-stack-decisions.md`), `functional-design/functional-spec.md`, `contract-design/contract-summary.md` (C4).

Đơn vị: `u1-thin-slice`. Một người dùng, một máy, 99.441 đơn cố định trong đợt này (`scalability-requirements.md` SC-U1-1..3). Thiết kế dưới đây **cố ý không mở rộng ngang**; giá trị của nó là ghi rõ khi nào phải xem lại, để lần mở rộng sau không phải đoán.

## 1. Quyết định thiết kế

### ADR-U1-SC1 — Một tiến trình, một người dùng, không tầng cân bằng tải

**Quyết định:** dashboard là một tiến trình Dash; dữ liệu nằm trong bộ nhớ tiến trình đó; không có bộ nhớ đệm dùng chung, không có hàng đợi, không có dịch vụ phụ.

**Hệ quả:** bản đã nạp là cache **cấp tiến trình** (`performance-design.md` ADR-U1-P1), nên hai phiên trình duyệt trỏ vào cùng tiến trình dùng chung một bản dữ liệu và không nạp lại CSV. Chỉ khi chạy **hai tiến trình** dashboard song song mới có hai bản độc lập — kịch bản không nằm trong phạm vi và không cần khoá chia sẻ.

### ADR-U1-SC2 — Mỗi lần chạy truy vấn có kết nối DuckDB riêng, đóng ngay

**Quyết định:** mở `duckdb.connect()` trong bộ nhớ, đăng ký DataFrame, chạy, lấy kết quả, đóng trong `finally`.

**Hệ quả:** không có kết nối sống lâu để rò rỉ, không có khoá tệp `warehouse/olist.duckdb`. Đổi lại, chi phí đăng ký lặp lại mỗi lần chạy (khoảng 0,02 giây theo `performance-design.md` §1) — trả giá này để đổi lấy việc không phải quản lý vòng đời kết nối.

### ADR-U1-SC3 — Trần dữ liệu trong bộ nhớ

Ước tính dấu chân của lát cắt: 5 cột × 99.441 dòng dạng chuỗi trong pandas ≈ 30–40 MB; danh sách dataclass `DonHang` dựng thêm ≈ 40–60 MB; kết quả truy vấn (12 tháng × 8 trạng thái) < 1 MB. Tổng dưới 120 MB trên máy 8 GB.

**Quyết định:** không phân trang, không đọc theo lô, không dựng chỉ mục. Toàn bộ tập nằm trong bộ nhớ.

**Hệ quả:** mã đơn giản, và trần này là **giới hạn đã biết**, không phải bất ngờ: khi vượt ngưỡng ở §3 phải chuyển sang đọc Parquet theo lô hoặc đẩy truy vấn xuống `warehouse/`.

### ADR-U1-SC4 — Không xử lý bất đồng bộ

**Quyết định:** nạp và truy vấn chạy đồng bộ trong callback, có `dcc.Loading` bọc thẻ để người dùng thấy trạng thái đang tải.

**Hệ quả:** một người dùng thì một luồng là đủ; thêm luồng nền chỉ thêm chỗ hỏng. Nếu sau này mỗi lần chạy vượt 2 giây thì việc đầu tiên là xem lại truy vấn (chỉ mục, cột hẹp hơn), không phải thêm luồng.

## 2. Ngưỡng năng lực

| Chiều | Hiện tại | Trần thoải mái | Vượt trần thì |
|---|---|---|---|
| Số dòng đơn | 99.441 | 1.000.000 (dấu chân bộ nhớ ≈ 1,2 GB) | Đọc Parquet theo lô thay vì nạp cả bảng; đẩy `GROUP BY` xuống DuckDB trên tệp |
| Số người dùng đồng thời | 1 | 1 | Cần xác thực + nhiều tiến trình + bộ nhớ đệm dùng chung: thay đổi phạm vi, phải chốt lại |
| Số truy vấn mẫu | 1 | 3 (đúng ba truy vấn của đợt) | Mỗi truy vấn mới phải có test hiệu năng riêng theo NFR1.4 |
| Tần suất làm mới dữ liệu | không có (dữ liệu tĩnh trong phiên) | nạp lại khi khởi động dashboard | Nếu cần nạp tăng dần, dùng `src/pipeline/` hiện có chứ không tự thêm cơ chế mới |

## 3. Điều kiện xem lại (ghi để lần sau không phải suy đoán)

Xem lại thiết kế này khi bất kỳ điều nào sau đây đúng:

1. Dữ liệu nguồn vượt **1.000.000 đơn**, hoặc thêm nguồn mới có số dòng cùng bậc.
2. Có yêu cầu **nhiều hơn một người xem** hoặc xem từ máy khác — kéo theo `security-design.md` ADR-U1-S1 và cần xác thực.
3. Một truy vấn mẫu vượt **2 giây** ở lần chạy bình thường (không phải lần đầu).
4. Xuất hiện truy vấn mẫu có **tham số do người dùng nhập** — kéo theo `security-design.md` ADR-U1-S3: tham số phải qua placeholder `?` và bộ kiểm kiểu.
5. Cần **nạp tăng dần** hoặc làm mới dữ liệu trong lúc dashboard đang mở.

Không có điều nào ở trên đúng trong đợt này, nên đơn vị này không dựng cơ sở hạ tầng mở rộng nào.

## 4. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Dữ liệu nguồn không đổi trong một phiên dashboard | Đúng theo `scalability-requirements.md` SC-U1-3 |
| A2 | Kích thước bộ nhớ ở ADR-U1-SC3 là ước tính theo số cột và số dòng, chưa đo bằng profiler | Giả định — không chặn; nếu máy đích dưới 4 GB thì phải đo trước khi sinh mã |
| Q1 | Có cần giới hạn số dòng kết quả truy vấn hiển thị (ví dụ 12 tháng như Workflow 3) hay hiển thị tất cả? | Không chặn: Workflow 3 đã chốt 12 tháng gần nhất; truy vấn vẫn trả toàn bộ để test đối chiếu |
