# Performance Test Results — intent `261111-model-feature-improvemen`

Nhật ký các lần đo, chạy trên máy phát triển (Windows, Python 3.13, `.venv`).

## 1. Lượt đo chính thức (2026-11-13)

| Lượt | Lệnh | Kết quả |
|---|---|---|
| P-1 | `pytest -m "not slow" -q` | 708 passed, 15 deselected, **25,24 s** |
| P-2 | `pytest --cov=src --cov-fail-under=80` | **723 passed**, phủ **92,71%**, **424,36 s** |
| P-3 | `pytest -m slow tests/integration/test_u2_model_end_to_end.py -q` | 1 passed, **27,33 s** (ngân sách `stats` 300 s, huấn luyện 240 s) |
| P-4 | `pytest -m slow tests/integration/test_u3_floor_end_to_end.py -q` | 1 passed, **25,15 s**; AUC 0,6482 vs baseline 0,5297 |
| P-5 | `pytest tests/unit/test_u3_prediction_section.py -k budget -q` | 3 passed; `score_item` **10,49 ms**, `load_model` **0,33 ms**, dựng khối **~2 ms** |
| P-6 | `pytest tests/unit/test_linkage_score.py -q` (chạy riêng, máy rảnh) | 16 passed, **11,11 s** (ngưỡng 60 s) |

## 2. Ca bất thường đã gặp

| Lần | Hiện tượng | Kết luận |
|---|---|---|
| Lượt `verify_intent.ps1` lần 1 của chặng C | `test_linkage_score.py::…under_sixty_seconds` đỏ: **69,6 s > 60 s** | máy chịu tải 59% (chính bộ test đang chạy); chạy riêng 11,11 s ⇒ không phải thoái hoá. **Không nới ngưỡng** |
| Lượt đo P-5 lần đầu | 2 test lỗi `TypeError` vì gọi helper sai chữ ký | sửa test, không sửa mã |

## 3. Khoảng trống

| Khoảng trống | Cách đóng |
|---|---|
| **PR3.4** (+20% thời gian mở tab) chưa có cặp số trước/sau | đo `render_analysis` bằng `time.perf_counter()` trên cây trước/sau thay đổi; ~10 phút, chưa làm |
| Không có p95/p99 cho lần bấm Dự đoán | chỉ có trung bình; với một người dùng, trung bình là đủ |
| Không có bộ nhớ đỉnh | không đo; khối dựng cây nhỏ, mô hình 4,8 KB |

## 4. Xu hướng qua ba đơn vị

| Mốc | Test | Phủ | Thời gian toàn bộ |
|---|---|---|---|
| U1 | 559 | 92,48% | — |
| U2 | 637 | 92,57% | — |
| U3 | **723** | **92,71%** | **424 s** |

Thời gian toàn bộ tăng chủ yếu vì thêm test `slow` dựng lại pipeline (U2 ~27 s, U3 ~25 s); phủ tăng nhẹ vì mô-đun mới có test riêng.
