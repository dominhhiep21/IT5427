# Câu hỏi — Rough Mockups

## Q1. Khối dự đoán nằm ở đâu trong tab

Tab hiện có ba mục theo thứ tự đọc: **Tóm tắt → Thống kê → Mô hình**. Tab có test canh hình dạng (3 mục, 4 thẻ, không `tabIndex` dương).

- A. **Mục thứ tư trong tab hiện có** — thêm `du-doan` sau `mo-hinh`, giữ nguyên ba mục cũ và thứ tự đọc
- B. **Ngăn kéo/modal** mở từ một nút trong mục Mô hình — không thêm mục, nhưng thêm một lớp phủ và một trạng thái mở/đóng
- C. **Tab thứ sáu riêng** — tách hẳn khỏi tab kết quả
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Biểu mẫu có bao nhiêu trường

Mô hình dùng đặc trưng ở grain dòng hàng, nên đầy đủ sẽ là khoảng 10–12 trường — nhiều hơn một người nhập tay muốn điền.

- A. **Sáu trường mạnh nhất** (ví dụ: bang người bán, bang người mua, giá, phí vận chuyển, số ngày xử lý, số ngày duyệt đơn); phần còn lại lấy giá trị mặc định và **hiện rõ** là mặc định
- B. **Đầy đủ mọi đặc trưng** — nhập hết mới dự đoán được
- C. **Ba trường** và mặc định cho phần còn lại — nhanh nhất nhưng dự đoán kém tin hơn
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q3. Kết quả hiển thị gồm những gì

- A. **Xác suất + quyết định theo ngưỡng** (ví dụ "0,37 · dưới ngưỡng 0,40 → không cảnh báo")
- B. Như A, **cộng mức đóng góp của từng trường** — đòi hỏi mô hình giải thích được, mà mô hình cây thì không cho hệ số
- C. **Chỉ quyết định** cảnh báo/không cảnh báo, không hiện xác suất
- X. Khác (vui lòng nêu rõ)

[Answer]: B

## Q4. Mức đóng góp từng trường lấy ở đâu — câu hỏi nối tiếp Q3

Bạn chọn hiện **mức đóng góp của từng trường**. Nhưng ở Market Research bạn đã chốt chạy **cả** hồi quy logistic và mô hình cây, chọn theo AUC. Hai điều này không cùng tồn tại được:

- Hồi quy logistic cho hệ số từng đặc trưng → quy ra mức đóng góp được.
- `HistGradientBoosting` **không cho hệ số**, và phương pháp giải thích từng dự đoán (SHAP) là **thư viện mới** — vi phạm ràng buộc không thêm phụ thuộc.

- A. **Luôn hiện mức đóng góp, nên mô hình phải là hồi quy logistic** — chấp nhận AUC thấp hơn nếu cây thắng, để giữ khả năng giải thích (đảo một phần Q2 của Market Research)
- B. **Hiện mức đóng góp khi mô hình thắng là logistic; nếu cây thắng thì ẩn phần đó** và ghi rõ lý do trên giao diện — giữ nguyên Q2 của Market Research
- C. Hiện **mức quan trọng toàn cục** (permutation importance, có sẵn trong `scikit-learn`) thay cho đóng góp từng dự đoán — không phải "vì sao đơn này bị gắn cờ"
- D. Chưa xác định — chốt ở Functional Design
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Bốn câu đã trả lời. Bản tóm tắt để bạn xác nhận:

- **Vị trí** [Q1 = A]: khối dự đoán là **mục thứ tư** trong tab, sau "Mô hình", giữ nguyên ba mục cũ và thứ tự đọc.
- **Biểu mẫu** [Q2 = A]: **sáu trường mạnh nhất** (bang người bán, bang người mua, giá, phí vận chuyển, số ngày xử lý, số ngày duyệt); phần còn lại dùng mặc định và **hiện rõ** là mặc định.
- **Kết quả** [Q3 = B]: xác suất · so ngưỡng · quyết định · **ba đóng góp lớn nhất** (không phải mười hai dòng).
- **Giải thích lấy từ đâu** [Q4 = A]: **mô hình triển khai là hồi quy logistic**, vì cần hệ số để tính đóng góp. Điều này **đảo một phần** Q2 của Market Research (chạy cả hai, chọn theo AUC): mô hình cây vẫn được chạy nhưng chỉ để **báo cáo** — biết mình bỏ bao nhiêu AUC để giữ khả năng giải thích.
- **Bốn trạng thái** của khối: chưa dự đoán, đang tính, có kết quả, mô hình chưa sẵn — trạng thái cuối là nhánh dễ bị bỏ sót nhất.
- **Ràng buộc**: không SHAP, không thư viện giải thích mới; không thẻ thứ năm, không tab mới, không token màu, không biểu đồ.

- Looks correct
- Request changes

[Answer]: Looks correct
