# Câu hỏi — Intent Capture & Framing

## Sources

- [desc] Initial description: "mở intent mới cho phần cải thiện đặc trưng\n\nBối cảnh đã chốt ở đợt 261109-stats-and-models (nguồn: operation/feedback-optimization/feedback-loop.md, mục B1 và B2):\n\n- Mục tiêu: cải thiện đặc trưng của mô hình dự đoán đơn giao trễ (u2-model) để đạt AUC tối thiểu 0,70.\n- Mốc so sánh bắt buộc: baseline một đặc trưng `customer_state` cho AUC 0,5333, cao hơn mô hình 11 đặc trưng hiện tại (0,5133) — đợt mới phải đánh bại 0,5333, không chỉ nhắm 0,70.\n- Gộp thêm mức B: dự đoán tương tác.\n- Phải mở lại scope-document vì đây là thay đổi phạm vi.\n- Giữ nguyên danh sách 10 cột cấm và quy tắc chia tập trước, mã hoá sau (fit chỉ trên train).\n- Khung dự đoán \"lúc đặt hàng\" phải được Ideation chốt lại trước khi viết bất kỳ đặc trưng nào; câu hỏi mở là có nên chuyển sang khung \"lúc bàn giao cho đơn vị vận chuyển\"."
- [scope] Workflow-selected scope: `feature`.

## Q1. Vấn đề kinh doanh nào đang được giải quyết

Mô hình dự đoán đơn giao trễ hiện có AUC 0,5133, thấp hơn cả baseline một đặc trưng `customer_state` (0,5333). Điều gì khiến việc cải thiện nó quan trọng **bây giờ**?

- A. Cảnh báo sớm để giảm tỉ lệ đơn trễ thật — mô hình phải đủ tốt để hành động được, không chỉ để báo cáo
- B. Yêu cầu học thuật của môn học: phải chứng minh quy trình cải thiện có kiểm soát, mô hình tốt hơn là hệ quả
- C. Chứng minh mô hình hiện tại **không** cứu được bằng thuật toán — cần bằng chứng để quyết định giữ hay bỏ hướng dự đoán
- D. Cả A và B
- E. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: D

## Q2. Ai hưởng lợi, và họ đau ở đâu

- A. Người bán (seller): biết đơn nào có nguy cơ trễ để xử lý trước
- B. Đội vận hành Olist: ưu tiên can thiệp vào nhóm đơn nguy cơ thay vì mọi đơn
- C. Người mua: nhận được thông báo chủ động khi đơn có nguy cơ trễ
- D. Người học/nhóm làm đồ án: chứng minh năng lực phân tích dữ liệu lớn
- E. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: D

## Q3. Thế nào là "xong" — thước đo thành công

Mốc hiện tại là AUC ≥ 0,70 **và** phải cao hơn 0,5333. Ngoài AUC, mô hình còn phải đạt gì để được coi là dùng được?

- A. Chỉ AUC: đạt ≥ 0,70 và > 0,5333 là đủ
- B. AUC như trên **và** precision đủ cao để cảnh báo không bị bỏ qua (nêu ngưỡng bạn muốn ở phần trả lời)
- C. AUC như trên **và** recall đủ cao để bắt được phần lớn đơn trễ thật
- D. AUC như trên, cộng một baseline bắt buộc thứ hai (ví dụ mô hình chỉ dùng `customer_state`) phải bị đánh bại **một cách rõ ràng**, không phải chênh lệch trong nhiễu
- E. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: A - tôi muốn có thể dự đoán, tương tác với giao diện để model dự đoán ...

## Q4. Khung dự đoán: dự đoán lúc nào

Đây là câu hỏi mở lại có chủ đích từ đợt trước. Khung hiện tại chỉ dùng thông tin có **lúc đặt hàng**, và đó là lý do chính khiến AUC thấp.

- A. Giữ khung "lúc đặt hàng" — dự đoán sớm mới can thiệp được; chấp nhận rằng 0,70 có thể không đạt và nói thẳng
- B. Chuyển sang khung "lúc bàn giao cho đơn vị vận chuyển" — AUC sẽ cao hơn vì đã biết người bán và tuyến, nhưng cảnh báo muộn hơn
- C. Làm **hai** mô hình, mỗi khung một mô hình, và so sánh chúng — mức B chính là mô hình thứ hai
- D. Giữ khung đặt hàng cho mô hình chính, nhưng cho phép thêm đặc trưng suy ra từ dữ liệu có sau khi đặt (ví dụ lịch sử người bán tính đến thời điểm đặt, không phải sau đó)
- E. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: B

## Q5. "Mức B — dự đoán tương tác" nghĩa là gì

Cụm này chưa được định nghĩa ở đợt trước; cần chốt trước khi lập kế hoạch.

- A. Dự đoán **theo từng tương tác** thay vì theo đơn: mỗi cặp (người bán, đơn) hoặc (người bán, khách) một điểm nguy cơ
- B. Dự đoán **hành động can thiệp** đi kèm: không chỉ "đơn này sẽ trễ" mà còn "nên làm gì"
- C. Dự đoán **tương tác có rủi ro** giữa người bán và người mua (ví dụ khiếu nại, đánh giá xấu) chứ không chỉ giao trễ
- D. Chỉ là tên gọi khác của mô hình thứ hai ở Q4-C
- E. Chưa xác định — cần một bước làm rõ riêng trước khi cam kết
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q6. Ranh giới chống rò rỉ dữ liệu

Đợt trước chốt **10 cột cấm** (thông tin chỉ có sau khi đơn kết thúc) và quy tắc **chia tập trước, mã hoá sau**. Nếu khung dự đoán đổi ở Q4, ranh giới này có đổi theo không?

- A. Giữ nguyên 10 cột cấm và quy tắc chia tập, bất kể khung nào được chọn
- B. Giữ nguyên danh sách cấm, nhưng **thêm** cột cấm mới nếu khung đổi (ví dụ thông tin vận chuyển khi dự đoán lúc bàn giao phải loại những gì xảy ra sau bàn giao)
- C. Cho phép dùng thông tin có sau khi đặt nếu khung đổi, miễn là ghi rõ thời điểm có thông tin đó
- D. Chưa xác định — chốt cùng lúc với Q4
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q7. Ai quyết định phạm vi và ai gây ảnh hưởng

- A. Một mình tôi quyết định; không có người phê duyệt thứ hai
- B. Tôi quyết định, nhưng giảng viên/hội đồng có thể yêu cầu thay đổi
- C. Nhóm có nhiều người, quyết định theo đồng thuận
- D. Not identified
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q8. Yêu cầu báo cáo và nhịp giao tiếp

- A. Không có yêu cầu báo cáo; ghi lại trong workspace AI-DLC là đủ
- B. Có báo cáo định kỳ cho giảng viên/hội đồng theo mốc (nêu mốc ở phần trả lời)
- C. Có người đọc kết quả nhưng không theo lịch cố định
- D. Not applicable
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q9. Phiên bản đầu tiên này **không** làm gì

Phạm vi `feature` đã được chọn. Câu hỏi chỉ là: sản phẩm đầu tiên của đợt này nên **loại trừ** điều gì?

- A. Không làm API/dịch vụ dự đoán trực tuyến; chỉ sinh báo cáo như hiện tại
- B. Không thêm loại mô hình mới ngoài hồi quy logistic (vấn đề là đặc trưng, không phải thuật toán)
- C. Không đụng vào 5 tab hiện có; mọi thay đổi hiển thị chỉ nằm trong tab "Kết quả phân tích"
- D. Cả A, B và C
- E. Không loại trừ gì — mọi thứ đều nằm trong phạm vi
- X. Khác (vui lòng nêu rõ)

[Answer]: E

## Q10. Ranh giới rò rỉ khi dự đoán **lúc bàn giao** — câu hỏi nối tiếp Q6

Bạn chọn Q4 = B (dự đoán lúc bàn giao cho đơn vị vận chuyển) và Q6 = A (giữ nguyên 10 cột cấm). Hai câu này đá nhau ở đúng một chỗ: `order_delivered_carrier_date` nằm trong danh sách cấm, mà nó chính là **thời điểm dự đoán** trong khung mới. Hệ quả nếu giữ nguyên tuyệt đối: không được tính `handling_days` (số ngày từ đặt tới bàn giao), vốn là đặc trưng mạnh nhất của khung này.

- A. Cho phép `order_delivered_carrier_date` **chỉ** để tính các đặc trưng có tại thời điểm bàn giao (ví dụ `handling_days`), vẫn cấm `order_delivered_customer_date`, `delivery_days`, `is_late`, `late_days` và toàn bộ cột review
- B. Giữ nguyên tuyệt đối 10 cột cấm như đợt trước, kể cả `order_delivered_carrier_date` — chấp nhận mất `handling_days`
- C. Mở rộng: cho phép cả thông tin tuyến đường/người vận chuyển nếu suy ra được từ dữ liệu có trước hoặc tại thời điểm bàn giao
- D. Chưa xác định — chốt ở Functional Design
- X. Khác (vui lòng nêu rõ)

[Answer]: C

## Q11. "Mức B — dự đoán tương tác" dự đoán ở đơn vị nào — câu hỏi nối tiếp Q5

Bạn chọn Q5 = A (dự đoán theo từng tương tác). Cần chốt "một tương tác" là gì, vì nó quyết định số dòng của tập huấn luyện.

- A. Mỗi **dòng hàng** (order_id, order_item_id) một điểm nguy cơ — mỗi món hàng có người bán riêng
- B. Mỗi **cặp (đơn, người bán)** một điểm nguy cơ — một đơn có thể có nhiều người bán, và đơn trễ là hệ quả của một trong số đó
- C. Mỗi **cặp (người bán, khách hàng)** một điểm nguy cơ — đo rủi ro quan hệ, không đo một đơn cụ thể
- D. Chưa xác định — cần một bước phân tích dữ liệu để chọn
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q12. Giao diện dự đoán có nằm trong đợt này — câu hỏi nối tiếp Q3 và Q9

Câu trả lời Q3 có thêm "tôi muốn có thể dự đoán, tương tác với giao diện để model dự đoán", và Q9 = E (không loại trừ gì). Cần biết giao diện đó là gì, vì nó là bề mặt mới chứ không phải chỉnh sửa tab hiện có.

- A. Có: thêm một vùng nhập liệu trên tab "Kết quả phân tích" để nhập vài thông số và xem điểm nguy cơ dự đoán ngay (mô hình chạy tại chỗ trong tiến trình dashboard)
- B. Có: một tab/trang dự đoán riêng, có biểu mẫu đầy đủ các đặc trưng
- C. Có: một API cục bộ (ví dụ endpoint trên `127.0.0.1`) để gọi dự đoán từ ngoài
- D. Không thêm giao diện nào — chỉ sinh báo cáo và hiện kết quả như hiện nay
- E. Chưa xác định — cần chốt ở Scope Definition
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q13. AUC là tiêu chí duy nhất — và giao diện là phạm vi hay tiêu chí chất lượng

Giả định 1 nói rằng "chỉ AUC" là thước đo, còn giao diện dự đoán là hạng mục phạm vi. Xác nhận lại cho chắc.

- A. Đúng: AUC là tiêu chí chất lượng duy nhất; giao diện chỉ là hạng mục phạm vi, hỏng giao diện không làm hỏng mục tiêu chất lượng
- B. AUC là tiêu chí duy nhất, nhưng giao diện dự đoán **phải** hiện kèm precision/recall để người xem tự đánh giá
- C. Có thêm một tiêu chí chất lượng thứ hai (nêu rõ ở phần trả lời)
- D. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: C - tôi muốn có thể đưa ra dự đoán từ model đã train thôi

## Q14. Giao diện dự đoán lấy mô hình ở đâu

Đợt trước mô hình không được lưu ra đĩa; mỗi lần `run --stage stats` là huấn luyện lại (1,56 s). Giao diện dự đoán cần một mô hình sẵn dùng.

- A. Lưu mô hình ra đĩa sau khi huấn luyện; dashboard nạp lại khi mở tab
- B. Huấn luyện lại ngay khi mở tab lần đầu (chậm khoảng 1,6 s, không thêm tệp trạng thái)
- C. Chưa xác định — chốt ở Functional Design
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q15. Nếu 0,70 không đạt được với khung mới

Giả định 3 nói mốc 0,70 là giả thuyết chưa kiểm chứng. Cần biết trước phải làm gì nếu thử hết đặc trưng đã định mà vẫn dưới mốc.

- A. Giữ mốc 0,70; nếu không đạt thì ghi rõ **không đạt** và dừng — không hạ mốc
- B. Hạ mốc xuống mức cao nhất đạt được, kèm ghi chú lý do
- C. Giữ mốc 0,70 và mở rộng thêm khung dự đoán/đặc trưng cho tới khi đạt, kể cả vượt phạm vi đã định
- D. Chưa xác định — quyết định lúc thấy kết quả
- X. Khác (vui lòng nêu rõ)

[Answer]: D

## Q16. Ai có thể gây ảnh hưởng tới quyết định phạm vi

Giả định 4 để mở vì Q7 = A chỉ nói bạn là người quyết định.

- A. Không có ai khác
- B. Giảng viên / hội đồng có thể yêu cầu thay đổi
- C. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q17. `order_delivered_carrier_date` có được dùng làm đặc trưng không — câu hỏi nối tiếp R-01

Người soát chỉ ra mâu thuẫn chưa giải: Q6 = A giữ nguyên 10 cột cấm (trong đó có `order_delivered_carrier_date`), còn Q10 = C chỉ nói về "thông tin tuyến đường/người vận chuyển". Trong dữ liệu Olist hiện có **không** có cột người vận chuyển hay bảng tuyến đường nào; thứ duy nhất về tuyến đường là bang/mã bưu chính của người bán so với người mua, vốn biết được ngay lúc đặt hàng. Vậy câu hỏi thật chỉ còn một: cột ngày bàn giao.

- A. Chỉ dùng `order_delivered_carrier_date` làm mốc thời gian (mốc chia tập và mốc dự đoán), **không** dùng làm đặc trưng — nên **không có** `handling_days`; đây là cách đọc đúng nguyên văn Q6 = A
- B. Cho phép dùng nó để tính `handling_days` như một đặc trưng, vì đó là thông tin đã biết tại thời điểm bàn giao — nghĩa là nới Q6 = A đúng một cột, và phải ghi rõ việc nới đó
- C. Cho phép dùng cả `order_approved_at` và `order_delivered_carrier_date` để tính thời gian xử lý (duyệt đơn → bàn giao) và thời gian từ đặt → duyệt
- D. Chưa xác định — chốt ở Functional Design
- X. Khác (vui lòng nêu rõ)

[Answer]: C

## Q18. Phải vượt baseline bao nhiêu — câu hỏi nối tiếp R-02

Baseline `customer_state` = 0,5333 được đo trên **đơn**, ở khung **lúc đặt hàng**. Khung và đơn vị đều đã đổi, nên baseline phải đo lại; câu hỏi là mức chênh buộc phải vượt sau khi đo lại.

- A. Chỉ cần cao hơn baseline đo lại, không ấn định mức chênh
- B. Cao hơn baseline ít nhất **0,05**
- C. Cao hơn baseline ít nhất **0,10**
- D. Chưa xác định — quyết định lúc thấy kết quả
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q19. Ai quyết định nếu AUC không đạt 0,70, và ở mốc nào — câu hỏi nối tiếp giả định 1

Q15 = D nói "quyết định lúc thấy kết quả". Câu này chốt **ai** và **ở mốc nào**, để đợt không kết thúc bằng một câu hỏi treo.

- A. Tôi quyết định ngay ở Build and Test khi thấy AUC, và quyết định đó ghi vào record
- B. Tôi quyết định sau khi đợt xong, dựa trên toàn bộ record
- C. Chốt trước một quy tắc cứng: dưới 0,70 thì ghi **không đạt** và dừng, không hạ mốc
- D. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q20. Có cần một mốc sàn ngoài mốc 0,70 — câu hỏi nối tiếp giả định 2

Mốc 0,70 chưa được kiểm chứng với khung mới. Một mốc sàn thấp hơn (dùng để chặn mô hình thoái hoá) là thứ đợt trước đã bỏ ngỏ.

- A. Không cần; chỉ có 0,70 và baseline đo lại
- B. Có: mốc sàn **0,55** trong CI để chặn mô hình tệ hơn hiện tại, còn 0,70 là mục tiêu
- C. Có, nhưng mốc sàn khác (nêu con số ở phần trả lời)
- D. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: B

## Q21. Đo baseline trong khung mới khi nào — câu hỏi nối tiếp giả định 3

Con số 0,5333 được đo trên đơn ở khung lúc đặt hàng, nên nó chưa phải mốc so sánh đã hiệu lực. Câu hỏi là đo lại lúc nào.

- A. **Bước đầu tiên của đợt**, trước mọi thay đổi đặc trưng; kết quả ghi vào record làm mốc so
- B. Đo cùng lúc với mô hình mới rồi so sau
- C. Không đo lại; dùng 0,5333 làm mốc tham chiếu lịch sử và ghi rõ đó là tham chiếu
- D. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Hai mươi mốt câu đã trả lời; không còn giả định nào mở. Bản tóm tắt để bạn xác nhận:

- **Vấn đề** [Q1 = D]: vừa để cảnh báo sớm có thể hành động, vừa để chứng minh quy trình cải thiện có kiểm soát.
- **Đối tượng** [Q2 = D]: người học / nhóm làm đồ án — không phải một nhóm người dùng vận hành.
- **Khung dự đoán** [Q4 = B]: **lúc bàn giao cho đơn vị vận chuyển**.
- **Đơn vị dự đoán** [Q5 = A, Q11 = A]: **mỗi dòng hàng**.
- **Ranh giới rò rỉ** [Q6 = A, Q17 = C]: danh sách cấm còn hiệu lực, nới đúng **hai cột mốc** và chỉ ở dạng **số ngày**; chia tập theo **`order_id`**; chỉ chấm AUC trên đơn đã tới bàn giao.
- **Mức B** [Q12 = A, Q13 = C, Q14 = A]: vùng nhập liệu trên tab "Kết quả phân tích", dự đoán từ mô hình đã huấn luyện và lưu lại; tiêu chí **cùng đầu vào → cùng điểm**.
- **Chất lượng** [Q3 = A, Q18 = A, Q20 = B]: AUC ≥ 0,70 là mục tiêu; **mốc sàn 0,55 trong CI** chặn mô hình thoái hoá; AUC phải cao hơn baseline **đo lại trong cùng khung/đơn vị**.
- **Baseline** [Q21 = A]: đo lại là **bước đầu tiên** của đợt, ghi vào record.
- **Mốc 0,70** [Q15 = D, Q19 = A]: mục tiêu hiện tại, không cam kết trước; nếu không đạt thì người làm quyết định **ngay ở Build and Test** và ghi vào record.
- **Quyết định và báo cáo** [Q7 = A, Q16 = A, Q8 = A]: một mình bạn quyết định, không ai khác gây ảnh hưởng, không yêu cầu báo cáo.
- **Phạm vi** [Q9 = E]: không loại trừ gì — artifact **nói rõ** việc này đảo ba khuyến nghị đóng của đợt trước.
- **Nửa học thuật** [Q1]: record phải có đủ baseline trước, thay đổi, kết quả sau, quyết định giữ hay hạ mốc.

- Looks correct
- Request changes

[Answer]: Looks correct
