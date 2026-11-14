# Quality Gates — intent `261111-model-feature-improvemen`

## 1. Cổng chặn hợp nhất

| ID | Cổng | Ngưỡng | Đỏ thì sao |
|---|---|---|---|
| QG1 | `ruff check .` | 0 lỗi | chặn |
| QG2 | `ruff format --check` (50 mục khai tay) | 0 tệp lệch | chặn |
| QG3 | `run --stage all` | `QualityGate` (21 + 9 + 10 check) và `KpiReconciler` (5 KPI) xanh | chặn — dữ liệu sai thì mọi số sau đó vô nghĩa |
| QG4 | `run --stage stats` | báo cáo v3 đọc lại được, tệp mô hình ghi được | chặn |
| QG5 | Bộ nhanh `-m "not slow"` | 0 đỏ (708 test) | chặn |
| QG6 | Phủ dòng `src/` | **≥ 80%** trên toàn bộ bộ test (đo được 92,71%) | chặn; **cấm hạ ngưỡng** |
| QG7 | Smoke cấu hình nguồn | `config/integration-sources.yaml` nạp được | chặn |
| QG8 | Mốc sàn mô hình | `beats_floor(auc, baseline_auc)` xanh trên báo cáo thật (test `slow`) | chặn |

## 2. Luật đứng sau các cổng

- **Không hạ cổng để cho một bước pass** (`team.md`, `project.md`). Nếu QG6 đỏ, sửa mã hoặc thêm test — không đổi `--cov-fail-under`.
- **Không đặt cờ lên riêng bộ nhanh**: cổng phủ chạy trên toàn bộ bộ test vì bảy mô-đun `src/` chỉ có phủ nhờ bộ `slow`.
- **`tests/unit/test_ci_config.py` canh chính các cổng**: danh sách format (mọi đường dẫn phải **tồn tại** và **tương đối**), ba nhánh trong cả hai trigger, và "cổng phủ không bị hạ".
- **Không có `continue-on-error`** cho bất kỳ bước nào.

## 3. Cổng ngoài CI (chạy tay, trước khi coi là xong)

`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_intent.ps1` — bốn bước: bộ nhanh → `--stage all` → `--stage stats` → toàn bộ + phủ. Đây là **cổng xác nhận của intent**, không thay CI, và cũng không được nới.

## 4. Điều CI **không** làm (và vì sao)

| Không làm | Vì sao |
|---|---|
| Deploy | không có môi trường triển khai; "phát hành" = chạy từ mã nguồn |
| SAST/DAST, quét phụ thuộc | repo không có bước bảo mật tự động; thêm là thay đổi ngoài phạm vi |
| Kiểm tra kiểu tĩnh (`mypy`/`pyright`) | quyết định đã chốt là **không** có |
| Cache artefact dữ liệu | `data/` sinh lại được; cache sẽ che lỗi tầng dữ liệu |
| Chạy trên Linux | mã có đường dẫn/encoding Windows; đổi runner là thay đổi hạ tầng |

## 5. Trạng thái hiện tại

Tất cả tám cổng **xanh** trên cây cuối: `ruff` sạch, `format` 50/50, hai tầng dữ liệu `success`, bộ nhanh 708 passed, phủ 92,71%, smoke xanh, mốc sàn xanh (`0,6482 ≥ max(0,55; 0,5297)`).
