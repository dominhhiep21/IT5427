# Feedback Loop — đầu vào cho đợt kế tiếp

Nguồn: `slo-report.md`, `cost-analysis.md`, `drift-report.md`, `../performance-validation/test-results.md`, `../deployment-execution/health-check-report.md`, `../incident-response/incident-plan.md`, `../observability-setup/dashboards.md`, `../../construction/u2-model/code-generation/reviews/review-01.md`, `../../construction/u1-statistics/code-generation/code-summary.md`.

## Vòng này đã giao gì

Một tầng `stats` là tầng thứ năm của `run --stage`, một tab thứ năm trên dashboard, và 537 test với phủ 92,45%. Năm KPI baseline không đổi, `ruff` sạch, CI xanh trên ba nhánh.

Điều đáng nói nhất không phải số test mà là **một con số đỏ được giữ nguyên chỗ đứng của nó**: AUC **0,5133**, dưới mốc 0,70 của FR2.3, và nó hiện trên tab kèm dòng "không đạt mốc 0,70" thay vì bị làm mờ đi.

## Phát hiện quan trọng nhất của vòng này

Người soát mã của U2 đã chạy lại đúng đường mã trên mart thật và đo được: mô hình 11 đặc trưng có AUC **0,5133**, còn **chỉ một đặc trưng `customer_state`** cho AUC **0,5333**.

Nghĩa là 10 đặc trưng còn lại đang **làm mô hình tệ đi**. Đây không phải "mô hình chưa đủ tốt" — đây là "mô hình đang nhiễu hơn một baseline một cột". Bất kỳ đợt cải thiện nào cũng phải bắt đầu từ đây, và phải đo lại đúng baseline đó.

Nguyên nhân gốc, đã ghi từ `functional-design`: mô hình chỉ được dùng thông tin **có lúc đặt hàng**, còn nhãn trễ phụ thuộc chủ yếu vào những gì xảy ra **sau** đó — người bán giao chậm, đơn vị vận chuyển, tuyến đường. Khung dự đoán này đúng về nghiệp vụ (dự đoán lúc đặt hàng mới có giá trị can thiệp) nhưng nó chặn gần hết tín hiệu.

## Việc nên làm ở đợt kế tiếp, theo thứ tự

| # | Việc | Vì sao bây giờ | Điều kiện nghiệm thu |
|---|---|---|---|
| B1 | **Cải thiện đặc trưng cho U2 + mức B (dự đoán tương tác)** | AUC 0,5133 dưới mốc 0,70 và dưới cả baseline một cột | AUC ≥ 0,70 **và** > 0,5333; danh sách 10 cột cấm giữ nguyên; `auc_below_target = false` |
| B2 | **Sàn chất lượng trong CI** — test khẳng định `auc ≥ 0,55` | hiện một mô hình thoái hoá hoàn toàn vẫn qua mọi cổng; sàn 0,55 nằm dưới mức hiện tại nên không đỏ oan | test mới, đỏ khi AUC tụt dưới 0,55, xanh ở 0,5133 **chỉ khi** B1 chưa xong — nếu B1 xong thì nâng sàn |
| B3 | **Đóng `TD-09`** — bộ nhanh hermetic | trên máy mới clone, bộ "nhanh" vẫn đỏ; CI che lỗ hổng bằng bước dựng dữ liệu | 6 test dashboard tự dựng dữ liệu; `pytest -m "not slow"` xanh trên checkout sạch |
| B4 | **Sửa `DR-1` và `DR-2`** | tài liệu chỉ dẫn sai, không test nào canh | `README.md` mục lint trỏ đúng danh sách; `docs/runbook.md` có mục cho `rong` và `mot-phan` |
| B5 | **Ba test canh NFR1.2, NFR1.4, NFR1.6** (và NFR5.5) | bốn mốc này "đạt" chỉ nhờ đo thủ công trong phiên | test có mốc rộng, không thành cổng thời gian cứng |
| B6 | **Đo NFR1.5 khi có dữ liệu 5×** | hiện là giả định, không suy ra được | có bộ dữ liệu lớn hơn và một lần đo thật |
| B7 | **Lượt làm đẹp tab bằng `refactoring-ui`** | tab đúng chức năng nhưng chưa được soát thị giác | đọc `assets/style.css` trước, không thêm token màu, giữ `--text-2` cho chữ <16px |

## Điều **không** nên làm ở đợt kế tiếp

| Không làm | Vì sao |
|---|---|
| Thêm mô hình thứ hai (cây, gradient boosting) | vấn đề là **đặc trưng**, không phải thuật toán. Đổi thuật toán trên cùng 11 cột sẽ cho cùng trần |
| Dựng dashboard giám sát, SLO, tracing | không có lưu lượng; `observability-setup/` đã ghi lý do cấu trúc cho từng thứ |
| Đổi cấu trúc 5 tab hiện có | mỗi tab đang có test canh hình dạng; đổi là churn không đổi giá trị |
| Tối ưu CI (C-1…C-4 trong `cost-analysis.md`) | ba trong bốn đề xuất đổi một chốt đúng lấy vài giây |
| Mở streaming / micro-batch cho tầng `stats` | dữ liệu vào bất biến và một cỡ; thêm đường ống là thêm chỗ lệch |

## Câu hỏi để lại cho Ideation

Câu hỏi lớn nhất không phải kỹ thuật mà là **sản phẩm**: khung dự đoán "lúc đặt hàng" có phải khung đúng không?

- Giữ khung đặt hàng: dự đoán dùng được để can thiệp sớm, nhưng trần tín hiệu thấp — nên đợt sau phải chấp nhận rằng 0,70 có thể **không đạt được** với dữ liệu này, và nói thẳng điều đó thay vì hạ mốc.
- Chuyển sang khung "lúc bàn giao cho đơn vị vận chuyển": AUC sẽ cao hơn nhiều vì đã biết người bán và tuyến, nhưng cảnh báo muộn hơn — giá trị can thiệp giảm.

Đợt này đã chốt giữ khung đặt hàng (người làm chọn), nên đây là câu hỏi **mở lại có chủ đích**, không phải câu hỏi bị bỏ sót. Nó phải được trả lời ở Ideation trước khi viết bất kỳ đặc trưng nào.

## Chỉ số cần theo dõi ở vòng sau

| Chỉ số | Giá trị hiện tại | Ngưỡng báo động |
|---|---|---|
| AUC trên tập kiểm tra | 0,5133 | dưới 0,5133 là **hồi quy**, khác với "dưới mục tiêu" |
| Baselines so sánh | `customer_state` đơn: 0,5333 | bất kỳ mô hình mới nào thấp hơn 0,5333 là thất bại, không phải "chưa đủ tốt" |
| `train_n + test_n` | 96.478 | lệch nghĩa là bộ lọc trạng thái hoặc mốc cắt đã đổi |
| Độ phủ test | 92,45% | dưới 80% là đỏ CI |
| 5 KPI baseline | khớp | bất kỳ lệch nào là P1 |

## Kết luận của vòng

Hệ thống **chạy đúng** ở mọi mặt vận hành và **yếu ở đúng một mặt**: năng lực dự báo. Không có gì bị ẩn — con số đỏ nằm trên tab người dùng nhìn, bốn mốc đo thủ công được đánh dấu là đo thủ công, và hai chỗ tài liệu sai được ghi thành `DR-1`, `DR-2` thay vì được coi là chuyện nhỏ.

Đó là trạng thái tốt nhất mà một vòng có thể để lại cho vòng sau: **không có gì phải khám phá lại**.
