# CI/CD Pipeline — u3-query-rewriter

Nguồn: `nfr-design/security-design.md` (ADR-U3-S1..S5), `nfr-design/logical-components.md` (L1–L7), `nfr-requirements/tech-stack-decisions.md` (TS-U3-1..10, NFR1.1–NFR6.2), `nfr-requirements/security-requirements.md` (SR-U3-1..10), `functional-design/functional-spec.md` (W1–W4), `.github/workflows/ci.yml`, `pytest.ini`, `ruff.toml`.

Đơn vị là thư viện trong tiến trình, không có hạ tầng triển khai. Tài liệu này mô tả **đường đi từ mã tới "coi như xong"** cho U3, trong khuôn khổ component `QueryRewriter` và `SemanticLayer` của `inception/domain-design/components.md`.

## 1. Đường ống hiện có

Giữ nguyên sáu bước đang có (kích hoạt, windows-2022, cài phụ thuộc, lint/format, dựng dữ liệu, test nhanh), cộng hai bước U5 đã thêm (đo phủ toàn bộ và smoke nạp cấu hình nguồn).

## 2. Đơn vị này thêm gì vào đường ống

| Thay đổi | Vì sao | Ở đâu |
|---|---|---|
| Thêm **bốn** tệp Python vào danh sách `ruff format --check` của CI | CI liệt kê từng tệp; `src/integration` đã là thư mục được quét nên `rewrite.py` tự động được kiểm, ba tệp còn lại phải thêm tay | `ci.yml` dòng 33: thêm `src/common/kpis.py`, `src/common/exceptions.py`, `tests/unit/test_integration_rewrite.py`, `tests/unit/test_common_kpis.py` |
| **Không** thêm gói | `duckdb`, `pandas`, `dataclasses`, `time` đã có | `requirements.txt` không đổi |
| **Không** thêm bước pipeline mới | U3 là thư viện; U6 quyết định khi nào gọi | `src/pipeline/stages.py` không đổi |
| Sửa `config/integration-tab.yaml` + `card.py` + ba test | BR3.1: tab có **bốn vùng** (ba mới + `don-theo-thang`) | cùng thay đổi sinh mã |
| Thêm **ba** trường mới trong `config/mediated-schema.yaml`, rồi cập nhật `config/integration-sources.yaml` | BR3.11/TS-U3-9: ba mẫu cần cước vận chuyển và hai ngày giao (trường mới); `don_hang.bang_giao` và `san_pham.ten_danh_muc` đã có sẵn và **đã `loaded: true` trong C8** — không còn bước bật cờ | cùng thay đổi sinh mã; cập nhật test U2 |

## 3. Cổng chất lượng của đơn vị

| Chỉ tiêu | Cổng | Chạy ở đâu | Ghi chú |
|---|---|---|---|
| NFR3.1 | `ruff check` + `ruff format --check` trên bốn tệp mới + hai tệp sửa | §4 bước 1–2; CI | Phạm vi cố định theo `tech-stack-decisions.md` §3 |
| NFR2.2 | `test_integration_rewrite.py` và `test_common_kpis.py` | §4 bước 4; CI | Mỗi mô-đun mới một tệp |
| NFR2.1 | `pytest --cov=src --cov-fail-under=80` | CI (bước U5 thêm) | Không hạ ngưỡng |
| NFR1.1 | Ghi `elapsed_ms` và `load_ms` của ba mẫu trên dữ liệu thật | Build and Test | Vượt `SLOW_QUERY_MS` chỉ cảnh báo (BR3.8) |
| NFR5.1/NFR5.2 | `--stage all`; `KpiReconciler`; số dòng 11 view | §4 bước 5; Build and Test | U3 không ghi mart/view |
| SR-U3-3/SR-U3-4 | Test tham số chứa `'`/`;`; test bảng/cột lạ | Bộ test của đơn vị | Hai ca âm bắt buộc |
| SR-U3-10 | Test lệch 0,02 → `KpiMismatchError` | Bộ test của đơn vị | Khoá cửa hậu nới dung sai |

## 4. Cổng xác nhận của đơn vị

1. `.venv\Scripts\python.exe -X utf8 -m ruff check src/integration/rewrite.py src/common/kpis.py src/integration/models.py src/common/exceptions.py src/integration/card.py tests/unit/test_integration_rewrite.py tests/unit/test_common_kpis.py`
2. Cùng danh sách với `ruff format --check`.
3. `.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all` (bộ test nhanh chưa hermetic — TD-09).
4. `.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_rewrite.py tests/unit/test_common_kpis.py`.
5. `.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80` (toàn bộ bộ test).
6. Ở Build and Test: `.venv\Scripts\python.exe -X utf8 -m pytest -m slow` để lấy số thật cho NFR1.1/NFR5.2.

## 5. Hoàn nguyên

| Thay đổi | Cách hoàn nguyên |
|---|---|
| `src/integration/rewrite.py`, hai tệp test | Xoá; gỡ lời gọi ở U6 trước |
| `src/common/kpis.py` | Xoá; `src/analytics` không phụ thuộc nó (L5 chỉ lớp truy vấn đọc) |
| `KpiComparison` thêm `group_key`/`delta` | Bỏ hai trường; đây là thay đổi cộng thêm của C4 |
| Ba trường lược đồ mới | Xoá **đúng ba trường mới** khỏi `config/mediated-schema.yaml` và tập trường U5; **giữ nguyên** `don_hang.bang_giao` và `san_pham.ten_danh_muc`, **không hoàn nguyên cờ `loaded`** (đã `true` từ C8); chạy lại `--stage all` |
| Thêm ba vùng bên cạnh `don-theo-thang` trong `integration-tab.yaml` | Hoàn nguyên = gỡ ba vùng mới, **giữ** `result_region_ids: [don-theo-thang]`, sửa lại `src/integration/card.py`, `src/dashboard/app.py` (callback của vùng) và ba test: `test_integration_query.py`, `test_integration_card.py`, `test_dashboard_smoke.py` |
| `KpiMismatchError` trong exceptions | Xoá lớp sau khi U6 thôi bắt |

## 6. Không có gì để triển khai

Không máy chủ, không container, không dịch vụ đám mây, không bí mật, không sao lưu. Sản phẩm chạy local từ mã nguồn (`team.md` — Deployment).
