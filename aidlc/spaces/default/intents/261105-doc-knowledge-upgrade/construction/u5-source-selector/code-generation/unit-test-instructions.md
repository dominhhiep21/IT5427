# Unit Test Instructions — u5-source-selector

## 1. Khung kiểm thử

| Hạng mục | Giá trị |
|---|---|
| Khung | pytest 9.1.1 |
| Đo phủ | pytest-cov 7.1.0 |
| Cấu hình | `pytest.ini` (đã có): `testpaths = tests`, marker `slow`, `addopts = -ra` |
| Tệp test của đơn vị | `tests/unit/test_integration_selector.py` (mới) |
| Fixture | Tự dựng trong `tmp_path`: một tệp `integration-sources.yaml` nhỏ và một `MediatedFieldCatalogue` dựng tay; **không** dùng `dataset/` |

## 2. Lệnh chạy của đơn vị (chính xác)

```
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_selector.py
```

- Chạy được **trước** vòng Red đầu tiên: pytest báo "no tests ran" chứ không lỗi cấu hình.
- Ngưỡng phủ riêng của mô-đun (dùng cho cổng NFR2.2): `.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_selector.py --cov=src.integration.selector --cov-fail-under=90`.
- Kiểm lint/định dạng của đơn vị: `.venv\Scripts\python.exe -X utf8 -m ruff check src/integration/selector.py src/integration/models.py src/common/exceptions.py src/config.py tests/unit/test_integration_selector.py` và cùng danh sách với `ruff format --check`.

## 3. Mục tiêu độ phủ

- Ngưỡng của dự án là **80% dòng cho `src/`**, đo bằng `.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80` trên **toàn bộ** bộ test (nhanh + `slow`), đúng `team.md` và `verification-command.txt`.
- **Build and Test đo ngưỡng đó trên toàn bộ bộ test của dự án lắp ráp**, không phải trên lệnh đơn vị ở §2.
- Mục tiêu của riêng đơn vị này: mọi nhánh của `selector.py` (L1–L5) và mọi kiểu trong `models.py` mà đơn vị này thêm đều có test đi qua; số hàm test dự kiến 20–26.

## 4. Hướng dẫn mock/stub

- Không mock hệ thống tệp: dựng tệp YAML thật trong `tmp_path` bằng `write_text`.
- `MediatedFieldCatalogue` dựng tay từ `src/integration/models.py` với đúng các mã `entity.field` mà fixture cần — không đọc `config/mediated-schema.yaml` trong unit test (trừ đúng một test đọc tệp cấu hình đang phát hành, và test đó cũng chỉ đọc tệp cấu hình nguồn, không đọc CSV).
- Logger: dùng lớp ghi lại trong bộ nhớ khi cần khẳng định sự kiện; khi kiểm mặc định không ghi thì **không** truyền logger và khẳng định không có đầu ra.
- Không mock `SOURCE_TABLES`: đó là hằng thật của dự án; test dùng tên thật (`olist_orders_dataset`, …) và một tên sai (`olist_khong_ton_tai`).
- Không gọi mạng, không gọi DuckDB, không đọc `dataset/` (NFR6.1, biên giới U5).

## 5. Quản lý dữ liệu test

- Mỗi test tự dựng thư mục tạm riêng; không có tệp fixture dùng chung trong `tests/`.
- Tệp YAML mẫu khai đủ ba nguồn và ba ánh xạ truy vấn; test chuyên về lỗi thì sửa đúng một chỗ trong chuỗi mẫu.
- Một test đọc **chính** `config/integration-sources.yaml` đã commit (không dùng `tmp_path`) để chứng minh tệp phát hành nạp được.
- Không có test `slow` trong đơn vị này: không cần dữ liệu thật.

## 6. Ghi chú về ngưỡng hiệu năng

NFR1.1 đo bằng `time.perf_counter()` bọc quanh `load_source_catalogue` và `select_source` trong test, khẳng định mỗi lần `<= 2000` ms trên fixture nhỏ. Con số đó chứng minh **cơ chế và cận trên**, không chứng minh hiệu năng thật; không thêm trường đo vào C3/C7 (hợp đồng không có `elapsed_ms`).

## 7. Test viết nhưng không chạy ở bước này

- Bộ `slow` của dự án (end-to-end + data-quality baseline) **không** chạy ở bước này — thuộc Build and Test.
- Lệnh xác nhận đầy đủ của đơn vị (`cicd-pipeline.md` §4) mới chạy được các bước lint/test/smoke; bước `src.pipeline run --stage all` chạy khi Build and Test xác nhận toàn bộ.
