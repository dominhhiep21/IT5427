# CI/CD Pipeline — u1-statistics

Nguồn: `../../../inception/requirements-analysis/requirements.md` (FR5.1, FR5.2, FR5.3, NFR2, NFR4), `.github/workflows/ci.yml`, `src/pipeline/stages.py`, `src/pipeline/cli.py`, `README.md`, `aidlc/spaces/default/memory/project.md` (`## Deployment`).

## Hiện trạng

`.github/workflows/ci.yml` chạy trên `windows-2022`, Python 3.13, cache pip. Chuỗi bước: `ruff check .` → `ruff format --check` (danh sách tệp khai tay) → `python -X utf8 -m src.pipeline run --stage all` → bộ test nhanh → `pytest --cov=src --cov-fail-under=80` trên toàn bộ bộ test → smoke nạp `config/integration-sources.yaml`. Không có bước deploy.

Trigger khai tay đúng hai danh sách `on.push.branches` và `on.pull_request.branches`, hiện có `main` và `feature/update-ui-ux`.

## Thay đổi đơn vị này cần

| # | Thay đổi | Vì sao | Ai làm |
|---|---|---|---|
| CI-1 | Thêm nhánh `feature/analysis-and-models` vào **cả hai** danh sách trigger **ngay trong thay đổi đầu tiên của đợt** | Nhánh này đã tồn tại trên máy và đã có commit; mọi push cho tới lúc sửa `ci.yml` không chạy cổng nào (FR5.2) | Code Generation, trước mọi thay đổi khác của đợt |
| CI-2 | Thêm mọi tệp nguồn mới của đơn vị vào danh sách `ruff format --check` | Danh sách khai tay; tệp không có trong danh sách thì không ai kiểm định dạng (NFR4.2) | Code Generation, cùng lúc với việc tạo tệp |
| CI-3 | Thêm tầng `stats` vào **cả hai** nơi khai danh sách tầng: `STAGES` trong `src/pipeline/stages.py` **và** bộ `choices` của tham số `--stage` trong `src/pipeline/cli.py` | Danh sách tầng đang khai hai lần; chỉ thêm vào `STAGES` thì lệnh `run --stage stats` bị argparse từ chối với `invalid choice` và bước CI mới đỏ ngay lần đầu. Đây cũng là dịp sửa chỗ lệch đã ghi ở `TD-11` (FR5.1) | Code Generation |
| CI-4 | Thêm bước `python -X utf8 -m src.pipeline run --stage stats` **sau** `--stage all` và **trước** bước test | Tầng mới chỉ được kiểm nếu CI chạy nó | Code Generation |
| CI-5 | Cập nhật `README.md` mục "CI" và mục "Test" cho khớp `ci.yml`, thêm mốc `CHANGELOG.md` | README hiện nói bộ `slow` và cổng phủ không chạy trong CI, trái với `ci.yml` (FR5.3) | Code Generation, cùng thay đổi |

## Thứ tự bước và một cái bẫy đã biết

Đặt bước `--stage stats` **sau** `--stage all` là bắt buộc: `stats` đọc `data/marts/` và `warehouse/olist.duckdb`, mà chỉ `--stage all` mới dựng ra chúng.

Nhưng đặt nó **trước** bước test lại mở đúng lỗ hổng đã ghi ở `TD-09`: một test đơn vị đọc `data/reports/analysis.json` sẽ xanh trong CI vì bước `stats` vừa sinh tệp, trong khi trên máy mới clone nó vẫn đỏ. Vì vậy:

- Bước `--stage stats` đứng sau `--stage all` và trước test — đúng như trên.
- Bộ test **không** được thêm phụ thuộc mới vào `data/reports/analysis.json`; test nào cần tệp thì tự dựng tệp trong thư mục tạm. Đây là điều kiện nghiệm thu của Code Generation, không phải việc của CI.

## Không thay đổi

- **Không thêm job, không tách workflow.** Một workflow một job đang chạy ổn; thêm job song song chỉ làm tăng thời gian chờ khởi động.
- **Không thêm cổng mới.** Cổng phủ 80% và `ruff` đã là cổng; thêm cổng nữa là thêm thứ để hạ ngưỡng sau này.
- **Không có bước deploy.** Không có môi trường để deploy tới.

## Chuỗi xác nhận cục bộ

CI không thay chuỗi bốn bước của nhóm (`memory/project.md`, `## Deployment`): bộ test nhanh → `--stage all` → `--stage stats` → mở dashboard.

## Điều phải kiểm khi viết mã

- Một test đọc `ci.yml` và khẳng định cả hai danh sách trigger có mặt nhánh đang làm — đọc từ `git branch --show-current` là không tất định trong CI detached HEAD, nên test so với hằng danh sách trong `ci.yml` chứ không so với nhánh hiện tại.
- Một test đọc `ci.yml` và khẳng định mỗi tệp nguồn mới của đơn vị có mặt trong danh sách `ruff format --check`.
- Một test khẳng định `stats` có mặt ở cả `STAGES` và `choices` của CLI.
