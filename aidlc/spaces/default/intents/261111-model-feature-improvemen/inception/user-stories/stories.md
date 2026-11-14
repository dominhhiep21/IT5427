# User Stories

Nguồn: `personas.md`, `../user-stories-assessment.md`, `../requirements-analysis/requirements.md`, `../../ideation/rough-mockups/{wireframes,user-flow}.md`.

Ba nhóm, chia **theo hành trình người dùng** (Q2 = A). Cả ba nhóm thuộc **P1 hoặc P2 đã khai trong `personas.md`** — không có persona thứ ba.

---

## Nhóm US1 — Người chạy pipeline (P1)

### US1.1 — Đo lại baseline trước khi tin bất kỳ con số nào
**Là** người chạy pipeline (P1), **tôi muốn** thấy AUC của baseline `customer_state` được đo trong đúng khung và đơn vị mới, **để** không so một con số mới với một con số đo trong điều kiện khác.

**Must Have** · FR1.1, FR1.2, FR1.3, NFR4

| ID | Given / When / Then |
|---|---|
| AC1.1.1 | **Given** báo cáo vừa sinh trên dữ liệu thật, **When** đọc `model.baseline_auc`, **Then** nó là số trong (0,1) **và** được ghi kèm `model.counts.cohort_rows` = 110.195 — tức đo trên quần thể grain dòng hàng, không phải 96.478 đơn |
| AC1.1.2 | **Given** lần chạy vừa xong, **When** đọc `model.counts`, **Then** `cohort_rows` = 110.195, `cohort_orders` = 96.476, `late_rows` = 8.713, `excluded_missing_carrier` = 2 |
| AC1.1.3 | **Given** đã thêm cột vào mart, **When** kiểm số dòng, **Then** 9 bảng mart và 11 view giữ nguyên số dòng |

### US1.2 — Biết mô hình mới có thực sự tốt hơn
**Là** người chạy pipeline (P1), **tôi muốn** một phép so tường minh giữa AUC mô hình triển khai và baseline đo lại, **để** không nhầm "khác đi" với "tốt hơn".

**Must Have** · FR2.5, FR2.7

| ID | Given / When / Then |
|---|---|
| AC1.2.1 | **Given** báo cáo thật, **When** so `model.auc` với `model.baseline_auc`, **Then** `model.auc > model.baseline_auc`; nếu không, test `slow` đỏ |
| AC1.2.2 | **Given** cùng báo cáo, **When** đọc `model.beats_baseline`, **Then** giá trị đó bằng đúng kết quả của phép so ở AC1.2.1 |
| AC1.2.3 | **Given** mô hình triển khai là logistic, **When** đọc `model.auc_tree`, **Then** trường đó có mặt và khác `model.auc` |
| AC1.2.4 | **Given** tệp báo cáo, **When** đọc trường `version`, **Then** giá trị là **3**; và mỗi chỉ số trong khối `model` có nhãn đơn vị nói rõ nó tính **trên dòng hàng** |

### US1.3 — Quyết định về mốc chất lượng được ghi lại
**Là** người chạy pipeline (P1), **tôi muốn** quyết định giữ hay hạ mốc được ghi kèm lý do ngay khi biết AUC, **để** mốc không trôi âm thầm.

**Must Have** · FR2.8

| ID | Given / When / Then |
|---|---|
| AC1.3.1 | **Given** AUC đã biết, **When** kết thúc Build and Test, **Then** record có một mục ghi rõ giữ hay hạ mốc và lý do |
| AC1.3.2 | **Given** mốc hiện hành là `M`, **When** đọc `counts.auc_below_target`, **Then** cờ đó bằng `model.auc < M` — theo **mốc hiện hành**, không hard-code 0,70 |

---

## Nhóm US2 — Hành trình dự đoán (P2)

### US2.1 — Mở tab và thấy khối dự đoán ở đúng chỗ
**Là** người dự đoán (P2), **tôi muốn** khối dự đoán nằm sau mục "Mô hình" trong tab kết quả, **để** đọc theo thứ tự tự nhiên.

**Must Have** · FR3, FR3.5, NFR6

| ID | Given / When / Then |
|---|---|
| AC2.1.1 | **Given** báo cáo `day-du`, **When** mở tab, **Then** có bốn mục theo thứ tự tóm tắt → thống kê → mô hình → dự đoán |
| AC2.1.2 | **Given** khối đã dựng, **When** kiểm cấu trúc, **Then** tiêu đề mục là `H3`, không `tabIndex` dương, không thẻ tóm tắt thứ năm, và **mọi vùng nội dung có `aria-label` hoặc heading ngữ nghĩa** |
| AC2.1.3 | **Given** dashboard đang chạy, **When** đếm callback và output, **Then** đúng **10** callback và **10** output |
| AC2.1.4 | **Given** khối đã dựng, **When** kiểm thông báo và màu, **Then** khối **không** đặt `aria-live` riêng (vùng `RESULT_BODY_ID` của tab là nơi duy nhất), **và** tab không dùng token màu mới nào ngoài `assets/style.css` |
| AC2.1.5 | **Given** thay đổi đã áp, **When** đọc `TEXTS["model_caption"]` và `README.md` mục Dashboard, **Then** cả hai **không còn** câu khẳng định tab chỉ đọc; và chữ dưới 16px trong khối dùng `--text-2`, đạt tương phản ≥ 4,5:1 |
| AC2.1.6 | **Given** khối đã dựng, **When** đọc câu mở đầu, **Then** câu đó nói rõ dự đoán là cho **một dòng hàng** (một món hàng trong một đơn, có người bán riêng) |

### US2.2 — Nhập thông tin và nhận một dự đoán
**Là** người dự đoán (P2), **tôi muốn** nhập bảy thông tin của một dòng hàng và nhận xác suất trễ, **để** biết trường hợp cụ thể này có đáng lo không.

**Must Have** · FR3.1, FR3.3

| ID | Given / When / Then |
|---|---|
| AC2.2.1 | **Given** khối ở trạng thái chưa dự đoán, **When** bấm Dự đoán với bảy ô hợp lệ, **Then** hiện xác suất, so với ngưỡng trong báo cáo, và một câu kết luận nói về **dòng hàng** |
| AC2.2.2 | **Given** bốn trường không nhập, **When** đọc cây thành phần, **Then** mỗi trường trong bốn trường hiện **đúng giá trị** đã chốt (`payment_type=credit_card`, `payment_installments=1`, `has_items=true`, `has_payment=true`) **và** có điều khiển cho phép sửa |
| AC2.2.3 | **Given** một ô để trống hoặc sai định dạng, **When** bấm Dự đoán, **Then** lỗi hiện ngay tại ô đó, không ném và không làm sập tab |

### US2.3 — Hiểu vì sao dòng hàng này bị đánh giá như vậy
**Là** người dự đoán (P2), **tôi muốn** thấy ba yếu tố đóng góp lớn nhất, **để** không phải tin một con số không giải thích.

**Must Have** · FR3.3

| ID | Given / When / Then |
|---|---|
| AC2.3.1 | **Given** một kết quả, **When** xem phần giải thích, **Then** có đúng **ba** dòng, mỗi dòng là một **trường** (mọi cột one-hot của trường đó đã gộp), kèm dấu và giá trị log-odds |
| AC2.3.2 | **Given** ba dòng đó, **When** đọc nhãn, **Then** nhãn ghi "Ba đóng góp lớn nhất (log-odds, không phải tổng)" |
| AC2.3.3 | **Given** dòng hàng có `customer_state=SP`, **When** xem ba dòng, **Then** không thể có hai dòng cùng là `customer_state` ở hai mức khác nhau |

### US2.4 — Tin rằng con số không đổi bí mật
**Là** người dự đoán (P2), **tôi muốn** cùng một đầu vào luôn cho cùng một xác suất, **để** con số dùng được khi bàn bạc với người khác.

**Must Have** · FR2.1, FR2.2, FR2.3, FR2.4, FR3.4

| ID | Given / When / Then |
|---|---|
| AC2.4.1 | **Given** cùng bảy ô, **When** bấm Dự đoán hai lần, **Then** hai xác suất giống nhau tuyệt đối |
| AC2.4.2 | **Given** cùng bảy ô, **When** khởi động lại dashboard rồi dự đoán lại, **Then** xác suất vẫn giống lần trước |
| AC2.4.3 | **Given** tệp mô hình được lưu, **When** nạp lại, **Then** khối dùng **đúng** trạng thái tiền xử lý đã lưu (danh sách phạm trù + tham số chuẩn hoá), không khớp lại trên dữ liệu lúc dự đoán |
| AC2.4.4 | **Given** hai tập huấn luyện/kiểm tra, **When** giao tập `order_id`, **Then** giao **rỗng** — không đơn nào ở cả hai phía |
| AC2.4.5 | **Given** ma trận đặc trưng, **When** so với `FORBIDDEN_COLUMNS`, **Then** không cột nào trong danh sách cấm xuất hiện; `order_delivered_carrier_date` và `order_approved_at` chỉ vào dưới dạng số ngày dẫn xuất |
| AC2.4.6 | **Given** mô hình cây được huấn luyện để báo cáo, **When** chạy `--stage stats` hai lần, **Then** `model.auc_tree` giống nhau (cùng `random_state`) |

### US2.5 — Gặp trạng thái thiếu mà không hoảng
**Là** người dự đoán (P2), **tôi muốn** mỗi trạng thái thiếu đều nói rõ phải làm gì, **để** không nhầm "chưa có dữ liệu" với "hệ thống hỏng".

**Must Have** · FR3.2

| ID | Given / When / Then |
|---|---|
| AC2.5.1 | **Given** chưa có báo cáo (`rong`), **When** mở tab, **Then** **không** có mục Dự đoán và tab hiện lệnh cần chạy |
| AC2.5.2 | **Given** báo cáo `loi`, **When** mở tab, **Then** **không** có mục Dự đoán, hiện lý do và đường dẫn tệp |
| AC2.5.3 | **Given** báo cáo `mot-phan` (thiếu khối mô hình), **When** dự đoán, **Then** hiện xác suất và câu "chưa có ngưỡng để so", **không** có câu cảnh báo |
| AC2.5.4 | **Given** báo cáo đủ nhưng thiếu `data/models/`, **When** mở khối, **Then** hiện đúng câu chứa nguyên văn `python -X utf8 -m src.pipeline run --stage stats` và `data/models/` |
| AC2.5.5 | **Given** khối ở trạng thái "chưa dự đoán", **When** xem, **Then** có một dòng nói bấm nút để xem, và **không** có số nào được hiện |
| AC2.5.6 | **Given** đã bấm Dự đoán, **When** đang tính, **Then** nút ở trạng thái chờ và kết quả cũ (nếu có) được làm mờ, không hiện như kết quả mới |

---

## Nhóm US3 — Đọc kết quả (P1, cùng người — không phải persona thứ ba)

### US3.1 — Thấy ngay mô hình có đạt mốc hay không
**Là** người chạy pipeline (P1) đọc lại kết quả của chính mình, **tôi muốn** dải tóm tắt nói rõ AUC đạt hay không đạt **mốc hiện hành**, **để** không phải tự so trong đầu.

**Must Have** · FR2.6

| ID | Given / When / Then |
|---|---|
| AC3.1.1 | **Given** `counts.auc_below_target = true`, **When** xem thẻ AUC, **Then** thẻ ghi "không đạt mốc" kèm **giá trị mốc đang áp** (không hard-code chữ "0,70") |
| AC3.1.2 | **Given** `counts.auc_below_target = false`, **When** xem thẻ AUC, **Then** thẻ ghi "đạt mốc" kèm cùng giá trị mốc đó |
| AC3.1.3 | **Given** mô hình cây đạt mốc còn logistic không, **When** xem thẻ, **Then** thẻ vẫn nói **không đạt** |

### US3.2 — Cổng chặn mô hình thoái hoá
**Là** người chạy pipeline (P1), **tôi muốn** một cổng trong CI bắt được mô hình tệ đi, **để** một thay đổi vô tình không lọt qua.

**Should Have** · NFR5

| ID | Given / When / Then |
|---|---|
| AC3.2.1 | **Given** báo cáo thật có `auc` dưới `max(MODEL_AUC_FLOOR, baseline_auc)`, **When** chạy bộ `slow`, **Then** test cổng đỏ |
| AC3.2.2 | **Given** báo cáo đạt, **When** chạy bộ `slow`, **Then** test cổng xanh và đọc **tệp thật** do `--stage stats` sinh, không dùng fixture |

---

## Điều các truyện này không phủ

U1 và U2 thuần kỹ thuật (thêm cột vào mart, ghi tệp mô hình) **không có truyện riêng**; chúng vào vai điều kiện tiên quyết (`US1.1`, `US2.4`) và tiêu chí nghiệm thu. FR1.4 (thay baseline ở năm nơi) ở lại `Deferred` → **code-generation**, vì nó là việc cập nhật hằng số ở nhiều tệp, không phải hành vi người dùng thấy được.
