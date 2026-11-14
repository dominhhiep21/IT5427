# Functional Spec — u2-features-and-models

Đơn vị: `u2-features-and-models` (kind `library`). Truyện nó tham gia: **US1.1, US1.2, US1.3, US2.2, US2.3, US2.4, US3.1** (xem `traceability.json` cho từng tiêu chí).
Nguồn: `entities.md` (hình dạng), `rules.md` (quyết định), `../../../inception/contract-design/contract-summary.md` (C1, C2, C2b, C3).

Tài liệu này là nguồn sự thật cho **thứ tự hành vi**.

## W1 — Dựng khung huấn luyện (grain dòng hàng)

| # | Bước | Điều kiện dừng |
|---|---|---|
| 1 | Đọc mart qua `AnalyticsService` — **một** truy vấn, trả **cặp** `(TrainingFrame, CohortCounts)` | lỗi truy vấn ⇒ `QueryExecutionError` |
| 2 | Truy vấn lọc `is_delivered` **và** `order_delivered_carrier_date IS NOT NULL`, gộp về grain `order_id + order_item_id`, kéo `seller_state` từ `v_fact_order_items` | — |
| 3 | Truy vấn trả kèm `CohortCounts` (bốn bộ đếm, đếm trên tập đơn **trước** khi lọc carrier) | lệch 110.195/96.476/8.713/2 ⇒ `ModelError` (BR2.1) |
| 4 | Dẫn xuất `approval_days` = số ngày từ `date_key` đến **ngày** của `order_approved_at` (**đặt→duyệt**), và `handling_days` = số ngày từ **ngày** của `order_approved_at` đến **ngày** của `order_delivered_carrier_date` (**duyệt→bàn giao`) — cả hai là số nguyên ngày dương lịch | mốc nguồn null ⇒ giá trị null, **không** bỏ dòng |
| 5 | Trả `(TrainingFrame, CohortCounts)` cho `PipelineStages`; khung mang đủ 14 cột đặc trưng của `feature_contract` | — |

**Vì sao bước 2 và 3 là một truy vấn.** Nếu đếm ở Python sau khi lọc, `excluded_missing_carrier` sẽ là số suy ra từ một lần lọc khác — và một lần chạy sau có thể cho số khác mà không ai biết. Một truy vấn, một sự thật. Phép đếm đó bắt buộc phải chạy trên tập đơn **trước** khi lọc carrier, nên nó nằm trong CTE đếm rồi `CROSS JOIN` vào khung — không phải lọc rồi đếm lại.

**Hình dạng trả về đã chốt.** Truy vấn trả **cặp** `(TrainingFrame, CohortCounts)`, không phải một `DataFrame` kèm bốn cột đếm lặp trên mọi dòng và cũng không phải một DataFrame kèm thuộc tính ẩn. `CohortCounts` là entity riêng (có `generated_at` làm danh tính), đi vào `BaselineMeasurement` và `counts` của báo cáo, rồi dừng — không đi tiếp vào W2–W6.

**Ba cột tổng hợp theo đơn, không phải rò rỉ.** `item_count`, `item_total`, `item_price_max` giữ nguyên tên và nghĩa như `TRAINING_FRAME_SQL` hiện tại (`service.py:38-46`): số món của **đơn**, tổng giá + phí của **đơn**, giá cao nhất trong **đơn** — lặp trên mọi dòng hàng của đơn đó. Chúng không phải rò rỉ vì mọi đầu vào của chúng biết được ngay lúc đặt hàng và cùng ba con số vẫn tính được lúc chấm điểm từ `item_price` + `item_count`.

**Hai cột mốc chỉ vào ở dạng số ngày.** `order_approved_at` và `order_delivered_carrier_date` không bao giờ là đặc trưng — chúng nằm trong `feature_contract.forbidden`; cột thứ nhất dùng để lọc quần thể, cả hai chỉ đi vào dưới dạng `approval_days` / `handling_days`.

**Vì sao hai đặc trưng ngày chỉ có độ phân giải ngày.** Mart không có cột `order_purchase_timestamp`: `v_fact_orders` (15 cột) chỉ có `date_key`, đã mất phần giờ. Nên `approval_days` buộc phải đo từ `date_key` đến ngày duyệt, còn `handling_days` đo giữa hai mốc ngày. Đánh đổi đã nhận: hai đặc trưng này có sai số dưới một ngày. Muốn chính xác đến giờ thì phải thêm cột mốc mua vào mart — việc đó thuộc một đơn vị khác và **không** làm ở đây; U1 đã xong, không mở lại.

**Chỗ cũ đã bị thay.** `delivered_population` (grain đơn, đòi 96.478 đơn / 7.826 đơn trễ) **bị thay** bằng phép kiểm quần thể grain dòng hàng: 110.195 dòng / 96.476 đơn / 8.713 dòng trễ — cùng bốn bộ đếm của `CohortCounts`, không phải một hằng thứ hai.

## W2 — Chia tập

| # | Bước | Điều kiện dừng |
|---|---|---|
| 1 | Lấy tập `order_id` duy nhất, chia tại `SPLIT_DATE` trên `date_key` của đơn | — |
| 2 | Gán cả **dòng hàng** theo `order_id`, không theo dòng | — |
| 3 | Kiểm giao hai tập `order_id` | giao khác rỗng ⇒ `ModelError` (BR2.2) |
| 4 | Ghi `SplitPlan` (cut_date, split_column, grain, train_n, test_n) | một phía rỗng ⇒ `ModelError` |
| 5 | `split_summary` kiểm `train_n + test_n == CohortCounts.cohort_rows` | lệch `cohort_rows` ⇒ `ModelError` (BR2.2) |

`split_summary` **không** còn nhận `expected_total = EXPECTED_DELIVERED` (96.478): cỡ mẫu kỳ vọng là `cohort_rows` của chính lần đọc. Chia theo `date_key` không phải chỗ sinh rò rỉ — ngày đặt là thuộc tính của đơn nên mọi dòng của một đơn luôn cùng một phía; chỗ sinh rò rỉ là chia ngẫu nhiên ở grain dòng, và đó là điều bước 2–3 chặn.

## W3 — Huấn luyện hai mô hình

| # | Bước | Điều kiện dừng |
|---|---|---|
| 1 | `validate_features()` — đúng **14** tên của `feature_contract`, đúng thứ tự | cột lạ, sai thứ tự, cột cấm, hay cột nội bộ ⇒ `ModelError` (BR2.3) |
| 2 | Mã hoá: one-hot **khớp trên tập huấn luyện**, số hoá + chuẩn hoá **khớp trên tập huấn luyện** | — |
| 3 | Fit logistic trên tập huấn luyện | không hội tụ ⇒ `ModelError` |
| 4 | Fit `HistGradientBoosting` trên **cùng** ma trận, cùng seed | — |
| 5 | Chấm điểm cả hai trên tập kiểm tra ⇒ `auc`, `auc_tree` | — |
| 6 | Chọn ngưỡng trên `THRESHOLD_GRID` theo F1 ⇒ `threshold`, `precision`, `recall` | ngưỡng ngoài (0,1) ⇒ `ModelError` (BR2.5) |
| 7 | Đóng góp log-odds: hệ số × giá trị, **gộp theo trường**, chọn ba lớn nhất | — |

## W4 — Đo baseline và dựng khối mô hình

| # | Bước | Điều kiện dừng |
|---|---|---|
| 1 | Gọi `measure_state_baseline` của U1 với `cut_date = SPLIT_DATE` trên **cùng** khung | `ModelError` từ U1 |
| 2 | Lắp `BaselineMeasurement` (feature, auc, `cohort_rows` từ `CohortCounts` do chính U2 sinh ở W1, same_split_as_model = true) | — |
| 3 | `beats_baseline = auc > baseline_auc`, cả hai trên giá trị đã làm tròn | lệch ⇒ `ModelError` (BR2.6) |
| 4 | `auc_below_target = auc < AUC_TARGET` trên giá trị đã làm tròn | — |
| 5 | Dựng `counts` **chín** khoá | thiếu khoá ⇒ `ModelError` (BR2.7) |
| 6 | Dựng `ModelBlock` 11 trường, `split` giữ **sáu** khoá của v2 | — |

## W5 — Ghi báo cáo và lưu mô hình

| # | Bước | Điều kiện dừng |
|---|---|---|
| 1 | `PipelineStages` gọi `assemble_report(stats, model, stamp)` | — |
| 2 | `assemble_report` đọc báo cáo cũ, giữ khối `model` khi người gọi không truyền khối mới | — |
| 3 | Ghi nguyên tử: tệp tạm → parse lại → kiểm cấu trúc → `os.replace` | parse lỗi ⇒ `ReportError`, tệp cũ còn nguyên |
| 4 | `ModelPersistence.save(FittedModel)` → `data/models/*.pkl` + `*.json` | ghi lỗi ⇒ `ModelError` |
| 5 | Nạp lại để kiểm: `load_model` trả đúng `feature_names` và trạng thái tiền xử lý | lệch ⇒ `ModelError` (BR2.8) |

## W6 — Chấm điểm một dòng hàng (C3)

Luồng của `score_item`, chạy **mỗi lần người dùng bấm Dự đoán** — không thuộc lần chạy lô `--stage stats`, không đọc tệp, không mở kết nối.

| # | Bước | Điều kiện dừng |
|---|---|---|
| 1 | U3 nạp `FittedModel` qua C2b và đọc `threshold` ở `model.threshold` của C2, rồi truyền cả hai vào | tệp vắng ⇒ trạng thái "mô hình chưa sẵn" ở U3, W6 không chạy |
| 2 | Kiểm 11 khoá nhập của `feature_contract.serve_inputs` | thiếu, sai kiểu, hay ngoài miền ⇒ `ModelError` nêu **TÊN TRƯỜNG** (BR2.11) |
| 3 | Dựng đúng **14** cột đặc trưng theo `serve_inputs.mapping`: tháng/thứ từ `order_date`, `customer_region` từ `state_regions`, `item_price_max`/`item_total` từ `item_price`, hai ô số ngày giữ nguyên | thiếu trạng thái đã lưu để mã hoá ⇒ `ModelError` (BR2.8) |
| 4 | Chấm bằng trạng thái đã lưu — phạm trù one-hot, `scaler_means`/`scaler_scales`, `feature_names` — **không** khớp lại | lệch số cột so với `feature_names` ⇒ `ModelError` (BR2.3) |
| 5 | Trả `PredictionOutcome` (probability, verdict so với `threshold`, ba đóng góp gộp theo trường) | — |

**Tất định là điều kiện, không phải mong muốn.** Cùng `FittedModel` + cùng 11 giá trị nhập ⇒ cùng probability tuyệt đối, qua nhiều lần bấm, qua hai lần chạy dashboard, và sau khi khởi động lại (FR3.4). Không `random`, không đọc đồng hồ, không phụ thuộc thứ tự gọi.

**Hai ô số ngày của biểu mẫu trùng độ phân giải với lúc huấn luyện.** Biểu mẫu hỏi thẳng "số ngày đặt→duyệt" và "số ngày duyệt→bàn giao"; đó đúng là hai số nguyên ngày mà W1 bước 4 dựng ra, nên không có phép đổi chiều hay làm tròn nào ở lúc chấm điểm.

## Mô hình quan hệ

```mermaid
erDiagram
  TrainingFrame ||--|| SplitPlan : "chia theo order_id"
  TrainingFrame ||--|| CohortCounts : "cùng một truy vấn"
  SplitPlan ||--o{ FittedModel : "huấn luyện"
  FittedModel ||--|| ModelArtifact : "lưu xuống đĩa"
  BaselineMeasurement ||--|| ModelBlock : "một trường của khối"
  FittedModel ||--|| ModelBlock : "auc, threshold, precision, recall"
  FittedModel ||--o{ PredictionOutcome : "score_item (C3)"
  PredictionOutcome ||--|{ PredictionContribution : "ba đóng góp, gộp theo trường""
```

## Trạng thái và chuyển tiếp

Tầng này là một lần chạy theo lô, không có máy trạng thái: `run --stage stats` chạy trọn W1→W5 hoặc dừng ở lỗi đầu tiên. Không có trạng thái "đang huấn luyện" được lưu — nếu chạy lại, nó chạy lại từ đầu và ghi đè nguyên khối.

W6 khác hẳn: nó là một lời gọi hàm đồng bộ, mỗi lần một dòng, không lưu gì và không đổi gì trên đĩa. Trạng thái duy nhất nó dùng là `FittedModel` đã nạp, và trạng thái duy nhất mà cả tầng này sở hữu là **tệp báo cáo** — trạng thái đó thuộc C2 (`day-du` / `mot-phan` / `rong` / `loi`), U3 đọc, U2 ghi.

## Tóm tắt luật (dẫn xuất từ `rules.md`)

| ID | Một dòng |
|---|---|
| `BR2.1` | Quần thể dòng hàng, một truy vấn, bốn bộ đếm, trả cặp `(TrainingFrame, CohortCounts)` |
| `BR2.2` | Chia theo `order_id`, giao rỗng, tổng lấy từ `CohortCounts` |
| `BR2.3` | Đúng 14 đặc trưng, đúng thứ tự; cột cấm bị từ chối |
| `BR2.4` | Hai mô hình cùng đặc trưng/mốc/quần thể/seed |
| `BR2.5` | Ngưỡng trên lưới, là nguồn duy nhất |
| `BR2.6` | Baseline đo lại; hai cờ trên giá trị đã làm tròn |
| `BR2.7` | v3, 11 trường, 9 khoá; thiếu ⇒ `loi` |
| `BR2.8` | `pickle` + metadata; không khớp lại lúc chấm điểm |
| `BR2.9` | `assemble_report` là đường duy nhất |
| `BR2.10` | Ba đóng góp gộp theo trường |
| `BR2.11` | `score_item`: 11 giá trị nhập → 14 đặc trưng, trạng thái đã lưu, tất định |
| `BR2.12` | `MODEL_AUC_FLOOR` + `beats_floor` thuộc U2; U3 chỉ import và gọi |

**Hợp đồng đặc trưng ở đâu.** Danh sách 14 cột — tên, thứ tự, nhóm mã hoá, cách dẫn xuất, danh sách cấm và ánh xạ từ 11 giá trị nhập — nằm trong khối `feature_contract` của `rules.md`; W1 bước 5 và W3 bước 1 dựa vào đúng khối đó, không khai lại danh sách ở đây.

## Điều kiện xong của đơn vị

1. `--stage stats` trên dữ liệu thật sinh báo cáo v3 + tệp mô hình; `auc > baseline_auc`.
2. `counts` chín khoá đúng giá trị; hai cờ khớp phép so; bốn bộ đếm quần thể đúng 110.195 dòng / 96.476 đơn / 8.713 dòng trễ / 2 đơn thiếu carrier date.
3. Bộ số baseline mới thay ở **năm nơi** (FR1.4); ba khai báo ngân sách cập nhật theo số đo mới.
4. ADR-008 thực thi: không còn chỗ thứ hai dựng `AnalysisReport`.
5. Chạy `--stage stats` hai lần cho cùng `auc_tree`.
6. Test end-to-end `slow` của U2 xanh.
7. `delivered_population` (grain đơn) và `split_summary(expected_total=96_478)` **đã bị thay**: phép kiểm quần thể nay là 110.195 dòng / 96.476 đơn / 8.713 dòng trễ, và `split_summary` lấy tổng từ `CohortCounts` — `EXPECTED_DELIVERED`/`EXPECTED_LATE` không còn là hằng của khung mới.
8. `FEATURES` có đúng **14** cột đúng thứ tự `feature_contract`; `validate_features` đỏ khi sai tên, sai thứ tự, hoặc có cột nội bộ; `order_approved_at` nằm trong `FORBIDDEN_COLUMNS`.
9. `MODEL_AUC_FLOOR = 0.55` cạnh `AUC_TARGET` trong `model.py`, và `beats_floor(auc, baseline_auc, floor)` có test đơn vị cho cả nhánh đỏ lẫn nhánh xanh; U3 chỉ `import`.
10. `score_item` chấm được một dòng hàng từ 11 giá trị nhập, trả `PredictionOutcome`; hai lần gọi liên tiếp cho cùng probability; thiếu một trường thì `ModelError` nêu đúng tên trường.
