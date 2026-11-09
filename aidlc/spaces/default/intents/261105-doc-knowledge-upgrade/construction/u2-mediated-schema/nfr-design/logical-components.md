# Logical Components — u2-mediated-schema

Nguồn: `nfr-requirements/security-requirements.md` (SR-U2-1..11), `nfr-requirements/tech-stack-decisions.md`
(TS-U2-1..10, NFR1.1–NFR6.1), `functional-design/functional-spec.md` (Workflow 1–4, A1–A2, Q1–Q2),
`inception/contract-design/contract-summary.md` (C1, C2, C6, C8).

## 1. Kiến trúc logic

```
config/mediated-schema.yaml ─┐
                             ├─► L1 kiểm cấu trúc + định danh ─► L2 kiểm thành viên (TABLE_SPECS)
dataset/*.csv (tiêu đề)  ────┘                                            │
                                                                          v
                                              L3 kiểm tiêu đề thật ─► L4 dựng view + catalogue
                                                                          │
                             C1/C6: MediatedSchemaView ◄──────────────────┤
                             C2:    MediatedFieldCatalogue ◄──────────────┘
                             (tuỳ chọn) L5 nhật ký ◄── logger do bên gọi truyền
```

<!-- Text fallback: tệp YAML đi qua lớp kiểm cấu trúc và định danh, rồi lớp kiểm thành viên với danh sách bảng nguồn; tiêu đề CSV thật đi vào lớp kiểm cột; lớp cuối dựng hai hợp đồng C1/C2 (và bản cho giao diện C6). Nhật ký là tuỳ chọn và chỉ chạy khi bên gọi truyền logger. -->

Toàn bộ nằm trong **một gói** `src/integration/`, hai tệp: `schema.py` (logic) và `models.py` (kiểu dữ
liệu hợp đồng). Không có biên giới triển khai riêng, không có tiến trình riêng — đơn vị kiểu `library`.

## 2. Danh mục khối

| Mã | Khối | Trách nhiệm | Không làm gì | Sở hữu |
|---|---|---|---|---|
| L1 | Kiểm cấu trúc và định danh | `safe_load`; kiểm `schema_kind = GAV`; mỗi thực thể/trường đủ khoá; định danh khớp `^[a-z][a-z0-9_]{0,63}$`; `field_name` duy nhất; `data_type` thuộc tập kín; `loaded` mặc định `True` (BR2.4–BR2.6, TS-U2-7) | Không mở tệp CSV, không dựng SQL, không tự sửa tên | `src/integration/schema.py` |
| L2 | Kiểm thành viên | `source_table` phải nằm trong `TABLE_SPECS` (theo `file_name`); bảng phải thuộc `source_tables` của chính thực thể (BR2.2, BR2.3, TS-U2-2) | Không kiểm cột (việc của L3), không khai lại tên bảng nguồn | `src/integration/schema.py` (dùng `TABLE_SPECS` của `src/ingest/schemas.py`) |
| L3 | Kiểm tiêu đề nguồn | Mở **dòng đầu** của từng tệp CSV nguồn bằng `csv.reader`, `utf-8-sig`; kiểm mọi `source_column` có thật (BR2.2, TS-U2-3, ADR-U2-S3) | Không đọc dữ liệu, không đọc cả tệp, không đọc khi L1/L2 đã hỏng | `src/integration/schema.py` |
| L4 | Dựng view và catalogue | Dựng `MediatedSchemaView` (C1/C6: entities, mappings, `schema_kind`, `elapsed_ms`, `partial`) và `MediatedFieldCatalogue` (C2: `fields_by_entity`), giữ thứ tự trường (BR2.1, BR2.7, TS-U2-5, TS-U2-8) | Không lọc theo truy vấn, không biết truy vấn nào cần trường nào | `src/integration/schema.py` + `src/integration/models.py` |
| L5 | Nhật ký (tuỳ chọn) | Ba sự kiện `integration.schema.*` khi bên gọi truyền logger; ánh xạ `error_code` theo bảng ở `security-requirements.md` §3 | Không tự phát khi không có logger; không ghi giá trị ô hay nội dung YAML | Dùng lại `src/common/logging.py` |
| L6 | Điểm vào | `load_schema(path, logger=None)` — hàm duy nhất consumer gọi | Không thêm lời gọi vào `src/pipeline/stages.py` (xem `tech-stack-decisions.md` §4) | `src/integration/schema.py` |

L1–L4 và L6 nằm cùng một tệp và luôn đổi cùng nhau; tách tệp chỉ để đếm cho đủ sẽ tạo ra các lớp
"chỉ nối dây" mà NFR2.2 vẫn đòi test riêng — cái giá lớn hơn lợi ích.

## 3. Phạm vi hỏng

| Vùng hỏng | Ảnh hưởng | Cô lập |
|---|---|---|
| Tệp lược đồ thiếu | Không có view; consumer không chạy được | `ConfigurationError` tại L1, trước khi mở bất kỳ CSV nào |
| Tệp lược đồ sai cấu trúc | Như trên | `SchemaError` tại L1, thông điệp nêu tên trường/tên cột (BR2.8) |
| Một tệp CSV nguồn thiếu | Không có view | `ConfigurationError` tại L3 (Q3 = A); không trả view "một phần" cho trường hợp này |
| Một thực thể thiếu trong tệp khai báo | Các thực thể còn lại vẫn dùng được | View mang `partial` (BR2.1); consumer hiện trạng thái "một phần" |
| Tiêu đề CSV khác khai báo (đổi tên cột nguồn) | Không có view | `SchemaError` tại L3, nêu tên cột thiếu |
| Logger hỏng/không ghi được | Mất chẩn đoán, không hỏng dữ liệu | Lỗi ghi nhật ký không làm hỏng view; bên gọi quyết định ghi hay không |
| Bộ nhớ | Không có rủi ro đáng kể: chỉ giữ chuỗi tiêu đề và danh sách trường (vài trăm mục) | Không đọc dữ liệu (ADR-U2-S3) |

## 4. Tài nguyên dùng chung

| Tài nguyên | Ai dùng | Tranh chấp | Cách xử lý |
|---|---|---|---|
| `dataset/*.csv` | L3 và toàn pipeline | Không (chỉ đọc) | Chỉ đọc tiêu đề; không đường ghi (SR-U2-8) |
| `src/ingest/schemas.py` (`TABLE_SPECS`) | L2 | Không (hằng số) | Đọc, không sửa; thêm bảng nguồn là thay đổi ở tệp đó, không ở đơn vị này |
| `src/common/exceptions.py` | L1–L3 | Không | Dùng `SchemaError`, `ConfigurationError` có sẵn |
| `src/common/logging.py` | L5 | Không | Chỉ dùng `Logger`/`NullLogger`, `normalise_error_code` |
| `config/mediated-schema.yaml` | L1 | Người sửa tay trong khi tiến trình đang nạp | Đọc một lần đầu mỗi lần nạp; tệp hỏng là lỗi nêu rõ, không đọc lại giữa chừng |
| `src/pipeline/stages.py` | **Không dùng** | — | Đơn vị này không thêm lời gọi vào pipeline; bên gọi tự quyết định |

## 5. Ranh giới với đơn vị khác

| Bên | Bàn giao | Không bàn giao |
|---|---|---|
| U3 (`u3-query-rewriter`) | `MediatedSchemaView` theo C1 (entities, mappings, `schema_kind`, `elapsed_ms`, `partial`) | Việc sinh SQL, chọn nguồn, biết truy vấn nào cần trường nào |
| U5 (`u5-source-selector`) | `MediatedFieldCatalogue` theo C2 (`fields_by_entity`) | Việc chọn nguồn, đánh giá độ phủ |
| U6 (`u6-integration-ui`) | Cùng view theo C6, kèm `elapsed_ms` và `partial` để hiện trạng thái | Việc hiển thị, định dạng số, WCAG AA (thuộc U6) |
| U1 (`u1-thin-slice`) | Nhận tệp khai báo **ba thực thể** theo C8; không đổi tên/thứ tự trường đang có | Không đổi tên `don_hang` hay nghĩa trường đang có (BR2.9) |
| Pipeline | Không gì (đơn vị không tự chạy) | Mọi lời gọi trong `stages.py`, `micro_batch` |

## 6. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Tiêu đề CSV đọc được không cần pandas, nên không kéo pandas vào đường nạp | Đúng: `csv` là thư viện chuẩn; đo bằng `view.elapsed_ms` (NFR1.1) |
| A2 | Bốn lớp L1–L4 đủ tách bạch về trách nhiệm dù ở cùng một tệp | Đúng theo NFR2.2: L1–L2 là hàm thuần, L3 là I/O duy nhất, L4 là dựng kiểu |
| A3 | `partial` chỉ áp cho "thiếu thực thể", không áp cho "thiếu tệp CSV" | Đúng theo Q3 = A và BR2.1; ghi rõ ở §3 |
| Q1 | Khi thêm thực thể thứ tư, `schema_kind` giữ `GAV` hay đổi `GLAV`? | Cần chủ C1 quyết (đã ghi ở `contract-summary.md`, mục Open questions); không chặn đợt này |
| Q2 | Có cần kiểm kiểu dữ liệu khớp cột nguồn (cột ngày phải là `timestamp`)? | Không chặn: cần đọc dữ liệu, thuộc tầng chất lượng (Q2 của `functional-spec.md`) |
| Ghi chú | Chỉ tiêu `NFRx.y` của đơn vị được khai trong `tech-stack-decisions.md` §3 vì đơn vị kiểu `library` không sinh tệp `*-requirements.md` cho hiệu năng/khả mở rộng; `traceability.json` của bước này vì vậy chỉ nêu `NFR1.1` — đúng tập mà công cụ truy vết đọc được từ nguồn, không phải thiếu sót thiết kế | Thông tin |
