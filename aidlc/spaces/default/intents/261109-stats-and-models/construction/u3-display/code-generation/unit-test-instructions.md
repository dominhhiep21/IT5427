# Unit Test Instructions — u3-display

Nguồn: `code-generation-plan.md`, `../functional-design/rules.md`, `../nfr-design/logical-components.md`, `## Testing Posture` trong `aidlc/spaces/default/memory/team.md`.

## Posture

**Methodology**: tdd. Mỗi lớp chạy được — viết test trước, thấy đỏ, rồi viết mã tới khi xanh.

## Bộ test

Bộ nhanh: `python -X utf8 -m pytest -m "not slow"`. Mọi test mới **tự dựng `ReportView` trong bộ nhớ**; không test nào đọc `data/reports/analysis.json` của repo (lỗ hổng `TD-09`). Test cần báo cáo thật mang marker `slow`.

## Phủ theo quy tắc

| Mã | Ca kiểm tối thiểu |
|---|---|
| BR3.1 | Năm `ReportView` mẫu → năm token đúng; không token nào tự sinh ngoài `chua-chay` |
| BR3.2 | Thứ tự `section_id` là tóm tắt → thống kê → mô hình |
| BR3.3 | `day-du` → bốn thẻ đúng thứ tự; thiếu khối mô hình → thẻ AUC ghi "chưa có", không dấu; thiếu khối stats → chỉ còn thẻ AUC |
| BR3.4 | `mot-phan` với `missing=("model",)` → khối thống kê vẫn đủ; với `("stats",)` → khối mô hình vẫn đủ |
| BR3.5 | Ba câu chữ của `rong`, `mot-phan`, `loi` đôi một khác nhau |
| BR3.6 | `skipped` rỗng → không dải; hai phần tử → hai dòng |
| BR3.7 | Không có `dcc.Slider`/`dcc.Input` trong mục mô hình |
| BR3.8 | Mỗi vùng có tiêu đề ngữ nghĩa **hoặc** `aria-label`; không `tabIndex` dương |
| BR3.9 | Không có lớp CSS mới ngoài `assets/style.css`; tab không thêm token màu |
| BR3.10 | `correlation`/`group_test`/`seasonal` null → hiện tên phép kèm lý do từ `skipped`; `comparisons` rỗng → câu nêu không đủ hai bang |
| NFR5.1 | `formatter` nhân 100: `0.0811` → `8,11%`; cặp màu đo được đạt 4,5:1 |
| NFR5.6 | Stub đếm: đúng một lần gọi `read_report` mỗi callback |

## Ca phải có cho mỗi tệp

- `analysis_tab.py`: mỗi BR một ca, cộng một ca đọc tệp hai lần bị phát hiện.
- `app.py` (phần sửa): một ca khẳng định tab mới nằm trong `tabs.children` và tìm được **theo `id`**, không theo vị trí.
- `test_dashboard_smoke.py`: sửa số tab và callback; **giữ nguyên assert output = 9**.

## Điều cấm

- Không `assert True`, không mock để test luôn xanh.
- Không hạ `--cov-fail-under`.
- Không thêm `per-file-ignores` mới.
- Không test nào gọi mạng hay mở trình duyệt.
