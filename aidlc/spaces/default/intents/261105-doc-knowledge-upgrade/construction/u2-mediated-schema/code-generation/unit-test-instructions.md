# Unit Test Instructions — u2-mediated-schema

## 1. Khung kiểm thử

| Hạng mục | Giá trị |
|---|---|
| Khung | pytest 9.1.1 |
| Đo phủ | pytest-cov 7.1.0 |
| Cấu hình | `pytest.ini` (đã có): `testpaths = tests`, marker `slow`, `addopts = -ra` |
| Tệp test của đơn vị | `tests/unit/test_integration_schema.py` (mới) |
| Fixture | Tự dựng trong `tmp_path`: một tệp `mediated-schema.yaml` và vài tệp CSV nhỏ (chỉ vài dòng), **không** dùng `dataset/` |

## 2. Lệnh chạy của đơn vị (chính xác)

```
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_schema.py
```

- Chạy được **trước** vòng Red đầu tiên: pytest báo "no tests ran" chứ không lỗi cấu hình, nên vòng Red đầu tiên có ý nghĩa.
- Chỉ chạy tệp của đơn vị này. Không dùng lệnh toàn dự án (`pytest`, `pytest -m "not slow"`) trong tệp này: Build and Test chạy lệnh của từng đơn vị, lệnh không phạm vi sẽ lặp cả bộ.
- Kiểm lint/định dạng của đơn vị: `ruff check src/integration tests/unit/test_integration_schema.py` và `ruff format --check src/integration tests/unit/test_integration_schema.py`.

## 3. Mục tiêu độ phủ

- Ngưỡng của dự án là **80% dòng cho `src/`**, đo bằng `.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80`.
- **Build and Test đo ngưỡng đó trên toàn bộ bộ test của dự án lắp ráp**, không phải trên lệnh đơn vị ở §2. Chạy riêng tệp của đơn vị có thể trượt ngưỡng dù mọi test đã chọn đều xanh — đó không phải test hỏng, và không được hạ ngưỡng để cho qua.
- Mục tiêu của riêng đơn vị này: mọi nhánh của `schema.py` (L1–L4) và mọi kiểu trong `models.py` mà đơn vị này thêm đều có test đi qua; số hàm test dự kiến 22–26.

## 4. Hướng dẫn mock/stub

- Không mock hệ thống tệp: dựng tệp thật trong `tmp_path` bằng `write_text` cho YAML và `write_text` cho CSV. Đây là cách duy nhất kiểm được hành vi "chỉ đọc tiêu đề".
- Logger: dùng một lớp ghi lại trong bộ nhớ (list) thay cho `NullLogger` khi cần khẳng định sự kiện; khi kiểm SR-U2-7 thì **không** truyền logger và khẳng định không có gì được ghi.
- Không mock `TABLE_SPECS`: nó là hằng số thật của dự án; test dùng các `file_name` có thật (`olist_orders_dataset.csv`, …).
- Không gọi mạng, không gọi DuckDB, không đọc `dataset/` (NFR6.1, biên giới U2).

## 5. Quản lý dữ liệu test

- Mỗi test tự dựng thư mục tạm riêng; không có tệp fixture dùng chung trong `tests/`.
- Tệp CSV mẫu tối thiểu: một dòng tiêu đề + một dòng dữ liệu. Dòng dữ liệu cố ý chứa giá trị sai kiểu để chứng minh đơn vị không đọc nó.
- Tệp YAML mẫu phải khai đủ ba thực thể (`don_hang`, `mat_hang`, `san_pham`) trừ test chuyên về `partial`.
- Không có test `slow` trong đơn vị này: không cần dữ liệu thật.

## 6. Ghi chú về ngưỡng hiệu năng

Test NFR1.1 khẳng định `view.elapsed_ms` là số nguyên dương và `<= 2000` trên fixture nhỏ. Con số đó gần như luôn nhỏ hơn nhiều so với 2 giây, nên test chứng minh **cơ chế đo tồn tại và có cận trên**, không chứng minh hiệu năng thật. Giá trị thật chỉ có khi bên gọi chạy trên `dataset/`; ghi đúng như vậy trong `code-summary.md`, không tuyên bố đã đo hiệu năng thật.
