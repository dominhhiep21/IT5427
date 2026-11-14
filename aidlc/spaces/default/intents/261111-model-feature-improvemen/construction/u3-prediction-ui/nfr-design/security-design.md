# Security Design — u3-prediction-ui

Nguồn: `../nfr-requirements/security-requirements.md` (SR3.1–SR3.12), `../functional-design/functional-spec.md` §3/§5/§7, `../functional-design/rules.md` (BR3.19, BR3.25), `src/analytics/persistence.py`, `src/config.py`.

## 1. Ranh giới tin cậy

```
người dùng (trình duyệt)  ──▶  Dash callback (tin cậy: cùng tiến trình, localhost)
                                  │
                                  ├─ validate_form        ← chặn đầu vào ở đây, một chỗ
                                  ├─ read_report          ← tệp do pipeline sinh
                                  ├─ load_model           ← tệp do pipeline sinh (pickle)
                                  └─ score_item           ← hàm thuần của U2
```

Ba điểm vào, ba mức tin cậy khác nhau:

| Điểm vào | Tin cậy | Kiểm |
|---|---|---|
| 11 giá trị biểu mẫu | **không tin** | `validate_form` (SD3.1) |
| `data/reports/analysis.json` | tin cậy có điều kiện | `read_report` kiểm hình dạng, sai → `loi` (đã có từ trước) |
| `data/models/*.pkl` | tin cậy có điều kiện | `load_model` kiểm metadata + payload, sai → `ModelError` |

## 2. Quyết định an ninh

| ID | Quyết định | Vì sao | Kiểm bằng |
|---|---|---|---|
| SD3.1 | **Một** chỗ kiểm đầu vào: `validate_form(values) -> dict[id, message]`, thuần, không I/O, chạy **trước** mọi lời gọi mô hình | một luật một chỗ; UI đặt lỗi đúng ô; `ModelError` của U2 là lưới thứ hai | test 8 trường sai + 4 giá trị biên |
| SD3.2 | `STATE_CODES` (27) và `PAYMENT_TYPES` (5) là **hằng đóng** trong `prediction_section.py`; không nhận danh sách từ tệp hay từ người dùng | tránh đường nạp dữ liệu cấu hình từ ngoài vào giao diện | test `len(...) == 27` / `== 5` |
| SD3.3 | Không `eval`, không `exec`, không `pickle.loads` trên bất kỳ chuỗi nào từ biểu mẫu; `load_model` là **đường duy nhất** chạm `pickle` và đường dẫn của nó đến từ `AppConfig` | thu hẹp bề mặt thực thi mã | grep + đọc mã |
| SD3.4 | **Chính sách lộ lỗi:** lỗi nạp mô hình hiện **câu hướng dẫn cố định** (dùng lại `RUN_STATS_HINT` của `report.py` + đường dẫn `data/models/`, không viết lại lệnh thành literal thứ hai); `str(ModelError)` **chỉ** vào nhật ký, vì nó nhúng đường dẫn tuyệt đối (`persistence.py:84,95`). Lỗi `score_item` hiện nguyên văn vì chỉ nêu **tên trường**. Phạm vi khẳng định "không có đường dẫn tuyệt đối" là **cây con kết quả dự đoán**, không phải cả tab: thông điệp `loi` của báo cáo ở `analysis_tab.py:131` là hành vi có sẵn, không thuộc đơn vị này | không lộ cấu trúc thư mục máy trong khối dự đoán | test: cây con `du-doan-ket-qua` không chứa `workspace_root` và không chứa `\\` |
| SD3.5 | Nhật ký có thể ghi **thông điệp thô** của lỗi nạp mô hình (kể cả đường dẫn tuyệt đối, vì đây là chẩn đoán cục bộ trong `logs/`), nhưng **không bao giờ** ghi giá trị biểu mẫu người dùng nhập | đầu vào không thuộc nhật ký; đường dẫn chỉ ở nhật ký máy | đọc mã: không `logger.info` giá trị biểu mẫu |
| SD3.6 | Rủi ro `pickle` được ghi nhận: tệp do chính máy sinh, không phải định dạng trao đổi, không có kênh nạp từ ngoài, không có endpoint nhận tệp | trung thực về giới hạn thay vì hứa "an toàn" | `security-requirements.md` §Ghi nhận rủi ro; README |
| SD3.7 | Render an toàn: mọi chuỗi đi qua Dash (escape mặc định); không `dangerously_allow_html`, không `Iframe`, không chèn HTML từ đầu vào | XSS không có đường vào | grep |
| SD3.8 | Không mạng ra ngoài, không ghi tệp từ callback, không route mới; vẫn chỉ `127.0.0.1:8050` | giữ nguyên bề mặt mạng | đọc `app.py` + `config.yaml` |
| SD3.9 | Không bí mật trong mã; không đọc biến môi trường trong khối mới | repo không có bí mật, không thêm | grep |
| SD3.10 | **Không thêm phụ thuộc**: khối chỉ dùng `dash`, `dash_mantine_components`, `pandas` đã ghim; `requirements.txt` không đổi | SR3.1; thêm gói là thay đổi chuỗi cung ứng không cần thiết | test đọc `requirements.txt` và so bộ gói import trong `prediction_section.py` |

## 3. Kiểm soát theo tầng

| Tầng | Kiểm soát | Nếu vượt qua |
|---|---|---|
| Biểu mẫu (trình duyệt) | `validate_form` chặn giá trị ngoài miền, ngày sai dạng, mã bang lạ | callback trả cây lỗi, không gọi mô hình |
| Hàm chấm điểm | `_serve_features` của U2 kiểm lại miền và nêu tên trường | `ModelError` hiện trong khối |
| Tệp mô hình | `load_model` kiểm metadata + payload | câu hướng dẫn cố định, nút tắt |
| Báo cáo | `read_report` kiểm 11 trường + 9 khoá `counts` | trạng thái `loi`, không có mục Dự đoán |

## 4. Ghi nhận rủi ro còn lại (đồng bộ với `security-requirements.md`)

| Rủi ro | Mức | Lý do chấp nhận |
|---|---|---|
| `pickle` có thể thực thi mã nếu tệp bị thay bằng tệp độc | Thấp | đường dẫn từ cấu hình, tệp do pipeline sinh, không có kênh nạp ngoài (SD3.3, SD3.6) |
| Người dùng nhập giá trị hợp lệ nhưng phi thực tế (giá 0) | Thấp | công cụ tham khảo; miền đã chặn giá trị phi vật lý rõ ràng |
| Nhật ký cục bộ chứa đường dẫn tuyệt đối | Thấp | `logs/` không commit, chỉ đọc trên máy chạy |

## 5. Nghĩa vụ kiểm thử

| Yêu cầu | Test |
|---|---|
| SR3.1 (SD3.10) | `test_prediction_section_imports_no_new_dependency` — đọc `requirements.txt`, so với bộ gói mà `prediction_section.py` import |
| SR3.2, SR3.9 | `test_validate_form` (9 luật cho 11 giá trị: 8 ô có miền + 1 luật cho `payment_type`; hai cờ boolean không có miền) |
| SR3.3 | `test_score_item_is_deterministic` (đã có ở U2; U3 gọi lại qua khối) |
| SR3.4, SR3.10, SD3.4 | `test_model_error_shows_guidance_without_absolute_path` |
| SR3.5, SR3.7 | `test_prediction_module_has_no_remote_or_upload_path` (grep `requests`/`urlopen`/id upload trong `prediction_section.py`) và `test_prediction_section_never_logs_form_values` (giả lập logger, gọi callback, khẳng định không có giá trị nào trong bản ghi) |
| SR3.6 | `test_no_secret_like_literals_in_prediction_module` — grep `password`/`token`/`secret` |
| SR3.8 | `test_no_html_injection_in_prediction_result` |
| SR3.11 | `test_prediction_module_imports_no_analytics_service` — `prediction_section.py` không import `AnalyticsService`, không mở `warehouse/` (không đòi điều đó ở `model.py`, nơi đã có sẵn) |
| SR3.12 | `test_dashboard_still_binds_localhost` (đọc `config.yaml`) |
