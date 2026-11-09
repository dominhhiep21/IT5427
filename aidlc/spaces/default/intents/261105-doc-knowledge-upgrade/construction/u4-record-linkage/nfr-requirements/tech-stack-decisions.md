# Tech Stack Decisions — u4-record-linkage

Nguồn: `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`, `requirements.txt`, `functional-design/functional-spec.md`, `functional-design/rules.md`, `inception/requirements-analysis/requirements.md` (NFR1–NFR6), `inception/contract-design/contract-summary.md` (C5).

## 1. Đã chốt ở cấp dự án

| Hạng mục | Lựa chọn | Ghi chú |
|---|---|---|
| Ngôn ngữ | Python 3.13 | Có sẵn |
| Xử lý dữ liệu | pandas 2.2.3 | Có sẵn |
| Đọc nguồn | `src/common/io.read_csv` + `TABLE_SPECS` của `src/ingest/schemas` | Đã có kiểm tiêu đề và `utf-8-sig`, ném `SchemaError` nêu cột thiếu |
| Ghi tệp | `src/common/io.AtomicWriter.write_json` | Ghi tạm rồi `os.replace`; **không** tự kiểm số dòng |
| Kiểm thử | pytest 9.1.1 + pytest-cov 7.1.0 | Có sẵn |

## 2. Quyết định riêng cho đơn vị này

| Mã | Quyết định | Lý do |
|---|---|---|
| TS-U4-1 | So chuỗi bằng `difflib.SequenceMatcher` (thư viện chuẩn) | Quy tắc dự án cấm import thư viện chưa ghim; `rapidfuzz` không có trong `requirements.txt` |
| TS-U4-2 | Chuẩn hoá thành phố bằng `unicodedata.normalize("NFKD")` rồi bỏ dấu kết hợp | Thư viện chuẩn; xử lý cả "São Paulo" và "Sao Paulo" |
| TS-U4-3 | Dựng tập `product_id` và tập `payment_value` **một lần** cho mỗi bản ghi (dict theo `customer_id`/`seller_id`), không truy vấn lại trong vòng lặp cặp | 806.705 cặp khách; tra lại nguồn trong vòng lặp là O(cặp × đơn) và không chạy nổi |
| TS-U4-4 | Đọc nguồn bằng helper dùng chung `read_csv(_source_path(config, table), TABLE_SPECS[table])` — helper đọc `encoding="utf-8-sig"`, `dtype=str`, rồi `validate_columns` với **đủ** bộ cột của `TableSpec` và ném `SchemaError` nêu tên cột thiếu | Một nguồn sự thật cho cách đọc CSV; `usecols` không dùng được qua helper (nó luôn đọc đủ cột), và đọc đủ cột là chấp nhận được với ba bảng này. Không sửa `read_csv` dùng chung cho một đơn vị |
| TS-U4-5 | Kiểm sau khi ghi bằng cách đọc lại tệp và đối chiếu số cặp | `write_json` không kiểm như `write_parquet`; payload không có "dòng" nên kiểm theo `len(pairs)` |
| TS-U4-6 | Chạy **một lần ở `run_all` của `src/pipeline/stages.py`, sau `integrate`**, và cũng sau `run_stage("integrate")`; **không** chạy trong `micro_batch` | `micro_batch` chạy `integrate_all` theo từng lô inbox; đặt vào đó sẽ nhân chi phí 806.705 cặp lên mỗi lô. `run_stage("integrate")` là lệnh runbook dùng khi chuyển thư mục repo, nên cũng phải làm mới tệp kết quả — nếu không, U6 đọc tệp cũ. Tệp mang `run_id` và `computed_at` để U6 biết tệp thuộc lần chạy nào; đó là cách duy nhất phát hiện tệp lạc hậu so với mart |
| TS-U4-7 | Không thêm gói nào | Giữ ràng buộc "chỉ thư viện nhỏ, mã nguồn mở" |

## 2.1 Ghi chú sau khi C8/C9 đổi (2026-11-09)

C8 (hình dạng tệp lược đồ) và C9 (`result_region_ids` cho vùng kết quả trong tab) vừa đổi ở Inception. U4 **không đọc** tệp lược đồ và **không** dựng giao diện, nên không quyết định nào ở trên phải sửa. Điều duy nhất cần giữ: U4 tiếp tục chỉ đọc `dataset/` và chỉ ghi `data/integration/linkage-<customer|seller>.json` theo C5 — không thêm phụ thuộc vào `src/integration/`.

## 3. Chỉ tiêu kỹ thuật

Các chỉ tiêu đo được của đơn vị nằm **toàn bộ** ở `performance-requirements.md` (tệp cùng thư mục) — đó là nguồn sự thật duy nhất cho mã `NFRx.y`: NFR1.1–1.2 (hiệu năng), NFR2.1–2.2 (chất lượng mã), NFR3.1 (lint), NFR5.1–5.2 (bảo đảm dữ liệu), NFR6.1 (local). Tệp này **không lặp lại** con số hay danh sách module nào; đọc tệp kia.

**Ghi rõ về NFR4 (tiếp cận):** không áp dụng cho đơn vị này vì nó không hiển thị gì; yêu cầu WCAG 2.1 AA thuộc `u6-integration-ui`. Bảng traceability ghi `N/A` kèm lý do này.

## 4. Việc cần làm ở bước sinh mã

- Tạo `src/linkage/` (chỉ phụ thuộc `common` và danh sách bảng nguồn của `ingest`), một tệp test cho mỗi tệp.
- Thêm lời gọi một lần vào `run_all` (TS-U4-6), không vào `micro_batch`.
- Ghi ba sự kiện theo danh mục ở `security-requirements.md` §3.
- Giữ nguyên `data/`, `warehouse/`, `dataset/` như các đơn vị trước; không chạm test hình dạng dashboard.
