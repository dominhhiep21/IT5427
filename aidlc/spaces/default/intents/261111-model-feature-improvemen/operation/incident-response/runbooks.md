# Runbooks — intent `261111-model-feature-improvemen`

Chỉ những sự cố **thật sự xảy ra được** trên một máy local, không có dịch vụ nền. Mỗi runbook: dấu hiệu → kiểm → sửa → xác nhận.

## RB-1 — Báo cáo ở trạng thái `loi`

**Dấu hiệu:** tab phân tích không có mục Dự đoán, hiện lý do và đường dẫn tệp.

1. Đọc `data/reports/analysis.json` — lỗi hình dạng nghĩa là tệp không đúng hợp đồng v3.
2. Chạy `python -X utf8 -m src.pipeline run --stage stats`.
3. Nếu vẫn `loi`: xoá `data/reports/analysis.json` rồi chạy lại bước 2.
4. Xác nhận: `data/reports/analysis.json` có `"version": 3`, khối `model` đủ 11 trường, `counts` đủ 9 khoá.

## RB-2 — Khối Dự đoán báo "mô hình chưa sẵn"

**Dấu hiệu:** câu hướng dẫn chứa `data/models/` và lệnh `--stage stats`, nút bị tắt.

1. Kiểm `data/models/` có `logistic.pkl` chưa. Trên máy mới clone thì **chưa có** — đây là trạng thái bình thường.
2. Chạy `python -X utf8 -m src.pipeline run --stage stats`.
3. Nếu tệp có mà vẫn báo lỗi: đọc `logs/` tìm `prediction.model_unavailable` — thông điệp thô ở đó (giao diện cố ý không hiện đường dẫn).
4. Xác nhận: mở lại tab, nút bật, bấm Dự đoán ra xác suất.

## RB-3 — Pipeline đỏ ở `QualityGate` hoặc `KpiReconciler`

**Dấu hiệu:** `run --stage all` trả mã thoát 1; CLI in check nào hỏng.

1. Đọc `data/reports/quality-report.json` và `kpi-reconciliation.json` — check nào đỏ.
2. Nếu số dòng bảng lệch: kiểm `dataset/` có bị sửa không (`git status dataset/` phải sạch).
3. Nếu KPI lệch: **không** cập nhật baseline để cho xanh; tìm nguyên nhân ở tầng clean/integrate.
4. Xác nhận: chạy lại `--stage all`, hai cổng xanh.

## RB-4 — Cổng phủ CI đỏ

**Dấu hiệu:** `pytest --cov=src --cov-fail-under=80` báo dưới 80%.

1. Đọc bảng phủ: mô-đun nào tụt.
2. Thêm test cho hành vi thật, không thêm test rỗng.
3. **Không** hạ `--cov-fail-under`, không đặt cờ lên riêng bộ nhanh.
4. Xác nhận: phủ ≥ 80% trên **toàn bộ** bộ test.

## RB-5 — Test `slow` mốc sàn đỏ

**Dấu hiệu:** `test_u3_floor_end_to_end.py` đỏ vì `beats_floor` sai.

1. Đọc `model.auc` và `model.baseline_auc` trong báo cáo thật.
2. Nếu AUC tụt thật: điều tra dữ liệu/đặc trưng — **không** hạ `MODEL_AUC_FLOOR`.
3. Nếu baseline tăng bất thường: kiểm `measure_state_baseline` và mart.
4. Xác nhận: chạy lại `--stage stats` rồi chạy test.

## RB-6 — Dashboard không mở / cổng bị chiếm

**Dấu hiệu:** `python -X utf8 -m src.dashboard` báo lỗi bind.

1. Kiểm tiến trình cũ còn giữ `8050`; đóng nó.
2. Nếu đang chạy `integrate`, đóng dashboard trước (khoá `warehouse/olist.duckdb`).
3. Xác nhận: mở `http://127.0.0.1:8050`.

## RB-7 — Kiểm định `test_linkage_score` đỏ do máy bận

**Dấu hiệu:** `assert 69.6… < 60.0` trong `test_scoring_two_hundred_thousand_pairs_stays_under_sixty_seconds`.

1. Chạy riêng tệp đó khi máy rảnh (đo được 11 s).
2. Nếu vẫn đỏ khi rảnh: đó là thoái hoá thật, điều tra `src/linkage/score.py`.
3. **Không** nới ngưỡng 60 s.

## RB-8 — Hoàn nguyên một thay đổi

1. `git revert <commit>` trên nhánh đợt.
2. Xoá artefact sinh ra nếu hợp đồng dữ liệu đổi: `data/`, `warehouse/`, `logs/`, rồi `--stage all` + `--stage stats`.
3. Xác nhận: bốn bước của `scripts/verify_intent.ps1` xanh.

## Nguồn của từng runbook

| Runbook | Nguồn |
|---|---|
| RB-1, RB-2, RB-6 | `../observability-setup/dashboards.md` (trạng thái báo cáo, tín hiệu hiển thị) và `../observability-setup/alarms.md` (cổng nào coi là "alarm") |
| RB-2, RB-4 | `../../construction/u3-prediction-ui/nfr-design/security-design.md` SD3.4/SD3.10 — thông điệp lỗi mô hình chỉ vào nhật ký, giao diện hiện câu cố định; và cổng phủ không được hạ (SD của CI) |
| RB-3, RB-5, RB-8 | `../../construction/u3-prediction-ui/infrastructure-design/infrastructure-specification.md` INF3.3–INF3.6 (vòng đời tệp), INF3.12 (máy mới phải chạy `--stage stats`), INF3.13 (không có dịch vụ nền) |
| RB-7 | `../observability-setup/alarms.md` §3 — ca nhạy tải không phải alarm, không nới ngưỡng |

Điều kiện để một runbook ở đây **không** còn đúng: khi có môi trường chạy dài hạn hoặc người thứ hai — lúc đó `escalation-matrix.md` §3 là danh sách phải sửa trước.
