# Performance Design — u3-prediction-ui

Nguồn: `../nfr-requirements/performance-requirements.md` (PR3.1–PR3.5, NFR1.1–NFR6.1), `../functional-design/functional-spec.md` §4, §7.

## 1. Hình dạng tải

Khối Dự đoán chịu hai loại tải, cả hai đều **nhỏ và cục bộ**:

| Loại | Tần suất | Việc thật sự xảy ra |
|---|---|---|
| Dựng panel | một lần mỗi lần tab được chọn (hoặc mỗi lần callback đọc báo cáo chạy) | đọc `analysis.json` một lần, dựng cây bốn mục |
| Một lần bấm | người dùng bấm nút | đọc lại `analysis.json`, `load_model`, `score_item`, dựng cây kết quả |

Không có vòng lặp theo số dòng dữ liệu: mọi phép tính trong khối chỉ chạm **một** dòng hàng và **một** ma trận 91 cột.

## 2. Quyết định hiệu năng

| ID | Quyết định | Vì sao | Đo bằng |
|---|---|---|---|
| PD3.1 | **Không cache `read_report`.** Panel dùng `ReportView` mà `render_analysis` đã đọc **một lần**; callback đọc **lại một lần** mỗi lần bấm | tệp bị `--stage stats` thay; cache không có tín hiệu vô hiệu hoá sẽ hiện số cũ (W2 bước 1) | PR3.5: test đếm số lần gọi; PR3.4 đo tay |
| PD3.2 | **Không cache `load_model` trong tiến trình.** Nạp một lần lúc dựng panel (LC3.11, để biết có tắt nút) và một lần mỗi lần bấm (LC3.5) | mỗi lượt 0,2–0,4 ms trên tệp 4,8 KB; cache sẽ giữ mô hình cũ sau khi huấn luyện lại | PR3.2 (đo cả hai lượt) |
| PD3.3 | Cây mục Dự đoán dựng **một lần** khi panel dựng; callback chỉ thay cây con `du-doan-ket-qua` | tránh dựng lại 10 thành phần biểu mẫu mỗi lần bấm, và quan trọng hơn: giá trị người dùng đã nhập nằm trong DOM nên không bị dựng lại thành mặc định giữa hai lần bấm | PR3.3 + PR3.5 |
| PD3.4 | One-hot **chỉ** cho 6 cột phân loại với đúng danh sách phạm trù đã lưu (`model.categories`); không quét lại dữ liệu huấn luyện | ma trận 91 cột cố định; không phụ thuộc kích thước mart | PR3.1 |
| PD3.5 | Không thêm `plotly` figure, không ảnh, không tài nguyên mạng | khối chỉ có chữ và danh sách; giữ thời gian dựng cây ở mức mili-giây | PR3.3 |
| PD3.6 | Không dùng `dcc.Store` để giữ kết quả cũ | thêm trạng thái ẩn là thêm đường đồng bộ; "đang tính" đã do `dcc.Loading` thể hiện (ADR-005) | đọc mã |

## 3. Ngân sách và cách kiểm

| Yêu cầu | Ngân sách | Nơi kiểm | Ghi chú |
|---|---|---|---|
| PR3.1 | `score_item` trung bình < 200 ms | `tests/unit/test_u3_prediction_section.py` | đo 20 lần, lấy trung bình; baseline đo được trên máy đợt này: **10,49 ms** (max 11,7 ms) |
| PR3.2 | `load_model` < 2 s | cùng tệp, dựng payload bằng `save_model` trong `tmp_path`; đo **cả** lượt lúc dựng panel (LC3.11) và lượt mỗi lần bấm (LC3.5) | baseline **0,33 ms**; ngưỡng chỉ bắt thoái hoá thảm khốc |
| PR3.3 | `build_prediction_body` < 300 ms | cùng tệp, 20 lần | không I/O |
| PR3.4 | mở tab không chậm quá +20% | đo tay trước/sau, ghi vào `code-summary.md` của U3 | không phải test |
| PR3.5 | ≤ 1 `read_report` + ≤ 1 `load_model` mỗi lần bấm | test với hàm giả lập đếm lời gọi | đọc mã cũng thấy |
| NFR1.1, NFR2.1 | 300 s / 240 s | test `slow` của U2 | U3 không đụng đường huấn luyện |

## 4. Rủi ro hiệu năng đã biết

| Rủi ro | Ảnh hưởng | Cách chặn |
|---|---|---|
| Đọc báo cáo hai lần mỗi lần bấm (một lần trong panel, một lần trong callback) | ~1 ms mỗi lần trên tệp vài chục KB | chấp nhận: đổi lấy tính đúng sau khi `--stage stats` ghi bản mới (PD3.1) |
| Nạp mô hình lần đầu trong tiến trình chậm hơn các lần sau do import `sklearn` | một lần ~0,5 s khi mở app | không tính vào PR3.2 (đo sau khi import); dashboard đã import `sklearn` từ trước |
| Dựng lại toàn bộ panel khi đổi tab | không tăng so với ba mục hiện có (một mục thêm) | PR3.4 |
| Log lỗi mô hình chứa đường dẫn dài | không ảnh hưởng thời gian; là vấn đề an ninh, xem `security-design.md` SD3.4 | — |
