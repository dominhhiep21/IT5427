# Feedback Loop — điều đợt sau nên biết

## 1. Cái đã chứng minh là đúng (giữ)

| Thực hành | Bằng chứng trong đợt |
|---|---|
| Vòng soát kiến trúc độc lập | bắt 1 Critical + 2 Major ở U2, 1 Critical + 1 Major ở U3 — không có cái nào do người dùng phát hiện |
| TDD cho lớp khó (mô hình) bằng test **hành vi** | test cỡ mẫu/chia tập/không rò rỉ đỏ trước, xanh sau; không có test nào ghim AUC |
| Test `slow` trên dữ liệu thật cho mỗi đơn vị | ba lần bắt được lệch thật (0,5133 cũ, callback_map, mốc sàn) |
| Ghi deviation ngay trong artifact (D-1, D-2) | người đọc sau không phải đoán vì sao thiếu một nhánh |
| Đo lại baseline trước khi so mô hình | 0,5297 là mốc thật, không phải số cũ |

## 2. Cái nên làm khác đi (đợt sau)

| # | Điều | Vì sao |
|---|---|---|
| F1 | **Đặt mục tiêu AUC theo khả năng của dữ liệu, hoặc nói rõ đây là mục tiêu thử nghiệm** | 0,6482 với 14 đặc trưng cho thấy 0,70 có thể ngoài tầm dữ liệu 2016–2018; đặt 0,70 rồi trượt là thông tin, nhưng nên nêu trước |
| F2 | Đo ngay cặp số cho mọi ngưỡng "đo tay" (PR3.4) | đã để lại một khoảng trống không đóng được về sau |
| F3 | Giữ tài liệu thiết kế cập nhật **trong** lúc thi công, không để cuối | 5 chỗ lệch (D8–D12) đều phát hiện muộn |
| F4 | Tách `analysis_tab.py` trước khi thêm mục thứ tư | tệp đã ~560 dòng; nay thành tệp lớn nhất repo |
| F5 | Cân nhắc gộp `stats` vào `--stage all` (TD-11) | hai lệnh cho một lần chạy là nguồn lỗi "quên bước 3" |

## 3. Việc cụ thể cho intent sau

| Ưu tiên | Việc | Vì sao |
|---|---|---|
| 1 | Quyết định mục tiêu AUC (giữ 0,70 với đặc trưng mới, hay đặt mục tiêu theo dữ liệu) | D1 |
| 2 | Xử lý điểm lệch `skeleton: on` vs "không dựng lát cắt mỏng" | D5 — đang treo từ hai đợt |
| 3 | Đóng PR3.4 bằng một cặp số trước/sau | D7 |
| 4 | Dọn `TD-06`, `TD-26` (hai import chéo) | nợ đã ghi, rẻ |
| 5 | Tách `analysis_tab.py` / thêm cache có vô hiệu hoá nếu mở tab chậm | F4 |

## 4. Điều **không** nên làm lại

- Đừng thêm test khẳng định một giá trị AUC cụ thể (ngoại lệ mốc sàn đã có lý do và đã ghi).
- Đừng nới ngưỡng thời gian khi máy bận — chạy lại khi rảnh trước.
- Đừng để `code-summary.md` làm nguồn số duy nhất; số phải đọc được từ lệnh chạy lại.

## 5. Nguồn

`../observability-setup/{dashboards,alarms,slo-config}.md` (tín hiệu và SLI), `../performance-validation/test-results.md` (số đo), `../incident-response/incident-plan.md` (mức sự cố đã dùng), và ba bộ `code-generation/reviews/` của U2/U3.
