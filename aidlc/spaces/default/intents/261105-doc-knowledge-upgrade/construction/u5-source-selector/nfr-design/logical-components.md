# Logical Components — u5-source-selector

Nguồn: `nfr-requirements/security-requirements.md` (SR-U5-1..16), `nfr-requirements/tech-stack-decisions.md` (TS-U5-1..15, NFR1.1–NFR6.2), `nfr-design/security-design.md` (ADR-U5-S1..S8), `functional-design/functional-spec.md` (W1–W4), `inception/contract-design/contract-summary.md` (C2, C3, C7).

## 1. Kiến trúc logic

```
config/integration-sources.yaml ─┐
                                 ├─► L1 nạp + kiểm toàn bộ ─► L2 dựng danh mục (coverage, partial)
C2: MediatedFieldCatalogue ──────┘                                  │
                                                                    v
                                         L3 đề xuất nguồn ──► C3: SourceSelection
                                              │                    C7: SourceCatalogue (bản mới)
                                              └── không nguồn nào ──► NoSourceAvailableError(catalogue=...)
                                                                    │
                                          L4 điểm vào công khai ◄───┘
                                          L5 nhật ký (tuỳ chọn, chỉ khi có logger)
```

<!-- Text fallback: tệp cấu hình và danh mục trường C2 đi vào L1 để kiểm toàn bộ; L2 dựng danh mục nguồn với câu khả năng đáp ứng và nhánh một phần; L3 đề xuất nguồn và trả C3 cùng bản C7 mới, hoặc ném ngoại lệ mang theo bản C7 mới; L4 là hai hàm công khai; L5 là nhật ký tuỳ chọn. -->

Toàn bộ nằm trong **một gói** `src/integration/`: `selector.py` (logic) và `models.py` (bốn kiểu hợp đồng mới). Phạm vi tệp đầy đủ của đơn vị — dùng cho lệnh lint của NFR3.1 — là: `src/integration/selector.py`, `src/integration/models.py`, `src/common/exceptions.py`, `src/config.py`, `config.yaml`, `config/integration-sources.yaml`, `tests/unit/test_integration_selector.py` (TS-U5-15). Không có tiến trình riêng, không có biên giới triển khai — đơn vị kiểu `library`.

## 2. Danh mục khối

| Mã | Khối | Trách nhiệm | Không làm gì | Sở hữu |
|---|---|---|---|---|
| L1 | Nạp và kiểm cấu hình | `safe_load`; kiểm **kiểu từng khoá** (ADR-U5-S7, gồm `latency_ms >= 0`); kiểm cấu trúc từng nguồn (đủ tám khoá, `cost_level` 1..5); tập tên nguồn kín; số nguồn mô phỏng đúng một; `covered_fields` đối chiếu C2; `tables` đối chiếu `SOURCE_TABLES`; ánh xạ truy vấn đúng ba `query_id` của FR2.1 **và mọi mã trường trong cả ba danh sách đối chiếu C2** (ADR-U5-S1, ADR-U5-S2, ADR-U5-S8, BR5.1–BR5.4) | Không đọc CSV nguồn, không tự sửa tên, không bỏ qua mục lạ | `src/integration/selector.py` |
| L2 | Dựng danh mục nguồn | Dựng `SourceProfile` cho ba nguồn; sinh câu `coverage` tiếng Việt từ `covered_fields` (BR5.3); mang **`query_fields`** (ánh xạ truy vấn → trường cần) trong danh mục; dựng `SourceCatalogue` rỗng `choices` kèm `partial_reason` và `pending_query_id` (BR5.9). **Không có `generated_at`**: dấu thời gian làm hai lần dựng cùng một cấu hình khác nhau, trái SR-U5-12 (`entities.md` đã bỏ trường này) | Không xếp hạng, không chọn nguồn, không đụng dữ liệu | `src/integration/selector.py` + `models.py` |
| L3 | Đề xuất nguồn | Đọc `required_fields` từ `catalogue.query_fields` (ADR-U5-S8); vị từ ứng viên (đủ trường, có dữ liệu, không mô phỏng — ADR-U5-S3); sắp xếp `(cost_level, latency_ms, source_name)` (ADR-U5-S6); dựng `SourceSelection` (kèm `catalogue` mới) và sáu nhánh lý do loại (BR5.4, BR5.5, BR5.11); ném `NoSourceAvailableError` mang `catalogue` (ADR-U5-S4) | Không sinh SQL, không đọc dữ liệu, không nhận thêm tham số ánh xạ từ bên ngoài | `src/integration/selector.py` |
| L4 | Điểm vào | `load_source_catalogue(path, field_catalogue, pending_query_id=None, logger=None)` và `select_source(catalogue, query_id, logger=None)` — đúng hai hàm consumer gọi (TS-U5-1, TS-U5-11, TS-U5-13); `pending_query_id` vắng mặt thì lấy truy vấn đầu theo thứ tự khai báo | Không thêm lời gọi vào `src/pipeline/stages.py`; U6 gọi khi khởi động màn hình | `src/integration/selector.py` |
| L5 | Nhật ký (tuỳ chọn) | Bốn sự kiện `integration.sources.*` khi bên gọi truyền logger; chỉ các trường trong danh sách trắng (ADR-U5-S5) | Không tự phát khi không có logger; không ghi giá trị ô hay nội dung YAML | Dùng lại `src/common/logging.py` |

L1–L4 nằm cùng một tệp và luôn đổi cùng nhau; tách tệp chỉ để đếm cho đủ sẽ tạo lớp "chỉ nối dây" mà NFR2.2 vẫn đòi test riêng.

## 3. Phạm vi hỏng

| Vùng hỏng | Ảnh hưởng | Cô lập |
|---|---|---|
| Tệp cấu hình thiếu | Không có danh mục; U6 không mở được màn hình nguồn | `ConfigurationError` tại L1, trước khi dựng bất kỳ hồ sơ nào |
| Cấu hình sai cấu trúc (thiếu khoá, `cost_level` ngoài 1..5, `tables` rỗng mà có trường) | Như trên | `ConfigurationError` tại L1, thông điệp nêu nguồn và khoá |
| Tên nguồn lạ/trùng, mã trường lạ, tên bảng lạ, ánh xạ truy vấn sai | Như trên | `SchemaError` tại L1, nêu tên vi phạm |
| C2 ném lỗi | Không dựng được danh mục | Lỗi của C2 lan nguyên vẹn; U5 không nuốt, không đổi lớp |
| Không nguồn nào đủ trường cho một truy vấn | Không chọn được nguồn, nhưng bảng nguồn vẫn hiển thị được | `NoSourceAvailableError` mang `catalogue` (ADR-U5-S4); các truy vấn khác không bị ảnh hưởng |
| Một nguồn bị loại | Không ảnh hưởng nguồn khác | Mỗi nguồn là một dòng độc lập trong danh mục |

## 4. Luồng dữ liệu giữa các đơn vị

| Bước | Ai gọi | Nhận gì | Trả gì |
|---|---|---|---|
| 1 | U6 khi khởi động màn hình | C2 từ U2 (`build_field_catalogue`) | — |
| 2 | U6 | `load_source_catalogue(config/integration-sources.yaml, C2)` | `SourceCatalogue` (C7) ban đầu |
| 3 | U6 khi bấm "Đề xuất nguồn" | `select_source(catalogue, query_id)` | `SourceSelection` (C3) mang `catalogue` là bản C7 mới |
| 4 | U3 | `SourceSelection` từ bước 3 | dùng để viết lại truy vấn |
| 5 | U6 | `selection.catalogue`, hoặc `error.catalogue` và `error.missing_fields` trên ngoại lệ | vẽ bảng nguồn, hoặc hiển thị thông báo kèm danh sách trường thiếu |

U5 không tự tìm C2 và không tự dựng C7 ở nơi khác: điểm ghép nối duy nhất là bước 2 (TS-U5-13). Không có trạng thái dùng chung nào ngoài đối tượng trả về.

## 5. Đo lường tại chỗ

| Chỉ tiêu | Cách đo trong đơn vị | Ghi chú |
|---|---|---|
| NFR1.1 | `time.perf_counter()` bọc quanh `load_source_catalogue` và `select_source` trong test; khẳng định mỗi lần `<= 2000` ms | Không thêm trường đo vào C3/C7 |
| SR-U5-12 | Đảo thứ tự khai báo trong fixture, khẳng định kết quả chọn không đổi | Kiểm được nhờ ADR-U5-S6 |
| SR-U5-6 | Fixture có nguồn mô phỏng rẻ nhất và đủ trường, khẳng định nó không bao giờ được chọn | Kiểm được nhờ ADR-U5-S3 |
| SR-U5-14 | Fixture có `tables: [olist_khong_ton_tai]`, khẳng định `SchemaError` | Kiểm được nhờ ADR-U5-S2 |
