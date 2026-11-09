<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-11-06T07:19:00Z [unit u1-thin-slice] — Q2 = A ("ghi chung tệp nhật ký của lần chạy gần nhất") đọc là: ghi nối vào tệp `logs/<run_id>.jsonl` mới nhất, còn trường `run_id` trong bản ghi là phiên dashboard (theo OB-U1-1). Hai nghĩa khác nhau của "run_id" được ghi rõ trong tài liệu thay vì chọn một cách hiểu.
- 2026-11-06T07:19:00Z [unit u1-thin-slice] — Q1 = A ("thử lại một lần rồi báo lỗi") áp cho bước **đọc** tệp; lỗi kiểm lược đồ không thử lại vì cùng một tệp thì cùng một tiêu đề, thử lại chỉ lặp đúng lỗi đó.
- 2026-11-06T07:19:00Z [unit u1-thin-slice] — "NFR Design" của một lát cắt mỏng nghĩa là chứng minh cơ chế, không phải dựng cơ sở hạ tầng mở rộng; các mẫu circuit breaker/bulkhead/rate limiter bị loại kèm lý do thay vì mô tả cho đủ bộ.
- 2026-11-06T08:05:00Z [unit u1-thin-slice] — sau vòng review 1: `bang_giao` ánh xạ tới `olist_customers_dataset.customer_state` và **không** được nạp ở lát cắt, nên "năm trường" của thực thể không bằng "năm cột đọc"; danh sách cột đọc lấy từ cờ `loaded` trong tệp lược đồ.
- Cập nhật 2026-11-09: `don_hang` nay **7 trường, mọi trường `loaded: true`** (kể cả `bang_giao`); ghi chú trên giữ làm lịch sử.
- 2026-11-06T08:05:00Z [unit u1-thin-slice] — bộ nhớ đệm nạp là **cấp tiến trình** (không phải cấp phiên), còn `dcc.Store` chỉ giữ `QueryRunResult` của phiên trình duyệt. Trước đây hai tài liệu nói hai phạm vi khác nhau.
- 2026-11-06T08:05:00Z [unit u1-thin-slice] — lược đồ nhật ký có một nguồn sự thật duy nhất là danh mục sự kiện ở `observability-design.md` §2; `security-design.md` §4 chỉ thêm ba giới hạn (không ghi giá trị bản ghi, `source_sql` chỉ ở một sự kiện, `error_code` là tập đóng).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-11-06T07:19:00Z [unit u1-thin-slice] — stage file gợi ý "logical infrastructure component inventory ... bridges NFR design with Infrastructure Design"; với một tiến trình local, tài liệu `logical-components.md` nghiêng về vùng hỏng và ranh giới với các đơn vị sau hơn là kiến trúc hạ tầng (không có hạ tầng nào để kiểm kê).

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-11-06T07:20:00Z [unit u1-thin-slice] — chọn nhiều tệp NFR Design ngắn, mỗi tệp có ADR riêng (`ADR-U1-P*`, `-S*`, `-SC*`, `-R*`, `-O*`) thay vì một tệp lớn: người review đọc được từng nhóm mà không phải giữ cả tài liệu trong đầu, đổi lại có vài chỗ nhắc lại ngữ cảnh giữa các tệp.
- 2026-11-06T07:20:00Z [unit u1-thin-slice] — đặt ngân sách độ trễ theo từng bước (bảng §1 của `performance-design.md`) dù chưa có số đo; mục đích là để test đỏ chỉ ra đúng bước, và các số này được ghi rõ là ngân sách chứ không phải số đo.
- 2026-11-06T08:05:00Z [unit u1-thin-slice] — C9: khai đủ bốn `card_ids` của màn hình tổng quan ngay từ lát cắt dù chỉ dựng một khối kết quả, vì C9 tồn tại để U6 không tự đặt tên; thêm khoá `result_block_ids` (bổ sung, đúng `change_policy`) cho khối thật sự dựng. Đổi lại, tệp cấu hình có bốn id chưa dùng tới — chấp nhận vì rẻ hơn việc U6 đổi tên về sau.
- Cập nhật 2026-11-09: khoá đó đã được thay bằng **`result_region_ids: [don-theo-thang]`** theo C9.
- 2026-11-06T08:05:00Z [unit u1-thin-slice] — C8: hình dạng tệp lược đồ mở rộng `fields: list[str]` của payload phác thảo thành danh sách ánh xạ theo trường (`field_name`, `source_table`, `source_column`, `data_type`, `loaded`). Đây là thay đổi cộng thêm; U2 đọc được và bỏ qua khoá lạ, nhưng phải được nêu khi bàn giao.
- Cập nhật 2026-11-09: C8 **chốt** `fields` là danh sách bản ghi (field_name, source_table, source_column, data_type, loaded), không còn là `list[str]`.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-11-06T08:05:00Z [unit u1-thin-slice] — câu hỏi định dạng tệp lược đồ đã đóng: YAML theo C8, đọc bằng `yaml.safe_load` của `PyYAML==6.0.2` đã ghim (ADR-U1-S5 viết lại).
- 2026-11-06T08:05:00Z [unit u1-thin-slice] — hành vi nút thử lại đã đóng ở ADR-U1-R5 (nạp lại + chạy khi lỗi nạp; chỉ chạy lại truy vấn khi lỗi truy vấn; chạy lại khi rỗng).
- 2026-11-06T08:05:00Z [unit u1-thin-slice] — còn mở đúng một điểm thuộc C8, không chặn: U2 có chấp nhận hình dạng ánh xạ theo trường hay không; nếu không, sửa tệp lược đồ, không sửa mã.

- 2026-11-07T09:55:36Z [unit u2-mediated-schema] Khong hoi cau nao cho buoc nay: ba cau hoi mo duy nhat cua don vi da duoc tra loi o NFR Requirements (Q1=A, Q2=A, Q3=A), va BR2.1-BR2.9 cung C1/C2/C6 da chot phan con lai; theo mau cua u4-record-linkage, de trong questions file thay vi hoi lai.
- 2026-11-07T09:55:36Z [unit u2-mediated-schema] Thiet ke chon eager validation voi thu tu co dinh (dinh danh truoc, mo tep sau) de mot tep YAML xau khong dieu khien duoc duong dan doc (ADR-U2-S1). Hang rao chong SQL injection cho U3 nam o lop thanh vien TABLE_SPECS + tieu de that, khong o tang tham so hoa cua U3 (ADR-U2-S2).
- 2026-11-07T09:55:36Z [unit u2-mediated-schema] Don vi kieu library nen traceability.json cua buoc nay chi nhan upstream_ids = [NFR1.1] do cong cu chi doc tep *-requirements.md; cac NFRx.y con lai duoc khai trong tech-stack-decisions.md muc 3. Da ghi chu ro o logical-components.md muc 6 de nguoi doc khong tuong la thieu truy vet.
