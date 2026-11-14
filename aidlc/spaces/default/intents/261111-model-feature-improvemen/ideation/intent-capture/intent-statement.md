# Intent Statement — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

## Problem Statement

Mô hình dự đoán đơn giao trễ hiện có AUC **0,5133**, thấp hơn cả baseline chỉ dùng một đặc trưng `customer_state` (**0,5333**) [desc]. Vấn đề không phải "mô hình chưa đủ tốt" mà là **mô hình đang nhiễu hơn một baseline một cột** — thêm 10 đặc trưng nữa lại làm kết quả tệ đi [desc].

Ba thay đổi lớn so với đợt trước [desc] [Q4]:

- **Đổi khung dự đoán** từ "lúc đặt hàng" sang **"lúc bàn giao cho đơn vị vận chuyển"** — dự đoán muộn hơn nhưng có nhiều thông tin thật hơn để dựa vào [Q4].
- **Đổi đơn vị dự đoán** từ mỗi đơn sang **mỗi dòng hàng**, tức mỗi cặp (đơn, món hàng) có người bán riêng, một điểm nguy cơ [Q5] [Q11].
- **Cho phép hai cột mốc thời gian làm đặc trưng dẫn xuất**: `order_approved_at` và `order_delivered_carrier_date`, chỉ ở dạng **số ngày** (đặt → duyệt, duyệt → bàn giao), không dùng giá trị ngày thô [Q17]. Đây là việc **nới** danh sách cấm của đợt trước đúng hai cột, và việc nới đó phải được ghi rõ ở Functional Design [Q6] [Q17].

### Ranh giới chống rò rỉ — chốt tường minh

| Quy tắc | Nội dung | Nguồn |
|---|---|---|
| Danh sách cấm còn hiệu lực | `order_delivered_customer_date`, `delivery_days`, `is_late`, `late_days`, toàn bộ cột review, `is_delivered`, `has_review` vẫn bị cấm tuyệt đối | [Q6] |
| Hai cột mốc được nới | `order_approved_at` và `order_delivered_carrier_date` được dùng **để tính đặc trưng số ngày**, không dùng làm giá trị ngày thô; `order_delivered_carrier_date` còn là mốc thời gian dự đoán | [Q17] |
| Chia tập theo đơn | Tập huấn luyện và tập kiểm tra chia theo **`order_id`** — mọi dòng hàng của cùng một đơn nằm cùng một phía, vì nhãn trễ là của đơn và đơn vị dự đoán là dòng hàng (112.650 dòng / 98.666 đơn) | [Q11] |
| Quần thể chấm điểm | Chỉ đơn **đã tới bàn giao** (có `order_delivered_carrier_date`) được chấm AUC, vì khung dự đoán đặt tại chính thời điểm đó | [Q4] [Q17] |

Nếu thiếu quy tắc chia tập theo `order_id`, các dòng của cùng một đơn rơi cả hai phía và AUC bị thổi lên — đúng loại rò rỉ mà cả bảng này tồn tại để chặn [Q11].

## Target Customer

Đối tượng đã chốt cho đợt này là **người học / nhóm làm đồ án** — bên hưởng lợi trực tiếp là năng lực phân tích và quy trình cải thiện có kiểm soát, không phải một nhóm người dùng vận hành cụ thể [Q2].

Điều này không mâu thuẫn với mục tiêu nghiệp vụ: vấn đề được đặt ra vì cảnh báo sớm chỉ có giá trị khi mô hình đủ tốt để hành động, **và** vì yêu cầu học thuật phải chứng minh quy trình cải thiện có kiểm soát [Q1]. Nhưng khi phải chọn một bên, đợt này chọn người học [Q2].

**Hệ quả cần nói rõ:** không có người dùng vận hành nào đặt yêu cầu về độ trễ, giao diện hay quy trình can thiệp, nên các tiêu chí đó không được suy ra từ nhu cầu người dùng — chúng chỉ đến từ mục tiêu kỹ thuật [Q2].

## Success Metrics

| Chỉ số | Ngưỡng | Nguồn |
|---|---|---|
| AUC trên tập kiểm tra, khung bàn giao, đơn vị dòng hàng | **≥ 0,70** | [Q3] [desc] |
| AUC so với baseline `customer_state` **đo lại cùng khung và cùng đơn vị** | cao hơn baseline đo lại; **không** ấn định mức chênh | [Q18] [Q21] |
| Mốc sàn chặn mô hình thoái hoá, chạy trong CI | **≥ 0,55** | [Q20] |
| Dự đoán tương tác dùng đúng mô hình đã huấn luyện | cùng một đầu vào cho **cùng một điểm** qua các lần chạy và sau khi khởi động lại dashboard, và điểm đó khớp với mô hình đã lưu | [Q13] [Q14] |
| Bằng chứng quy trình | record của đợt phải có đủ bốn thứ: baseline trước, thay đổi đã làm, kết quả sau, quyết định giữ hay hạ mốc | [Q1] [Q15] |

Bốn tiêu chí này độc lập nhau: một mô hình đạt AUC 0,70 vẫn **không** được coi là xong nếu giao diện không đưa ra được dự đoán từ chính mô hình đó [Q13]; và giao diện chạy đúng không cứu một mô hình dưới mốc [Q3].

**Về mốc 0,70:** đây là **mục tiêu hiện tại** và **chưa có bằng chứng nào cho thấy khung mới đạt được nó** trên dữ liệu hiện có — chính vì vậy mới có mốc sàn 0,55 để không đánh giá một mô hình thoái hoá là "gần đạt" [Q20]. Hạ mốc vẫn là một lựa chọn còn sống; nó không bị chốt trước [Q15].

**Ai quyết định nếu 0,70 không đạt:** người làm quyết định **ngay ở Build and Test khi thấy AUC**, và quyết định đó được ghi vào record thay vì để treo tới cuối đợt [Q19].

**Baseline đo lại là bước đầu tiên**, trước mọi thay đổi đặc trưng, và kết quả được ghi vào record làm mốc so [Q21]. Con số 0,5333 chỉ là tham chiếu lịch sử đo trên đơn ở khung lúc đặt hàng, nên nó không thay được phép đo mới [Q18].

Mô hình được huấn luyện một lần rồi lưu lại; dashboard nạp lại khi mở tab, thay vì huấn luyện lại mỗi lần bấm [Q14]. Đây là thay đổi so với đợt trước, khi mô hình không được lưu ở đâu cả.

## Initiative Trigger

Đợt trước kết thúc với một phát hiện được ghi lại: 11 đặc trưng cho AUC 0,5133, còn **một** đặc trưng `customer_state` cho 0,5333 [desc]. Một mô hình thua baseline một cột là trạng thái không thể để nguyên — hoặc phải sửa, hoặc phải bỏ hướng dự đoán [Q1].

Đợt này là nhánh "phải sửa": giữ hướng dự đoán, đổi khung và đặc trưng [Q4] [Q5]. Mốc 0,70 vẫn là mục tiêu của đợt, nhưng điều gì xảy ra nếu không đạt thì chưa chốt [Q15].

## Initial Scope Signal

- **Workflow-selected scope:** `feature` — workflow-selected [scope].
- **Product boundary — điều người dùng xác nhận:** **không loại trừ gì**; mọi hạng mục đều nằm trong phạm vi [Q9].

**Việc Q9 = E đảo lại, phải nói ra:** ba khuyến nghị đóng của đợt trước nay không còn hiệu lực [Q9]:

| Khuyến nghị của đợt trước | Trạng thái sau Q9 = E | Nguồn |
|---|---|---|
| "Không thêm loại mô hình mới ngoài hồi quy logistic — vấn đề là đặc trưng, không phải thuật toán" | không còn bị loại trừ | [Q9] |
| "Không làm API/dịch vụ dự đoán trực tuyến" | không còn bị loại trừ | [Q9] |
| "Không đụng vào 5 tab hiện có ngoài tab Kết quả phân tích" | không còn bị loại trừ | [Q9] |

Hệ quả: Scope Definition **không** có danh sách "Ngoài phạm vi" thừa hưởng từ đợt trước, và mọi mở rộng về sau phải tự khai lại danh sách đó thay vì dựa vào một biên đã có [Q9].

Ba hạng mục mới được xác nhận cụ thể [Q9]:

| Hạng mục | Nội dung | Nguồn |
|---|---|---|
| Khung dự đoán mới | dự đoán lúc bàn giao cho đơn vị vận chuyển, thay cho lúc đặt hàng | [Q4] |
| Mức B — dự đoán tương tác | một điểm nguy cơ cho mỗi dòng hàng (đơn, món hàng, người bán riêng) | [Q5] [Q11] |
| Giao diện dự đoán | vùng nhập liệu trên tab "Kết quả phân tích", đưa ra điểm nguy cơ từ mô hình đã huấn luyện và lưu lại | [Q12] [Q13] [Q14] |

## Assumptions & Open Questions

None.
