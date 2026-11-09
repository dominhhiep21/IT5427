# Security Requirements — u6-integration-ui

Nguồn: `functional-design/functional-spec.md`, `functional-design/rules.md` (BR6.1–BR6.12), `inception/requirements-analysis/requirements.md` (NFR4, NFR6, C1–C6, OS5), `inception/contract-design/contract-summary.md`.

## 1. Yêu cầu dẫn xuất

| Mã | Yêu cầu | Cách đáp ứng | Đo bằng |
|---|---|---|---|
| SR-U6-1 | Dashboard chỉ bind `127.0.0.1`, không mở ra mạng | Giữ nguyên cấu hình `config.yaml` hiện có | Rà `config.yaml`; không đổi host |
| SR-U6-2 | Không xác thực, không phân quyền (OS5 ngoài phạm vi) | Không thêm đăng nhập; ghi rõ ở §3 | Rà mã: không form đăng nhập |
| SR-U6-3 | Không bí mật trong mã hay layout | Không token, không API key | Rà mã |
| SR-U6-4 | **Không hiển thị traceback hay thông điệp nội bộ** | BR6.5: bắt đủ lỗi của C3–C7, dựng câu tiếng Việt | Test: lỗi giả → màn hình chỉ có câu tiếng Việt |
| SR-U6-5 | Không chèn HTML từ dữ liệu | Mọi chuỗi từ hợp đồng đi qua `html.Td(str(...))`/text, không `dangerously_allow_html` | Rà mã: không `dangerously_allow_html` |
| SR-U6-6 | Không gọi mạng ngoài tiến trình | Chỉ gọi U3/U5/U2/U4 trong tiến trình | Rà mã: không `requests`, `urllib` |
| SR-U6-7 | Không lộ dữ liệu cá nhân ngoài phạm vi | Màn hình chỉ hiện danh mục, tháng, bang, mã đơn; không hiện tên/địa chỉ khách | Rà màn hình + mẫu dữ liệu |
| SR-U6-8 | Ba tab cũ không bị ảnh hưởng, và tab mới không đọc hợp đồng lúc dựng layout | Tab mới đọc C5/C6/C7 **bên trong callback**, không đọc khi dựng `app.layout`: một hợp đồng lỗi lúc khởi động sẽ không làm hỏng cả bốn tab. Callback và `id` riêng; ba tab cũ giữ nguyên 2 callback | Test: dựng layout khi C5/C6/C7 đều không có vẫn xanh; `test_dashboard_smoke.py` khẳng định 2 callback cũ + **6** callback mới = **8** |
| SR-U6-9 | Chỉ dùng **một** gói UI: `dash-mantine-components`, đã ghim phiên bản | FR5.4 buộc dùng DMC; gói **đã có** trong `requirements.txt` với `dash-mantine-components==2.8.1` và đã cài trong `.venv`. Giữ nguyên bản 2.8.1 — bản 3.x đòi `dash>=4.5.0` còn repo ghim `dash==4.4.1`. Không thêm gói UI nào khác | `requirements.txt` vẫn đúng một dòng DMC; `pip show dash-mantine-components` trả `2.8.1` |

## 2. Mối đe doạ đã cân nhắc

| Mối đe doạ | Đánh giá | Kiểm soát |
|---|---|---|
| Rò rỉ thông tin qua thông báo lỗi | Có thật — lỗi hợp đồng có thể chứa đường dẫn | SR-U6-4 |
| Chèn HTML qua chuỗi lý do/coverage | Thấp — chuỗi do hệ thống sinh | SR-U6-5 |
| Người khác trong cùng máy mở dashboard | Chấp nhận — bind localhost, không đăng nhập (OS5) | SR-U6-1, SR-U6-2 |
| Tab mới làm hỏng ba tab cũ | Có thật — cùng `app.layout` | SR-U6-8 |

## 3. Không áp dụng

- **Xác thực/phân quyền**: ngoài phạm vi (OS5).
- **Mã hoá khi truyền**: không có kênh mạng.
- **Tuân thủ dữ liệu cá nhân**: không hiển thị PII (SR-U6-7).
