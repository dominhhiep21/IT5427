# Unit Test Instructions — u2-features-and-models

Chiến lược **Standard** (5–8 test mỗi thành phần) + sàn phủ 80% của scope `feature`. Phương pháp **TDD** (đỏ → xanh → refactor) theo `team.md` `## Testing Posture`.

## Lệnh, chính xác

```
python -X utf8 -m pytest tests/unit/test_analytics_training_frame.py tests/unit/test_analytics_features.py tests/unit/test_analytics_split.py tests/unit/test_analytics_threshold.py tests/unit/test_analytics_baseline_block.py tests/unit/test_analytics_report_v3.py tests/unit/test_analytics_persistence.py tests/unit/test_analytics_score_item.py -q
```

Bộ nhanh:

```
python -X utf8 -m pytest -m "not slow" -q
```

Test `slow` của đơn vị:

```
python -X utf8 -m pytest -m slow tests/integration/test_u2_model_end_to_end.py -q
```

Cổng phủ (không hạ ngưỡng):

```
python -X utf8 -m pytest --cov=src --cov-fail-under=80
```

## Tệp test phải có

| Tệp | Lớp | Số test | Khẳng định gì |
|---|---|---|---|
| `test_analytics_training_frame.py` | truy cập dữ liệu | 8 | một dòng mỗi `(order_id, order_item_id)`; `order_id` **không** duy nhất; có `seller_state`, `handling_days`, `approval_days`; bốn bộ đếm 110195/96476/8713/2 trên mart tạm; hai cột ngày null khi mốc null; không lọc dòng |
| `test_analytics_features.py` | logic | 8 | đúng 14 tên theo thứ tự; 6+6+2; `forbidden` có hai cột mốc thô; `validate_features` ném khi lệch tên/thứ tự; thứ tự mã hoá `numeric → flags → one-hot`; `feature_names` = cột ma trận đã mở rộng |
| `test_analytics_split.py` | logic | 6 | chia theo `order_id`; giao rỗng; dòng hàng của một đơn cùng phía; đơn đúng mốc thuộc tập kiểm tra; một phía rỗng ⇒ `ModelError`; `split_summary` đếm dòng hàng |
| `test_analytics_threshold.py` | logic | 6 | ngưỡng thuộc lưới; ngoài (0,1) ⇒ `ModelError`; precision/recall trên tập kiểm tra; làm tròn 4 chữ số; ngưỡng là nguồn duy nhất |
| `test_analytics_baseline_block.py` | logic | 7 | baseline gọi hàm U1 với `SPLIT_DATE`; `beats_baseline` khớp phép so trên giá trị đã làm tròn; `auc_below_target` khớp `auc < AUC_TARGET`; `counts` chín khoá; `flagged + not_flagged == total == split["test_n"]`; `beats_floor` hai nhánh; floor ngoài (0,1) ⇒ `ModelError` |
| `test_analytics_report_v3.py` | hợp đồng | 8 | `REPORT_VERSION == 3`; 11 trường; `split` sáu khoá v2; chín khoá `counts`; đọc v2 ⇒ `loi`; thiếu trường mới ⇒ `loi`; `assemble_report` giữ khối cũ; một đường dựng duy nhất (ADR-008) |
| `test_analytics_persistence.py` | lưu trữ | 7 | ghi rồi nạp khớp `feature_names`/`categories`/`scaler`; vắng tệp ⇒ `None`; tệp rác ⇒ `ModelError`; metadata có `trained_at`/`library_versions`; không khớp lại lúc nạp; đường dẫn từ tham số `models_dir`; không ghi ngoài thư mục |
| `test_analytics_score_item.py` | logic | 8 | xác suất trong [0,1]; **ba** đóng góp gộp theo trường, không hai dòng cùng trường; tất định; thiếu trường ⇒ `ModelError` nêu tên; so **toàn bộ** danh sách cột; `verdict` theo ngưỡng đọc từ báo cáo; 11 khoá đầu vào; không dùng cột cấm |
| `tests/integration/test_u2_model_end_to_end.py` (viết lại) | end-to-end (`slow`) | 6 | 110.195/96.476/8.713/2; `auc > baseline_auc`; `auc_tree` giống nhau qua hai lần chạy; báo cáo v3 với 11 trường; tệp mô hình nạp lại và chấm được; `counts` chín khoá |

Tổng: **78 test đơn vị** + **1 test `slow`**.

## Ràng buộc

- **TDD thật:** mỗi bước Red phải chạy và **thấy đỏ** trước khi viết mã; ghi lệnh + kết quả đỏ vào `code-summary.md`.
- **Không khẳng định một giá trị AUC cụ thể** làm kỳ vọng (`project.md`); chỉ khẳng định hành vi (miền giá trị, thứ tự, tất định, các nhánh lỗi). Mốc sàn là cổng chống thoái hoá so với mốc đã báo cáo, và việc ghi ngoại lệ này thuộc cổng learnings.
- **Không dựa vào `warehouse/`/`data/marts/`** trong bộ nhanh (`TD-09`) — dựng mart tạm bằng SQL trong `tmp_path`.
- **Không import `numpy`** trực tiếp; dùng `pandas` và `random`.
- Không hạ `--cov-fail-under`, không `per-file-ignores` mới; tệp mới vào `ci.yml:35` **và** `NEW_FILES` **cùng lúc**.
- Mọi lệnh `python -X utf8`.

## Điều kiện coi là xong

1. Tám tệp test đơn vị xanh, phủ đủ các nhánh lỗi ở bảng.
2. `test_u2_model_end_to_end.py` xanh trên `dataset/` thật, trong ngân sách 300 s tầng và 240 s bước mô hình.
3. Bộ nhanh xanh (không hồi quy, kể cả test cũ của đơn vị khác).
4. `ruff check .` và `ruff format --check` sạch.
5. Cổng phủ 80% xanh trên toàn bộ bộ test.
