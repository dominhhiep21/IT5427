# Câu hỏi — Market Research

## Q1. Kết luận của đợt này có được phép nói về tương lai không

Dữ liệu đóng băng ở 2018-10. Một mô hình đạt 0,70 trên đó không chứng minh nó dự đoán được đơn hàng hôm nay.

- A. Không — kết luận chỉ đúng cho giai đoạn 2016–2018; ghi rõ giới hạn này ở mọi nơi có con số
- B. Có — nhưng phải kèm một mục "giả định chuyển giao" nói rõ cần kiểm gì trước khi dùng thật
- C. Không quan tâm — đây là bài toán học thuật, không cần nói tới chuyển giao
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Có được thử mô hình cây không

`scikit-learn` đã ghim có sẵn `HistGradientBoostingClassifier` — dùng nó **không thêm phụ thuộc nào**. Nhưng đổi thuật toán làm mất khả năng đọc hệ số như hồi quy logistic.

- A. Chỉ hồi quy logistic; giữ khả năng đọc hệ số, đổi lại chấp nhận trần thấp hơn
- B. Đặc trưng trước bằng logistic, **sau đó** mới thử mô hình cây nếu kết quả chững lại
- C. Thử cả hai ngay từ đầu rồi chọn cái tốt hơn theo AUC
- D. Chưa xác định — quyết định khi thấy kết quả bước đặc trưng
- X. Khác (vui lòng nêu rõ)

[Answer]: C

## Q3. Nếu mô hình mới vẫn thua baseline, kết luận đó có được công bố không

Đây là kết quả có thể xảy ra, và nó khác với "chưa đủ tốt".

- A. Có — ghi thẳng "hướng dự đoán này không cứu được bằng đặc trưng" và dừng, không thử thêm
- B. Có, nhưng kèm một lần thử cuối bằng mô hình cây trước khi kết luận
- C. Không — mở rộng phạm vi (thêm nguồn dữ liệu, thêm khung) cho tới khi thắng
- D. Chưa xác định — quyết định lúc thấy kết quả
- X. Khác (vui lòng nêu rõ)

[Answer]: B

## Consolidated Summary Confirmation

Ba câu đã trả lời. Bản tóm tắt để bạn xác nhận:

- **Tính chuyển giao** [Q1 = A]: kết luận **chỉ đúng cho giai đoạn 2016–2018**; giới hạn này phải đi kèm mọi con số, không được bỏ qua.
- **Thuật toán** [Q2 = C]: thử **cả** hồi quy logistic và mô hình cây (`HistGradientBoostingClassifier`, có sẵn trong `scikit-learn` đã ghim, **không thêm phụ thuộc**) ngay từ đầu, trên **cùng một bộ đặc trưng**, chọn theo AUC. Đánh đổi: mất khả năng đọc hệ số, và đánh đổi đó phải ghi trong báo cáo cuối.
- **Nếu vẫn thua baseline** [Q3 = B]: được **một lần thử cuối** bằng mô hình cây với cấu hình khác, rồi công bố kết luận "hướng này không cứu được bằng đặc trưng" — coi đó là kết quả có giá trị, không phải thất bại cần che.
- **Ba artifact**: `competitive-analysis.md` (đối thủ là các baseline: 0,5333 là mốc thật, 0,5133 là cái đang chạy), `market-trends.md` (không có xu hướng thị trường; thứ thay đổi thật là dự án tự đổi và tệ đi), `build-vs-buy.md` (B4 khả dụng không thêm phụ thuộc; thứ tự thử cả hai trên cùng đặc trưng).

- Looks correct
- Request changes

[Answer]: Looks correct
