# Unit Test Instructions — u1-statistics

Nguồn: `code-generation-plan.md`, `../functional-design/rules.md`, `../nfr-requirements/reliability-requirements.md`, `## Testing Posture` trong `aidlc/spaces/default/memory/team.md`.

## Posture

**Methodology**: tdd. **Ordering**: với mỗi lớp chạy được, viết test trước cho hành vi mong đợi, chạy thấy đỏ, rồi viết mã tới khi xanh, rồi mới sang lớp kế.

## Bộ test và marker

Bộ nhanh: `python -X utf8 -m pytest -m "not slow"`. Bộ chậm: `-m slow`, cần `data/` và `warehouse/` đã sinh.

Mọi test mới **tự dựng dữ liệu của mình** trong `tmp_path`. Không test nào đọc `data/reports/analysis.json` hay `warehouse/olist.duckdb` của repo — nếu không, bộ nhanh lại phụ thuộc môi trường như `TD-09`.

## Phủ theo quy tắc

| Mã | Ca kiểm tối thiểu | Bộ |
|---|---|---|
| BR1.1 | Tỉ lệ và khoảng Wilson khớp phép tính độc lập trên dữ liệu mẫu; `total = 0` thì dừng tầng | nhanh |
| BR1.2 | Bang dưới 100 đơn không vào `comparisons`; `excluded` bằng tổng đơn của chúng; dưới hai bang đủ điều kiện thì `[]` + một `SkipEntry` | nhanh |
| BR1.3 | `n` đúng; `n = 3` trả `null` + `SkipEntry`; khoảng tin cậy chứa `r` | nhanh |
| BR1.4 | Ô kỳ vọng nhỏ nhất dưới 5 thì `null` + `SkipEntry`; `dof = số vùng - 1` | nhanh |
| BR1.5 | Trục tháng liên tục, điền 0; dưới 24 tháng thì `null`; hằng đẳng thức `observed = trend + seasonal + residual` đúng trên giá trị **chưa** làm tròn | nhanh |
| BR1.6 | `skipped` có đúng một dòng mỗi phép bị bỏ, không trùng tên | nhanh |
| BR1.7 | `confidence == 1 - alpha` | nhanh |
| BR1.8 | Số trong tệp ghi ra có đúng số chữ số đã chốt | nhanh |
| BR1.9 | Sáu mẫu: không tồn tại → `rong`; không parse được → `loi`; sai phiên bản → `loi`; thiếu trường → `loi`; sai kiểu → `loi`; đủ khối → `day-du` | nhanh |
| BR1.10 | Tệp `version = 1` trả `loi` và thông điệp nêu việc chạy lại, **kiểm trước** nhánh thiếu trường | nhanh |
| BR1.11 | Tệp tạm bị làm hỏng sau khi ghi thì tệp cũ còn nguyên và có ngoại lệ | nhanh |
| NFR2.1 | Không có test trivially-true; mỗi nhánh `loi` của BR1.9 có ít nhất một mẫu | nhanh |
| NFR1.1 | Tầng `stats` trên dữ liệu thật dưới 5 phút | `slow` |
| NFR1.3 | Bộ nhớ đỉnh qua `MemoryProbe` dưới `quality.memory_fail_mb` | `slow` |
| NFR3.4 | Hai lần chạy liên tiếp cho tệp giống nhau sau khi bỏ `generated_at` | `slow` |
| NFR4.2 | `ci.yml` có nhánh trong cả hai danh sách và có mọi tệp mới trong danh sách ruff | nhanh |
| FR5.1 | `stats` có trong `STAGES` **và** trong `choices` của `--stage`; CLI vẫn 3 lệnh con | nhanh |

## Ca phải có cho mỗi tệp mới

- `report.py`: sáu mẫu đọc, một ca ghi thành công, một ca ghi thất bại giữa chừng.
- `statistics.py`: năm ca happy path cộng ít nhất hai ca nhánh bỏ qua.
- `service.py` (phần thêm): mỗi phương thức mới một ca happy path trên DuckDB tạm; một ca khẳng định câu SQL chỉ chạm view trong `VIEW_TABLES`.
- `pipeline/stages.py` và `cli.py`: một ca cho danh sách tầng, một ca cho `choices`.

## Điều cấm

- Không có `assert True`, không mock để test luôn xanh.
- Không hạ `--cov-fail-under`, không tách cổng sang bộ nhanh.
- Không thêm `per-file-ignores` mới.
- Không test nào gọi mạng.
