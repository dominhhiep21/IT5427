# User Stories — Assessment

Nguồn: `../requirements-analysis/requirements.md`, `../intent-capture/stakeholder-map.md`, `../../ideation/scope-definition/scope-document.md`, `codekb/Tich-hop-va-xu-li-du-lieu-lon/business-overview.md`.

## Quyết định: **Execute**

## Vì sao

Bốn dấu hiệu trong điều kiện chạy đều có mặt:

| Dấu hiệu | Ở đợt này |
|---|---|
| Có bề mặt người dùng | khối dự đoán là giao diện thật, có biểu mẫu bảy ô và sáu trạng thái (FR3) |
| Có persona | người phân tích là người duy nhất (Q2 = D ở Intent Capture), nhưng họ đóng **hai** vai khác nhau: người chạy pipeline và người đọc kết quả |
| Logic nghiệp vụ phức tạp | ranh giới rò rỉ, chia tập theo `order_id`, đóng góp log-odds, hai mô hình (FR2) |
| Phối hợp nhiều tầng | mart → mô hình → báo cáo → giao diện, mỗi tầng chạm tệp khác nhau (U1 → U2 → U3) |

## Nơi truyện sẽ đóng góp nhiều nhất

1. **Chuẩn hoá trạng thái giao diện** (FR3.2): sáu trạng thái là thứ dễ bị gộp thành "chạy được là xong" khi viết mã. Một tiêu chí Given/When/Then cho từng trạng thái buộc phải xử lý đủ.
2. **Ranh giới rò rỉ** (FR2.1, FR2.2): đây là chỗ sai **im lặng** — một tiêu chí kiểm được là "không đơn nào ở cả hai tập", không phải một câu mô tả.
3. **Năm chỗ khai baseline** (FR1.4): truyện có thể nêu rõ việc cập nhật đồng thời là một phần của "xong", không phải việc dọn sau.

## Điều assessment này không hứa

Nó không hứa truyện thay được yêu cầu. `requirements.md` vẫn là nguồn sự thật cho **cái gì** phải đúng; truyện chỉ thêm **ai** và **khi nào coi là đúng**. Hai tài liệu lệch nhau thì yêu cầu thắng.

## Phạm vi sẽ không có truyện

Không có truyện cho U1/U2 thuần kỹ thuật nội bộ (thêm cột, huấn luyện, ghi tệp). Chúng không có người dùng trực tiếp; chúng đi vào truyện với tư cách **điều kiện tiên quyết** hoặc **tiêu chí nghiệm thu**, không phải truyện riêng. Ghi rõ ở đây để không ai đi tìm truyện cho chúng.
