# Tech Stack Decisions — u3-query-rewriter

## Gia cố tiêu thụ C3 (2026-11-09)

`run_template` không chỉ lấy `source_name` từ C3 nữa: `_checked_selection` nay kiểm **nguồn thắng phải khai đủ bảng** mà mẫu truy vấn đọc (`TEMPLATE_TABLES`), thiếu thì ném `SchemaError` nêu tên bảng. Lý do: trước đó chọn nguồn khác vẫn ra đúng một câu SQL trên cùng CSV, tức C3 bị tiêu thụ hình thức. Kết quả chọn nguồn không khai bảng nào (bộ dựng thử) được bỏ qua phép kiểm để không báo lỗi sai.

Đây là ràng buộc **mới ở mức mã**, chưa có trong danh sách SR cũ; test khoá nằm ở `tests/unit/test_integration_rewrite.py`.


Nguồn: `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`, `requirements.txt`, `functional-design/functional-spec.md`, `functional-design/rules.md`, `inception/requirements-analysis/requirements.md` (NFR1–NFR6, C1–C6), `inception/contract-design/contract-summary.md` (C1, C3, C4).

## 1. Đã chốt ở cấp dự án

| Hạng mục | Lựa chọn | Ghi chú |
|---|---|---|
| Ngôn ngữ | Python 3.13 | Có sẵn |
| Máy truy vấn | DuckDB | Đang dùng ở `src/analytics/service.py`, `src/integrate/connections.py` |
| Kết nối | `duckdb.connect()` **in-memory**, đăng ký khung pandas đọc từ `dataset/`; không mở `warehouse/` | Không tạo đường ghi nào; không phụ thuộc `src/integrate/connections.py` |
| Tham chiếu KPI | `src/analytics` (dịch vụ hiện có) | Nguồn đối chiếu của FR2.5 |
| Kiểu hợp đồng | `dataclass(frozen=True)` ở `src/integration/models.py` | Cùng chỗ với C1/C2/C4/C6 |
| Lỗi | `PipelineError` và lớp con | `KpiMismatchError` đã có trong C4 |

## 2. Quyết định riêng cho đơn vị này

| Mã | Quyết định | Lý do |
|---|---|---|
| TS-U3-1 | Mô-đun mới `src/integration/rewrite.py` (mẫu, kế hoạch, chạy) + mở rộng `src/integration/models.py` | Cùng gói đang chứa `query.py`, `load.py`, `card.py`; không tạo gói mới |
| TS-U3-2 | Mẫu SQL và kế hoạch là **hằng trong mã**, không đọc từ cấu hình | BR3.4/BR3.5: mẫu khai tay; cấu hình ngoài sẽ mở đường chèn định danh |
| TS-U3-3 | Ba mẫu dùng đúng ba `template_id` của U5 | BR3.1; lệch mã là lỗi khởi tạo |
| TS-U3-4 | **Cộng thêm** ba vùng vào `result_region_ids` trong `config/integration-tab.yaml`, giữ `don-theo-thang`, không chạm `card_ids`; sửa `src/integration/tab.py` (nơi có `REGION_RENDERERS`/`renderers` — `card.py` chỉ dựng vùng `don-theo-thang`) và các test hình dạng tab | BR3.1: tab có bốn vùng (ba mới + `don-theo-thang`); thay đổi C9 chốt với U1/U6 |
| TS-U3-5 | Sổ KPI đặt ở **`src/common/kpis.py`** (mô-đun trung lập) | BR3.9: cả `src/analytics` và `src/integration` cùng đọc, không tầng nào import tầng kia → giữ hướng phụ thuộc của `team.md` |
| TS-U3-6 | Đối chiếu gọi `src/analytics` **một lần** cho mỗi lần chạy, cùng bộ tham số | BR3.6/BR3.12; tránh hai bên lọc lệch nhau |
| TS-U3-7 | Dung sai là hằng số trong mã: `0.01` tiền, `0` số dòng, `0.01` phần trăm | SR-U3-10; không cho nới từ ngoài |
| TS-U3-8 | Kết quả chạy gần nhất giữ trong bộ nhớ tiến trình (dict theo `template_id`), không ghi tệp | FR2.4 chỉ cần đọc lại trong phiên; không thêm trạng thái bền |
| TS-U3-9 | Bổ sung bốn trường lược đồ (BR3.11) trong cùng thay đổi với U2 | Không ai khác cần; phải cập nhật `config/mediated-schema.yaml`, `config/integration-sources.yaml`, test U2 |
| TS-U3-10 | Không thêm gói | `duckdb`, `dataclasses`, `time` đã có |

## 3. Chỉ tiêu kỹ thuật

```yaml
nfr_requirements:
  - id: NFR1.1
  - id: NFR2.1
  - id: NFR2.2
  - id: NFR3.1
  - id: NFR4
  - id: NFR5.1
  - id: NFR5.2
  - id: NFR6.1
  - id: NFR6.2
```

| Mã | Chỉ tiêu | Ngưỡng | Đo bằng | Nguồn |
|---|---|---|---|---|
| NFR1.1 | Thời gian chạy một truy vấn mẫu trên DuckDB | dưới 2 giây | `QueryRunResult.elapsed_ms` đo quanh lời gọi (BR3.8). Đúng như BR3.8, vượt ngưỡng là **ghi nhận, không phải lỗi chặn**: gói đã có `SLOW_QUERY_MS` và phát `integration.query.slow`; bộ chậm đo và ghi lại số thật, không đỏ vì chậm | NFR1 |
| NFR2.1 | Độ phủ dòng toàn dự án | ≥ 80% | `.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80` trên toàn bộ bộ test | NFR2 |
| NFR2.2 | Mỗi mô-đun mới có test riêng | 1 tệp test cho `src/integration/rewrite.py` **và** 1 tệp test cho `src/common/kpis.py` | Rà `tests/unit/` | NFR2 |
| NFR3.1 | Lint và định dạng | 0 vi phạm | `ruff check` + `ruff format --check` trên **đúng các tệp Python của đơn vị**: `src/integration/rewrite.py`, `src/integration/models.py`, `src/integration/tab.py` (nơi dựng vùng kết quả cho ba mẫu mới), `src/common/kpis.py`, `src/common/exceptions.py`, `src/integration/card.py`, `tests/unit/test_integration_rewrite.py`, `tests/unit/test_integration_tab.py`, `tests/unit/test_dashboard_smoke.py`, `tests/integration/test_u3_end_to_end.py`, `tests/unit/test_common_kpis.py` | NFR3 |
| NFR4 | Tiếp cận | **N/A** | Đơn vị không hiển thị; WCAG 2.1 AA thuộc U6 | NFR4 |
| NFR5.1 | Pipeline và đối chiếu KPI xanh | 5 KPI lệch 0 | `python -X utf8 -m src.pipeline run --stage all`; `KpiReconciler` | NFR5 |
| NFR5.2 | Số dòng 11 view không đổi | Khớp baseline | `pytest -m slow` (`test_u2_end_to_end.py`) | NFR5 |
| NFR6.1 | Không mạng | 0 lời gọi mạng | Rà mã | NFR6 |
| NFR6.2 | Chạy UTF-8 | mọi lệnh `-X utf8` | Lệnh xác nhận của đơn vị | NFR6 |

## 4. Việc cần làm ở bước sinh mã

- Thêm `KpiMismatchError(PipelineError)` vào `src/common/exceptions.py` (C4 đã khai nhưng mã chưa có), cùng `missing_fields`/`delta` mà nó mang.
- Thêm bốn trường lược đồ (TS-U3-9) và cập nhật tập trường của U5 cùng test U2.
- Thêm `src/common/kpis.py` (TS-U3-5) với ba KPI và định nghĩa doanh thu.
- Mở rộng `src/integration/models.py`: `QueryTemplate`, `RewriteStep`, `KpiComparison` theo nhóm, `QueryRunResult` (thêm `total_orders`, `months`, `partial`).
- Tạo `src/integration/rewrite.py` (TS-U3-1) với mẫu SQL, kế hoạch, hàm chạy và hàm đối chiếu.
- Cộng thêm ba vùng vào `result_region_ids` trong `config/integration-tab.yaml` (giữ `don-theo-thang`, không chạm `card_ids`), sửa `src/integration/tab.py` và các test hình dạng tab (TS-U3-4).
- Viết `tests/unit/test_integration_rewrite.py`; cập nhật test U2 và test dashboard theo thay đổi C9.
