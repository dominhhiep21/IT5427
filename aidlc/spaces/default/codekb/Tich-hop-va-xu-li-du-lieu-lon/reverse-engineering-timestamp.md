# Reverse Engineering Timestamp

## Run Record

- Date: 2026-11-11
- Commit: `ea77bdf88d1431de11c36e1b739972bd594063f0` ("chore: lưu trữ hồ sơ 261105-default")
- Repo: `Tich-hop-va-xu-li-du-lieu-lon` (workspace root, single-repo intent)
- Branch: `feature/analysis-and-models`
- Intent: `261111-model-feature-improvemen` — cải thiện đặc trưng cho mô hình dự đoán đơn trễ (đổi khung dự
  đoán sang lúc bàn giao cho đơn vị vận chuyển, đổi đơn vị dự đoán sang dòng hàng, thêm vùng nhập liệu dự đoán
  vào tab thứ năm của dashboard)
- Scan breadth: **FOCUSED**, depth **Standard** — chỉ `src/analytics/`, `src/integrate/`, `src/dashboard/`,
  `src/pipeline/`, `tests/`
- Phương pháp: chỉ đọc mã và cấu hình; **không** chạy test, build hay chương trình của dự án.
- Chế độ: quét tập trung **hợp nhất trên một kho CodeKB CŨ** (dựng ngày 2026-11-09 bởi intent
  `261109-stats-and-models` tại cùng commit). Văn bản ngoài vùng quét được giữ nguyên; riêng vùng quét được
  viết lại theo mã hiện tại.

### Cảnh báo quan trọng: commit không phản ánh nội dung đã quét

Commit đầu là `ea77bdf`, nhưng **cây làm việc khác commit đó**: 23 mục đã sửa (11 tệp thuộc dự án + 12 tệp
trong workspace AI-DLC) và 18 mục chưa được theo dõi (13 trong số đó là tệp mã/test của dự án). Lần quét này
mô tả **cây làm việc trên đĩa**, không mô tả commit `ea77bdf`. Cụ thể:

- Mới (chưa commit), **4 tệp mã**: `src/analytics/model.py` (368), `src/analytics/report.py` (502),
  `src/analytics/statistics.py` (313), `src/dashboard/analysis_tab.py` (566).
- Mới (chưa commit), **9 tệp test**: 7 trong `tests/unit/`
  (`test_analytics_model.py`, `test_analytics_report.py`, `test_analytics_statistics.py`,
  `test_ci_config.py`, `test_dashboard_analysis_tab.py`, `test_analysis_tab_contrast.py`,
  `test_pipeline_stages.py`) và 2 trong `tests/integration/`
  (`test_u1_stats_end_to_end.py`, `test_u2_model_end_to_end.py`).
- Đã sửa (chưa commit), **11 tệp dự án**: `src/analytics/service.py`, `src/dashboard/app.py`,
  `src/pipeline/cli.py`, `src/pipeline/stages.py`, `tests/unit/test_dashboard_smoke.py`,
  `tests/integration/test_u3_end_to_end.py`, `requirements.txt`, `.github/workflows/ci.yml`, `README.md`,
  `CHANGELOG.md`, `assets/style.css` (cộng 12 tệp `aidlc/**`: 9 tệp codekb, `intents.json`, 2 tệp `memory/`).

Fingerprint dưới đây băm trạng thái **trên đĩa**, nên nó đúng cho lần đối chiếu sau; nhưng một người đọc
commit `ea77bdf` sẽ thấy mã khác.

### Tóm tắt lần quét

| Hạng mục | Kết quả |
|---|---|
| Tệp Python trong `src/` | **74** tệp, **11.333** dòng (lần trước: 70 / 9.444) |
| Tệp test | **54** tệp / **49** mô-đun `test_*` / **499** hàm test (**12** hàm `slow`), **10.086** dòng (lần trước: 45 / 40 / 353 / 9 / 7.358) |
| Gói thay đổi nhiều nhất | `src.analytics` 3/289 → **6/1.578**; `src.dashboard` 5/742 → **6/1.322**; `src.pipeline` 8/648 → **8/668** |
| Mô-đun mới | `analytics/{statistics,model,report}.py`, `dashboard/analysis_tab.py` |
| Dashboard | **5 tab**, **9 callback**, **9 output** của callback báo cáo (lần trước: 4 / 8 / 9) |
| Tầng pipeline | `STAGES` **5** tên (thêm `stats`); `_run_all` vẫn ghi **6** `StageResult` và **không** chạy `stats` |
| Thống kê / học máy trong `src/` | **có**: `scipy==1.15.2` (`statistics.py`), `scikit-learn==1.6.1` (`model.py`) |
| Phụ thuộc ghim | **12** gói (lần trước: 10) — thêm `scipy`, `scikit-learn`; **`numpy` vẫn không ghim** |
| Hợp đồng báo cáo | `data/reports/analysis.json`, **phiên bản 2**, hai khối `stats` + `model` |
| Lưu mô hình | **không có**: không `models_dir`, không `joblib`/`pickle`, không `data/models/` |
| Không mở | 9 CSV trong `dataset/`, PDF và quiz trong `doc/`, sản phẩm sinh ra (`data/`, `warehouse/`, `logs/`, `inbox/`, `.tmp-diag/`), cache, và bản cài AI-DLC (`.aidlc/`, `aidlc/`, `.opencode/`, …) |

### Ghi chú về phạm vi

- `kind: partial` vì lần quét này **chỉ** đọc sâu năm đường dẫn. Toàn bộ phần còn lại của `src/`
  (`ingest`, `clean`, `quality`, `external`, `integration`, `linkage`), `config/`, `docs/`, `assets/`
  giữ nguyên văn bản của lần quét trước — coi là **chưa xác minh lại**.
- `requirements.txt` **từng** là đường dẫn quét sâu của lần trước nhưng lần này chỉ đọc để lấy phiên bản và
  lý do ghim → bị **hạ xuống `shallow.paths`**, đúng luật hợp nhất tập trung.
- Chỉ số dòng của mọi tệp đã được **đo lại trên đĩa**, kể cả tệp không đọc sâu; đó là phép đo, không phải
  phân tích mới.
- Mọi kết luận về dữ liệu (số dòng, dị thường, grain) vẫn dựa trên hằng số trong mã, tài liệu dự án và test,
  không dựa trên việc chạy phân tích dữ liệu trong lần quét này.
- Bản cài AI-DLC (`.aidlc/`, `aidlc/`, `.opencode/`, …) không được quét và không nằm trong fingerprint.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: model-feature-improvemen
fingerprint: 3011bfaffb418f9e9fca2c8d34977877503131d3
analyzed:
  paths:
    - src/analytics/
    - src/integrate/
    - src/dashboard/
    - src/pipeline/
    - tests/
  components:
    - src.analytics
    - src.integrate
    - src.dashboard
    - src.pipeline
    - tests
shallow:
  paths:
    - requirements.txt
    - src/ingest/
    - src/clean/
    - src/quality/
    - src/common/
    - src/external/
    - src/integration/
    - src/linkage/
    - src/config.py
    - config.yaml
    - config/
    - docs/
    - README.md
    - CHANGELOG.md
    - AGENTS.md
    - assets/style.css
    - .github/workflows/ci.yml
    - ruff.toml
    - pytest.ini
    - dataset/external/ibge/
```
