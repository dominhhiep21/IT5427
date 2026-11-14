# Security Requirements — u1-mart-and-baseline

Đơn vị: `u1-mart-and-baseline` (kind `library`). Nguồn: `functional-spec.md`, `rules.md`, `../../../inception/requirements-analysis/requirements.md`, `../../../inception/contract-design/contract-summary.md` (C1), mã thật `src/integrate/`, `src/common/`.

Đơn vị này không có bề mặt mạng, không xác thực người dùng, không lưu thông tin định danh cá nhân mới. Vì vậy phần an toàn của nó là **bảo vệ tính toàn vẹn của dữ liệu dẫn xuất** và **không mở thêm bề mặt tấn công** — không phải chống truy cập trái phép, và tài liệu này nói đúng như thế.

## NFR4.1 — Không hồi quy dữ liệu (yêu cầu gốc của đơn vị này)

**NFR gốc:** NFR4 — "5 KPI baseline, 9 bảng nguồn, 9 bảng mart, 11 view, khớp tuyệt đối".

Đây là yêu cầu **trung tâm** của đơn vị, không phải một mục an toàn: thêm ba cột phải để lại 5 KPI và mọi số dòng y nguyên. Cơ chế giữ nó là `KpiReconciler` (5 KPI + 5 dung sai) và `StarSchemaValidator` (9 check số dòng), chạy **trước** khi mart được ghi.

**Kiểm:** `BR1.1` và `BR1.6` trong `../functional-design/rules.md`; test `slow` của U1 chạy `run --stage all` trên `dataset/` và khẳng định cả hai cổng xanh.

## Kiểm soát an toàn riêng của dự án — không kế thừa NFR nào

Sáu mục dưới đây là kiểm soát riêng của dự án này, **không** phải yêu cầu phi chức năng nào đã khai ở Requirements Analysis. Chúng không mang mã `NFRx.y` vì không có NFR thượng nguồn để kế thừa; đánh số `NFR4.x` cho chúng sẽ là mượn mã của một yêu cầu khác nghĩa.

## SEC1 — Không có bề mặt xác thực hay phân quyền

Đơn vị chạy trong tiến trình CLI trên máy người dùng, đọc `dataset/` và ghi `data/`, `warehouse/`. Không có endpoint, không có người dùng thứ hai, không có vai trò. **Yêu cầu:** không thêm bất kỳ cơ chế xác thực nào "cho đủ bộ" — một lớp xác thực không có ai gọi là bề mặt tấn công không được kiểm.

**Kiểm:** `grep` trên `src/` không tìm thấy mô-đun/khai báo xác thực nào (`login`, `password`, `token`, `auth`), và `requirements.txt` không có gói xác thực.

## SEC2 — Dữ liệu gốc bất biến; chỉ có một ngoại lệ đã biết

9 CSV trong `dataset/` là nguồn sự thật duy nhất và **chỉ đọc**. **Yêu cầu:** đơn vị này không mở tệp CSV nào trong `dataset/` ở chế độ ghi.

**Ngoại lệ phải nói rõ, vì bản trước của mục này nói sai:** `dataset/external/ibge/` là **cache** của API IBGE do tầng `integrate` ghi (`src/config.py:89` mặc định `ibge_dir` vào đó; `src/external/ibge.py` ghi `estados.json` và `metadata.json`). Đó là dữ liệu **sinh ra**, không phải dữ liệu gốc, và nó đã nằm trong repo. Vì vậy câu "không ghi gì vào `dataset/`" là **sai**; câu đúng là "không ghi vào 9 CSV gốc".

**Vì sao đây là yêu cầu an toàn:** nếu một lần chạy ghi đè lên CSV gốc, không có bản sao nào để khôi phục — dữ liệu gốc là nguồn sự thật duy nhất của cả dự án, và một lỗi như thế không phát hiện được bằng test số dòng.

**Kiểm:** test `slow` so **hash của 9 CSV gốc** trước và sau `run --stage all`. Cache IBGE nằm ngoài phép kiểm này, và điều đó được ghi ngay tại đây thay vì để người đọc tự phát hiện.

## SEC3 — Không có bí mật nào trong mã hay trong mart

Đơn vị này không cần khoá API, không có token, không có chuỗi kết nối có mật khẩu. API IBGE là endpoint công khai, không cần khoá.

**Yêu cầu:** không thêm biến môi trường, không thêm tệp `.env`, không đọc bí mật nào. Nếu sau này cần, nó phải đi qua biến môi trường hoặc secrets manager, không hard-code.

**Kiểm:** `grep` không tìm thấy chuỗi giống khoá/mật khẩu trong `src/integrate/`; `requirements.txt` không thêm gói mới.

## SEC4 — Ba cột mới không làm lộ thông tin cá nhân

`order_approved_at`, `order_delivered_carrier_date`, `seller_state` là **mốc thời gian vận hành** và **bang của người bán** — không phải tên, địa chỉ, số điện thoại, hay mã bưu chính đầy đủ.

**Yêu cầu:** không thêm cột nào chứa định danh trực tiếp. `seller_state` phải là **bang**, không phải thành phố hay mã bưu chính — chi tiết hơn mức cần cho mô hình là mở rộng phạm vi không có lý do.

**Kiểm:** thuộc `tests/data_quality/test_real_dataset.py` (bộ `slow`, nơi đã có dữ liệu thật): khẳng định `seller_state` có đúng 23 giá trị, tất cả khớp mẫu hai chữ hoa. **Không** đặt ở bộ nhanh — bộ nhanh không có dữ liệu thật, và nhét một test cần dữ liệu thật vào đó sẽ tái lập `TD-09`.

## SEC5 — Đường dẫn lấy từ cấu hình, không từ đầu vào người dùng

Mọi đường dẫn đọc/ghi của đơn vị này lấy từ `AppConfig` (`load_config`), không nhận từ dòng lệnh hay từ dữ liệu.

**Vì sao:** đây là kiểm soát chống ghi đè ngoài ý muốn. Một đường dẫn nhận từ đầu vào có thể trỏ vào `dataset/` hoặc ra ngoài workspace; đường dẫn cố định trong cấu hình thì không.

**Kiểm:** `grep` không thấy `Path(` dựng từ tham số người dùng trong `src/integrate/`; test cấu hình khẳng định `AppConfig` là frozen dataclass.

## SEC6 — Lỗi không rò rỉ nội dung dữ liệu

Thông điệp lỗi của `QualityGateError` hiện nêu `expected`/`actual` của từng check — đó là **số đếm**, không phải nội dung dòng. **Yêu cầu:** giữ nguyên tính chất đó. Không đưa giá trị ô dữ liệu, mã đơn hàng hay tên người bán vào thông điệp lỗi.

**Vì sao:** log được ghi ra `logs/` và có thể bị chia sẻ khi báo lỗi; một thông điệp chứa cả dòng dữ liệu là rò rỉ ngoài ý muốn.

**Kiểm:** test đơn vị khẳng định thông điệp lỗi của kiểm số dòng chỉ chứa tên check và hai số.

## Điều tài liệu này không hứa

Không có phòng chống tấn công mạng, không có mã hoá at-rest, không có kiểm toán truy cập. Những thứ đó không tồn tại trong dự án này — dữ liệu chạy trên máy một người, không có dịch vụ công khai. Hứa chúng ở đây sẽ là mô tả một hệ thống khác.
