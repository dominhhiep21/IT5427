# Kế hoạch Application Design

**Dự án**: Olist E-commerce Data Pipeline
**Giai đoạn**: INCEPTION - Application Design (Planning)

## 1. Mục tiêu

Chốt kiến trúc mức cao trước khi chia unit:

- Thành phần chức năng và trách nhiệm.
- Interface giữa các thành phần (chưa đi vào business rule chi tiết).
- Service orchestration cho pipeline và dashboard.
- Phụ thuộc và luồng dữ liệu.

## 2. Thành phần đề xuất

| Thành phần | Trách nhiệm chính |
|---|---|
| `config` | Đường dẫn, hằng số, ngưỡng chất lượng, cấu hình runtime |
| `common` | Logging có run_id, đọc/ghi Parquet, hash, tiện ích thời gian |
| `ingest` | Đọc 9 CSV, kiểm tra schema, checksum, ghi raw Parquet |
| `quality` | Kiểm tra khóa, orphan, số dòng, khoảng giá trị; quality gate |
| `clean` | Parse timestamp, chuẩn hóa city, gộp geolocation, dịch danh mục, cờ ngoại lai |
| `external` | Tải/cache IBGE, ánh xạ 27 bang → 5 vùng |
| `integrate` | Xây fact/dimension, ghi mart Parquet, tạo catalog DuckDB |
| `analytics` | Truy vấn KPI, tổng hợp doanh thu/danh mục/vùng/giao hàng |
| `dashboard` | Ứng dụng Plotly Dash, layout, callback, định dạng tiếng Việt |
| `pipeline` | Orchestrator CLI, thứ tự stage, manifest micro-batch, run summary |
| `tests` | Unit test, data quality test, test KPI |

## 3. Nguyên tắc thiết kế

- **Functional core**: logic làm sạch/tính KPI là hàm thuần, dễ test.
- **Hợp đồng rõ ràng**: mỗi stage có input/output xác định; ranh giới stage dùng Parquet.
- **Bất biến nguồn**: không ghi vào `dataset/`.
- **Idempotent**: chạy lại một stage không tạo bản ghi trùng.
- **Fail-fast**: lỗi schema/khóa dừng pipeline với thông báo cụ thể.
- **Tách build và serve**: dashboard không đọc CSV thô.

## 4. Câu hỏi thiết kế

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Tổ chức component
Cấu trúc package nên theo hướng nào?

A) Theo tầng: `ingest/`, `clean/`, `integrate/`, `analytics/`, `dashboard/` (khuyến nghị)
B) Theo miền nghiệp vụ: `orders/`, `customers/`, `catalog/`, `geography/`
C) Kết hợp: tầng ở cấp ngoài, module con theo miền ở `clean/` và `integrate/`
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — Hợp đồng dữ liệu giữa component
Dữ liệu nên được trao đổi như thế nào?

A) DataFrame trong bộ nhớ; Parquet tại ranh giới stage (khuyến nghị)
B) Chỉ Parquet giữa mọi component, kể cả bước nhỏ
C) Chỉ DataFrame trong một tiến trình, không ghi trung gian
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — Orchestration
Cách điều phối pipeline?

A) Orchestrator Python + CLI (`python -m src.pipeline run --stage ...`) (khuyến nghị)
B) Script PowerShell/Bash gọi từng module
C) Workflow engine (Prefect/Airflow/Dagster)
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Dashboard đọc dữ liệu từ đâu?
Cách truy cập dữ liệu cho Plotly Dash?

A) Dash truy vấn DuckDB view/table trỏ tới Parquet (khuyến nghị)
B) Dash đọc mart Parquet/JSON đã tổng hợp sẵn; DuckDB chỉ dùng lúc build
C) Dash đọc trực tiếp CSV đã làm sạch
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 5 — Cấu hình
Cấu hình đường dẫn/ngưỡng nên đặt ở đâu?

A) `config.yaml` + giá trị mặc định trong code (khuyến nghị)
B) Chỉ biến môi trường
C) Hằng số Python trong `config.py`
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 5. Checklist thực hiện

### Planning
- [x] Đọc requirements và user stories
- [x] Xác định component, service, interface mức cao
- [x] Tạo kế hoạch và câu hỏi
- [x] Thu thập câu trả lời
- [x] Phân tích mơ hồ/mâu thuẫn
- [ ] Chốt thiết kế và được phê duyệt

### Generation
- [x] Tạo `components.md`
- [x] Tạo `component-methods.md`
- [x] Tạo `services.md`
- [x] Tạo `component-dependency.md`
- [x] Kiểm tra tính đầy đủ và nhất quán
- [x] Cập nhật `aidlc-state.md`
- [ ] Trình bày để phê duyệt
