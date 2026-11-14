# Câu hỏi — Yêu cầu phi chức năng cho u1-statistics

## Q1. [Tech] Thư viện cho các phép kiểm định

Bối cảnh: `requirements.txt` hiện chưa có gói thống kê nào. Cần chọn một hướng và ghim kèm lý do.

A. `scipy` cho phân phối và kiểm định; khoảng tin cậy tự viết bằng công thức đã chốt trong `rules.md`
B. `statsmodels` cho cả kiểm định lẫn phân rã mùa vụ
C. Cả hai: `scipy` cho kiểm định, `statsmodels` cho phân rã mùa vụ
X. Other (please specify)

[Answer]: C

## Q2. [Tech] Cách hiện thực phân rã mùa vụ

Bối cảnh: `rules.md` đã chốt trung bình động giữa có cửa sổ thu hẹp ở hai đầu — một biến thể không có sẵn trong `statsmodels`.

A. Tự viết theo đúng quy tắc đã chốt, chỉ dùng `numpy` (đi kèm `pandas`)
B. Dùng `statsmodels.seasonal_decompose` và chấp nhận hai đầu bị cắt, sửa lại quy tắc
C. Dùng `statsmodels` nhưng bọc lại để xử lý hai đầu theo quy tắc đã chốt
X. Other (please specify)

[Answer]: A

## Q3. [Ops] Mức ghi nhật ký cho tầng `stats`

Bối cảnh: nhật ký hiện là JSONL, mỗi sự kiện có `timestamp`, `level`, `run_id`, `stage`, `event`.

A. Chỉ dùng đúng năm trường sẵn có: một sự kiện bắt đầu, một sự kiện kết thúc kèm thời lượng, một sự kiện cho mỗi kiểm định bị bỏ
B. Thêm trường riêng cho tầng `stats` (số dòng đọc, số đơn đã giao, số bang đủ điều kiện)
C. Không ghi gì thêm ngoài lỗi
X. Other (please specify)

[Answer]: A

## Q4. [Tech] `statsmodels` còn dùng vào việc gì

Bối cảnh: câu trả lời Q1 = C chọn `statsmodels` **cho phân rã mùa vụ**, nhưng câu trả lời Q2 = A lại tự viết phần phân rã bằng `numpy`. Hai câu không cùng đứng được: nếu phân rã tự viết thì `statsmodels` không còn việc nào, mà quy tắc của dự án là mọi thư viện ghim vào `requirements.txt` phải có lý do.

A. Bỏ `statsmodels`; chỉ ghim `scipy`, và tự viết phân rã theo Q2 = A
B. Giữ `statsmodels` nhưng chuyển sang cho các phép kiểm định (chi-square, phân phối); `scipy` lo phần còn lại; phân rã vẫn tự viết
C. Giữ nguyên hướng Q1 = C: dùng `statsmodels` cho phân rã, tức là bỏ Q2 = A
X. Other (please specify)

[Answer]: A
