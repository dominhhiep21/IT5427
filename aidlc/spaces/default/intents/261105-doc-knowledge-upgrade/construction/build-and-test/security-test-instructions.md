# Security Test Instructions

## 1. Kiểm soát phải giữ

| Mã | Kiểm soát | Cách kiểm |
|---|---|---|
| SR-U1-1 / SR-U6-x | Dashboard chỉ bind `127.0.0.1:8050` | đọc `config.yaml` và `src/dashboard/__main__.py`; không có `0.0.0.0` |
| SR-U2-x | `yaml.safe_load`, không `yaml.load` | rà `src/integration/schema.py`, `selector.py`, `card.py` |
| SR-U2-x | Định danh bảng/cột phải qua `checked_identifier` trước khi ghép SQL | test `test_integration_schema.py`, `security-design.md` ADR-U2-S2 |
| SR-U3-x | Không chèn SQL: giá trị truyền qua placeholder `?`; tên cột/bảng là hằng | rà `src/integration/rewrite.py` |
| SR-U4-x | Tệp kết quả ghép không chứa `customer_unique_id` | test đọc `data/integration/linkage-*.json` và khẳng định không có khoá mốc |
| SR-U5-x | Không đọc biến môi trường, không gọi mạng | `grep -r "os.environ" src/integration`; `grep -rE "urllib|requests|socket" src/integration src/linkage` |
| SR-U6-x | Không nhúng HTML người dùng nhập; mọi chuỗi hiển thị qua Dash component | rà `src/integration/tab.py` |
| Toàn bộ | Không bí mật trong mã hay `config.yaml` | `grep -riE "api[_-]?key|password|token|secret" src/ config.yaml` |

## 2. Lệnh kiểm

```powershell
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_schema.py -q
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_linkage_result.py -q
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_selector.py -q
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_rewrite.py -q
```

## 3. Rà tay bắt buộc trước phát hành

- **Egress**: ngoài lời gọi IBGE có điều kiện trong bước `integrate` (khi cache thiếu/hỏng hoặc có `--refresh-ibge`), không có lời gọi mạng nào. Dashboard không gọi mạng.
- **Dữ liệu gần định danh**: tệp ghép chứa `zip_prefix` (5 chữ số) — thu hẹp một người tới một khu vực nhỏ. Chấp nhận vì Olist là bộ công khai đã ẩn danh và tệp không rời máy; nếu sau này chia sẻ tệp, đây là chỗ phải xem lại trước.
- **`is_correct`**: cột này nói thẳng hai `customer_id` là cùng một người. Đây là mục đích của U4, được khai ở SR-U4-8; điều không được phép là tiết lộ thêm khoá mốc.
- **Nhật ký**: `integration.linkage.failed` ghi `message=str(exc)[:200]`, và một số thông điệp lỗi có thể nhúng mã bản ghi. Nếu cần chặt hơn, che `record_a`/`record_b` trước khi ghi.

## 4. Không áp dụng

Không có xác thực người dùng, không có phân quyền, không có dữ liệu cá nhân thật: hệ chạy local một người dùng, dữ liệu Olist công khai đã ẩn danh. Không cần kiểm thâm nhập, không cần quét phụ thuộc định kỳ trong đợt này.
