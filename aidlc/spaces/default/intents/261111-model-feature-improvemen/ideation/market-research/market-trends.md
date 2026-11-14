# Market Trends

Nguồn: `../intent-capture/intent-statement.md`, `competitive-analysis.md`, `../../../261109-stats-and-models/operation/feedback-optimization/feedback-loop.md`, `dataset/olist_orders_dataset.csv`.

## Không có xu hướng thị trường để báo cáo, và đây là lý do cụ thể

"Một xu hướng" là một khẳng định về thứ đang thay đổi ngoài kia, và nó cần một nguồn. Workspace này không có nguồn nào như vậy [intent-statement]. Bịa ra một xu hướng — "ngành đang chuyển sang mô hình chuỗi cung ứng", "dự đoán trễ đang là ưu tiên" — sẽ là đúng loại khẳng định mà ideation guardrail cấm: trình bày suy đoán như sự thật.

## Thứ thật sự đang thay đổi trong phạm vi dự án này

| Điều thay đổi | Bằng chứng | Hệ quả |
|---|---|---|
| Bản thân mô hình đã đổi một lần và **tệ đi** | 11 đặc trưng cho 0,5133, một đặc trưng cho 0,5333 [feedback-loop] | thêm đặc trưng không tự động là cải thiện; hướng của đợt này phải chứng minh ngược lại |
| Khung dự đoán đã đổi | đợt này chuyển sang lúc bàn giao [intent-statement] | mọi con số cũ mất hiệu lực so sánh cho tới khi đo lại |
| Kỳ dữ liệu | `dataset/` phủ 2016-09-04 … 2018-10-17, đóng băng | không có "xu hướng theo thời gian" nào để ngoại suy; mọi kết luận chỉ đúng cho giai đoạn này |

## Điều đáng gọi là xu hướng, và nó nằm trong repo

Chuỗi ba đợt của dự án cho thấy một mẫu rõ: **mỗi lần thêm năng lực, con số chất lượng lại không tự cải thiện.** Đợt một dựng được thống kê; đợt hai dựng được mô hình nhưng nó thua baseline một cột; đợt ba (đợt này) phải sửa chính điều đó.

Đó không phải xu hướng thị trường, nhưng nó là xu hướng **của dự án**, và nó dự báo đúng thứ cần cảnh giác: một đợt nữa thêm đặc trưng mà không đo lại baseline sẽ lặp lại đúng kết quả của đợt trước [feedback-loop].

## Về tính chuyển giao — điều không được hứa

Dữ liệu đóng băng ở 2018, nên một mô hình đạt 0,70 trên đó **không** chứng minh nó dự đoán được đơn hàng của hôm nay. Người làm đã chốt: kết luận **chỉ đúng cho giai đoạn 2016–2018**, và giới hạn này phải được ghi ở mọi nơi có con số [intent-statement].

Ghi rõ ở đây để không ai đọc con số cuối cùng thành một cam kết về tương lai — và để câu "đạt 0,70" luôn đi kèm câu "trên dữ liệu 2016–2018".

## Điều không có

Không báo cáo ngành, không dữ liệu khảo sát thị trường, không phân tích đối thủ thương mại, không dự phóng quy mô thị trường. Không có gì để tổng hợp, và không có nguồn nào để trích.
