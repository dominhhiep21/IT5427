# Test Results

Nguồn: lần chạy thật của lệnh nghiệm thu `python -X utf8 -m pytest --cov=src --cov-fail-under=80` ở lần nghiệm thu `u3-display` (2026-11-11T08:38:41Z → 08:43:26Z), cộng lần chạy bộ nhanh sau bản sửa cuối.

## Kết quả

| Bộ | Lệnh | Kết quả |
|---|---|---|
| Toàn bộ | `pytest --cov=src --cov-fail-under=80` | **537 passed**, exit 0, 281,85 s |
| Nhanh | `pytest -m "not slow"` | **525 passed**, 12 deselected, 18,62 s |
| Lint | `ruff check .` | All checks passed |
| Định dạng | `ruff format --check` trên tệp đã chạm | clean |

## Độ phủ

**92,45%** toàn `src/` (4.634 câu lệnh đo được, 350 chưa phủ). Cổng 80% đạt, không hạ ngưỡng.

Các tệp mới của đợt:

| Tệp | Phủ |
|---|---|
| `src/analytics/report.py` | 97% |
| `src/analytics/statistics.py` | 100% |
| `src/analytics/model.py` | 100% |
| `src/dashboard/analysis_tab.py` | 99% |

Dòng chưa phủ duy nhất ở `analysis_tab.py` là thân callback trong `register_callback` — chỉ chạy khi Dash phục vụ request thật. Đường mã tương đương đã phủ qua `render_analysis` và đã xác nhận chạy thật trên trình duyệt.

## Tồn đọng đã biết, không phải hồi quy

| Mục | Vì sao |
|---|---|
| `src/pipeline/stages.py` 56% | Nợ có từ trước; nhánh `stats` mới được phủ bởi test đơn vị và test `slow` |
| `src/pipeline/cli.py` 62% | Nợ có từ trước |
| `TD-09` — bộ nhanh cần `warehouse/` và `data/marts/` | Chưa chốt sửa trong đợt này |

## Kết luận

Ba đơn vị xanh trên cùng một lần chạy, không có test nào bị bỏ qua bằng marker, không ngưỡng nào bị nới.
