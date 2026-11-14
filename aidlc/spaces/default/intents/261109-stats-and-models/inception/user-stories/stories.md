# User Stories

Nguồn: `../requirements-analysis/requirements.md` (FR1–FR5, NFR1–NFR5), `personas.md`, và các câu trả lời Q1–Q5 trong `user-stories-questions.md`.

Ưu tiên dùng đúng mức đã chốt trong `../../ideation/scope-definition/scope-document.md`: **Bắt buộc** hoặc **Nên có**. Tiêu chí nghiệm thu gồm Given/When/Then cho luồng chính và danh sách kiểm tra cho điều kiện phụ. [Q3]

## US1.1 — Chạy kiểm định thống kê và đọc kết quả

- **Vai:** Người chạy phân tích (P1)
- **Ưu tiên:** Bắt buộc [Q4]
- **Phủ:** FR1.1, FR1.2, FR1.3, FR1.4, FR1.5

**Given** bộ dữ liệu đã qua tầng integrate
**When** người dùng chạy `python -X utf8 -m src.pipeline run --stage stats`
**Then** báo cáo có đủ năm nhóm kiểm định: tỉ lệ trễ kèm khoảng tin cậy, so sánh hai tỉ lệ, tương quan, so sánh nhóm, phân rã mùa vụ.

**Kiểm tra thêm:**

- [ ] Mỗi kết quả ghi mức ý nghĩa 0,05 và độ tin cậy 95%. [Q1]
- [ ] So sánh hai tỉ lệ chỉ dùng bang có tối thiểu 100 đơn đã giao, và ghi rõ số đơn bị loại.
- [ ] Kết quả tương quan có r, n và khoảng tin cậy.
- [ ] Phân rã mùa vụ ghi rõ định nghĩa doanh thu và phương pháp.

## US2.1 — Huấn luyện mô hình đơn trễ và đọc chỉ số

- **Vai:** Người chạy phân tích (P1)
- **Ưu tiên:** Bắt buộc [Q4]
- **Phủ:** FR2.1, FR2.2, FR2.3, FR2.4

**Given** dữ liệu đơn hàng có nhãn trễ
**When** chạy bước mô hình
**Then** báo cáo có AUC trên tập kiểm tra, ngưỡng cảnh báo đã chọn, precision và recall ở ngưỡng đó.

**Kiểm tra thêm:**

- [ ] Danh sách đặc trưng không chứa thông tin chỉ có sau khi giao.
- [ ] Có ghi mốc chia theo thời gian và cỡ mẫu từng tập.
- [ ] Nếu AUC dưới 0,70 thì báo cáo ghi rõ là không đạt, không ẩn đi.

## US3.1 — Nhận một tệp báo cáo dùng chung

- **Vai:** Người chạy phân tích (P1)
- **Ưu tiên:** Bắt buộc [Q4]
- **Phủ:** FR3.1, FR3.2

**Given** bước thống kê và bước mô hình đã chạy
**When** quá trình ghi hoàn tất
**Then** có đúng một tệp JSON chứa cả hai khối kết quả, kèm thời điểm sinh. [Q2]

**Kiểm tra thêm:**

- [ ] Tệp được ghi qua `AtomicWriter`; số dòng đọc lại khớp.
- [ ] Ghi đè lên báo cáo cũ không làm hỏng tệp nếu tiến trình dừng giữa chừng.

## US4.1 — Mở tab kết quả và đọc theo thứ tự

- **Vai:** Người đọc báo cáo (P2)
- **Ưu tiên:** Bắt buộc [Q4]
- **Phủ:** FR4.1, FR4.2, FR4.3, NFR5

**Given** báo cáo đã có
**When** người dùng mở tab kết quả
**Then** thấy dải tóm tắt trước, rồi mục thống kê, rồi mục mô hình. [Q2]

**Kiểm tra thêm:**

- [ ] Chưa có báo cáo thì hiện trạng thái rỗng kèm câu lệnh cần chạy. [Q5]
- [ ] Báo cáo hỏng thì hiện trạng thái lỗi kèm đường dẫn tệp. [Q5]
- [ ] Mọi nút và vùng đọc được bằng bàn phím; mỗi vùng có nhãn cho trình đọc màn hình.
- [ ] Bố cục không vỡ ở chiều rộng 1280px.

## US5.1 — Chạy đúng chuỗi xác nhận của nhóm

- **Vai:** Người chạy phân tích (P1)
- **Ưu tiên:** Bắt buộc [Q4]
- **Phủ:** FR5.1, FR5.2, FR5.3, NFR1, NFR2, NFR3, NFR4

**Given** một thay đổi đã hoàn tất
**When** người dùng chạy chuỗi xác nhận
**Then** bốn bước chạy đúng thứ tự và dừng ở bước đỏ đầu tiên: bộ test nhanh, pipeline đầy đủ, tầng `stats`, mở dashboard.

**Kiểm tra thêm:**

- [ ] `python -m src.pipeline run --stage stats` chạy được; CLI vẫn 3 lệnh con. [Q4]
- [ ] Nhánh đang làm có trong cả hai danh sách trigger của CI.
- [ ] `pytest --cov=src --cov-fail-under=80` xanh trên toàn bộ bộ test. [Q5]
- [ ] `ruff check .` và `ruff format --check` sạch; tệp mới có trong danh sách của `ci.yml`.
