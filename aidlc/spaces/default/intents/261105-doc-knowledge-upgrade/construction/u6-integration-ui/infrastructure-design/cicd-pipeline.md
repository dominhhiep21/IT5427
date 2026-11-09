# CI/CD Pipeline — u6-integration-ui

Nguồn: `nfr-design/{security-design,logical-components}.md`, `nfr-requirements/tech-stack-decisions.md` (TS-U6-1..7), `functional-design/functional-spec.md`, `.github/workflows/ci.yml`, `pytest.ini`, `ruff.toml`, `requirements.txt`.

## 1. Đơn vị này thêm gì vào đường ống

| Thay đổi | Vì sao | Ở đâu |
|---|---|---|
| **Cài `dash-mantine-components` trong `.venv`, đọc phiên bản thực cài được, rồi ghim đúng số đó** vào `requirements.txt` dạng `dash-mantine-components==<phiên bản>` | FR5.4 buộc dùng DMC; gói chưa có trong repo. Không đoán số phiên bản: cài trong `.venv`, chạy `pip show dash-mantine-components` lấy `Version`, ghi đúng số đó. `FR5.4` **thắng** câu "không thêm thư viện UI mới" ở `functional-spec.md` dòng 122 — câu đó sửa thành "không thêm thư viện UI nào ngoài DMC" trong cùng thay đổi | `.venv` → `requirements.txt` → `functional-spec.md` |
| Thêm `src/integration/tab.py`, `tests/unit/test_integration_tab.py` vào danh sách `ruff format --check` | CI liệt kê từng tệp | `ci.yml` dòng 33 |
| Không thêm bước pipeline mới | Tab là tầng hiển thị; CI hiện có đã chạy test dashboard | `ci.yml` không đổi bước |

## 2. Cổng chất lượng

| Chỉ tiêu | Cổng | Chạy ở đâu |
|---|---|---|
| NFR3.1 | `ruff check` + `ruff format --check` trên tệp của đơn vị | §3 bước 1–2; CI |
| NFR2.2 | `tests/unit/test_integration_tab.py` | §3 bước 4; CI |
| NFR2.1 | `pytest --cov=src --cov-fail-under=80` | CI (bước U5 thêm) |
| NFR5.1/NFR5.2 | `test_dashboard_smoke.py` (4 thẻ; 2 callback cũ + 6 callback mới = **8**) + `KpiReconciler` | §3 bước 5; CI |
| NFR1.1–NFR1.4 | Đo callback trong test dashboard với `time.perf_counter`, ngưỡng **2000 ms** mỗi callback; số thật ghi ở Build and Test | §3 bước 4 |
| NFR4.1 (WCAG 2.1 AA) | Rà thật, ghi vào `code-summary.md`: (a) mọi điều khiển là `<button>`/`<a>` thật, (b) tab bàn phím đi hết bốn thẻ và bốn màn hình, (c) viền `:focus-visible` tương phản ≥ 3:1, (d) chữ thường tương phản ≥ 4,5:1, (e) không dùng màu làm tín hiệu duy nhất (mỗi `StateBlock` có câu chữ) | §3 bước 6 (mở dashboard bằng mắt) + rà mã trong review; không có cổng tự động |

## 3. Cổng xác nhận của đơn vị

1. `.venv\Scripts\python.exe -X utf8 -m ruff check src/dashboard/app.py src/integration/card.py src/integration/tab.py src/common/kpis.py tests/unit/test_integration_tab.py tests/unit/test_dashboard_smoke.py tests/integration/test_u3_end_to_end.py`
2. Cùng danh sách với `ruff format --check`.
3. `.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all` (bộ nhanh chưa hermetic — TD-09).
4. `.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_tab.py tests/unit/test_dashboard_smoke.py`.
5. `.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80`.
6. Mở dashboard bằng mắt: bốn tab, tab "Tích hợp" có bốn thẻ, vào/ra bốn màn hình chi tiết (bước 3 của lệnh xác nhận dự án).

## 4. Hoàn nguyên

| Thay đổi | Cách hoàn nguyên |
|---|---|
| `src/integration/tab.py`, `tests/unit/test_integration_tab.py` | Xoá; `app.py` quay lại dựng ba khối cũ |
| `config/integration-tab.yaml` | Gỡ sáu callback mới, giữ hai callback cũ, **giữ `result_region_ids`**; trả `TabConfig` phần thẻ mới về hình dạng cũ |
| `result_block_ids` (đã bị gỡ) | Khôi phục khoá cũ trong `config/integration-tab.yaml` và nhánh đọc tương ứng trong `load_tab_config`; **giữ nguyên `card_ids`** vì nó đã có sẵn từ C9 và không phải thứ đơn vị này thêm |
| `dash-mantine-components` | Bỏ dòng trong `requirements.txt`; gỡ khỏi `.venv` |
| Callback mới | Gỡ **sáu** callback; giữ hai callback cũ |
| Câu cấm trong `functional-spec.md` dòng 122 | Trả lại câu "không thêm thư viện UI mới"; đồng thời gỡ dòng DMC khỏi `requirements.txt` nếu hoàn nguyên cả đơn vị |
| `load_tab_config`/`TabConfig` | Khôi phục nhánh đọc `result_block_ids` và năm test của `test_integration_card.py` |

## 5. Không có gì để triển khai

Không máy chủ, không container, không môi trường thứ hai. "Phát hành" = chạy local theo `team.md`.
