# Unit Dependencies — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `unit-of-work.md`, `../domain-design/components.md`.

Tài liệu này mô tả **cấu trúc phụ thuộc** (cái gì cần cái gì để build và test được). Nó **không** chọn thứ tự thi công hay đường tới hạn — đó là quyết định kinh tế của Delivery Planning.

## Dependency DAG

```
u1-mart-and-baseline  ──▶  u2-features-and-models  ──▶  u3-prediction-ui
```

Ba đơn vị, hai cạnh, một đường duy nhất. Vì DAG là một chuỗi thẳng nên chỉ có **một** thứ tự tô-pô hợp lệ — không có cơ hội song song thật.

### Vì sao từng cạnh là cạnh thật

| Cạnh | Vì sao cần, không phải "cho gọn" |
|---|---|
| `u2` → `u1` | `TrainingFrame` đọc ba cột mà U1 thêm (`approval_days`, `handling_days`, `seller_state`); `CohortCounts` do U1 sinh là đầu vào của `counts` mà U2 ghi vào báo cáo; hàm đo baseline do U1 giao là thứ U2 gọi để có `baseline_auc`. Không có U1 thì U2 không build được test nào trên dữ liệu thật. |
| `u3` → `u2` | Vùng dự đoán đọc `model.threshold` và gọi hàm chấm điểm đã lưu; mốc sàn đọc `auc` và `baseline_auc` từ báo cáo do U2 sinh; tệp mô hình do U2 ghi là thứ U3 nạp. Không có U2 thì U3 chỉ dựng được khung rỗng và không kiểm được trạng thái `day-du`. |

**Cạnh không có, và vì sao:**

- `u1 → u3`: không có import, không có dữ liệu chung. U3 đọc báo cáo, không đọc mart.
- `u2 → u3`: không có. U2 không import gì từ giao diện; tab không phải đầu vào của mô hình.

## Integration points

| Giữa | Cơ chế | Hình dạng dữ liệu | Chủ hợp đồng |
|---|---|---|---|
| U1 → U2 | gọi hàm trong cùng tiến trình | mart có ba cột mới (schema mart, vẫn grain đơn) + hàm thuần `(DataFrame, cut_date) -> float` đo baseline | U1 (dữ liệu + hàm), U2 (cách dùng) |
| U2 → U3 | **tệp** `data/reports/analysis.json` v3 + **tệp** `data/models/` (`pickle` + JSON mô tả) | `ModelBlock` 11 trường; `ModelArtifact` | U2 (người ghi), U3 (người đọc) |

`TrainingFrame` **không** đi qua ranh giới U1 → U2: nó do U2 dựng, từ mart mà U1 đã mở cột.

Hai hợp đồng này **không** phải API mạng, không phải event: cùng một tiến trình và hai tệp trên đĩa. Vì vậy không có versioning động, không có retry, không có timeout — chỉ có kiểm phiên bản (v3) và trạng thái lỗi có thông điệp.

## Parallel development opportunities

**Không có.** DAG là chuỗi thẳng: mỗi đơn vị cần đơn vị trước đã xong để test của nó xanh. Điều này đã được chốt ở Q3 = A, sau khi cân nhắc phương án cho U3 làm song song phần khung tĩnh: phương án đó chỉ đổi chỗ chờ, không bớt chờ, vì phần nối số của U3 vẫn cần cả báo cáo v3 lẫn tệp mô hình.

Không có cạnh song song nghĩa là **không tồn tại hai tập đơn vị độc lập nào để chạy cùng lúc**; chọn đường đi qua DAG và cách chia việc thành các đợt là quyết định của Delivery Planning, không phải của tài liệu này.

## Walking skeleton

Scope `feature` khai `skeleton: on`, nhưng người làm đã chốt **không dựng lát cắt mỏng** (Q2 của đợt = A, ghi trong `team.md` mục `## Walking Skeleton`, và `project.md` ghi việc này là điểm lệch đã biết). Vì vậy tài liệu này **không** đánh dấu đơn vị đầu là lát cắt tích hợp; U1 là đơn vị đầu vì dữ liệu, không vì nghi thức skeleton. Điểm lệch vẫn nguyên và không được tự giải quyết ở đây.

## Edge block

```yaml
units:
  - name: u1-mart-and-baseline
    kind: library
    depends_on: []
  - name: u2-features-and-models
    kind: library
    depends_on: [u1-mart-and-baseline]
  - name: u3-prediction-ui
    kind: ui
    depends_on: [u2-features-and-models]
```
