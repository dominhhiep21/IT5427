# Test Results — Performance Validation

Nguồn: `load-test-plan.md`, `../../construction/u1-statistics/nfr-requirements/performance-requirements.md`, `../../construction/u1-statistics/nfr-requirements/scalability-requirements.md`, `../../construction/u1-statistics/nfr-design/performance-design.md`, `../../construction/u1-statistics/nfr-design/scalability-design.md`, `../../construction/u3-display/nfr-requirements/performance-requirements.md`, `../../construction/u3-display/nfr-design/performance-design.md`, `../observability-setup/dashboards.md`.

## Môi trường đo

| Mục | Giá trị |
|---|---|
| Máy | Windows, máy người làm — cùng máy đã dùng cho `build-and-test` |
| Python | 3.13, trong `.venv`, mọi lệnh chạy `-X utf8` |
| Dữ liệu | `dataset/` thật: 99.441 đơn, 112.650 dòng hàng, 96.478 đơn `delivered` |
| Thời điểm | 2026-11-11 |
| Mô hình | `scikit-learn 1.6.1`, `numpy 2.2.1`, `scipy 1.15.2` |

## P1 — Lặp lại và tất định

| Lần | Thời gian tường | `late_rate.rate` | `model.auc` | `model.threshold` |
|---|---|---|---|---|
| 1 | 3,696 s | 0,0811 | 0,5133 | 0,4 |
| 2 | 3,493 s | 0,0811 | 0,5133 | 0,4 |
| 3 | 3,609 s | 0,0811 | 0,5133 | 0,4 |

**Đạt.** Ba con số giống nhau tuyệt đối; chênh lệch thời gian giữa lần nhanh nhất và chậm nhất là **0,203 s trên 3,7 s ≈ 5,5%**, dưới mốc 20% của kế hoạch.

## P2 — Dò quy mô theo số tháng (NFR1.4)

| Số tháng | Thời gian trung bình |
|---|---|
| 120 | 1,682 ms |
| 240 | 1,961 ms |
| 480 | 2,895 ms |
| 960 | 4,283 ms |

**Đạt.** Độ dài tăng **8 lần** (120 → 960), thời gian tăng **2,55 lần**. Tăng trưởng **dưới tuyến tính**, nên chắc chắn không có chi phí bậc hai ẩn: `rolling` một lượt của `PD-4` đúng như thiết kế.

Một quan sát phụ đáng ghi: ở 36 so với 72 tháng thì tỉ lệ là **0,94** (1,363 ms so với 1,286 ms) — ở độ dài nhỏ, chi phí cố định của pandas lớn hơn phần tăng thêm, nên phép đo hai điểm ngắn **không** phân biệt được tuyến tính với hằng số. Phải đo ở chuỗi dài mới thấy độ dốc.

## P3 — Dò quy mô theo số dòng (NFR1.6)

| Số dòng | Đỉnh `tracemalloc` | Tỉ lệ so với mức trước |
|---|---|---|
| 20.000 | 1,24 MB | — |
| 40.000 | 2,45 MB | ×1,98 |
| 80.000 | 4,89 MB | ×2,00 |

**Đạt.** Nhân đôi số dòng làm đỉnh bộ nhớ tăng đúng 2 lần, hệ số góc không đổi; quy ra khoảng **61 byte mỗi dòng**, phần lớn là hai `Series` `float64` của `price` và `freight_value` sau khi `astype`.

## P4 — Thời gian từng phép và toàn tầng

| Phép | Thời gian (truy vấn + tính) |
|---|---|
| BR1.1 tỉ lệ trễ | **244,8 ms** |
| BR1.2 so sánh bang | 78,6 ms |
| BR1.3 tương quan giá–phí | 129,0 ms |
| BR1.4 vùng × trễ | 78,8 ms |
| BR1.5 mùa vụ | 145,1 ms |
| **Tổng năm phép** | **676,3 ms** |

| Mục khác | Giá trị | Mốc |
|---|---|---|
| `collect_stats` trọn vẹn (5 truy vấn + 5 phép + dựng khối) | **619,2 ms** | — |
| Huấn luyện mô hình `train_model` | **1.560,3 ms** | dưới 15 phút (900.000 ms) |
| Toàn tầng `run --stage stats`, tính cả khởi động Python | **3,49–3,70 s** | dưới 5 phút (300 s) |
| Đỉnh bộ nhớ của `collect_stats` (`MemoryProbe`) | **8,45 MB** | dưới 2.048 MB (`quality.memory_fail_mb`) |

**Đạt cả bốn.** Con số `collect_stats` (619,2 ms) nhỏ hơn tổng năm phép đo riêng (676,3 ms) vì lần đo riêng cộng thêm chi phí mở kết nối riêng cho từng phép — chênh lệch là nhiễu khởi tạo, không phải mâu thuẫn.

## P5 — Thời gian dựng tab (NFR5.5)

Hai lượt đo, mỗi lượt 20 lần gọi `render_analysis(config, "phan-tich")` trên `data/reports/analysis.json` thật:

| Lượt | Lần đầu | 19 lần sau | Trung vị | P95 |
|---|---|---|---|---|
| A | 3,32 ms | 0,78–1,48 ms | **1,157 ms** | — |
| B | 8,11 ms | 0,78–1,48 ms | **0,917 ms** | 1,481 ms |

**Đạt.** Lần gọi **đầu tiên** của mỗi lượt đắt hơn hẳn (3,3 ms và 8,1 ms) — đó là chi phí khởi tạo thành phần Dash, không phải chi phí đọc tệp. Mọi lần sau ở dưới 1,5 ms, cách xa mốc 1 giây hơn hai bậc độ lớn.

**NFR5.6** (đúng một `read_report` mỗi callback) đã có test canh: `tests/unit/test_dashboard_analysis_tab.py::test_callback_reads_the_report_exactly_once`.

## Phân tích điểm nghẽn

| Hạng | Thành phần | Thời gian | Chiếm bao nhiêu của tầng |
|---|---|---|---|
| 1 | Huấn luyện mô hình | 1.560 ms | ~42% của 3,7 s |
| 2 | Năm phép kiểm định | 619–676 ms | ~17% |
| 3 | Dựng mart đã có sẵn + nạp `pandas`/`scipy`/`scikit-learn` | phần còn lại ~1,5 s | ~40% |

Điểm nghẽn lớn nhất **không phải** thuật toán mà là **nhập thư viện**: gần 40% thời gian tầng là chi phí cố định của tiến trình Python, không đổi theo dữ liệu. Đây là lý do `performance-design.md` của U1 đúng khi không tối ưu truy vấn thêm: cắt một truy vấn 100 ms không cứu được 1,5 s khởi động.

## Điều các con số này **không** nói

Bốn phép đo NFR1.2 (nửa từng phép), NFR1.4, NFR1.6 và NFR5.5 ở trên là **đo thủ công trong phiên này**. Không có test nào canh chúng — khác với NFR1.1, NFR1.3 và NFR5.6 vốn đã có test. Hệ quả cụ thể: một thay đổi làm chậm `train_model` gấp mười lần sẽ **không** làm CI đỏ.

Đó là khoảng trống thật, đã ghi ở `nfr-validation-matrix.md`, và cách bịt rẻ nhất là thêm ba test đơn vị có mốc rộng (như cách NFR5.5 từng được đề nghị ở `review-02.md` của U3). Tôi không thêm chúng trong stage này vì stage này đo và ghi lại, không sinh mã — và thêm mã ở đây sẽ vượt phạm vi đợt mà không có cổng duyệt nào.
