# Infrastructure Specification — u3-prediction-ui

Nguồn: `../nfr-design/{performance-design,security-design,logical-components}.md`, `../functional-design/functional-spec.md`, `../../../inception/contract-design/contract-summary.md` (C2b), `../../../inception/domain-design/components.md`, `../../../../memory/team.md` `## Deployment`.

## 1. Mô hình triển khai: không có hạ tầng đám mây

Đơn vị này **không** thêm tài nguyên hạ tầng nào. Repo chạy từ mã nguồn trên máy local, và đợt này giữ nguyên mô hình đó:

| Hạng mục | Hiện trạng | Đơn vị này thay đổi? |
|---|---|---|
| Đám mây / container / scheduler | không có | không |
| Tiến trình | 1 tiến trình Dash (`127.0.0.1:8050`) + 1 tiến trình CLI (`python -m src.pipeline`) | không |
| Cơ sở dữ liệu | `warehouse/olist.duckdb` (DuckDB nhúng, không server) | không |
| Tệp | `data/`, `warehouse/`, `logs/`, `inbox/` (sinh ra, bị `.gitignore`) | thêm `data/models/` — **đã có từ U2** |
| Mạng ra ngoài | chỉ API IBGE khi `--refresh-ibge` | không |
| Bí mật | không có | không |

Vì vậy "infrastructure" ở đây là **bố cục tệp + tiến trình + cấu hình**, không phải máy chủ.

## 2. Kiểm kê tài nguyên

| ID | Tài nguyên | Vị trí | Vòng đời | Ghi chú |
|---|---|---|---|---|
| INF3.1 | Mã khối dự đoán | `src/dashboard/prediction_section.py` | commit | mới |
| INF3.2 | Khung/CSS dùng chung | `src/dashboard/analysis_tab.py`, `src/dashboard/app.py`, `assets/style.css`, `README.md`, `CHANGELOG.md` | commit | sửa: mục thứ tư, `.field-error`, đăng ký callback, câu chữ/nhãn, mốc CHANGELOG |
| INF3.3 | Báo cáo | `data/reports/analysis.json` | sinh bởi `--stage stats` | không commit |
| INF3.4 | Tệp mô hình | `data/models/*.pkl` + metadata | sinh bởi `--stage stats` | không commit; máy mới phải sinh lại |
| INF3.5 | Nhật ký | `logs/*.jsonl` (giữ 10 tệp gần nhất) | sinh mỗi lần chạy | không commit |
| INF3.6 | Kho DuckDB | `warehouse/olist.duckdb` | sinh bởi `--stage integrate` | giao diện **không** mở |
| INF3.7 | Tệp nguồn gốc | `dataset/` | bất biến | chỉ đọc |
| INF3.8 | Cấu hình | `config.yaml` → `AppConfig` (bất biến) | commit | `models_dir` đã có |

## 3. Topology tiến trình

```
powershell: python -X utf8 -m src.dashboard
  └─ tiến trình → Dash server 127.0.0.1:8050
       ├─ đọc data/reports/analysis.json   (mỗi lần render tab, một lần mỗi lần bấm)
       └─ đọc data/models/*.pkl            (một lần lúc dựng panel, một lần mỗi lần bấm)

powershell: python -X utf8 -m src.pipeline run --stage stats
  └─ ghi data/reports/analysis.json (nguyên tử qua AtomicWriter)
     + data/models/*.pkl (ghi trực tiếp — KHÔNG nguyên tử, xem đoạn dưới)
```

Hai tiến trình **không** giao tiếp qua mạng; chúng chỉ chia sẻ tệp. Phía ghi báo cáo dùng `AtomicWriter` (`os.replace`) nên phía đọc thấy bản cũ hoặc bản mới trọn vẹn. **Tệp mô hình thì không nguyên tử**: `persistence.py::save_model` mở thẳng `data/models/logistic.pkl` bằng `"wb"` rồi `pickle.dump` (đã ghi là nợ ở vòng soát U2). Hệ quả được chấp nhận: nếu người dùng bấm đúng lúc tệp đang được ghi, `load_model` ném `ModelError` và khối hiện câu hướng dẫn (BR3.25); chạy lại `--stage stats` sửa được. Không có khoá giữa hai tiến trình, và đây là lý do phải nói rõ thay vì hứa "nguyên tử".

## 4. Ràng buộc vận hành

| ID | Ràng buộc | Lý do | Cách kiểm |
|---|---|---|---|
| INF3.9 | Mọi lệnh Python chạy UTF-8 (`-X utf8` hoặc `PYTHONUTF8=1`) | đường dẫn có tiếng Việt, dữ liệu có tiếng Bồ Đào Nha | lệnh trong README/`runbook.md` ghi rõ; **CI hiện không đặt `env:` chung** — từng bước tự ghi `-X utf8` là cách duy nhất đang có |
| INF3.10 | Không bind địa chỉ khác `127.0.0.1` | dashboard chỉ dùng nội bộ | `config.yaml` |
| INF3.11 | Không commit `data/`, `warehouse/`, `logs/`, `inbox/`, `.venv/`, `.coverage` | `.gitignore` | `git status` sạch với các thư mục đó |
| INF3.12 | Một máy mới clone phải chạy `--stage stats` **trước khi** khối dự đoán dùng được | tệp mô hình không được commit (C2b) | câu hướng dẫn trong khối (BR3.25) + mục "Lưu ý" của README |
| INF3.13 | Không thêm cổng, route, dịch vụ nền, cron | ngoài phạm vi đợt | đọc `app.py`/`config.yaml` |
| INF3.14 | Không đổi `config.yaml` cấu trúc; chỉ đọc `models_dir` đã có | `AppConfig` là hợp đồng bất biến | `load_config` + test cấu hình |

## 5. Môi trường

Chỉ **một** môi trường: máy phát triển. Không staging, không production, không parity (đúng `team.md` `## Deployment`). Hệ quả: không có cấu hình theo môi trường, không có biến môi trường mới, không có bí mật theo môi trường. "Phát hành" = chạy bốn bước xác nhận trên máy đó.

## 6. Sao lưu và khôi phục

| Tài nguyên | Sao lưu | Khôi phục |
|---|---|---|
| `dataset/` | git | clone lại |
| Mã nguồn | git | clone lại |
| `data/`, `warehouse/` | **không** sao lưu (sinh ra) | xoá bốn thư mục sinh ra, chạy `--stage all` rồi `--stage stats` |
| `data/models/` | **không** sao lưu | như trên; máy khác sinh lại tệp của mình |

## 7. Điều kiện dừng

Đơn vị này không có tài nguyên nào cần huỷ: không máy chủ, không bucket, không hàng đợi. Teardown = xoá `data/`, `warehouse/`, `logs/`, `inbox/` — đã là quy trình có sẵn.
