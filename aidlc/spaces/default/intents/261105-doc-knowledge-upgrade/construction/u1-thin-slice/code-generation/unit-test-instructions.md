# Unit Test Instructions — u1-thin-slice

## Framework và cấu hình

| Hạng mục | Giá trị |
|---|---|
| Test runner | `pytest` 9.1.1 (đã ghim trong `requirements.txt`) |
| Đo phủ | `pytest-cov` 7.1.0 (đã ghim) |
| Cấu hình | `pytest.ini` hiện có: `testpaths = tests`, marker `slow`. **Không sửa** `pytest.ini` trừ khi buộc; nếu buộc thì ghi lý do vào `code-summary.md` |
| Marker | `-m "not slow"` = bộ nhanh; `-m slow` = bộ cần dữ liệu thật hoặc sinh ra |
| Thư mục test của đơn vị này | `tests/unit/` |

## Lệnh chạy của đơn vị (đúng bộ tệp, không chạy cả repo)

Chạy từ gốc repo:

```
python -X utf8 -m pytest tests/unit/test_integration_model.py tests/unit/test_integration_load.py tests/unit/test_integration_query.py tests/unit/test_integration_card.py tests/unit/test_log_pruning.py tests/unit/test_dashboard_smoke.py -m "not slow"
```

Đây là lệnh dùng cho mọi vòng Đỏ → Xanh → Refactor. Năm tệp đầu là của đơn vị này (bốn tệp theo lớp cộng `test_log_pruning.py` cho hàm dọn nhật ký); `test_dashboard_smoke.py` được thêm vào vì đơn vị này **sửa hình dạng dashboard** và NFR5.3 buộc cập nhật nó trong cùng thay đổi.

**Revision 2 — cổng đúng đắn dữ liệu (NFR5.5).** Tệp `tests/unit/test_integration_correctness.py` thuộc bộ chậm vì đọc dữ liệu thật:

```
python -X utf8 -m pytest tests/unit/test_integration_correctness.py -m slow
```

Tệp này tính lại số đơn theo `(tháng, trạng thái)` **độc lập bằng pandas từ `dataset/olist_orders_dataset.csv`** rồi so với `run_monthly_orders` của lát cắt: từng nhóm và tổng toàn kỳ, sai lệch 0. Nó là cổng đúng đắn duy nhất của lát cắt, nên chạy nó trước khi coi đơn vị là xong — kể cả khi bộ nhanh đã xanh.

Chạy riêng một lớp khi đang ở vòng Đỏ của lớp đó (ví dụ lớp data model):

```
python -X utf8 -m pytest tests/unit/test_integration_model.py -m "not slow"
```

**Điều kiện trước:** `tests/unit/test_dashboard_smoke.py` gọi `load_config()` nên cần `warehouse/olist.duckdb` và `data/marts/` đã tồn tại (nợ `TD-09`, cả hai bị `.gitignore`). Trên máy mới clone, chạy `python -X utf8 -m src.pipeline run --stage all` một lần trước. Không sửa test đó để nó bỏ qua bước này, và không hạ ngưỡng nào để né.

## Ngưỡng phủ

| Hạng mục | Giá trị |
|---|---|
| Ngưỡng đặt ra cho `src/` | **80% dòng** (NFR2.1, luật dự án) |
| Ai đo ngưỡng này | Build and Test đo trên **toàn bộ** bộ test của dự án đã lắp ráp; lệnh unit-scoped ở trên **không** phán ngưỡng này, vì chạy riêng test của một đơn vị có thể thiếu phần phủ do đơn vị khác cung cấp |
| Lệnh đo khi cần xem trước | `python -X utf8 -m pytest --cov=src --cov-report=term-missing` (không kèm `--cov-fail-under`) |
| Lệnh đo có cổng (đứng riêng, không có bước nào sau nó) | `python -X utf8 -m pytest --cov=src --cov-fail-under=80` |

Nếu lệnh có cổng thoát khác 0 **chỉ vì ngưỡng** trong khi mọi test được chọn đều xanh, ghi lại đúng như vậy cùng kết quả test của đơn vị — đó không phải test hỏng.

## Mock/stub

| Thành phần | Cách xử lý |
|---|---|
| `time.sleep` trong vòng thử lại | `monkeypatch.setattr("time.sleep", lambda _: None)` để test không chậm thật |
| Lỗi đọc tệp lần đầu | Tiêm bằng `monkeypatch` trên hàm đọc, trả lỗi ở lần gọi 1 và dữ liệu ở lần 2; khẳng định đúng **hai** lần gọi |
| DuckDB | Không mock: dùng `duckdb.connect()` in-memory thật với DataFrame nhỏ — đây là ranh giới thật của đơn vị và mock nó sẽ che lỗi SQL |
| Đồng hồ / thời gian chạy | Không mock `perf_counter`; test hiệu năng đo thật với ngưỡng 2.000 ms |
| Mạng | Không có lời gọi mạng nào trong đơn vị này; nếu một test cố gọi mạng thì đó là lỗi thiết kế test |
| Dashboard | Gọi thẳng `build_integration_card(...)` với `QueryRunResult` dựng tay; không khởi động server |

## Dữ liệu test

- Không đọc `dataset/` thật trong unit test, **trừ đúng một ngoại lệ có chủ đích**: `tests/unit/test_integration_correctness.py` (NFR5.5) đọc `dataset/olist_orders_dataset.csv` để làm phép tính độc lập, và vì vậy nó mang marker `slow`. Mọi test khác dựng CSV nhỏ trong `tmp_path` (5–20 dòng) với đúng tiêu đề của bảng nguồn.
- Tệp lược đồ dùng trong test: bản rút gọn viết vào `tmp_path`, có đủ năm trường và `loaded` đúng như `config/mediated-schema.yaml`.
- Bốn ca dữ liệu tối thiểu phải có: (1) vài dòng hợp lệ; (2) một `ma_don` trùng; (3) một `ngay_dat` rỗng; (4) một `trang_thai` ngoài tám giá trị.
- Test độ phủ tương tác bàn phím dùng cây Dash trả về và kiểm thuộc tính, không dựng trình duyệt.

## Bộ test chậm

Bộ `slow` không chạy trong CI (`cicd-pipeline.md` §1). Nó chạy ở lần xác nhận trước khi phát hành và ở lệnh xác nhận của cổng nghiệm thu (`pytest --cov=src --cov-fail-under=80`, không lọc marker). Ở đơn vị này bộ `slow` **có** một thành viên bắt buộc: `tests/unit/test_integration_correctness.py` — cổng đúng đắn NFR5.5. Nếu tệp đó chưa chạy, `code-summary.md` phải ghi rõ "chưa chạy", không được coi là đã xong.
