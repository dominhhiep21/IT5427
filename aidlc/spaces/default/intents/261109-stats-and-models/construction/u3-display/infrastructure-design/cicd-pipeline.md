# CI/CD Pipeline — u3-display

Nguồn: `../nfr-design/logical-components.md`, `../nfr-design/security-design.md`, `../functional-design/functional-spec.md`, `../../../inception/contract-design/contract-summary.md`, `../../../inception/domain-design/components.md`, `.github/workflows/ci.yml`, `aidlc/spaces/default/memory/project.md` (`## Deployment`).

## Hiện trạng

Không có môi trường triển khai: dự án chạy từ mã nguồn, GitHub Actions là cổng tự động duy nhất. U1 đã nối tầng `stats` vào `ci.yml`; U2 chỉ thêm phụ thuộc và tệp vào danh sách định dạng.

## Thay đổi đơn vị này cần

| # | Thay đổi | Vì sao | Ai làm |
|---|---|---|---|
| CI-U3-1 | Thêm mọi tệp **nguồn và tệp test** mới của U3 vào danh sách `ruff format --check` trong `ci.yml` **và** vào tuple `NEW_FILES` của `tests/unit/test_ci_config.py` | Cả hai danh sách đều tính tệp test (8/11 mục trong `NEW_FILES` là test). Chỉ thêm tệp nguồn thì tệp test mới lọt khỏi cổng định dạng mà test canh vẫn xanh (NFR4.1) | Code Generation, cùng lúc với việc tạo tệp |
| CI-U3-2 | Sửa **ba** test hình dạng trong cùng thay đổi: `tests/unit/test_dashboard_smoke.py` (số tab 4→5, số callback 8→9 — **số output giữ nguyên 9**, vì assert đó đo tuple của callback KPI chứ không phải toàn dashboard), `tests/integration/test_u3_end_to_end.py` (số callback), và mọi chỗ lấy tab bằng `tabs.children[-1]` | Tab mới đổi hình dạng giao diện. Ba test lấy tab **theo vị trí cuối**, nên thêm tab thứ năm làm chúng đọc nhầm tab — hỏng vì vị trí chứ không vì con số | Code Generation |
| CI-U3-3 | Cập nhật `README.md` mục Test và `CHANGELOG.md` cho mốc tab mới | Tài liệu phải khớp hành vi | Code Generation |
| CI-U3-4 | Không thêm bước CI mới | Tab được kiểm bởi bộ test hiện có; thêm bước chạy dashboard trong CI là thêm một tiến trình dài mà không kiểm thêm gì | — |

## Bẫy đã biết

- **Bẫy 1 — số tab.** `tests/unit/test_dashboard_smoke.py` khẳng định cả số tab, số callback và số output. Sửa một con số mà quên hai con số kia sẽ đỏ ở chỗ khác, khó lần.
- **Bẫy 2 — `dmc.Title` cần `dmc.MantineProvider`.** Gốc ứng dụng không bọc provider; chỉ `src/integration/tab.py` tự bọc tab của nó. Tab mới dùng `dmc.Title` thì phải bọc tương tự, nếu không sẽ lỗi lúc chạy chứ không lúc test tĩnh.
- **Bẫy 3 — bộ nhanh.** Không test nào của U3 được đọc `data/reports/analysis.json` của repo; test dựng `ReportView` trong bộ nhớ. Test cần tệp thật mang marker `slow`.

## Không thay đổi

- **Không thêm job, không tách workflow.**
- **Không thêm cổng mới.** Cổng phủ 80% và `ruff` đã đủ.
- **Không có bước deploy**, không có môi trường để deploy tới.
- **Không chạy trình duyệt trong CI.** Repo chỉ có `pytest`; mốc 1280px kiểm bằng mắt ở bước 4 chuỗi xác nhận, ghi kết quả vào `code-summary.md`.

## Chuỗi xác nhận cục bộ

Bộ test nhanh → `--stage all` → `--stage stats` → mở dashboard, xem tab mới ở 1280px.

## Điều phải kiểm khi viết mã

- Một test đọc `ci.yml` và khẳng định mỗi tệp nguồn mới của U3 có mặt trong danh sách `ruff format --check`.
- Một test khẳng định tab mới được bọc trong `dmc.MantineProvider` khi dùng `dmc.Title`.
