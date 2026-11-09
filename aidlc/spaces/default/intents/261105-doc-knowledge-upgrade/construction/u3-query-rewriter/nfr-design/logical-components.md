# Logical Components — u3-query-rewriter

Nguồn: `nfr-requirements/security-requirements.md` (SR-U3-1..10), `nfr-requirements/tech-stack-decisions.md` (TS-U3-1..10), `nfr-design/security-design.md` (ADR-U3-S1..S5), `functional-design/functional-spec.md` (W1–W4), `inception/contract-design/contract-summary.md` (C1, C3, C4).

## 1. Kiến trúc logic

```
C3: SourceSelection (U6 truyền vào) ─┐
C2: MediatedFieldCatalogue ─────────┴─► L1 kiểm mẫu + định danh ─► L2 dựng SQL từ mẫu
                                                              │
                     L3 chạy trên DuckDB (chỉ đọc) ◄──────────┘
                              │
                              v
                     L4 đối chiếu KPI ◄── src/analytics + src/common/kpis.py
                              │
                              v
                     C4: QueryRunResult ─► IntegrationUI
                              ấ
                     L5 nhật ký (tuỳ chọn)
```

<!-- Text fallback: C3 của U5 và C2 đi vào lớp kiểm mẫu/định danh; lớp này dựng SQL từ mẫu khai tay; lớp chạy mở kết nối DuckDB chỉ đọc; lớp đối chiếu so với src/analytics dùng sổ KPI ở src/common; kết quả thành C4 cho giao diện; nhật ký là tuỳ chọn. -->

Đơn vị nằm trong `src/integration/` (`rewrite.py` + `models.py`) và một mô-đun trung lập `src/common/kpis.py`.

## 2. Danh mục khối

| Mã | Khối | Trách nhiệm | Không làm gì | Sở hữu |
|---|---|---|---|---|
| L1 | Kiểm mẫu và định danh | Ba mẫu khai tay; kiểm bảng thuộc `SOURCE_TABLES`, cột có trong tiêu đề tệp nguồn; kiểm `template_id` trùng U5 (BR3.1, BR3.5, ADR-U3-S2) | Không đọc cấu hình để lấy SQL; không chạy gì | `src/integration/rewrite.py` |
| L2 | Dựng SQL | Điền tham số qua `?`; mang kế hoạch từng bước; giữ hai bản SQL cho C4 (BR3.3, BR3.4, BR3.10, ADR-U3-S1) | Không nối chuỗi; không đổi mẫu theo dữ liệu | `src/integration/rewrite.py` |
| L3 | Chạy truy vấn | Mở **DuckDB trong bộ nhớ** (`duckdb.connect()`), đọc các bảng nguồn cần dùng từ `dataset/*.csv` bằng pandas rồi `register()` — đúng mẫu `query.py` đang dùng; nạp ngày bằng `parse_dates` để so sánh ngày đúng; đo `elapsed_ms`; phát `integration.query.slow` khi vượt `SLOW_QUERY_MS` (BR3.8, SR-U3-7, ADR-U3-S5) | Không mở `warehouse/olist.duckdb`, không ghi vào `data/`/`warehouse/`; không tự đổi truy vấn khi lỗi | `src/integration/rewrite.py` |
| L7 | Đường chạy cũ (không sở hữu) | `src/integration/query.py` + `card.py` vẫn phục vụ mẫu `don-theo-thang` của lát cắt mỏng; U3 chỉ sửa phần đăng ký tab theo BR3.1/TS-U3-4 | Không đổi ngữ nghĩa mẫu cũ, không xoá nó khi còn chỗ dùng | U1 sở hữu |
| L4 | Đối chiếu KPI | Gọi `src/analytics` một lần với cùng bộ tham số; so từng nhóm; ném `KpiMismatchError` mang `(kpi_id, group_key, delta)` cho từng nhóm lệch; khi lệch dung sai hằng (BR3.6, ADR-U3-S3). KPI giao trễ: dùng đúng định nghĩa của `src/analytics.delivery_kpis` — mẫu số là **mọi** đơn `delivered`, tử số là đơn `delivered` có ngày giao thực tế **muộn hơn** ngày dự kiến; đơn thiếu ngày giao thực tế không bị loại khỏi mẫu số | Không nới dung sai; không bỏ qua nhóm thiếu (ghi `partial`); không định nghĩa lại KPI giao trễ | `src/integration/rewrite.py` |
| L5 | Sổ KPI | Ba định nghĩa KPI + định nghĩa doanh thu trong `src/common/kpis.py` (BR3.9). **Đợt này chỉ lớp truy vấn đọc sổ**; `src/analytics` KHÔNG bị sửa, vẫn dùng 5 KPI hiện có của nó — nối `src/analytics` vào sổ là việc của đợt sau, để không chạm hợp đồng không hồi quy | Không import `src/analytics` hay `src/integration`; không refactor `src/analytics` | `src/common/kpis.py` |
| L6 | Điểm vào | `run_template(template_id, params, selection, logger=None)` và `latest_sql(template_id)` | Không gọi từ `stages.py`; U6 gọi | `src/integration/rewrite.py` |

L1–L4 và L6 nằm cùng một tệp và đổi cùng nhau; `L5` tách ra vì hai tầng cùng đọc.

## 3. Phạm vi hỏng

| Vùng hỏng | Ảnh hưởng | Cô lập |
|---|---|---|
| Mẫu SQL tham chiếu cột không còn | Truy vấn của mẫu đó không chạy | `SchemaError` ở L1, trước khi mở DuckDB |
| `dataset/` thiếu tệp hoặc CSV đổi cột | Không nạp được khung nguồn | `QueryExecutionError` ở L3 (nạp) hoặc `SchemaError` ở L1 (kiểm tiêu đề) |
| `warehouse/olist.duckdb` khoá hoặc thiếu | Không đối chiếu được KPI | `QueryExecutionError` ở **L4** (qua `src/analytics` → `ConnectionFactory.read_only()`); kết quả cũ vẫn đọc được |
| Một nhóm không có giá trị tham chiếu | Nhóm đó vào `partial` | Các nhóm khác vẫn đối chiếu |
| Một nhóm lệch quá dung sai | Cả lần chạy là lỗi | `KpiMismatchError` nêu nhóm và delta |
| U5 không chọn được nguồn | Không chạy | `NoSourceAvailableError` lan nguyên vẹn (ADR-U3-S4) |

## 4. Luồng dữ liệu giữa các đơn vị

| Bước | Ai gọi | Nhận gì | Trả gì |
|---|---|---|---|
| 1 | U6 khi bấm chạy | `template_id`, bộ tham số | — |
| 2 | U6 → U5, **trước** khi gọi U3 | `query_id` = `template_id` | `SourceSelection` (C3) hoặc `NoSourceAvailableError` |
| 2b | U6 → U3 | `selection` của bước 2 (C3) | Nếu U5 đã lỗi thì U3 không được gọi; lỗi hiển thị do U6 lo |
| 3 | U3 nội bộ | C1, C2 | mẫu SQL đã kiểm |
| 4 | U3 → DuckDB | SQL đã tham số hoá | `rows`, `elapsed_ms` |
| 5 | U3 → `src/analytics` + `src/common/kpis.py` | cùng KPI, cùng tham số | giá trị tham chiếu |
| 6 | U3 → U6 | — | `QueryRunResult` (C4) |

U3 không giữ trạng thái ngoài bộ nhớ tiến trình: `latest_sql` đọc từ kết quả gần nhất đã lưu trong dict của tiến trình (TS-U3-8).

## 5. Đo lường tại chỗ

| Chỉ tiêu | Cách đo | Ghi chú |
|---|---|---|
| NFR1.1 | `elapsed_ms` quanh lời gọi DuckDB; bộ chậm ghi số thật, không đỏ khi chậm | Vượt `SLOW_QUERY_MS` → `integration.query.slow` |
| NFR2.2 | Hai tệp test: `test_integration_rewrite.py`, `test_common_kpis.py` | Chạy trong cổng của đơn vị |
| SR-U3-10 | Test một ca lệch 0,02 phải ném `KpiMismatchError` | Khoá cửa hậu nới dung sai |
| SR-U3-4 | Test mẫu có bảng/cột lạ | `SchemaError` trước khi kết nối |
| SR-U3-3 | Test tham số chứa `'` và `;` | Không lỗi SQL, không đổi kết quả |
| NFR3.1 | `ruff check` + `ruff format --check` trên bảy tệp Python đã liệt kê ở `tech-stack-decisions.md` §3 | Phạm vi cố định, không format toàn repo |
| NFR5.1/NFR5.2 | `--stage all` sau khi thêm đơn vị; `KpiReconciler` và 11 view | U3 không ghi mart/view |
| NFR6.1/NFR6.2 | Rà mã không thư viện mạng; lệnh chạy dùng `-X utf8` | — |
