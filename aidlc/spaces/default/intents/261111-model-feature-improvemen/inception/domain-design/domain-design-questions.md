# Câu hỏi — Domain Design

Hai quyết định ranh giới dưới đây là chỗ có nhiều hơn một cách chia hợp lý. Phần còn lại của thiết kế chỉ có một cách làm đúng (đã ghi trong `components.md` và `decisions.md`).

## Q1. Lưu mô hình: khối riêng hay gộp vào mô-đun mô hình?

`team.md` quy định mô-đun suy luận là hàm thuần, mọi I/O nằm ngoài. Đợt này lần đầu phải ghi mô hình ra đĩa.

- A. **Khối riêng `ModelPersistence`** — nhận `FittedModel` từ `ModelModule`, chịu mọi I/O (`pickle` + metadata). Thêm một mô-đun, nhưng giữ đúng quy ước hàm thuần và tách test I/O
- B. Gộp vào `ModelModule` — ít tệp hơn, nhưng `model.py` chạm đĩa và test của nó kéo `tmp_path`
- C. Đặt trong `stages.py` — không thêm mô-đun, nhưng định dạng tệp nằm ở điểm ghép nối
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Mục thứ tư trong tab: dùng lại khuôn có sẵn hay lớp riêng?

Ba mục hiện có dựng bằng `_section` với `className="chart-card"` (nền, viền, bán kính, bóng đã có). `assets/style.css` chỉ có 8 selector `.analysis-tab`, tất cả chỉ đổi màu chữ.

- A. **Dùng lại `_section`/`.chart-card`**, chỉ thêm CSS cho `fieldset`, nút, danh sách đóng góp
- B. Tạo lớp `section` riêng cho tab phân tích — kiểm soát nhiều hơn, nhưng hai hệ song song trong cùng tab
- C. Dùng style inline từ token — không thêm CSS, nhưng trái quy ước và không test được bằng token
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Hai câu đã trả lời. Bản tóm tắt:

- **Lưu mô hình** [Q1 = A]: khối riêng **`ModelPersistence`**, nhận `FittedModel` từ `ModelModule` và chịu mọi I/O (`pickle` + metadata). Giữ quy ước "mô-đun suy luận là hàm thuần" của `team.md`.
- **Mục thứ tư** [Q2 = A]: dùng lại **`_section`/`.chart-card`**; chỉ **thêm** CSS cho `fieldset`, nút và danh sách đóng góp, dưới `.analysis-tab`.
- **Tám khối** trong `components.md`: MartIntegration, AnalyticsService, ModelModule, ReportContract, ModelPersistence, PipelineStages, AnalysisTab, DashboardApp — đồ thị **không vòng**, YAML đã kiểm parse và đối chiếu tên.
- **Bảy ADR** trong `decisions.md`, gồm ba quyết định đã đảo ở stage trước (logistic thay vì chọn theo AUC; giữ 10 output và hạ AC2.5.6; dùng lại `.chart-card`).
- **`traceability.json`**: 10/US, không có GAP.

- Looks correct
- Request changes

[Answer]: Looks correct
