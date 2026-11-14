# Security Requirements — u3-prediction-ui

Nguồn: `../functional-design/functional-design-rules` (`rules.md` BR3.19, BR3.25, BR3.28, BR3.31), `../../../inception/requirements-analysis/requirements.md` (NFR6, SEC-2, SEC-5), `../../../inception/contract-design/contract-summary.md` (C2b, C3), `src/analytics/persistence.py`.

Bề mặt tấn công của đơn vị này nhỏ nhưng có ba điểm thật: đầu vào người dùng, tệp `pickle`, và ranh giới hiển thị. Mỗi yêu cầu dưới đây có cách kiểm cụ thể.

| ID | Yêu cầu | Cách kiểm |
|---|---|---|
| SR3.1 | **Không thêm phụ thuộc** ngoài `requirements.txt`; giao diện chỉ dùng `dash`, `dash_mantine_components`, `pandas` đã có | `pip freeze` không đổi; `requirements.txt` không sửa |
| SR3.2 | Đầu vào người dùng được **kiểm trước khi** chạm mô hình: 11 giá trị, miền số và dạng mã bang như §5 của đặc tả. Không có `eval`, không `exec`, không `pickle.loads` trên đầu vào | test gọi `validate_form` với từng ô sai; grep mã không có `eval`/`exec` |
| SR3.3 | `score_item` là **hàm thuần**: không đọc tệp, không mở kết nối, không `random`, không đọc đồng hồ. Đầu vào lạ bị `ModelError` nêu tên trường | test hai lần gọi cho cùng xác suất; test `_serve_features` với 8 giá trị ngoài miền |
| SR3.4 | `pickle` chỉ nạp **tệp do chính máy này sinh** trong `config.models_dir`; đường dẫn lấy từ `AppConfig`, không từ đầu vào người dùng. Tệp hỏng ⇒ `ModelError` bị **bắt**, giao diện hiện **câu hướng dẫn cố định** (BR3.25) và giữ nút tắt; thông điệp thô **chỉ vào nhật ký**, không vào cây thành phần | test `load_model` với tệp rác; test cây thành phần không chứa chuỗi đường dẫn |
| SR3.5 | Rủi ro `pickle` được **ghi nhận, không che**: tệp mô hình không phải định dạng trao đổi giữa các máy; máy khác sinh lại tệp của mình (C2b). Không có cơ chế nạp tệp từ xa, không có API nhận tệp | đọc mã: không có `requests`, không có upload; ghi chú trong README |
| SR3.6 | Không có bí mật nào trong mã hay trong cây thành phần; không có khoá, token, mật khẩu | grep `TODO`/`FIXME`/`password`/`token` trong `src/dashboard/` |
| SR3.7 | Không có đường thoát dữ liệu: không gọi mạng, không ghi tệp từ giao diện, không log **giá trị** người dùng nhập (giá, bang, ngày). Nhật ký chỉ nhận loại lỗi và tên tệp tương đối; **riêng** thông điệp thô của `load_model` được ghi vì nó là thông tin chẩn đoán cục bộ (`logs/`, không commit) — nhưng **không** được vào cây thành phần (SR3.10) | đọc mã callback: không `logger.info` giá trị biểu mẫu; cây thành phần không chứa đường dẫn |
| SR3.8 | Hiển thị an toàn: mọi chuỗi người dùng nhập được render qua Dash (escape mặc định); không dùng `dangerously_allow_html`, không `html.Iframe` | đọc mã: không có `dangerously_allow_html=True` |
| SR3.9 | Từ chối dịch vụ cục bộ: mọi ô số có miền hữu hạn (0…365, giá ≥ 0), ngày phải parse được; không có vòng lặp phụ thuộc độ lớn đầu vào | test với `1e308`, `-1`, `"abc"`, ngày rác |
| SR3.10 | Không rò rỉ đường dẫn tuyệt đối của máy vào giao diện: **không** hiển thị `str(ModelError)` của `load_model` (nó chứa `payload_path` tuyệt đối — `persistence.py:84,95`); chỉ hiển thị câu hướng dẫn cố định dùng đường dẫn tương đối `data/models/`. `ModelError` của `score_item` được hiển thị vì chỉ nêu **tên trường** | test khẳng định chuỗi hiển thị không chứa `workspace_root` và không chứa `\\` |
| SR3.11 | Không đụng `dataset/`; không đọc `warehouse/` từ giao diện (chỉ U2/U1 đọc) | đọc mã import của `prediction_section.py` |
| SR3.12 | Bề mặt công khai vẫn chỉ `127.0.0.1:8050`; đơn vị này không thêm route, không thêm cổng | `config.yaml` không đổi; không có `app.server.route` mới |

## Ghi nhận rủi ro còn lại

| Rủi ro | Mức | Chấp nhận vì |
|---|---|---|
| `pickle` có thể thực thi mã khi nạp tệp độc | Thấp | Tệp do chính pipeline sinh trong `data/models/`, đường dẫn từ cấu hình, không có kênh nạp từ ngoài (SR3.4, SR3.5) |
| Người dùng nhập giá trị vô lý nhưng trong miền (ví dụ giá 0) | Thấp | Dự đoán là công cụ tham khảo; miền đã chặn giá trị phi vật lý rõ ràng (âm, > 365 ngày) |
| Thông điệp lỗi của U2 có thể đổi câu chữ | Thấp | Giao diện hiện nguyên văn; test của U2 canh nêu tên trường |
