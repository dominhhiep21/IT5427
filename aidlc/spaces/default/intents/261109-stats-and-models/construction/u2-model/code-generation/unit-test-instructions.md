# Unit Test Instructions — u2-model

Nguồn: `code-generation-plan.md`, `../functional-design/rules.md`, `../nfr-requirements/tech-stack-decisions.md`, `## Testing Posture` trong `aidlc/spaces/default/memory/team.md`.

## Posture

**Methodology**: tdd. **Ordering**: mỗi lớp chạy được — viết test trước, thấy đỏ, rồi viết mã tới khi xanh.

## Bộ test và marker

Bộ nhanh: `python -X utf8 -m pytest -m "not slow"`. Bộ chậm: `-m slow`.

Mọi test mới **tự dựng dữ liệu trong `tmp_path`**. Không test nào đọc `data/reports/analysis.json` hay `warehouse/olist.duckdb` của repo (lỗ hổng `TD-09`).

## Phủ theo quy tắc

| Mã | Ca kiểm tối thiểu | Bộ |
|---|---|---|
| BR2.1 | Mọi dòng huấn luyện có `is_delivered = true`; cỡ mẫu 96.478; số trễ 7.826 | `slow` |
| BR2.1 (đơn vị) | Bảng mẫu có 1 đơn chưa giao → bị loại; tổng khác 96.478 → ngoại lệ | nhanh |
| BR2.2 | `train_end < test_start`; đơn đúng ngày cắt thuộc tập kiểm tra; `train_n + test_n` khớp | nhanh |
| BR2.3 | Danh sách 11 đặc trưng và tập 10 cột cấm rời nhau; **khung đặc trưng thật** chỉ chứa đúng 11 tên | nhanh |
| BR2.4 | Tham số cân trọng số lớp được truyền | nhanh |
| BR2.5 | Với bộ điểm số dựng sẵn, ngưỡng chọn đúng là điểm trên lưới có F1 lớn nhất; hoà chọn cao hơn | nhanh |
| BR2.6 | AUC 0,69 → `true`; 0,70 → `false` | nhanh |
| BR2.7 | `flagged + not_flagged != total` → ngoại lệ; `total != test_n` → ngoại lệ | nhanh |
| BR2.8 | Hàm dựng khối **không** mở tệp báo cáo; tầng `stats` ghép khối và giữ `stats` cũ | nhanh |
| BR2.9 | Số có đúng 4 chữ số; ngưỡng sau làm tròn vẫn trong (0,1) | nhanh |
| TS-6 | One-hot dùng phạm trù khớp trên **tập huấn luyện**; phạm trù chỉ có ở tập kiểm tra thành vector 0 | nhanh |
| TS-8 | Đơn không có dòng hàng / dòng thanh toán vẫn ở lại tập, không dòng nào bị bỏ | nhanh |
| TS-9 | Chuẩn hoá khớp trên tập huấn luyện; cảnh báo không hội tụ bị biến thành ngoại lệ | nhanh |
| NFR1.1 | Cả bước mô hình dưới 15 phút trên dữ liệu thật | `slow` |
| NFR1.3 | Hai lần chạy cho cùng `auc`, `threshold`, `precision`, `recall` | `slow` |
| NFR4.1 | `model.py` có trong danh sách `ruff format --check` của `ci.yml` | nhanh |

## Ca phải có cho mỗi tệp mới

- `model.py`: mỗi BR một ca, cộng hai ca rò rỉ nhãn (rời nhau, khung thật), cộng một ca tái lập.
- `service.py` (phần thêm): một ca happy path trên DuckDB tạm; một ca khẳng định câu SQL chỉ chạm view trong `VIEW_TABLES`.
- `stages.py` (nhánh `stats`): một ca khẳng định bước mô hình chạy sau bước thống kê và khối `stats` còn nguyên.

## Điều cấm

- Không `assert True`, không mock để test luôn xanh.
- Không hạ `--cov-fail-under`, không tách cổng sang bộ nhanh.
- Không thêm `per-file-ignores` mới.
- Không test nào gọi mạng.
- Không test nào ghi vào `data/reports/` của repo.
