# Quiz DI — Tích hợp dữ liệu

> Nguồn: https://docs.google.com/forms/d/e/1FAIpQLSc8DR6HH0XTUUxeUus5KZYwhUeiYF70hqe3RUVkmgSFwlfxkA/viewform  
> Trích xuất: 24/10/2026

---

**Câu 1.** Mô tả nguồn dữ liệu trong hệ thống tích hợp dữ liệu dùng để làm gì? *(checkbox)*

- [ ] Mô tả cách thức truy cập vào nguồn dữ liệu
- [ ] Xác định nguồn nào liên quan đến truy vấn
- [ ] Xóa các nguồn dữ liệu không cần thiết
- [ ] Mô tả lược đồ tích hợp

---

**Câu 2.** Điều nào sau đây KHÔNG phải là vấn đề chính trong tích hợp dữ liệu? *(checkbox)*

- [ ] Đồng nhất lược đồ
- [ ] Xử lý truy vấn phân tán
- [ ] Trực quan hóa dữ liệu tự động
- [ ] Vấn đề về bảo mật và quyền riêng tư

---

**Câu 3.** Trong tích hợp dữ liệu, "lược đồ trung gian" đề cập đến *(checkbox)*

- [ ] Lược đồ của nguồn dữ liệu lớn nhất
- [ ] Một lược đồ tiêu chuẩn ánh xạ đến nhiều lược đồ nguồn khác nhau
- [ ] Bản sao lưu của tất cả các cơ sở dữ liệu vật lý
- [ ] Bản sao của kho dữ liệu mới nhất

---

**Câu 4.** Trường hợp nào sau đây là ví dụ về sự không đồng nhất ngữ nghĩa giữa hai nguồn dữ liệu? *(checkbox)*

- [ ] Sử dụng tên bảng và thuộc tính khác nhau để biểu diễn cùng một đối tượng
- [ ] Có lược đồ giống nhau nhưng dữ liệu khác nhau
- [ ] Sử dụng 2 giá trị khác nhau để biểu diễn cùng 1 trạng thái của cùng 1 đối tượng
- [ ] Hai nguồn chứa cùng dữ liệu và cùng lược đồ

---

**Câu 5.** Trong cách ánh xạ lược đồ Global-as-View (GAV) *(checkbox)*

- [ ] Mối quan hệ trong lược đồ trung gian được định nghĩa là một view từ các nguồn dữ liệu
- [ ] Mỗi quan hệ nguồn là một view trên lược đồ trung gian
- [ ] Định nghĩa ánh xạ phụ thuộc tập hợp các nguồn tham gia vào hệ thống
- [ ] Lược đồ trung gian không cần đến dữ liệu nguồn

---

**Câu 6.** Mô hình ánh xạ lược đồ nào định nghĩa mỗi nguồn như một view trên lược đồ trung gian? *(checkbox)*

- [ ] Local-as-View (LAV)
- [ ] Global-as-View (GAV)
- [ ] Cả hai GAV và LAV
- [ ] Không có đáp án nào đúng

---

**Câu 7.** Điểm yếu lớn nhất của ánh xạ theo kiểu GAV là gì? *(checkbox)*

- [ ] Không hỗ trợ ánh xạ từ nhiều nguồn
- [ ] Không hỗ trợ các bảng có quan hệ khóa ngoại
- [ ] Không thể xử lý dữ liệu phi cấu trúc
- [ ] Không linh hoạt với thay đổi nguồn vì mỗi thay đổi cần cập nhật lại lược đồ trung gian

---

**Câu 8.** Trong bối cảnh dữ liệu không đầy đủ, ánh xạ nào phù hợp nhất để bảo toàn tính linh hoạt và mở rộng các truy vấn có tính chất suy diễn? *(checkbox)*

- [ ] GAV
- [ ] LAV
- [ ] GLAV
- [ ] ETL Pipeline

---

**Câu 9.** Ngôn ngữ mô tả nguồn dữ liệu cần đáp ứng *(checkbox)*

- [ ] Hỗ trợ cập nhật nguồn
- [ ] Linh hoạt trong biểu diễn quan hệ giữa các lược đồ thực tế
- [ ] Chỉ dùng cho một nguồn dữ liệu
- [ ] Hỗ trợ biểu diễn các nguồn có cấu trúc không nhất quán

---

**Câu 10.** Trong GAV, mediated schema được định nghĩa như thế nào? *(checkbox)*

- [ ] Là tập các view trên các nguồn dữ liệu
- [ ] Là tập các nguồn dữ liệu trên mediated schema
- [ ] Là tập các khóa ngoại
- [ ] Là tập các file vật lý

---

**Câu 11.** Viết lại truy vấn trong GAV thường tương ứng với: *(checkbox)*

- [ ] Query/View unfolding
- [ ] Định vị các nguồn dữ liệu
- [ ] Answering queries using views
- [ ] Định vị các phân đoạn dữ liệu

---

**Câu 12.** Trong LAV, các nguồn dữ liệu được định nghĩa như thế nào? *(checkbox)*

- [ ] Là khóa của mediated schema
- [ ] Là view trên mediated schema
- [ ] Dựa trên cách thực thi tối ưu truy vấn
- [ ] Không phải cách nào

---

**Câu 13.** Trong GLAV, biểu thức mapping thường liên hệ giữa *(checkbox)*

- [ ] Query trên mediated schema và query trên data sources
- [ ] Người dùng và trình duyệt
- [ ] Xóa các tuple trùng lặp
- [ ] File và thư mục

---

**Câu 14.** Query unfolding có nghĩa là: *(checkbox)*

- [ ] Mở rộng truy vấn bằng cách thay view bằng định nghĩa của view đó
- [ ] Tối ưu truy vấn bằng cách rút gọn các bảng biểu diễn nó
- [ ] Sử dụng khóa chính để kết nối
- [ ] Viết lại truy vấn

---

**Câu 15.** Mediated Query là *(checkbox)*

- [ ] Câu truy vấn của người dùng hệ tích hợp
- [ ] Câu truy vấn trên các nguồn dữ liệu
- [ ] Câu truy vấn biểu diễn ánh xạ giữa lược đồ tích hợp và lược đồ nguồn
- [ ] Câu truy vấn phân tán trên các nguồn

---

**Câu 16.** Mục tiêu chính của tích hợp dữ liệu là gì? *(checkbox)*

- [ ] Xóa bỏ tất cả các cơ sở dữ liệu cũ
- [ ] Kết nối nhiều nguồn dữ liệu khác nhau dưới một lược đồ chung
- [ ] Tăng khả năng xử lý truy vấn
- [ ] Chuyển toàn bộ dữ liệu sang định dạng văn bản

---

**Câu 17.** Trong kiến trúc tích hợp dữ liệu, lược đồ tích hợp (mediated schema) có vai trò gì? *(checkbox)*

- [ ] Là nơi lưu duy nhất toàn bộ dữ liệu vật lý
- [ ] Là ánh xạ giữa các nguồn dữ liệu
- [ ] Là giao diện/lược đồ chung để người dùng truy vấn nhiều nguồn dữ liệu
- [ ] Là khóa chính của tất cả bảng

---

**Câu 18.** Ánh xạ ngữ nghĩa giữa các lược đồ (Semantic mappings) dùng để làm gì? *(radio)*

- [ ] Nén dữ liệu
- [ ] Mô tả quan hệ ngữ nghĩa giữa lược đồ chung và các nguồn dữ liệu
- [ ] Xóa các bảng trùng nhau
- [ ] Tạo định dạng chung biểu diễn yêu cầu truy vấn

---

**Câu 19.** Tính không đồng nhất về lược đồ (Schema heterogeneity) thể hiện: *(checkbox)*

- [ ] Các hệ thống có thể cùng tên bảng và cùng thuộc tính
- [ ] Các nguồn dữ liệu khác nhau về lược đồ
- [ ] Giá trị dữ liệu trong các nguồn khác nhau có thể biểu diễn theo các cách khác nhau
- [ ] Các nguồn sử dụng các công cụ lưu trữ khác nhau

---

**Câu 20.** Mục tiêu của tích hợp dữ liệu là cung cấp: *(checkbox)*

- [ ] Một hệ thống phần mềm mới
- [ ] Một ngôn ngữ lập trình mới
- [ ] Một tổ chức lưu trữ mới
- [ ] Một truy vấn thống nhất đến nhiều nguồn dữ liệu

---

**Câu 21.** Yếu tố nào sau đây làm tích hợp dữ liệu trở nên khó? *(checkbox)*

- [ ] Khác biệt nền tảng hệ thống
- [ ] Khác biệt lược đồ và dữ liệu
- [ ] Vấn đề bảo mật, riêng tư, hiệu năng
- [ ] Kích thước dữ liệu

---

**Câu 22.** Trong kiến trúc kho dữ liệu (data warehouse), dữ liệu được tích hợp bằng cách nào? *(checkbox)*

- [ ] Chỉ dùng dữ liệu XML
- [ ] Biểu diễn bởi cùng 1 lược đồ
- [ ] Đưa dữ liệu vào một kho dữ liệu vật lý chung
- [ ] Không cần ánh xạ dữ liệu

---

**Câu 23.** Kiến trúc tích hợp dữ liệu ảo (virtual data integration) hoạt động như thế nào? *(checkbox)*

- [ ] Luôn sao chép toàn bộ dữ liệu về một nơi
- [ ] Để dữ liệu tại nguồn và truy cập khi có truy vấn
- [ ] Không sử dụng truy vấn
- [ ] Chỉ hoạt động với một nguồn dữ liệu duy nhất

---

**Câu 24.** Điểm chung của kho dữ liệu và tích hợp ảo dữ liệu là gì? *(checkbox)*

- [ ] Cả hai đều gặp vấn đề dị biệt ngữ nghĩa
- [ ] Cả hai đều có thể gặp vấn đề tính không đồng nhất ngữ nghĩa
- [ ] Cả hai đều không cần lược đồ
- [ ] Cả hai đều không cần nguồn dữ liệu

---

**Câu 25.** Bộ trích lọc/trình bao bọc (Wrapper/Extractor) trong kiến trúc tích hợp dữ liệu có nhiệm vụ gì? *(checkbox)*

- [ ] Thay thế cho nguồn dữ liệu
- [ ] Gửi truy vấn đến nguồn dữ liệu và chuyển kết quả về mô hình dữ liệu chung
- [ ] Xóa dữ liệu lỗi
- [ ] Biểu diễn dữ liệu được trích chọn từ các nguồn sử dụng ngôn ngữ biểu diễn chung

---

**Câu 26.** Nhược điểm của kho dữ liệu là *(checkbox)*

- [ ] Truy vấn luôn làm gián đoạn nguồn dữ liệu
- [ ] Dữ liệu thường không hoàn toàn cập nhật do làm mới offline/lazy refresh
- [ ] Xử lý tính toán phức tạp
- [ ] Không cần thiết kế lược đồ vật lý
