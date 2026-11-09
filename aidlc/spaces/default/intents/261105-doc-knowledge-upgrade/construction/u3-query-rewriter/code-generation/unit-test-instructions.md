# Unit Test Instructions — u3-query-rewriter

## 1. Khung kiểm thử

| Hạng mục | Giá trị |
|---|---|
| Khung | pytest 9.1.1 |
| Đo phủ | pytest-cov 7.1.0 |
| Cấu hình | `pytest.ini` |
| Tệp test của đơn vị | `tests/unit/test_integration_rewrite.py`, `tests/unit/test_common_kpis.py` (mới) |
| Fixture | CSV nhỏ trong `tmp_path` + DuckDB trong bộ nhớ; không đọc `dataset/` trong unit test (trừ một test smoke đọc tệp cấu hình phát hành) |

## 2. Lệnh chạy

```
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_rewrite.py tests/unit/test_common_kpis.py
```

- Lint: `.venv\Scripts\python.exe -X utf8 -m ruff check src/integration/rewrite.py src/common/kpis.py src/integration/models.py src/common/exceptions.py src/integration/card.py tests/unit/test_integration_rewrite.py tests/unit/test_common_kpis.py`
- Định dạng: cùng danh sách với `ruff format --check`.

## 3. Mục tiêu độ phủ

- Ngưỡng dự án: **80% dòng cho `src/`**, đo bằng `pytest --cov=src --cov-fail-under=80` trên toàn bộ bộ test.
- Đơn vị: mọi nhánh của `rewrite.py` và `kpis.py` có test; dự kiến 28–34 hàm test.

## 4. Mock/stub

- Không mock DuckDB: dùng `duckdb.connect()` trong bộ nhớ và `register()` khung nhỏ.
- Không mock `src/analytics` trong unit test; test đối chiếu dùng một hàm tham chiếu nhỏ được tiêm vào (dependency injection qua tham số), còn phép so với analytics thật thuộc Build and Test.
- Không gọi mạng; không đọc `warehouse/`.

## 5. Dữ liệu test

- Mỗi test dựng CSV nhỏ riêng trong `tmp_path` với đủ cột ba mẫu cần, gồm một dòng giao trễ và một dòng thiếu ngày giao.
- Một test đọc chính `config/mediated-schema.yaml` để khẳng định bốn trường mới/cờ `loaded` đã có.

## 6. Ngưỡng hiệu năng

`elapsed_ms` chỉ đo phần SQL (BR3.8); phần nạp CSV đo riêng bằng `load_ms` và ghi vào log, không cộng vào ngưỡng. Bộ chậm ghi số thật cho cả hai, không đỏ khi chậm.

## 7. Test viết nhưng không chạy ở bước này

- Bộ `slow` (end-to-end, data-quality) chạy ở Build and Test cùng `--stage all`.
