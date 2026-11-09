# Unit Test Instructions — u6-integration-ui

## 1. Khung kiểm thử

| Hạng mục | Giá trị |
|---|---|
| Khung | pytest 9.1.1 |
| Đo phủ | pytest-cov 7.1.0 |
| Tệp test của đơn vị | `tests/unit/test_integration_tab.py` (mới) + cập nhật `test_dashboard_smoke.py`, `test_integration_card.py`, `tests/integration/test_u3_end_to_end.py` |
| Fixture | Hợp đồng giả dựng tay (C4/C5/C6/C7) trong bộ nhớ; không đọc `dataset/`, không cần `warehouse/` |

## 2. Lệnh chạy

```
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_tab.py tests/unit/test_dashboard_smoke.py
```

- Lint: `.venv\Scripts\python.exe -X utf8 -m ruff check src/dashboard/app.py src/integration/card.py src/integration/tab.py tests/unit/test_integration_tab.py`
- Định dạng: cùng danh sách với `ruff format --check`.

## 3. Mục tiêu độ phủ

- Ngưỡng dự án: **80% dòng cho `src/`**, đo trên toàn bộ bộ test.
- Đơn vị: mọi nhánh dựng giao diện có test; dự kiến 20–26 hàm.

## 4. Mock/stub

- Không mock Dash: gọi `build_layout` và các hàm dựng màn hình trực tiếp, kiểm cây `html`/`dmc` trả về.
- Hợp đồng được tiêm qua tham số; một test dựng layout khi cả bốn hợp đồng đều vắng để khẳng định ba tab cũ vẫn xanh (SR-U6-8).
- Không gọi mạng; không mở DuckDB.

## 5. Dữ liệu test

- Mỗi test dựng một hợp đồng nhỏ trong bộ nhớ, gồm cả ca "một phần" (`partial` khác rỗng) và ca lỗi.
- Một test dùng `config/integration-tab.yaml` thật để khẳng định `card_ids` bốn giá trị và `result_region_ids` chứa `don-theo-thang`.

## 6. Ngưỡng hiệu năng

Đo `time.perf_counter` quanh `load_overview`, `route`, `run_query`, `suggest_source` trong test; khẳng định `< 2000` ms trên fixture. Số thật của lần chạy trên dữ liệu Olist ghi vào `code-summary.md`.

## 7. Tiếp cận

Rà thủ công theo BR6.9 và ghi kết quả vào `code-summary.md`: nút thật, tab bàn phím, `:focus-visible`, tương phản, không dùng màu làm tín hiệu duy nhất.
