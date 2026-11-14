# Entities — u2-model

Nguồn: `../../../inception/units-generation/unit-of-work.md`, `../../../inception/domain-design/components.md`, `../../../inception/contract-design/contract-summary.md` (C1, C3 — phiên bản 2), `../../../inception/requirements-analysis/requirements.md`, `../../../inception/user-stories/stories.md` (US2.1), `functional-design-questions.md`.

U2 sở hữu khối `model` trong tệp báo cáo dùng chung. Hình dạng dưới đây khớp C1 và C3 từng trường; phần metadata mà C1 chưa có chỗ được đặt trong `counts` theo Q1 = B.

```yaml
entities:
  - name: ModelBlock
    description: Khối mô hình trong tệp báo cáo dùng chung
    owner: U2
    attributes:
      - { name: target, type: string, required: true, allowed: ["is_late"], note: "cột mục tiêu của mô hình" }
      - { name: split, type: dict, required: true, keys: ["train_start", "train_end", "test_start", "test_end", "train_n", "test_n"], note: "mốc chia theo thời gian và cỡ mẫu từng tập" }
      - { name: auc, type: float, required: true, min: 0, max: 1 }
      - { name: threshold, type: float, required: true, constraint: "0 < threshold < 1" }
      - { name: precision, type: float, required: true, min: 0, max: 1 }
      - { name: recall, type: float, required: true, min: 0, max: 1 }
      - { name: counts, type: dict, required: true, keys: ["flagged", "not_flagged", "total", "threshold_method", "auc_below_target"] }
    constraints:
      - "flagged + not_flagged = total"
      - "total = test_n"
      - "threshold_method luôn có giá trị, kể cả khi mô hình không đạt mốc AUC — người đọc phải biết ngưỡng đến từ đâu"
      - "auc_below_target là true khi và chỉ khi auc < 0.70"

  - name: TrainingFrame
    description: Bảng đặc trưng và nhãn dùng để huấn luyện, dựng từ mart
    attributes:
      - { name: features, type: "list[str]", required: true, note: "chỉ cột có được trước khi đơn được giao" }
      - { name: label, type: string, required: true, value: "is_late" }
      - { name: train_rows, type: integer, required: true }
      - { name: test_rows, type: integer, required: true }
    constraints:
      - "không cột nào trong features phụ thuộc ngày giao, ngày giao thực tế hay số ngày giao"
      - "tập huấn luyện đứng trước tập kiểm tra trên trục thời gian, không xen kẽ"

  - name: ThresholdPoint
    description: Một điểm trên đường cong precision/recall tại một ngưỡng
    attributes:
      - { name: threshold, type: float, required: true }
      - { name: precision, type: float, required: true }
      - { name: recall, type: float, required: true }
      - { name: f1, type: float, required: true, note: "trung bình điều hoà của precision và recall" }
    constraints:
      - "chỉ dùng nội bộ để chọn ngưỡng; không ghi vào báo cáo"
```

## Danh sách đặc trưng (cụ thể theo cột)

Mỗi dòng là **một đơn đã giao**, khoá `order_id`. Cột lấy từ ba nguồn, và mọi phép gộp đều đưa về grain đơn trước khi ghép:

| Cột đặc trưng | Nguồn | Cách gộp về grain đơn |
|---|---|---|
| `item_count` | `v_fact_order_items` | đếm dòng theo `order_id` |
| `item_total` | `v_fact_order_items` | tổng `price + freight_value` theo `order_id` |
| `item_price_max` | `v_fact_order_items` | max `price` theo `order_id` |
| `payment_type` | `v_fact_payments` | phương thức của `payment_sequential = 1` — **không** cộng `payment_value` |
| `payment_installments` | `v_fact_payments` | max `payment_installments` theo `order_id` |
| `customer_state` | `v_dim_customer` | ghép theo `customer_id`, quan hệ 1:1 |
| `customer_region` | `v_dim_customer` | như trên |
| `purchase_month` | `v_fact_orders` ghép `v_dim_date` theo `date_key` | lấy `month` của `v_dim_date` |
| `purchase_weekday` | `v_fact_orders` ghép `v_dim_date` theo `date_key` | lấy `weekday` của `v_dim_date` |
| `has_items` | `v_fact_orders` | cờ sẵn có: đơn có ít nhất một dòng hàng |
| `has_payment` | `v_fact_orders` | cờ sẵn có: đơn có ít nhất một dòng thanh toán |

Tổng cộng **11 cột**, và đó là danh sách cuối cùng mà BR2.3 ràng buộc. Hai cờ `has_*` không phải cột suy ra thêm: mart đã có sẵn, và TS-8 dùng chúng thay cho bốn cờ mới.

**Cột bị cấm** — tên chính xác, để phép kiểm của BR2.3 viết được: `order_delivered_customer_date`, `order_delivered_carrier_date`, `delivery_days`, `is_late`, `late_days`, `review_score`, `review_comment_title`, `review_comment_message`, `is_delivered`, `has_review`, và mọi cột dẫn xuất từ chúng.

`is_late` là **nhãn**, không phải đặc trưng: nó có mặt trong bảng nhưng nằm ngoài danh sách `features`.

## Tóm tắt tập thực thể

| Thực thể | Vai | Ghi chú |
|---|---|---|
| `ModelBlock` | Kết quả mô hình | Bảy trường C1/C3; hai khoá metadata nằm trong `counts` |
| `TrainingFrame` | Đầu vào huấn luyện | Danh sách đặc trưng là thứ chống rò rỉ, nên nó là một trường có tên |
| `ThresholdPoint` | Trung gian | Không ra khỏi tiến trình |

## Quan hệ

- `AnalysisReport` chứa 0..1 `ModelBlock` — U1 giữ khung, U2 ghi khối.
- `TrainingFrame` sinh ra đúng một `ModelBlock`.
- `ThresholdPoint` là danh sách nội bộ của bước chọn ngưỡng.

## Ghi chú về hợp đồng

- Hai khoá `threshold_method` và `auc_below_target` nằm trong `counts` (Q1 = B) thay vì hai trường mới, để `REPORT_VERSION` giữ nguyên 2 và U1/U3 không phải sửa cùng lúc. Cái giá: `counts` không còn thuần là đếm, nên tên khoá phải được ghi rõ ở đây và ở C3.
- `split` và `counts` là `dict` theo C3; tên khoá do C3 chốt và được liệt kê lại ở trên để người thi công không phải mở hai tệp.
