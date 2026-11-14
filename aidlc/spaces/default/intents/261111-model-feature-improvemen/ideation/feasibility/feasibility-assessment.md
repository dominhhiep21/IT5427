# Feasibility Assessment

Nguồn: `../intent-capture/intent-statement.md`, `../market-research/{competitive-analysis,market-trends,build-vs-buy}.md`, `src/analytics/model.py`, `src/analytics/service.py` (`TRAINING_FRAME_SQL`), `warehouse/olist.duckdb`, `data/cleaned/orders.parquet`.

## Kết luận ngắn

**Khả thi, và mạnh hơn dự kiến ở phần dữ liệu — nhưng có một chỗ vướng thật: mart hiện tại không có cột nào của khung mới.** Phần lớn công việc của đợt là *mở đường dữ liệu*, không phải huấn luyện mô hình.

## Bằng chứng đã đo, không phải ước lượng

Đo trực tiếp trên `warehouse/olist.duckdb` ghép `data/cleaned/orders.parquet`:

| Đại lượng | Giá trị | Ý nghĩa |
|---|---|---|
| Dòng hàng thuộc đơn đã giao **và có `order_delivered_carrier_date`** | **110.195** | quần thể huấn luyện theo khung mới |
| Đơn trong quần thể | **96.476** | chia tập theo `order_id` trên đơn vị này |
| Người bán phân biệt | **2.970** | đủ để học đặc trưng theo người bán |
| Dòng hàng trễ | **8.713** (7,91%) | nhãn cân bằng tương đương mức 8,11% ở grain đơn |
| Dòng hàng đã giao **thiếu** carrier date | **2** | gần như không mất mát |
| Đơn đã giao có **nhiều hơn một người bán** | **1.278** | chứng minh dự đoán theo dòng hàng khác thật so với theo đơn |
| Đơn đã giao có nhiều hơn một dòng hàng | **9.635** | cùng lý do |

Ba điều rút ra:

1. **Quần thể đủ lớn.** 110.195 dòng hàng nhiều gấp ~14 lần số đặc trưng dự kiến; không có nguy cơ thiếu mẫu.
2. **Mất mát gần bằng không.** Chỉ 2 dòng hàng thiếu carrier date trên 110.197 — nên lọc theo khung mới **không** làm rỗng quần thể, khác với lo ngại ban đầu về 1.783 đơn thiếu ngày này (con số đó tính trên toàn bộ 99.441 đơn, gồm cả đơn chưa giao).
3. **1.278 đơn có nhiều người bán** là lý do định lượng để đổi đơn vị dự đoán: nếu vẫn dự đoán theo đơn, 1.278 đơn đó phải gộp nhiều người bán vào một điểm nguy cơ duy nhất, và mô hình không thể học "người bán nào chịu trách nhiệm".

## F1 — Chỗ vướng: mart không có cột của khung mới

| Cần | Có trong mart? |
|---|---|
| `order_delivered_carrier_date` | **Không** — `v_fact_orders` không có cột này |
| `order_approved_at` | **Không** — cùng lý do |
| `seller_state` (bang người bán) | **Không** — `v_fact_order_items` chỉ có `seller_id` |

Nhưng `data/cleaned/orders.parquet` **có đủ** `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, và `v_dim_seller` có `state`/`region`. Vậy dữ liệu tồn tại — chỉ là chưa đi tới chỗ mô hình đọc.

Hai đường, và chọn đường nào là một quyết định thật:

| Đường | Việc phải làm | Giá |
|---|---|---|
| **O1 — nới mart** | thêm 2 cột mốc vào `v_fact_orders`, thêm `seller_state` vào `v_fact_order_items`; chạm `src/integrate/*`, `VIEW_TABLES`, `StarSchemaValidator`, test số cột | giữ nguyên tắc "analytics đọc mart"; nhưng đụng vào hợp đồng 11 view và phải cập nhật đồng thời nhiều nơi |
| **O2 — đọc cleaned qua `AnalyticsService`** | một truy vấn mới trong `service.py` đọc `read_parquet` cleaned | không đụng mart, không đổi hợp đồng 11 view; nhưng tạo một nguồn đọc thứ hai cho analytics, và `training_frame` hiện có vẫn ở lại |

Không có đường thứ ba rẻ hơn: `seller_id` một mình không cho biết bang, mà bang người bán là đặc trưng tuyến đường duy nhất dữ liệu này có (như đã ghi ở `intent-statement`).

## F2 — Nhãn là của đơn, đơn vị là dòng hàng

Nhãn `is_late` sống ở grain **đơn**. Ở grain dòng hàng, mọi dòng của một đơn mang cùng nhãn — nên nếu chia tập theo dòng, một đơn xuất hiện ở cả hai phía và AUC bị thổi lên. Bắt buộc phải chia theo `order_id` như `intent-statement` đã ghi.

Hệ quả về đo lường: AUC ở grain dòng hàng **không** so trực tiếp được với AUC 0,5333 ở grain đơn. Đó là lý do Q21 đòi đo lại baseline trong cùng khung — và đây là chỗ kỹ thuật xác nhận lại điều đó.

## F3 — Lưu mô hình là việc mới, chưa từng làm

Đợt trước không lưu mô hình ở đâu cả; `train_model` trả khối rồi thôi. Giao diện dự đoán (Q12 = A, Q13 = C, Q14 = A) cần một mô hình dùng lại được. Việc này khả thi nhưng phải chốt **ba** thứ trước khi viết mã: định dạng tệp, chỗ lưu (và nó có bị `.gitignore` không), và cách kiểm mô hình nạp lại cho đúng cùng kết quả.

## F4 — Mô hình cây không thêm phụ thuộc, nhưng đổi thứ phải kiểm

`HistGradientBoostingClassifier` nằm trong `scikit-learn==1.6.1` đã ghim. Không cần đổi `requirements.txt`, không cần cài gì. Rủi ro duy nhất là nó không cho hệ số — đánh đổi đã được chấp nhận ở `build-vs-buy.md` [intent-statement].

## F5 — Điều không kiểm được

Mốc AUC ≥ 0,70 vẫn là **giả thuyết**. Không có phép đo nào trong đợt này chứng minh khung bàn giao đạt được nó; 110.195 dòng chỉ chứng minh **đủ mẫu**, không chứng minh **đủ tín hiệu**. Đó là rủi ro số một của đợt và nó nằm ở `raid-log.md`, không bị che.

## Bốn quyết định đã chốt ở stage này

| Vấn đề | Chốt | Hệ quả |
|---|---|---|
| Đưa cột mới tới chỗ mô hình đọc | **O1 — nới mart**: thêm 2 cột mốc vào `v_fact_orders`, thêm `seller_state` vào `v_fact_order_items`, **chỉ thêm cột, không đổi số dòng** | phải cập nhật `StarSchemaValidator`, `VIEW_TABLES` và test cùng lúc; hợp đồng 5 KPI và 11 view giữ nguyên vì số dòng không đổi |
| Lưu mô hình | tệp nhị phân trong `data/models/` (bị `.gitignore`) + một tệp JSON mô tả đặc trưng và phiên bản thư viện | lần đầu repo có mô hình lưu lại; `data/models/` phải được thêm vào `.gitignore` nếu chưa có |
| Hai dòng hàng thiếu carrier date | **lọc khỏi quần thể**, ghi rõ số bị lọc trong báo cáo | quần thể còn 110.195 dòng, không gán giá trị giả |
| Mốc cắt tập | giữ **2018-04-01**, chia theo **ngày đặt hàng** | giữ được so sánh với đợt trước |

### Một hệ quả của mốc cắt phải ghi lại

Chia theo **ngày đặt hàng** trong khi dự đoán tại **thời điểm bàn giao** tạo ra một chỗ lệch thời gian: một đơn đặt ngày 2018-03-31 nhưng bàn giao ngày 2018-04-05 nằm ở tập huấn luyện, dù thời điểm dự đoán của nó **sau** mốc cắt. Đó không phải rò rỉ nhãn — nhãn là kết quả giao hàng, muộn hơn nữa — nhưng nó làm yếu tính "ngoài thời gian" của phép chia.

Chấp nhận đánh đổi này vì nó giữ được so sánh với 64.322/32.156 của đợt trước. Nếu về sau cần một phép chia chặt theo thời điểm dự đoán, đó là một thay đổi riêng có ghi lại, không phải sửa lén.
