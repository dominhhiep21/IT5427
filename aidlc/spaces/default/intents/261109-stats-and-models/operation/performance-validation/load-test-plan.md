# Load Test Plan

Nguồn: `../../construction/u1-statistics/nfr-requirements/performance-requirements.md`, `../../construction/u1-statistics/nfr-requirements/scalability-requirements.md`, `../../construction/u1-statistics/nfr-design/performance-design.md`, `../../construction/u1-statistics/nfr-design/scalability-design.md`, `../../construction/u3-display/nfr-requirements/performance-requirements.md`, `../../construction/u3-display/nfr-design/performance-design.md`, `../observability-setup/dashboards.md`.

## Kế hoạch này không phải kế hoạch tải, và tên tệp giữ nguyên để khớp hợp đồng

"Load test" giả định có lưu lượng: nhiều người gọi cùng lúc, đường cong tải, điểm bão hoà. Hệ thống này không có cả ba. Nó chạy theo lệnh trên một máy, một người dùng, và `performance-design.md` của U1 đã ghi rõ "không song song hoá năm phép".

Vậy nên thứ được kiểm ở đây là **ba loại phép đo khác**, và mỗi loại trả lời đúng câu hỏi mà một load test sẽ trả lời nếu có tải:

| Loại | Thay cho | Trả lời câu hỏi gì |
|---|---|---|
| Lặp lại nhiều lần | kiểm tra tải bền | chạy nhiều lần có ra cùng số không, thời gian có ổn định không |
| Dò quy mô (scale probe) | kiểm tra mở rộng | chi phí thời gian và bộ nhớ tăng thế nào khi dữ liệu dài hơn |
| Đo từng phép | phân tích điểm nghẽn | phép nào chiếm phần lớn thời gian |

## P1 — Lặp lại và tất định

| Mục | Giá trị |
|---|---|
| Lệnh | `python -X utf8 -m src.pipeline run --stage stats` |
| Số lần | 3 lần liên tiếp trên cùng dữ liệu |
| Ghi lại | thời gian tường, `late_rate.rate`, `model.auc`, `model.threshold` |
| Điều kiện đạt | ba lần cho **cùng ba con số**; thời gian không lệch quá 20% giữa lần nhanh nhất và chậm nhất |
| Vì sao | một tầng thống kê cho ra số khác nhau giữa hai lần chạy là lỗi nặng hơn chậm: nó làm mọi so sánh sau đó vô nghĩa |

## P2 — Dò quy mô theo số tháng (NFR1.4)

| Mục | Giá trị |
|---|---|
| Hàm | `seasonal_decomposition` trên chuỗi dựng tại chỗ |
| Độ dài | 120, 240, 480, 960 tháng |
| Số lần mỗi độ dài | 10, lấy trung bình |
| Điều kiện đạt | thời gian tăng **không nhanh hơn** độ dài — tỉ lệ thời gian ≤ tỉ lệ độ dài |
| Vì sao | `PD-4` hứa chi phí tuyến tính bằng `rolling` một lượt; một vòng lặp ẩn sẽ làm chi phí thành bậc hai và chỉ lộ ra khi dữ liệu dài |

## P3 — Dò quy mô theo số dòng (NFR1.6)

| Mục | Giá trị |
|---|---|
| Hàm | `price_freight_correlation` trên khung dựng tại chỗ |
| Số dòng | 20.000, 40.000, 80.000 |
| Đo | `tracemalloc` đỉnh, tính bằng MB |
| Điều kiện đạt | nhân đôi số dòng thì đỉnh bộ nhớ tăng khoảng 2 lần (hệ số góc không đổi) |
| Vì sao | `SCD-3` nói bộ nhớ tỉ lệ với số **nhóm**; đo trên một hàm nhận dòng thô là phép kiểm ngược lại — nếu nó cũng tuyến tính thì không có chỗ nào giữ dòng thô lại |

## P4 — Thời gian từng phép và toàn tầng (NFR1.1, NFR1.2, NFR1.3)

| Mục | Cách đo |
|---|---|
| Năm phép kiểm định | đồng hồ quanh từng cặp (truy vấn + tính), trong cùng tiến trình |
| Huấn luyện mô hình | đồng hồ quanh `train_model(config)` |
| Toàn tầng | thời gian tường của cả tiến trình `run --stage stats`, tính cả khởi động Python |
| Bộ nhớ đỉnh | `MemoryProbe` của `src/common/memory.py` quanh `collect_stats` |

## P5 — Thời gian dựng tab (NFR5.5, NFR5.6)

| Mục | Giá trị |
|---|---|
| Hàm | `render_analysis(config, "phan-tich")` trên tệp `data/reports/analysis.json` thật |
| Số lần | 20 |
| Ghi lại | trung vị, nhỏ nhất, lớn nhất |
| Điều kiện đạt | trung vị dưới 1 giây; và đúng một lần `read_report` mỗi callback (đã có test canh) |

## Điều kế hoạch này không làm, và vì sao

- **Không có kịch bản đồng thời.** Một người dùng, một tiến trình. Thêm 100 luồng gọi cùng lúc sẽ đo tranh chấp khoá DuckDB, không đo hệ thống.
- **Không có kịch bản tăng tải dần.** Không có điểm bão hoà để tìm: mỗi lần chạy là một lần trọn vẹn, không có hàng đợi.
- **Không đặt cổng thời gian trong CI.** Máy CI khác máy phát triển; một cổng thời gian sẽ đỏ vì lý do không liên quan tới thay đổi. Các con số dưới đây là **mốc nghiệm thu đo một lần**, đúng như `performance-design.md` của cả U1 và U3 đã ghi.
- **NFR1.5 không có kịch bản.** Dữ liệu 5 lần cỡ hiện tại không tồn tại và `dataset/` là bất biến. Nó ở lại dạng **giả định**, không phải một phép đo bị bỏ quên — xem `nfr-validation-matrix.md`.
