# Logical Components — u4-record-linkage

Nguồn: `nfr-requirements/` (hai tệp yêu cầu), `functional-design/functional-spec.md` (Workflow 1–4, BR4.1–BR4.10), `functional-design/entities.md`, `inception/domain-design/components.md` (khối `RecordLinkage`), `inception/contract-design/contract-summary.md` (C5).

## 1. Kiến trúc logic

```
dataset/*.csv ──► L1 chỉ mục bằng chứng ──► L2 chấm điểm cặp ──► L3 tổng hợp + ghi
                  (product_id, payment)        (geo + order)      data/integration/linkage-<entity>.json
                        │                            │
                        └──────────► logs/ ◄─────────┘  (L4, dùng chung)
```

<!-- Text fallback: nguồn nuôi bước dựng chỉ mục; chỉ mục nuôi bước chấm điểm; bước chấm điểm nuôi bước tổng hợp và ghi tệp; cả hai bước giữa ghi vào nhật ký dùng chung. -->

## 2. Danh mục khối

| Mã | Khối | Trách nhiệm | Không làm gì | Sở hữu |
|---|---|---|---|---|
| L1 | Chỉ mục bằng chứng | Đọc bảng nguồn bằng `pd.read_csv` với **đủ bộ cột của `TableSpec`** (không `usecols`), kiểm tiêu đề, rồi chọn cột con; dựng `dict[customer_id → (city, zip, frozenset product_id, frozenset payment_value)]` cho mỗi đối tượng | Không chấm điểm, không ghi tệp, không khai lại danh sách cột nguồn (lấy từ `src/ingest/schemas.py`) | `src/linkage/index.py` |
| L2 | Chấm điểm cặp | Sinh cặp trong mỗi nhóm chặn, tính `geo_ratio`, `order_ratio`, `score`, quyết định theo ngưỡng | Không đọc lại nguồn (dùng chỉ mục của L1), không ghi tệp | `src/linkage/score.py` |
| L3 | Tổng hợp và ghi | Tính `summary`, áp trần, dựng `LinkageResult`, ghi bằng `AtomicWriter`, đọc lại kiểm | Không biết gì về giao diện | `src/linkage/result.py` |
| L4 | Nhật ký | Ba sự kiện `integration.linkage.*` | Không mang giá trị bản ghi | Dùng lại `src/common/logging.py` |
| L5 | Điểm vào pipeline | Gọi L1→L3 một lần cho mỗi đối tượng, sau `integrate`, trong `run_all` và sau `run_stage("integrate")` | Không chạy trong `micro_batch` | `src/pipeline/stages.py` (sửa) |

Ba khối L1–L3 nằm trong **một** gói `src/linkage/`; chúng luôn đổi cùng nhau và không có biên giới triển khai riêng.

## 3. Phạm vi hỏng

| Vùng hỏng | Ảnh hưởng | Cô lập |
|---|---|---|
| Bảng khách/người bán thiếu cột | Chỉ đối tượng đó; tệp của nó không được ghi | `SchemaError` trước khi dựng chỉ mục; đối tượng kia vẫn chạy (Workflow 4 bước 6) |
| Ghi tệp lỗi | Chỉ đối tượng đó | `AtomicWriter` ghi tạm rồi `os.replace`; lỗi nổi lên pipeline sau khi đối tượng kia xong |
| Chấm điểm lỗi ở một cặp | Không hỏng cả lô | Cặp vào `skipped` với lý do |
| Quá nhiều cặp vượt ngưỡng | Tệp lớn | Trần 10.000 cặp (BR4.10), số đếm đầy đủ trong `summary` |
| `logs/` không ghi được | Mất chẩn đoán | Ghi nhật ký lỗi không làm hỏng kết quả |

## 4. Tài nguyên dùng chung

| Tài nguyên | Ai dùng | Tranh chấp | Cách xử lý |
|---|---|---|---|
| `dataset/` | L1 và toàn pipeline | Không (chỉ đọc) | SR-U4-7 |
| `data/integration/linkage-*.json` | L3 ghi, U6 đọc | Ghi trong lúc U6 đang đọc | `os.replace` là thao tác nguyên tử; U6 đọc được bản cũ hoặc bản mới, không thấy tệp dở |
| `logs/` | L4 và dashboard | Hai tiến trình ghi nối | Đã chấp nhận ở đơn vị u1 (`observability-design.md` §5) |
| `src/common/io.py` | L3 | Không | Chỉ dùng `AtomicWriter`; không sửa helper dùng chung (TS-U4-4) |

## 5. Ranh giới với đơn vị khác

| Bên | Bàn giao | Không bàn giao |
|---|---|---|
| U6 (`u6-integration-ui`) | Hai tệp `linkage-customer.json`, `linkage-seller.json` theo C5 + các trường bổ sung trong `summary` | Việc hiển thị, trạng thái rỗng/lỗi, phân trang, đọc tệp |
| U2/U3 | Không gì — đơn vị này đọc nguồn trực tiếp, không dùng lược đồ trung gian | Mọi phụ thuộc vào `config/mediated-schema.yaml` |
| Toàn pipeline | Ba sự kiện nhật ký và hai tệp kết quả | Không chạm `data/marts`, `warehouse/`, `dataset/` |

## 6. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Chỉ mục bằng chứng vừa bộ nhớ: khoảng 99.441 entry khách, mỗi entry vài chục `product_id` | Giả định — ước tính dưới 100 MB; đo ở Build and Test bằng đỉnh bộ nhớ của lần chạy |
| A2 | Ba tệp trong gói là đủ tách biệt để test riêng từng tệp | Đúng theo NFR2.2 |
| A3 | Đọc bằng đủ bộ cột rồi chọn cột con không tốn đáng kể so với `usecols` | Đúng ở mức 99.441 dòng: chi phí chủ yếu là parse, không phải băng thông; đổi lại tránh được lỗi thứ tự cột của `validate_columns` (nó so theo vị trí, còn `usecols` trả theo thứ tự tệp) |
| Q1 | U6 có cần thêm trường nào để hiện "cặp xem lại" khác "cặp ghép" không? C5 đã có `decision` | Không chặn — `decision` đủ; nếu U6 cần thêm thì đó là thay đổi cộng thêm của C5 |
| Q2 | Có bỏ `is_correct` khỏi tệp để giảm tiết lộ (giữ `correct_rate` + cỡ mẫu) không? | Cần chủ hợp đồng C5 quyết (xem `security-design.md` ADR-U4-S3); hiện giữ nguyên vì C5 yêu cầu |
