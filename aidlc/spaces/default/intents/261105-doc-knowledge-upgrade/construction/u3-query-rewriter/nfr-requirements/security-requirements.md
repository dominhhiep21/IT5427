# Security Requirements — u3-query-rewriter

Nguồn: `functional-design/functional-spec.md` (W1–W4, công thức ba KPI), `functional-design/rules.md` (BR3.1–BR3.12), `functional-design/entities.md`, `inception/requirements-analysis/requirements.md` (NFR1–NFR6, C1–C6, OS5), `inception/contract-design/contract-summary.md` (C1, C3, C4), `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`.

Đơn vị này là **thư viện trong tiến trình** chạy truy vấn trên DuckDB. Bề mặt tấn công của nó khác U5: nó **dựng và chạy SQL**, nên rủi ro chính là một định danh (bảng, cột) hoặc một giá trị đi vào câu SQL mà không qua kiểm soát.

## 1. Yêu cầu dẫn xuất

| Mã | Yêu cầu | Cách đáp ứng | Đo bằng |
|---|---|---|---|
| SR-U3-1 | Không xác thực, không mở cổng | Thư viện chỉ chạy trong tiến trình dashboard; không bind cổng, không HTTP | Rà mã: không `socket`, không `http.server` |
| SR-U3-2 | Không thêm bí mật, không đọc biến môi trường | Không API key; đường dẫn DuckDB lấy từ `AppConfig` | Rà `os.environ` trong mã mới |
| SR-U3-3 | **Mọi giá trị vào SQL đi qua placeholder `?`** | BR3.5: tham số hoá; không nối chuỗi từ đầu vào người dùng | Rà mã: không `f"{...}"` hay `+` dựng câu SQL; test với tham số chứa `'` và `;` |
| SR-U3-4 | **Định danh trong SQL thuộc tập đóng** | Tên bảng thuộc `SOURCE_TABLES`; tên cột lấy từ tiêu đề tệp nguồn; cả hai là hằng trong mã, không phải đầu vào người dùng | Test: mẫu chứa bảng/cột lạ → `SchemaError` |
| SR-U3-5 | Không gọi mạng | `src/analytics` gọi trong tiến trình; không HTTP | Rà mã: không `requests`, `urllib`, `httpx` |
| SR-U3-6 | Không để lộ dữ liệu cá nhân trong lỗi hay log | Khoá nhóm là tên danh mục, tháng, mã bang — công khai; không có mã khách/người bán trong thông điệp | Rà mẫu thông điệp lỗi trong test |
| SR-U3-7 | Kết nối DuckDB chỉ đọc | Mở `duckdb.connect()` **in-memory** rồi đăng ký khung pandas đã đọc từ `dataset/`; không mở `warehouse/olist.duckdb`, không có đường ghi nào từ U3 | Rà mã: không `INSERT`/`CREATE`/`COPY`; không tham chiếu `warehouse/` |
| SR-U3-8 | Không thêm gói phụ thuộc | Dùng `duckdb`, `dataclasses`, `time` — đã có | `requirements.txt` không đổi |
| SR-U3-9 | Lỗi theo tầng, mỗi lớp một nghĩa | `SchemaError` (mẫu/tham số sai), `ConfigurationError` (thiếu cấu hình), `QueryExecutionError` (DuckDB), `KpiMismatchError` (lệch quá dung sai), `NoSourceAvailableError` (U5, lan nguyên vẹn) | Test cho từng nhánh |
| SR-U3-10 | Đối chiếu KPI không được nới dung sai để cho qua | Dung sai 0,01 tiền, 0 số dòng, 0,01 phần trăm (BR3.6); hằng số trong mã, không tham số hoá từ ngoài | Rà mã: dung sai là hằng; test một ca lệch 0,02 phải ném `KpiMismatchError` |

## 2. Mối đe doạ đã cân nhắc

| Mối đe doạ | Đánh giá | Kiểm soát |
|---|---|---|
| Chèn SQL qua tham số | Có thật — đơn vị chạy SQL | SR-U3-3 |
| Chèn định danh qua tên bảng/cột | Có thật nếu mẫu SQL đọc từ cấu hình ngoài | SR-U3-4: mẫu là hằng trong mã, đối chiếu tập đóng |
| Ghi đè dữ liệu qua kết nối DuckDB | Thấp — chỉ đọc | SR-U3-7 |
| Lộ dữ liệu khách hàng qua thông điệp lỗi | Thấp — khoá nhóm công khai | SR-U3-6 |
| Đối chiếu KPI bị "làm cho khớp" bằng cách nới dung sai | Có thật — đây là cửa hậu của FR2.5 | SR-U3-10 |
| Tấn công chuỗi cung ứng | Thấp — không thêm gói | SR-U3-8 |

## 3. Nhật ký

Bốn sự kiện, **giữ nguyên tên gói đang dùng** trong `src/integration/query.py` (ba test hiện ghim `slow` và `failed`), chỉ khi bên gọi truyền logger (mặc định `NullLogger`):

| Sự kiện | Mức | Trường | Khi nào |
|---|---|---|---|
| `integration.query.started` | INFO | `plan_id`, `template_id` | trước khi sinh SQL |
| `integration.query.completed` | INFO | `plan_id`, `template_id`, `row_count`, `elapsed_ms` | sau khi SQL trả về và đối chiếu xong |
| `integration.query.slow` | WARNING | `plan_id`, `elapsed_ms`, `threshold_ms` (`SLOW_QUERY_MS`) | khi `elapsed_ms` vượt `SLOW_QUERY_MS` — đây là cách BR3.8 được cài, không phải lỗi chặn |
| `integration.query.failed` | ERROR | `error_code`, `message` | khi ném `SchemaError`, `ConfigurationError`, `QueryExecutionError`, `KpiMismatchError` hoặc `NoSourceAvailableError` |

Không ghi giá trị ô dữ liệu; không ghi mã khách/người bán.

**Ánh xạ `error_code`** (tập đóng `ERROR_CODES` của `src/common/logging.py`): thiếu tệp/cấu hình → `file_not_found`; sai mẫu, tham số, bảng/cột → `identifier_invalid`; DuckDB lỗi khi chạy → **`sql_error`** (mã đã có trong tập đóng và đang được `test_integration_rewrite.py` ghim); lệch KPI → `unknown` (là kết quả nghiệp vụ, không phải lỗi hạ tầng); không có nguồn → giữ `error_code` U5 trả về.

## 3.1 Chỉ tiêu NFR mà các yêu cầu trên bảo vệ

Bảng chỉ liệt kê chỉ tiêu **thật sự** có yêu cầu bảo vệ; chỉ tiêu không có dòng ở đây dựa vào lệnh chạy tay/CI, không phải vào mã của đơn vị.

| Mã | Chỉ tiêu | Yêu cầu bảo vệ |
|---|---|---|
| NFR1.1 | Dưới 2 giây mỗi truy vấn | SR-U3-1, SR-U3-5 |
| NFR5.1 | Pipeline và KPI xanh | SR-U3-7, SR-U3-10 |
| NFR5.2 | 11 view tồn tại; số dòng 9 bảng mart không đổi | SR-U3-7 |
| NFR6.1 | Không mạng | SR-U3-5 |
| NFR6.2 | Chạy UTF-8 | SR-U3-8 |

**Không có SR bảo vệ:** NFR2.1 (phủ ≥ 80%), NFR2.2 (test riêng mỗi mô-đun), NFR3.1 (ruff sạch) — ba cổng vận hành, chạy tay hoặc trong CI.

## 4. Không áp dụng

- **Mã hoá khi lưu/truyền**: đơn vị không lưu và không truyền dữ liệu ra ngoài tiến trình.
- **Tuân thủ dữ liệu cá nhân**: đơn vị đọc dữ liệu tổng hợp theo danh mục/tháng/bang; không xuất mã khách hay người bán.

## 5. Rủi ro đã biết

- **`src/analytics` là nguồn tham chiếu**: nếu chính nó sai, phép đối chiếu vẫn "khớp". Đây là giới hạn của FR2.5 (chứng minh không đổi ngữ nghĩa, không chứng minh số liệu đúng).
- **Dung sai 0,01 cho tiền** khớp `src/integrate/reconcile.py`; nếu sau này đổi dung sai ở đó, phải đổi ở đây cùng lúc.
