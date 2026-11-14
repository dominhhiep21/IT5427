# Tech Stack Decisions — u3-prediction-ui

Nguồn: `../../../inception/requirements-analysis/requirements.md` (§Constraints), `../../../../codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`, `../../../../../requirements.txt`, `../../../../../src/dashboard/`.

## 1. Quyết định

| # | Quyết định | Vì sao | Đổi ý thì đổi ở đâu |
|---|---|---|---|
| TS3.1 | Dùng **Dash + `dash_mantine_components`** đã có, không thêm khuôn giao diện | Ba tab hiện có cùng khuôn; thêm React/bundler là thay đổi hạ tầng cho một khối | `src/dashboard/app.py` |
| TS3.2 | Mục Dự đoán là **hàm dựng cây thuần** trong `src/dashboard/prediction_section.py` (tệp mới), không nhồi vào `analysis_tab.py` (đã 560 dòng) | giữ `analysis_tab.py` dưới ngưỡng đọc; test dựng cây không cần app | tên tệp + một import |
| TS3.3 | Callback đăng ký trong `prediction_section.register_callback(app, config)` | cùng mẫu `register_callback` của tab hiện có; giữ số callback đếm được | `app.py` chỗ gọi |
| TS3.4 | **Không thêm phụ thuộc**; không thêm `plotly` figure mới, không `dash-bootstrap-components` | mọi thứ cần đã có; `requirements.txt` là 12 gói ghim | `requirements.txt` (không đổi) |
| TS3.5 | Dùng `dcc.Loading` cho trạng thái "đang tính" | ADR-005: spinner là đủ; tránh Output thứ hai | `prediction_section.py` |
| TS3.6 | `STATE_CODES` (27 UF) và `PAYMENT_TYPES` (5) là **hằng của U3** trong `prediction_section.py` | repo không có danh sách UF dùng được cho `seller_state`; `state_regions` chỉ phủ `customer_state` | hằng trong tệp |
| TS3.7 | Định dạng số dùng `src/dashboard/formatting.py` (`format_number`, `format_percent`) | định dạng Brazil đã thống nhất; `format_percent` **không** nhân 100 | `formatting.py` (không đổi) |
| TS3.8 | Thời gian đo bằng `time.perf_counter()` trong test đơn vị, không thêm `pytest-benchmark` | tránh phụ thuộc mới; ngưỡng ở PR3.1–PR3.3 đủ thô để đo bằng tay | `requirements.txt` |
| TS3.9 | Không dùng `functools.lru_cache` cho `read_report`/`load_model` | cache sẽ trả bản cũ sau khi `--stage stats` ghi bản mới; W2 bước 1 đọc lại mỗi lần bấm | `prediction_section.py` |
| TS3.10 | CSS mới chỉ một luật `.field-error` trong `assets/style.css` | token `--text-2` đã có; không thêm biến màu | `assets/style.css` |

## 2. Vị trí mã

| Tệp | Vai trò | Trạng thái |
|---|---|---|
| `src/dashboard/prediction_section.py` | dựng cây mục Dự đoán, `validate_form`, `register_callback` | **mới** |
| `src/dashboard/analysis_tab.py` | thêm mục thứ tư vào `SECTION_IDS`/`sections_for`; xoá nhánh dự phòng AUC; sửa `model_caption`; đổi nhãn grain | sửa |
| `README.md` | mục Dashboard: bỏ câu "khối mô hình chỉ đọc"; thêm ghi chú tệp mô hình ở `data/models/` (BR3.15, SR3.5) | sửa |
| `src/dashboard/app.py` | gọi `prediction_section.register_callback` | sửa |
| `assets/style.css` | thêm `.field-error` | sửa |
| `tests/unit/test_u3_prediction_section.py` | hành vi khối + `validate_form` + số thành phần + đọc `README.md` khẳng định không còn câu "chỉ đọc" | **mới** |
| `tests/integration/test_u3_floor_end_to_end.py` | cổng mốc sàn trên báo cáo thật (`slow`) | **mới** |
| `tests/unit/test_dashboard_smoke.py`, `tests/unit/test_dashboard_analysis_tab.py`, `tests/integration/test_u3_end_to_end.py` | cập nhật hình dạng (10 callback, 4 mục, 5 tab) | sửa |
| `tests/unit/test_ci_config.py`, `.github/workflows/ci.yml` | thêm **ba** đường dẫn mới vào **cả hai** danh sách khai tay | sửa |
| `tests/unit/test_analysis_tab_contrast.py` | thêm khẳng định `.field-error` dùng `var(--text-2)` (NFR6) | sửa |

## 3. Phiên bản và ràng buộc

- Python 3.13, Dash và DMC theo phiên bản đã ghim trong môi trường hiện có; không nâng cấp trong đợt này.
- `ruff` là cổng lint/format duy nhất; tệp mới phải vào danh sách `ruff format --check`.
- Không có kiểm tra kiểu tĩnh (`mypy`/`pyright`) — quyết định đã chốt, không thêm.

| # | Ràng buộc đã có, đơn vị này **giữ nguyên** | Nguồn |
|---|---|---|
| TS3.11 | Cổng phủ `pytest --cov=src --cov-fail-under=80` chạy trên toàn bộ bộ test; không hạ ngưỡng, không đặt cờ lên riêng bộ nhanh | NFR3, `ci.yml` |
| TS3.12 | Mốc sàn `MODEL_AUC_FLOOR` được kiểm bằng một test `slow` trên báo cáo thật; U3 chỉ `import` hằng, không sửa `model.py`. Đây là **ngoại lệ** với luật NEVER "không đặt AUC làm kỳ vọng test" (`project.md` `## Forbidden`), nên phải được ghi qua nghi thức learnings vào `project.md` `## Corrections` **trước khi đóng intent**, dẫn lại nguyên văn câu NEVER và lý do NFR5 | NFR5, C3, `project.md` |
| TS3.13 | Không hồi quy dữ liệu: 5 KPI, 9 bảng mart, 11 view; lệnh xác nhận của intent chạy `--stage all` nên cổng này được kiểm lại | NFR4 |
| TS3.14 | Tiếp cận: nhãn cho mọi vùng, không `tabIndex` dương, `--text-2` cho chữ < 16px | NFR6 |

## 4. Điều bị từ chối

| Phương án | Vì sao từ chối |
|---|---|
| Thêm `dash-bootstrap-components` để có form đẹp hơn | phụ thuộc mới cho một khối; `html.Fieldset` + CSS hiện có đủ |
| Dùng `State` để truyền ngưỡng vào callback | ngưỡng phải là bản mới nhất của tệp; `State` giữ giá trị lúc dựng panel (W2 bước 1) |
| Cache `load_model` trong bộ nhớ tiến trình | mô hình chỉ đổi khi chạy `--stage stats`; cache sẽ giữ bản cũ mà không có tín hiệu vô hiệu hoá |
| Thêm endpoint `/predict` | không có nhu cầu ngoài dashboard; thêm bề mặt mạng là thay đổi an ninh không cần thiết (SR3.12) |
| Gom mục Dự đoán vào `analysis_tab.py` | tệp đã 560 dòng, thêm ~250 dòng làm nó thành tệp lớn nhất repo |
