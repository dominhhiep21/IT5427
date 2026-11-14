# Initiative Brief — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `../intent-capture/{intent-statement,stakeholder-map}.md`, `../market-research/{competitive-analysis,market-trends,build-vs-buy}.md`, `../feasibility/{feasibility-assessment,constraint-register,raid-log}.md`, `../scope-definition/{scope-document,intent-backlog}.md`, `../team-formation/{team-assessment,skill-matrix,mob-composition}.md`, `../rough-mockups/{wireframes,user-flow}.md`.

## Vấn đề, trong một câu

Mô hình dự đoán đơn giao trễ đang **thua baseline một cột**: AUC 0,5133 so với 0,5333 của riêng `customer_state` — thêm 10 đặc trưng nữa lại làm kết quả tệ đi.

## Đợt này làm gì

Đổi ba thứ cùng lúc, có chủ ý:

| Đổi | Từ | Sang |
|---|---|---|
| Khung dự đoán | lúc đặt hàng | **lúc bàn giao cho đơn vị vận chuyển** |
| Đơn vị dự đoán | mỗi đơn | **mỗi dòng hàng** (đơn × món hàng, người bán riêng) |
| Đặc trưng | 11 cột của khung cũ | đặc trưng dựng từ khung mới, gồm hai mốc thời gian ở dạng số ngày và bang người bán |

Và thêm một bề mặt: **vùng nhập liệu dự đoán** trong tab "Kết quả phân tích", chạy từ mô hình đã lưu.

## Đánh giá thị trường — kết luận thật

Không có thị trường bên ngoài. Đối thủ thật của mô hình là **các baseline**, và mốc phải thắng là 0,5333 **đo lại trong khung mới**, không phải con số lịch sử. Dữ liệu đóng băng 2016–2018, nên kết luận **chỉ đúng cho giai đoạn đó** — không hứa gì về tương lai.

## Khả thi — bằng số, không bằng ước lượng

| Đại lượng | Giá trị |
|---|---|
| Dòng hàng thuộc đơn đã giao **và** có `order_delivered_carrier_date` | **110.195** |
| Đơn trong quần thể | **96.476** |
| Người bán phân biệt | **2.970** |
| Dòng hàng trễ | **8.713** (7,91%) |
| Dòng hàng đã giao thiếu carrier date | **2** (trên 110.197) |
| Đơn có nhiều hơn một người bán | **1.278** |

Chỗ vướng thật: **mart không có cột nào của khung mới** — `v_fact_orders` thiếu hai cột mốc, `v_fact_order_items` thiếu bang người bán. Đã chốt: nới mart, **chỉ thêm cột, không đổi số dòng**.

## Rủi ro hàng đầu

| Mã | Rủi ro | Ứng phó |
|---|---|---|
| R-01 | Khung mới **không** đạt AUC 0,70 dù đủ mẫu | đo sớm; người làm quyết định ngay ở Build and Test; đã chấp nhận ở cổng này |
| R-02 | Vẫn thua baseline đo lại | một lần thử cuối bằng mô hình cây rồi công bố kết luận |
| R-04 | Rò rỉ qua đơn vị lồng nhau | chia tập theo `order_id`, có test canh |
| R-08 | Chia tập theo ngày đặt, dự đoán lúc bàn giao | đã biết và chấp nhận; đổi lại mất so sánh với đợt trước |

## Phạm vi

**Trong:** U1 (nới mart + đo baseline) → U2 (đặc trưng + logistic triển khai + cây để báo cáo + lưu mô hình) → U3 (giao diện dự đoán + mốc sàn CI 0,55). Cả ba **Bắt buộc**.

**Ngoài:** thuật toán ngoài `scikit-learn`; API dự đoán; bốn tab còn lại; sửa `dataset/`; đổi hợp đồng 5 KPI / 9 bảng / 11 view; tối ưu CI; SLO và dashboard giám sát.

## Đội và nhịp

Một người, **5–10 giờ/tuần**, ba Bolt, ước lượng **4–7 tuần**. Vai "reviewer độc lập" **không tồn tại** — bù bằng test trên dữ liệu thật và agent soát.

## Hình dạng giao diện

Mục thứ tư trong tab có sẵn (`H3`, cùng cấp ba mục kia), **bảy ô** nhập, kết quả gồm xác suất · so ngưỡng · quyết định · **ba đóng góp log-odds** lớn nhất. Sáu trạng thái, phân biệt bằng chữ chứ không bằng màu.

## Khuyến nghị go/no-go

**GO.** Lý do: vấn đề được phát biểu bằng một con số đo được, quần thể đã đo đủ lớn, đường dữ liệu đã xác định, và tiêu chí thất bại được định nghĩa trước (AUC < 0,70 hoặc ≤ baseline đo lại → ghi không đạt, không hạ mốc).

**Điều kiện:** mốc 0,70 áp cho **mô hình logistic triển khai**; con số AUC của mô hình cây phải xuất hiện trong record cạnh nó, kèm lý do không được chọn.
