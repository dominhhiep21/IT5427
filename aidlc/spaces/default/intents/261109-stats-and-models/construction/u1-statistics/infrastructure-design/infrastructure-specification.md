# Infrastructure Specification — u1-statistics

Nguồn: `../nfr-design/{performance-design.md,security-design.md,scalability-design.md,reliability-design.md,observability-design.md,logical-components.md}`, `../functional-design/functional-spec.md`, `../../../inception/domain-design/components.md`, `../../../inception/contract-design/contract-summary.md`.

## Bối cảnh: đơn vị này không có hạ tầng triển khai

Dự án chạy từ mã nguồn trên máy người làm. Không có máy chủ, không có container, không có dịch vụ đám mây, không có môi trường staging hay production. Vì vậy tệp này **không** mô tả VPC, IAM, autoscaling hay CDN — mô tả chúng cho một tiến trình chạy 5 phút trên máy cá nhân là bịa ra hạ tầng không tồn tại.

Cái thật sự là "hạ tầng" của đơn vị này gồm bốn thứ, và cả bốn đã có sẵn:

| # | Thành phần | Hiện trạng | Vai trò với u1 |
|---|---|---|---|
| INF-1 | Máy phát triển Windows, Python 3.13 trong `.venv` | Có | Nơi tầng `stats` chạy |
| INF-2 | `warehouse/olist.duckdb` + `data/marts/*.parquet` | Có, sinh bởi `--stage all` | Nguồn dữ liệu duy nhất |
| INF-3 | `data/reports/analysis.json` | Sinh bởi tầng `stats` | Đầu ra của đơn vị; `run_stage` còn ghi `run-summary.json` cho mọi tầng, đó là của khung pipeline chứ không của đơn vị |
| INF-4 | `.github/workflows/ci.yml` trên GitHub Actions | Có | Cổng tự động duy nhất |

## Yêu cầu lên hạ tầng

| Mã | Yêu cầu | Vì sao |
|---|---|---|
| IND-1 | Thư mục `data/reports/` phải tồn tại trước khi ghi | `load_config` đã tạo sẵn; không mở rộng thêm |
| IND-2 | `scipy` phải cài trong `.venv` của repo, không cài toàn cục | Quy tắc ghim phụ thuộc của dự án |
| IND-3 | Không cần quyền mạng lúc chạy | Chỉ đọc đĩa cục bộ |
| IND-4 | Không cần quyền ghi ngoài `data/`, `warehouse/`, `logs/`, `inbox/` và `dataset/external/ibge/` | Bốn thư mục sinh ra đã bị `.gitignore`; thư mục cuối là cache nguồn ngoài của tầng `integrate`, không thuộc đơn vị này nhưng cùng tiến trình |

## Điều không có, và vì sao

- **Không container hoá.** Một tiến trình Python chạy bằng một lệnh; thêm Docker chỉ thêm một lớp phải đồng bộ với `.venv` và với đường dẫn có ký tự tiếng Việt.
- **Không dịch vụ đám mây.** Không có gì cần chạy thường trực, không có ai gọi từ ngoài.
- **Không môi trường thứ hai.** "Triển khai lại từ đầu" là xoá bốn thư mục sinh ra và chạy `--stage all`; một môi trường staging sẽ phải giữ cùng dữ liệu mà không có lợi ích nào.
- **Không sao lưu.** Báo cáo sinh lại được bằng một lệnh từ mart.

## Rủi ro hạ tầng

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Khoá `warehouse/olist.duckdb` khi dashboard đang mở | `--stage all` hỏng giữa chừng | Đóng dashboard trước khi chạy, đã ghi trong `docs/runbook.md` |
| View DuckDB chứa đường dẫn tuyệt đối tới Parquet | Chuyển thư mục repo hoặc dùng worktree khác là view trỏ sai, `stats` đọc nhầm hoặc không đọc được | Chạy lại `integrate` sau khi chuyển thư mục — đây là điều kiện vận hành do cấu trúc view quyết định, chưa có trong `docs/runbook.md` nên phải bổ sung cùng thay đổi |
| `.venv` thiếu `scipy` sau khi clone | Tầng `stats` không import được | `requirements.txt` là nguồn sự thật; CI cài từ đó |
