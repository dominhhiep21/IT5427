# Câu hỏi — Practices Discovery

Bản nháp đã đọc `memory/team.md` (đã được chốt ở đợt trước) và codekb mới. Phần lớn thực hành vẫn đúng; chỉ có ba chỗ bằng chứng **không** tự trả lời được.

## Q1. Giữ TDD cho đợt này không

Đợt trước chốt `tdd`. Đợt này có một phần khó viết test trước: dựng đặc trưng mới và so hai mô hình — kết quả AUC chỉ biết sau khi chạy.

- A. Giữ **TDD** cho mọi lớp, kể cả phần mô hình (viết test trước cho hành vi: cỡ mẫu, chia tập theo `order_id`, không rò rỉ)
- B. **Test-after** riêng cho phần mô hình; TDD cho phần còn lại
- C. `custom` — mô tả cách trộn (nêu ở phần trả lời)
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Build a thin end-to-end slice first?

Một **walking skeleton** là bản tối thiểu chạy xuyên suốt: mart → mô hình → tab, dựng trước để chứng minh các mảnh khớp nhau rồi mới làm tính năng thật. Đợt trước chốt **không** dựng; scope `feature` thì khai `skeleton: on`.

- A. Giữ **không** dựng lát cắt mỏng — làm trọn từng Bolt như đợt trước
- B. Năm nay **dựng** một lát mỏng trước: nới mart → một đặc trưng → mô hình logistic thô → vùng nhập liệu trống trong tab, rồi mới làm thật
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q3. Lưu mô hình bằng gì — và nó đổi định nghĩa "phát hành"

Hiện không có chỗ lưu mô hình, không `joblib`/`pickle`, và `.gitignore` chặn `data/`. Chọn cách nào cũng phải sửa `## Deployment` (định nghĩa "phát hành" hiện là chạy lại từ mã nguồn).

- A. Lưu vào `data/models/` bằng **`pickle` của thư viện chuẩn** — không thêm phụ thuộc nào, nhưng tệp mô hình không vào git và mỗi máy phải tự sinh lại
- B. Lưu vào `data/models/` bằng **`joblib`** (phải ghim thêm một gói vào `requirements.txt`) — cùng hệ sinh thái `scikit-learn`, xử lý mảng lớn tốt hơn
- C. Lưu vào một thư mục **được commit** (ví dụ `models/`) để mọi checkout có sẵn mô hình — đổi lại repo chứa tệp nhị phân sinh ra
- D. Chưa xác định — chốt ở Functional Design
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Ba câu đã trả lời. Bản tóm tắt để bạn xác nhận:

- **Thực hành kiểm thử** [Q1 = A]: giữ **TDD** cho mọi lớp, kể cả phần mô hình. Test viết trước khẳng định **hành vi** (cỡ mẫu, chia tập theo `order_id`, không rò rỉ), **không** khẳng định một AUC mục tiêu.
- **Lát cắt mỏng** [Q2 = A]: **không dựng** — làm trọn từng Bolt như đợt trước. Điểm lệch với `skeleton: on` của scope vẫn được ghi nguyên văn, không bị giải quyết lặng lẽ.
- **Lưu mô hình** [Q3 = A]: `data/models/` bằng **`pickle` của thư viện chuẩn**, không thêm phụ thuộc. Hệ quả đã ghi vào `## Deployment`: tệp mô hình **không được commit**, chỉ sinh bởi `run --stage stats`, và **máy mới clone phải chạy bước 3 trước khi vùng dự đoán dùng được**.
- **Sửa 16 khẳng định lỗi thời** trong baseline: 74 tệp/11.333 dòng, 499 hàm test, 5 tab, 12 gói ghim, `test_pipeline_stages.py` đã tồn tại, README mục CI đã khớp `ci.yml`.
- **`discovered-rules.md`**: thêm 6 quy tắc mới (3 `ALWAYS`, 3 `NEVER`) và bỏ `pickle` khỏi danh sách thư viện bị cấm — nó là thư viện chuẩn và nay là cách lưu đã chốt.

- Looks correct
- Request changes

[Answer]: Looks correct
