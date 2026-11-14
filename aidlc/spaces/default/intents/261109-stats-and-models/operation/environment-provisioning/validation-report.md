# Validation Report

Nguồn: `environment-inventory.md`, `../deployment-pipeline/rollback-runbook.md`, `../../construction/build-and-test/test-results.md`, `../../construction/ci-pipeline/quality-gates.md`.

## Xác nhận môi trường

Chạy từ trạng thái hiện tại, đúng thứ tự bốn bước:

| Bước | Lệnh | Kết quả |
|---|---|---|
| 1 | `pytest -m "not slow"` | 525 passed, 12 deselected |
| 2 | `run --stage all` | success; `QualityGate` + `KpiReconciler` xanh |
| 3 | `run --stage stats` | success; báo cáo `day-du` |
| 4 | mở dashboard | 5 tab; tab kết quả hiện đủ ba khối ở 1280px |

Bộ đầy đủ: **537 passed**, phủ **92,45%**, `ruff` sạch.

## Kiểm từng thành phần kiểm kê

| # | Kiểm gì | Kết quả |
|---|---|---|
| E1 | `python --version` trong `.venv` | 3.13 |
| E2 | `pip show scipy scikit-learn numpy` | `scipy 1.15.2`, `scikit-learn 1.6.1`, `numpy 2.2.1` — **không bị nâng** |
| E3 | `dataset/` không đổi | không tệp nào bị sửa trong đợt |
| E4 | `data/` được sinh đủ | cleaned, marts, reports có mặt |
| E5 | `warehouse/olist.duckdb` | mở được, 11 view |
| E6 | `logs/` | JSONL mỗi lần chạy, có `run_id` |
| E7 | 11 thư mục do `load_config` tạo | có, gồm `inbox/` và `dataset/external/ibge/` |
| E8 | dashboard bind đúng cổng | `127.0.0.1:8050` |
| E9 | CI | workflow chạy trên ba nhánh khai tay |

## Điều xác nhận là **chưa** đạt

| Mục | Trạng thái |
|---|---|
| AUC ≥ 0,70 | **không đạt** — 0,5133, ghi bằng `auc_below_target = true` và hiện trên tab |
| NFR1.2, NFR1.4, NFR1.6 | chưa có phép đo, đánh `Deferred` |
| NFR1.5 | giả định, không kiểm được vì `dataset/` chỉ một cỡ |
| `TD-09` | bộ nhanh vẫn cần `warehouse/` và `data/marts/` |

## Kết luận

Môi trường đủ để chạy và đã chạy thật. Bốn mục chưa đạt ở trên là **giới hạn đã biết**, không phải môi trường hỏng — và mỗi mục đều có chỗ ghi trong record thay vì bị ẩn đi.
