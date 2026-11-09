# Security Design — u3-query-rewriter

Nguồn: `nfr-requirements/security-requirements.md` (SR-U3-1..10), `nfr-requirements/tech-stack-decisions.md` (TS-U3-1..10), `functional-design/functional-spec.md` (W1–W4, công thức ba KPI), `functional-design/rules.md` (BR3.1–BR3.12), `inception/contract-design/contract-summary.md` (C1, C3, C4).

Đơn vị chạy SQL do chính nó dựng. Bốn quyết định dưới đây là toàn bộ cách nó giữ cho câu SQL đó chỉ có thể là một trong ba câu đã biết.

## ADR-U3-S1 — Mẫu SQL là hằng trong mã, không bao giờ đến từ cấu hình

**Bối cảnh.** Có sẵn một tệp cấu hình cho tab và một tệp cấu hình cho nguồn. Nếu mẫu SQL đi theo đường cấu hình, người sửa tệp có thể đưa bất kỳ câu lệnh nào vào hệ thống.

**Quyết định.** Ba mẫu SQL là hằng số trong `src/integration/rewrite.py`. Cấu hình chỉ mang `template_id`, không mang mảnh SQL nào. Mọi giá trị thay đổi được truyền qua placeholder `?`.

**Hệ quả.** Tập câu lệnh chạy được là hữu hạn và đọc được trong mã. Đổi mẫu là sửa mã và đi qua review; không có đường "sửa cấu hình để đổi truy vấn".

**Phương án đã loại.** *Mẫu trong tệp cấu hình*: linh hoạt hơn nhưng mở đường chèn định danh. *Sinh SQL động từ kế hoạch*: chính U3 đã loại ở Q2 = A.

## ADR-U3-S2 — Định danh phải thuộc tập đóng trước khi câu SQL được dựng

**Bối cảnh.** Ba mẫu tham chiếu bảng và cột. Một lỗi gõ hoặc một tệp nguồn đổi tên làm câu SQL sai, và lỗi chỉ lộ khi chạy.

**Quyết định.** Trước khi chạy, mỗi mẫu được kiểm: mọi bảng thuộc `SOURCE_TABLES`, mọi cột có trong tiêu đề tệp nguồn tương ứng (đọc dòng đầu, như U2). Sai → `SchemaError` nêu bảng hoặc cột, trước khi mở kết nối.

**Hệ quả.** Không có câu SQL nào chạm DuckDB mà chưa qua kiểm định danh. Chi phí: đọc tiêu đề ba tệp mỗi lần chạy — không đáng kể so với chính truy vấn.

**Phương án đã loại.** *Tin vào mẫu vì nó là hằng*: mẫu là hằng nhưng **cột nguồn** thì không; một lần đổi tên cột trong `dataset/` sẽ làm hỏng âm thầm.

## ADR-U3-S3 — Đối chiếu KPI không được nới dung sai

**Bối cảnh.** FR2.5 đòi sai lệch 0. Nếu dung sai là tham số, một lần "cho qua" sẽ biến phép chứng minh thành hình thức.

**Quyết định.** Dung sai là hằng trong mã: `0.01` cho tiền (khớp `src/integrate/reconcile.py` vì `src/analytics` làm tròn 2 chữ số), `0` cho số dòng, `0.01` cho phần trăm sau khi làm tròn 2 chữ số hai bên. Không có tham số, không có biến môi trường. Lệch quá dung sai → `KpiMismatchError` mang danh sách nhóm lệch và delta.

**Hệ quả.** Phép đối chiếu không thể bị làm nhẹ từ ngoài. Một thay đổi dung sai phải sửa mã, và khi đó cả `reconcile.py` phải sửa cùng lúc (ghi ở `security-requirements.md` §5).

**Phương án đã loại.** *Dung sai cấu hình được*: mở đường hạ ngưỡng. *So tuyệt đối 0 trên số thực*: `src/analytics` làm tròn 2 chữ số nên sẽ đỏ vì sai số biểu diễn, không vì sai số liệu.

## ADR-U3-S4 — Lỗi của U5 và của DuckDB đi qua nguyên vẹn

**Bối cảnh.** **U6 gọi U5 trước**, rồi truyền `SourceSelection` (C3) vào U3; U3 chỉ gọi DuckDB và `src/analytics`. Nuốt lỗi của hai bên đó sẽ biến "không chạy được" thành "chạy ra rỗng".

**Quyết định.** U3 không tự gọi U5 và không tự chọn nguồn: nếu `selection` rỗng hoặc thiếu `selected_sources`, U3 ném `SchemaError` (lỗi lập trình của người gọi), và lỗi `NoSourceAvailableError` do U5 ném ra thì **U6** bắt, không đi qua U3. `QueryExecutionError` của DuckDB, lỗi của `src/analytics`, và `KpiMismatchError` đều lan nguyên lớp và nguyên `error_code`; U3 chỉ thêm ngữ cảnh ở dòng log `integration.query.failed`. U3 không có nhánh "chạy tiếp với nguồn mặc định".

**Hệ quả.** Giao diện luôn phân biệt được bốn tình huống: không có nguồn, DuckDB hỏng, KPI lệch, và chạy thành công. Không có kết quả rỗng giả.

**Phương án đã loại.** *Bọc mọi lỗi thành `QueryExecutionError`*: mất thông tin mà U6 cần để hiển thị đúng thông báo.

## ADR-U3-S5 — SQL chạy trên DuckDB trong bộ nhớ, không trên warehouse

**Bối cảnh.** `warehouse/olist.duckdb` chỉ có 11 view `v_dim_*`/`v_fact_*`/`v_agg_*` (xem `src/integrate/catalog.py`); ba mẫu SQL lại tham chiếu chín bảng nguồn `olist_*`. Chạy mẫu trên warehouse sẽ lỗi "table not found", và ghi vào warehouse từ tầng truy vấn sẽ phá NFR5.1.

**Quyết định.** L3 mở `duckdb.connect()` trong bộ nhớ, đọc các bảng nguồn cần dùng từ `dataset/*.csv` bằng pandas (chỉ các cột mẫu dùng), ép kiểu ngày bằng `parse_dates`, rồi `register()` từng khung với tên bảng nguồn. Đây đúng mẫu `src/integration/query.py` đang dùng. Không mở `warehouse/olist.duckdb`, không ghi đĩa.

**Hệ quả.** Câu SQL của ba mẫu chạy được ngay và kiểu ngày so sánh được (điều kiện để tính giao trễ). **Lưu ý:** bước đối chiếu KPI (L4) vẫn cần `warehouse/olist.duckdb` vì `src/analytics` đọc từ đó; nếu tệp đó thiếu hoặc bị khoá, lỗi thuộc **L4**, không phải L3. Chi phí: đọc lại các cột cần dùng từ CSV mỗi lần chạy — đo riêng bằng `load_ms` trong log (không cộng vào `elapsed_ms`), và với ba mẫu trên dữ liệu Olist vẫn dưới ngưỡng NFR1.1.

**Phương án đã loại.** *Chạy trên warehouse*: thiếu bảng nguồn, và mở đường ghi. *View CSV trực tiếp trong DuckDB (`read_csv_auto` trong SQL)*: đặt đường dẫn tệp vào câu SQL, trái ADR-U3-S1 (mẫu là hằng, không nhận đường dẫn).

## Bảng truy vết quyết định → yêu cầu

| Quyết định | Yêu cầu bảo mật | Chỉ tiêu |
|---|---|---|
| ADR-U3-S1 | SR-U3-3, SR-U3-4 | NFR3.1 |
| ADR-U3-S2 | SR-U3-4 | NFR3.1 |
| ADR-U3-S3 | SR-U3-10 | NFR1.1 |
| ADR-U3-S4 | SR-U3-9 | NFR2.1 |
| ADR-U3-S5 | SR-U3-7 | NFR5.1 |

## Không áp dụng

- **Mã hoá khi lưu/truyền**: đơn vị không lưu, không truyền ra ngoài tiến trình.
- **Tuân thủ dữ liệu cá nhân**: kết quả chỉ theo danh mục, tháng, bang; không xuất mã khách hay người bán.
