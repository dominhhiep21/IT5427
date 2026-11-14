# Câu hỏi phân tích và định nghĩa KPI

Tài liệu này chốt **hỏi gì** và **đo bằng công thức nào** cho toàn bộ phần phân tích của đề tài Olist
(mục 5 của bảng phân công; phụ trách: Nguyễn Lâm Nghĩa). Mọi con số trên dashboard, trong báo cáo phân
tích và báo cáo đối soát đều phải tính theo đúng các định nghĩa ở đây.

- Kết quả phân tích: [`analysis-report.md`](analysis-report.md)
- Bằng chứng số liệu đúng: [`reconciliation-report.md`](reconciliation-report.md)
- Mã nguồn: `src/analytics/insights.py` (truy vấn), `src/analytics/reconciliation.py` (đối soát)

## 1. Câu hỏi phân tích

| Nhóm | Câu hỏi nghiệp vụ | KPI trả lời | Phân tích (`--show <mã>`) |
|---|---|---|---|
| Kinh doanh (mục 17) | Sàn bán được bao nhiêu, xu hướng theo thời gian ra sao? | K01, K05, K06, K08, K09 | `kpi_headline`, `monthly_trend`, `yearly_same_period`, `peak_days` |
| | Doanh thu đến từ đâu (vùng, ngày trong tuần, phương thức thanh toán)? | K12, K20 | `revenue_by_region`, `weekday_pattern`, `payment_mix` |
| | Khách có quay lại không? | K10, K11 | `customer_repeat` |
| Sản phẩm, người bán (mục 18) | Danh mục, sản phẩm, người bán nào đóng góp nhiều nhất? Tập trung đến mức nào? | K01, K05, K12 | `category_ranking`, `top_products`, `top_sellers`, `seller_concentration`, `seller_by_state` |
| | Nhóm nào bán nhiều nhưng phục vụ kém? | K15, K17, K18 | `top_sellers`, `category_quality` |
| Giao vận (mục 19) | Giao mất bao lâu, trễ bao nhiêu, khác nhau thế nào giữa các khu vực? | K13, K14, K15, K16 | `delivery_overview`, `delivery_by_region`, `delivery_by_state`, `delivery_monthly`, `delivery_buckets`, `delivery_route` |
| Đánh giá (mục 20) | Khách hài lòng đến đâu? Điểm đánh giá liên hệ thế nào với giao trễ? | K17, K18, K19 | `review_distribution`, `review_by_late`, `review_by_delay`, `review_late_contingency`, `review_confounder` |

## 2. Quy ước chung

| Quy ước | Nội dung | Lý do |
|---|---|---|
| Phạm vi đơn | Chỉ đơn có `order_status = 'delivered'` (cờ `is_delivered`) | Đơn hủy hoặc chưa giao chưa phải doanh thu thực nhận; 97,02% đơn là delivered |
| Mốc thời gian | Mọi KPI gắn với **ngày đặt hàng** (`order_purchase_timestamp` → `date_key`) | Một đơn chỉ thuộc đúng một tháng, nên cộng theo tháng không trùng |
| Tiền tệ | BRL, làm tròn 2 chữ số ở bước cuối | Tránh sai số cộng dồn do làm tròn sớm |
| Khách hàng | Đếm theo `customer_unique_id`, không theo `customer_id` | `customer_id` sinh mới cho mỗi đơn; dùng nó thì mọi khách đều "mới" |
| Đánh giá | Mỗi đơn lấy **một** đánh giá mới nhất | 547 đơn có nhiều đánh giá; ghép thẳng sẽ đếm lặp các đơn đó |
| Giai đoạn thưa | Năm 2016 gắn cờ `is_sparse_period`, không dùng để tính tăng trưởng | 3 tháng năm 2016 chỉ có 267 đơn delivered |
| Grain trước, JOIN sau | Bảng nhiều dòng trên một đơn phải gộp về grain đơn trước khi ghép | Tránh nhân bản dòng (xem DS-09, DS-10 trong báo cáo đối soát) |

## 3. Danh mục KPI

Ký hiệu: `I` = `fact_order_items` (grain: dòng hàng), `O` = `fact_orders` (grain: đơn), `R` = `fact_reviews`,
`P` = `fact_payments`, `C` = `dim_customer`. Mọi công thức đã ngầm lọc `is_delivered`.

| Mã | KPI | Công thức | Bảng, grain | Đơn vị | Tính cộng |
|---|---|---|---|---|---|
| K01 | Doanh thu | `SUM(I.price + I.freight_value)` | I, dòng hàng | BRL | Cộng được |
| K02 | Tiền hàng | `SUM(I.price)` | I | BRL | Cộng được |
| K03 | Phí vận chuyển | `SUM(I.freight_value)` | I | BRL | Cộng được |
| K04 | Tỷ trọng phí vận chuyển | `100 × K03 / K01` | I | % | Không (tỷ số) |
| K05 | Số đơn | `COUNT(DISTINCT order_id)` | I hoặc O | đơn | Không qua danh mục/người bán; có qua thời gian, vùng |
| K06 | Giá trị đơn trung bình (AOV) | `K01 / K05` | I | BRL/đơn | Không (tỷ số) |
| K07 | Số dòng hàng trên một đơn | `COUNT(*) / K05` | I | dòng/đơn | Không (tỷ số) |
| K08 | Tăng trưởng theo tháng | `100 × (K01 tháng này − K01 tháng trước) / K01 tháng trước`, chỉ khi hai tháng liền kề và tháng trước không thưa | I | % | Không |
| K09 | Tăng trưởng cùng kỳ | `100 × (K năm nay − K năm trước) / K năm trước`, trên cùng dải tháng | I | % | Không |
| K10 | Số khách hàng | `COUNT(DISTINCT C.customer_unique_id)` | O ⋈ C | người | Không |
| K11 | Tỷ lệ mua lại | `100 × số khách có ≥ 2 đơn / K10` | O ⋈ C | % | Không |
| K12 | Tỷ trọng doanh thu của một nhóm | `100 × K01 của nhóm / K01 toàn bộ`; lũy kế theo thứ hạng giảm dần | I | % | Cộng được trong cùng một cách chia nhóm |
| K13 | Thời gian giao hàng | `order_delivered_customer_date − order_purchase_timestamp`; báo cáo trung bình, trung vị, phân vị 90 | O, đơn | ngày | Không (thống kê phân phối) |
| K14 | Số đơn giao trễ | `COUNT(*)` các đơn có `order_delivered_customer_date > order_estimated_delivery_date` | O | đơn | Cộng được |
| K15 | Tỷ lệ giao trễ | `100 × K14 / số đơn delivered` | O | % | Không (tỷ số) |
| K16 | Số ngày lệch so với dự kiến | `order_delivered_customer_date − order_estimated_delivery_date` (dương = trễ, âm = sớm) | O | ngày | Không |
| K17 | Điểm đánh giá trung bình | `AVG(review_score)`, mỗi đơn một đánh giá mới nhất | R → O | điểm (1–5) | Không |
| K18 | Tỷ lệ đánh giá thấp | `100 × số đơn có điểm ≤ 2 / số đơn có đánh giá` | R → O | % | Không |
| K19 | Tỷ lệ 5 sao | `100 × số đơn 5 điểm / số đơn có đánh giá` | R → O | % | Không |
| K20 | Cơ cấu thanh toán | `100 × SUM(payment_value) của phương thức / SUM(payment_value)` | P, dòng thanh toán | % | Giá trị cộng được; số đơn thì không |

### Vì sao cột "Tính cộng" quan trọng

- **Cộng được** (doanh thu, số đơn trễ): cộng các nhóm con ra đúng tổng. Có thể lưu sẵn trong bảng aggregate.
- **Không cộng được** (số đơn, số khách): một đơn có thể thuộc nhiều danh mục, một khách có thể mua ở nhiều tháng.
  Phải đếm `DISTINCT` lại ở grain gốc. Cộng cột `orders` của `agg_sales_daily` ra 97.276 thay vì 96.478 (DS-11).
- **Tỷ số** (AOV, tỷ lệ trễ): phải tính lại từ tử số và mẫu số. Trung bình AOV của 23 tháng là 154,39 BRL trong khi
  AOV đúng là 159,83 BRL (DS-12).

## 4. Các quyết định định nghĩa

| Quyết định | Phương án đã chọn | Phương án bị loại | Lý do |
|---|---|---|---|
| Doanh thu lấy từ đâu | Dòng hàng: `price + freight_value` | Tổng `payment_value` | Dòng hàng gắn được với sản phẩm, danh mục, người bán. Thanh toán lệch tiền hàng ở 303 đơn (từ 0,02 BRL trở lên), chủ yếu là đơn trả góp nhiều kỳ (DS-13) |
| Có gồm phí vận chuyển không | Có | Chỉ tiền hàng | Khớp số tiền khách thực trả; K02 và K03 được tách riêng để ai cần vẫn xem được |
| Đơn nào được tính | Chỉ `delivered` | Mọi trạng thái | Xem mục 2 |
| Thế nào là "giao trễ" | So **mốc thời gian** thực tế với dự kiến | So theo ngày lịch | Khớp baseline của nhóm và chặt hơn. Lưu ý: ngày dự kiến luôn là 00:00, nên 1.292 đơn giao trong chính ngày dự kiến bị tính là trễ; theo ngày lịch tỷ lệ là 6,77% thay vì 8,11% (DS-14) |
| Đánh giá nào đại diện cho đơn | Đánh giá mới nhất | Trung bình các đánh giá | Giữ được điểm nguyên 1–5 để lập phân bố và bảng chéo |
| Danh mục của một đơn | Danh mục có doanh thu lớn nhất trong đơn (`fact_orders.category`) khi cần gán đơn vào đúng một nhóm | — | Dùng cho điểm đánh giá và giao trễ theo danh mục. Doanh thu theo danh mục vẫn tính theo từng dòng hàng (DS-17) |

## 5. Giá trị chuẩn

Năm KPI đầu là baseline bắt buộc của nhóm: `src/integrate/reconcile.py` chặn pipeline nếu lệch quá dung sai.
Các giá trị còn lại là giá trị tham chiếu của báo cáo phân tích.

| KPI | Giá trị | Dung sai |
|---|---:|---:|
| K01 Doanh thu | 15.419.773,75 BRL | 0,01 |
| K05 Số đơn | 96.478 | 0 |
| K06 AOV | 159,83 BRL | 0,01 |
| K14 Số đơn giao trễ | 7.826 | 0 |
| K15 Tỷ lệ giao trễ | 8,11% | 0,01 |
| K02 Tiền hàng | 13.221.498,11 BRL | — |
| K03 Phí vận chuyển | 2.198.275,64 BRL (14,26%) | — |
| K10 Số khách hàng | 93.358 | — |
| K11 Tỷ lệ mua lại | 3,00% | — |
| K13 Thời gian giao | trung bình 12,56; trung vị 10,22; phân vị 90: 23,10 ngày | — |
| K17 Điểm đánh giá trung bình | 4,16 | — |
| K18 Tỷ lệ đánh giá thấp | 12,81% | — |

## 6. Liên hệ với các thành phần khác của hệ thống

| Thành phần | Vai trò | Quan hệ với tài liệu này |
|---|---|---|
| `src/common/kpis.py` | Sổ KPI của ba truy vấn mẫu trên tab "Tích hợp" | Dùng cùng định nghĩa K01 (`REVENUE_DEFINITION`) và K15 |
| `src/integrate/reconcile.py` | Cổng chặn pipeline theo baseline | Năm giá trị đầu ở mục 5 |
| `src/analytics/service.py` | Truy vấn phục vụ dashboard | Tính K01, K05, K06, K15 theo bộ lọc |
| `src/analytics/insights.py` | 26 truy vấn phân tích | Hiện thực toàn bộ KPI ở mục 3 |
| `src/analytics/reconciliation.py` | 17 kiểm tra đối soát | Chứng minh các KPI không bị đếm trùng |

## 7. Chạy lại

```powershell
# Đối soát + toàn bộ phân tích, sinh lại docs/analysis-report.md và docs/reconciliation-report.md
.\.venv\Scripts\python.exe -X utf8 -m src.analytics

# Chỉ đối soát (mã thoát 1 nếu có kiểm tra không đạt)
.\.venv\Scripts\python.exe -X utf8 -m src.analytics --check

# Liệt kê và xem từng phân tích
.\.venv\Scripts\python.exe -X utf8 -m src.analytics --list
.\.venv\Scripts\python.exe -X utf8 -m src.analytics --show monthly_trend
```

Yêu cầu: đã chạy `python -X utf8 -m src.pipeline run --stage all` để có `data/marts/`. Phần phân tích đọc
thẳng các tệp Parquet bằng DuckDB trong bộ nhớ, nên chạy được cả khi dashboard đang mở.
