# Unit Test Instructions — u3-prediction-ui

Chiến lược **Standard** (5–8 test mỗi thành phần) + sàn phủ 80% của scope `feature`. Phương pháp **TDD** (đỏ → xanh → refactor) theo `team.md` `## Testing Posture`.

## Lệnh, chính xác

Ba tệp test của đơn vị:

```
python -X utf8 -m pytest tests/unit/test_u3_prediction_section.py tests/unit/test_dashboard_analysis_tab.py tests/unit/test_dashboard_smoke.py -q
```

Bộ nhanh (trước mỗi điểm dừng chặng):

```
python -X utf8 -m pytest -m "not slow" -q
```

Test `slow` của đơn vị (gần cuối, sau khi `--stage stats` đã sinh tệp thật):

```
python -X utf8 -m pytest -m slow tests/integration/test_u3_floor_end_to_end.py -q
```

Cổng phủ (không hạ ngưỡng):

```
python -X utf8 -m pytest --cov=src --cov-fail-under=80
```

## Tệp test phải có

| Tệp | Lớp | Số test | Khẳng định gì |
|---|---|---|---|
| `tests/unit/test_u3_prediction_section.py` | logic giao diện | 74 | `len(STATE_CODES) == 27`; `len(PAYMENT_TYPES) == 5`; `TEXTS3` caption nêu "dòng hàng"; `validate_form` 9 luật (bang lạ, ngày sai, giá âm/không phải số, số món 0, trả góp 0, ngày âm, ngày > 365, thanh toán lạ) + không lỗi khi hợp lệ; `build_prediction_body` có **10** thành phần cho **11** giá trị, bốn trường mặc định đúng và sửa được; `chua-chay` không có chữ số; `mo-hinh-chua-san` chứa hai nguyên văn và nút `disabled`; cây con kết quả không chứa `workspace_root`/`\`; `build_outcome_view` ba đóng góp + nhãn log-odds + nhãn tiếng Việt; tất định hai lần gọi; lỗi tại ô ⇒ không gọi `score_item`; mỗi lần bấm ≤ 1 `read_report` + ≤ 1 `load_model` |
| `tests/unit/test_dashboard_analysis_tab.py` (sửa) | hình dạng | +3/−1 | `SECTION_IDS` bốn mục đúng thứ tự; mục Dự đoán là `H3`; không `aria-live` thứ hai; không thẻ tóm tắt thứ năm; `_auc_note` chỉ đọc cờ (nhãn đổi khi `AUC_TARGET` đổi); **xoá** test dự phòng `auc < AUC_TARGET`; nhãn grain "dòng hàng"; `model_caption` không còn "chỉ đọc" |
| `tests/unit/test_dashboard_smoke.py` (sửa) | hình dạng | +1 | `len(app.callback_map) == 10`; `build_dashboard_outputs` vẫn trả **9** |
| `tests/unit/test_analysis_tab_contrast.py` (sửa) | a11y | +1 | `.field-error` tồn tại trong `assets/style.css` và dùng `var(--text-2)` |
| `tests/integration/test_u3_end_to_end.py` (sửa) | end-to-end | +0/−0 | 5 tab, 10 callback; bỏ chỗ ghim chuỗi "0,70"; panel thật dựng được từ báo cáo thật |
| `tests/integration/test_u3_floor_end_to_end.py` (mới, `slow`) | cổng | 1 | `run_stage(config, "stats")` rồi `beats_floor(model.auc, model.baseline_auc) is True` trên **tệp thật** |

Tổng: **74 test** trong tệp mới + 1 test `slow`; `beats_floor` hai nhánh đã có ở `test_analytics_baseline_block.py` (không tạo tệp trùng).

## Mốc

- Baseline trước khi tạo tệp (bước 1 của kế hoạch): `.\.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow" -q`
  → **623 passed, 14 deselected** (47,01 s).
- `python` toàn cục của máy **không** có `pytest`, nên mọi lệnh ở trên chạy bằng Python của `.venv`;
  chi tiết và số đo từng bước Red/Green ghi ở `code-summary.md` §Chặng A.

## Ràng buộc

- **TDD thật:** mỗi bước Red phải chạy và **thấy đỏ** trước khi viết mã; ghi lệnh + kết quả đỏ vào `code-summary.md`.
- **Không khẳng định một giá trị AUC cụ thể** làm kỳ vọng (`project.md` `## Forbidden`). Test `slow` của mốc sàn là **ngoại lệ có chủ đích** (NFR5) và phải được ghi qua nghi thức learnings vào `project.md` `## Corrections` trước khi đóng intent.
- **Không dựa vào `warehouse/`/`data/marts/`** trong bộ nhanh (`TD-09`): dựng báo cáo và mô hình trong `tmp_path` bằng `write_report`/`save_model`. Chỉ test `slow` chạm `dataset/`.
- **Không import `requests`/`numpy`**; chỉ `dash`, `dash_mantine_components`, `pandas`.
- Test hình dạng **phải sửa trong cùng thay đổi** với mã (10 callback, 4 mục, 5 tab, `build_dashboard_outputs` giữ 9).
- Mọi lệnh `python -X utf8`.
