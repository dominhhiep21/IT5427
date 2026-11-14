# NFR Validation Matrix

Nguồn: `test-results.md`, `load-test-plan.md`, `../../construction/u1-statistics/nfr-requirements/performance-requirements.md`, `../../construction/u1-statistics/nfr-requirements/scalability-requirements.md`, `../../construction/u1-statistics/nfr-design/performance-design.md`, `../../construction/u1-statistics/nfr-design/scalability-design.md`, `../../construction/u3-display/nfr-requirements/performance-requirements.md`, `../../construction/u3-display/nfr-design/performance-design.md`, `../../../inception/requirements-analysis/requirements.md`, `../observability-setup/dashboards.md`.

## Ma trận mốc so với thực đo

Cột **Bằng chứng** nói phép đo đến từ đâu, vì "đạt" có ba mức độ khác nhau và gộp chúng lại là cách để một bảng nói dối.

| Mã | Mốc | Thực đo | Kết luận | Bằng chứng |
|---|---|---|---|---|
| NFR1.1 | tầng `stats` dưới 5 phút | **3,49–3,70 s** | **ĐẠT** — dư hai bậc độ lớn | đo thật, 3 lần chạy; có test `slow` canh |
| NFR1.2 | mỗi phép dưới 60 s | **78,6–244,8 ms** (5 phép) | **ĐẠT** | đo thủ công trong phiên này — **không có test canh** |
| NFR1.2 | huấn luyện dưới 15 phút | **1,56 s** | **ĐẠT** — dư gần ba bậc | đo thủ công; test `slow` U2 khẳng định dưới 15 phút |
| NFR1.3 | đỉnh bộ nhớ dưới `quality.memory_fail_mb` (2.048 MB) | **8,45 MB** | **ĐẠT** — dư hơn 200 lần | `MemoryProbe` trong test `slow` U1 |
| NFR1.4 | chi phí phân rã tuyến tính theo số tháng | 8× độ dài → **2,55× thời gian** | **ĐẠT** (dưới tuyến tính) | đo thủ công — **không có test canh** |
| NFR1.5 | dữ liệu 5× vẫn dưới 5 phút | **không đo được** | **N/A — giả định** | `dataset/` bất biến, chỉ một cỡ |
| NFR1.6 | bộ nhớ đỉnh tăng tuyến tính theo số dòng | 20k→40k→80k: ×1,98; ×2,00 | **ĐẠT** | đo thủ công — **không có test canh** |
| NFR1.7 | số nhóm chặn bởi 27 bang / 36 tháng / 5 vùng | 27 / 26 / 5 | **ĐẠT** | test đơn vị trên dữ liệu thật (U1) |
| NFR2 | phủ test ≥ 80% | **92,45%** (537 passed) | **ĐẠT** | `ci.yml:46`, cổng thật |
| NFR3 | 5 KPI + 9 bảng + 11 view không hồi quy | khớp cả năm KPI | **ĐẠT** | `KpiReconciler`, `StarSchemaValidator` |
| NFR4 | `ruff check .` và `ruff format --check` sạch | sạch | **ĐẠT** | CI |
| NFR5.1 | tương phản ≥ 4,5:1 trên mọi cặp (chữ, nền) của tab | đạt trên `--text` và `--text-2`; `--text-3` bị loại khỏi tab vì chỉ 3,85:1 | **ĐẠT** | test đơn vị đọc token từ `assets/style.css` |
| NFR5.2 | 100% vùng có nhãn | 100% | **ĐẠT** | test đơn vị duyệt cây thành phần |
| NFR5.3 | đi được bằng bàn phím, đúng thứ tự đọc | đạt | **ĐẠT** | test đơn vị trên `tabIndex` |
| NFR5.4 | không vỡ bố cục ở 1280px | đạt | **ĐẠT** | xem bằng mắt ở bước 4 của chuỗi xác nhận |
| NFR5.5 | tab dựng dưới 1 giây | trung vị **0,917–1,157 ms** | **ĐẠT** — dư ba bậc | đo thủ công 20 lần; **không có test canh** |
| NFR5.6 | đúng một `read_report` mỗi callback | đúng một | **ĐẠT** | test đơn vị có stub đếm |

## Bốn mức độ của chữ "đạt"

| Mức | Nghĩa | Mã |
|---|---|---|
| **Đạt, có test canh** | một thay đổi làm vỡ nó sẽ khiến CI đỏ | NFR1.1, NFR1.2 (nửa huấn luyện), NFR1.3, NFR1.7, NFR2, NFR3, NFR4, NFR5.1, NFR5.2, NFR5.3, NFR5.6 |
| **Đạt, chỉ đo thủ công** | hôm nay đúng số, nhưng không có gì báo khi nó hỏng | NFR1.2 (nửa từng phép), NFR1.4, NFR1.6, NFR5.5 |
| **Đạt bằng mắt** | không phải phép đo; một lần xem ở 1280px | NFR5.4 |
| **Không kết luận** | không đo được, và không được suy ra | NFR1.5 |

Bốn mục ở mức hai là **khoảng trống thật**, không phải chi tiết hình thức. Một thay đổi làm `train_model` chậm gấp mười (1,56 s → 15,6 s) vẫn dưới mốc 15 phút và vẫn xanh CI; chỉ khi vượt hẳn mốc mới có test bắt.

Cách bịt, rẻ nhất trước: thêm ba test đơn vị có mốc rộng cho `train_model`, `seasonal_decomposition` và `price_freight_correlation` — cùng kiểu với đề nghị `R-04` ở `review-02.md` của U3. Không làm trong stage này vì stage này đo, không sinh mã.

## NFR1.5 ở lại dạng giả định

`scalability-design.md` của U1 đã ghi NFR1.5 là giả định, và phép đo ở đây không đổi được điều đó: muốn kiểm cần dữ liệu 5 lần cỡ, mà `dataset/` là bất biến và chỉ có một cỡ.

Điều **có thể** suy ra từ P2 và P3: cả thời gian lẫn bộ nhớ đều tăng **không nhanh hơn tuyến tính** theo kích thước đầu vào. Nếu tuyến tính giữ đến 5×, `stats` sẽ vào khoảng 18 s — vẫn dưới 300 s. Nhưng đó là **suy luận**, không phải phép đo, và nó phải được ghi đúng như vậy.

## Kết luận

17 dòng NFR trong phạm vi ba đơn vị: **11 đạt có test canh**, **4 đạt chỉ nhờ đo thủ công**, **1 đạt bằng mắt** (NFR5.4), **1 không kết luận** (NFR1.5). Không có mục nào bị đánh đạt mà thiếu bằng chứng, và không có ngưỡng nào bị nới để đạt.
