# Logical Components — u3-prediction-ui

Nguồn: `performance-design.md` (PD3.1–PD3.6), `security-design.md` (SD3.1–SD3.9), `../functional-design/frontend-components.md` §1, `../functional-design/rules.md`.

Đơn vị này là `ui` chạy **trong** tiến trình dashboard. Không có container, không có tiến trình riêng; "thành phần" ở đây là **đơn vị mã** với ranh giới trách nhiệm rõ, để biết NFR nào áp ở đâu và hỏng thì lan tới đâu.

## 1. Kiểm kê thành phần

| ID | Thành phần (đơn vị mã) | Trách nhiệm | NFR áp | Ghi chú |
|---|---|---|---|---|
| LC3.1 | `build_prediction_body(report, model_present)` | dựng **thân** mục Dự đoán: biểu mẫu + vùng kết quả (không bọc `_section` — `analysis_tab` bọc) | PR3.3, PD3.3, PD3.5 | hàm thuần, **không I/O**; `model_present` do LC3.11 cấp |
| LC3.11 | `model_available(config, logger=None)` | hỏi "có tệp mô hình dùng được không" **một lần** lúc dựng panel: `load_model` → `True`; `None`/`ModelError` → `False` + log | PD3.2 (lượt nạp lúc dựng panel), SD3.4 | I/O **duy nhất** ở phía panel; trả `bool`, không ném |
| LC3.2 | `validate_form(values)` | kiểm 11 giá trị, trả lỗi theo `id` ô | SD3.1, SD3.2, PR3.1 (không đáng kể) | hàm thuần |
| LC3.3 | `build_outcome_view(outcome, threshold)` | dựng xác suất + câu so ngưỡng + ba đóng góp | PD3.4 | hàm thuần |
| LC3.4 | `read_prediction_report(config)` | bọc `read_report(report_path(config))`, trả `ReportView` hoặc `None` | PD3.1, SD3.4 | I/O duy nhất phía báo cáo |
| LC3.5 | `load_prediction_model(config)` | bọc `load_model(config.models_dir)`, bắt `ModelError` → `None` + log | PD3.2, SD3.3, SD3.4 | I/O duy nhất phía mô hình |
| LC3.6 | `register_prediction_callback(app, config)` | đăng ký **một** callback, một `Output` | PR3.5, NFR6.1 | không dựng cây |
| LC3.7 | `STATE_CODES`, `PAYMENT_TYPES`, `TEXTS3` | hằng đóng của khối | SD3.2, NFR6.1 | dữ liệu tĩnh |
| LC3.8 | `TEXTS["model_caption"]` (sửa trong `analysis_tab.py`) + nhãn grain | câu chữ, nhãn "dòng hàng" | BR3.15, BR3.30 | sửa tệp có sẵn |
| LC3.9 | `.field-error` trong `assets/style.css` | một luật CSS, dùng `var(--text-2)` | NFR6.1, SD3.7 | không token màu mới |
| LC3.10 | `beats_floor` (import từ U2) | cổng mốc sàn | NFR5.1 | **không sửa**, chỉ gọi trong test |

## 2. Ranh giới và luật phụ thuộc

```
app.py ──▶ register_prediction_callback (LC3.6) ──▶ read_prediction_report (LC3.4)
                                                 ├─ load_prediction_model (LC3.5)
                                                 ├─ validate_form (LC3.2)
                                                 └─ build_outcome_view (LC3.3) ─▶ analytics.model.score_item

render_analysis ──▶ model_available (LC3.11)  [một lượt load_model lúc dựng panel]
             └──▶ sections_for(view, model_present) ──▶ _section(..., build_prediction_body(...))
                                                          └─ prediction_section.build_prediction_body (LC3.1)
                                                             ├─ validate_form (LC3.2)
                                                             ├─ build_outcome_view (LC3.3)
                                                             └─ STATE_CODES / PAYMENT_TYPES / TEXTS3 (LC3.7)
```

- Hướng phụ thuộc **một chiều**: `analysis_tab.py` **import** `prediction_section`; `prediction_section.py` **không** import `analysis_tab`. Không có vòng.
- **Hai lượt nạp mô hình, cả hai đều có chủ:** LC3.11 nạp **một lần lúc dựng panel** để biết có tắt nút hay không (BR3.25, AC2.5.4); LC3.5 nạp **một lần mỗi lần bấm** để lấy trạng thái mới nhất (PD3.1). Cả hai đều đo trong PR3.2.
- `render_analysis` truyền `model_present` vào `sections_for(view, model_present)`; `sections_for` chỉ chuyển tiếp, không tự gọi I/O.
- LC3.5 và LC3.11 nhận `logger=None`; `app.py`/`render_analysis` truyền logger của dashboard (`_integration_logger`) để thông điệp thô của `ModelError` có chỗ ghi (SD3.4, SD3.5). Không có logger thì im lặng — không ném.
- `_section`/`_section_header` ở lại `analysis_tab.py`; `prediction_section` chỉ trả **thân** mục, nên không phải import hàm riêng tư và không nhân bản khung/CSS.
- `sections_for` bọc **riêng** lời gọi `build_prediction_body` trong `try/except`, trả một mục thay thế có câu cố định nếu nó ném. Không dựa vào `try` ở `render_analysis`: khối đó chỉ bọc **lần đọc tệp** (`analysis_tab.py:554-557`), còn `AnalysisPanel(...)` ở `:558` nằm ngoài.
- `prediction_section.py` chỉ import `score_item`, `load_model`, `read_report`; **không** import `AnalyticsService` (dù `model.py` có import nó), không đọc `warehouse/`.
- `app.py` **không** ghép cây; nó chỉ đăng ký callback (LC3.6) và gọi `register_callback` của tab như hiện có.

## 3. Miền lỗi và bán kính ảnh hưởng

| Thành phần hỏng | Người dùng thấy | Lan tới đâu |
|---|---|---|
| LC3.1 ném lỗi khi dựng thân mục | mục Dự đoán hiện câu "tạm thời không dựng được"; ba mục cũ nguyên vẹn | **đã giảm**: `analysis_tab` gọi trong `try/except` (BR3.25 "tab không sập") |
| LC3.4 không đọc được báo cáo | không có mục Dự đoán (trạng thái `rong`/`loi` của tab) | vừa |
| LC3.11 không đọc được tệp mô hình | mục vẫn có, nút tắt, câu hướng dẫn | nhỏ — đúng thiết kế (BR3.25) |
| LC3.5 không nạp được mô hình lúc bấm | khối hiện câu hướng dẫn; nếu tệp vừa bị xoá giữa hai lần, người dùng thấy đúng lý do | nhỏ |
| LC3.2 bỏ sót một miền | `score_item` ném `ModelError`, hiện trong khối | nhỏ — lưới thứ hai của U2 |
| LC3.6 đăng ký sai | callback không chạy hoặc app không khởi động | lớn — test hình dạng bắt ở CI |
| LC3.9 thiếu lớp CSS | chữ lỗi không đúng kiểu, vẫn đọc được | rất nhỏ |

## 4. Tài nguyên chia sẻ

| Tài nguyên | Chia sẻ với | Rủi ro | Cách xử lý |
|---|---|---|---|
| `RESULT_BODY_ID` (`analysis-result`) | callback của tab | tranh chấp `aria-live`/thay thế nội dung | khối là **con** của vùng đó, không tự đặt `aria-live` (BR3.14) |
| `analysis.json` | tab và khối dự đoán | đọc lúc tệp đang bị thay | phía **ghi** dùng `AtomicWriter` (`os.replace`), nên phía đọc thấy bản cũ hoặc bản mới trọn vẹn; `read_report` kiểm hình dạng, sai ⇒ `loi`; callback đọc lại một lần mỗi bấm (PD3.1) |
| `data/models/` | chỉ khối dự đoán | `pickle` hỏng | `load_model` + SD3.4 |
| `AUC_TARGET`, `MODEL_AUC_FLOOR` | U2 sở hữu | U3 vô tình sửa | chỉ `import`; test canh không sửa `model.py` |

## 5. Áp dụng NFR theo thành phần

| NFR | Thành phần chịu trách nhiệm chính |
|---|---|
| NFR1.1, NFR2.1 | không thành phần nào của U3 (thuộc U2) — LC3.10 chỉ đọc kết quả |
| NFR3.1 | LC3.1–LC3.6 (mọi tệp mới vào danh sách `ci.yml`) |
| NFR4.1 | không thành phần nào (U3 không chạm dữ liệu); `read_report` chỉ đọc tệp báo cáo nên không ảnh hưởng 5 KPI |
| NFR5.1 | LC3.10 + test `slow` mới |
| NFR6.1 | LC3.1, LC3.7, LC3.9 |
