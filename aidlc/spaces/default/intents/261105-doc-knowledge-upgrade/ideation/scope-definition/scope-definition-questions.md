# Scope Definition — Câu hỏi làm rõ

## Q1. [Sản phẩm] Phạm vi tối thiểu đủ giá trị cho lần nâng cấp này là gì?

Feasibility đã chỉ ra quỹ thời gian 1–2 tuần là ràng buộc chặt. Câu hỏi này chốt mức tối thiểu bạn muốn có.

- A. Cả bốn nhóm chủ đề ở mức tối thiểu, cộng giao diện cơ bản
- B. Hai nhóm cốt lõi (đồng nhất lược đồ + viết lại truy vấn), cộng giao diện
- C. Một nhóm (đồng nhất lược đồ / lược đồ trung gian), cộng dashboard
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q2. [Sản phẩm] Nhóm chủ đề nào bắt buộc phải có? (chọn tất cả nếu áp dụng)

Nhóm bắt buộc sẽ quyết định thứ tự thi công và phần nào không được phép cắt khi hết thời gian.

- A. Đồng nhất lược đồ / lược đồ trung gian
- B. Ghép bản ghi / nhận dạng thực thể
- C. Xử lý và viết lại truy vấn
- D. Chọn nguồn dữ liệu
- E. Tất cả đều bắt buộc
- X. Other (please specify)

[Answer]: E

## Q3. [Kỹ thuật] Ưu tiên thi công theo hướng nào?

Ba cách xếp thứ tự hợp lý nhưng cho kết quả khác nhau khi thời gian eo hẹp.

- A. Theo phụ thuộc: lược đồ trung gian trước (nền cho các nhóm còn lại)
- B. Theo giá trị thấy được: ghép bản ghi trước vì dễ trình diễn
- C. Theo rủi ro: viết lại truy vấn trước vì khó nhất, làm sớm để kịp
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q4. [Sản phẩm] Giao diện tối thiểu cho phần mới là gì?

Ảnh hưởng tới khối lượng việc ở giai đoạn Construction và cách trình bày trước hội đồng.

- A. Một tab mới "Tích hợp" gộp cả bốn nhóm
- B. Bốn tab mới, mỗi nhóm một tab
- C. Chỉ thêm phần hiển thị vào ba tab hiện có, không thêm tab
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q5. [Kỹ thuật] Phần nào của hệ hiện tại tuyệt đối không được thay đổi? (chọn tất cả nếu áp dụng)

Đây là biên giới không hồi quy, dùng để đặt test bảo vệ ở giai đoạn sau.

- A. Số liệu KPI và ba tab hiện có phải giữ nguyên
- B. Lệnh CLI và pipeline hiện có (`src/pipeline`) phải giữ nguyên cách gọi
- C. Cấu trúc lưu trữ (`data/marts`, `warehouse/olist.duckdb`) phải giữ nguyên
- D. Không giới hạn — được refactor thoải mái nếu test vẫn xanh
- E. Not applicable (không áp dụng)
- X. Other (please specify)

[Answer]: D

## Q6. [Sản phẩm] Chốt lại: MVP là 2 nhóm hay cả 4 nhóm bắt buộc?

Hai câu trả lời đang lệch nhau: ở câu 1 bạn chọn phạm vi tối thiểu là hai nhóm cốt lõi, nhưng ở câu 2 bạn chọn cả bốn nhóm đều bắt buộc. Chọn cách hiểu đúng để mình xếp thứ tự và cắt phạm vi khi cần.

- A. MVP để nộp là hai nhóm cốt lõi; hai nhóm còn lại làm nếu còn thời gian, không tính là bắt buộc
- B. Cả bốn nhóm bắt buộc; "tối thiểu" ở câu 1 chỉ nói về thứ tự ưu tiên, hết thời gian vẫn phải cố đủ bốn
- C. Cả bốn nhóm bắt buộc nhưng mỗi nhóm ở mức tối thiểu (một kịch bản demo), riêng hai nhóm cốt lõi làm sâu hơn
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Phạm vi: cả bốn nhóm chủ đề đều bắt buộc, mỗi nhóm ở mức tối thiểu (một kịch bản demo); riêng hai nhóm cốt lõi — đồng nhất lược đồ và viết lại truy vấn — làm sâu hơn.
- Thứ tự thi công: theo phụ thuộc, lược đồ trung gian làm trước vì là nền cho các nhóm còn lại.
- Giao diện: một tab mới "Tích hợp" gộp cả bốn nhóm.
- Biên giới không hồi quy: không khoá cứng phần nào; được refactor nếu bộ test vẫn xanh.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
