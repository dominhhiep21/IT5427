# CI/CD Pipeline — u1-thin-slice

Nguồn: `nfr-design/` (`reliability-design.md` §4.1, `observability-design.md`, `security-design.md`, `performance-design.md`, `scalability-design.md`, `logical-components.md`), `functional-design/functional-spec.md`, `inception/domain-design/components.md`, `inception/contract-design/contract-summary.md`.

Đơn vị: `u1-thin-slice`. Quyết định đã chốt: **Q1 = C** (tag `v0.x` + `CHANGELOG.md`) và **Q2 = B** (một workflow CI tối thiểu, không chạy bộ `slow`). Pipeline ở đây có hai đường: đường **phát hành local** (đường chính, đã có từ trước) và đường **CI** (mới, chỉ để bắt lỗi sớm). CI không thay đường local và không phải cổng duy nhất.

## 1. Hai đường, một bộ cổng

| Cổng | Lệnh | Đạt khi | Local | CI |
|---|---|---|---|---|
| Lint | `ruff check .` | 0 vi phạm | Có | Có |
| Định dạng | `ruff check .` + `ruff format --check src/integration tests/unit/test_integration_*.py tests/unit/test_log_pruning.py` | 0 vi phạm lint; 0 tệp cần định dạng trong phạm vi | Có | Có — phạm vi định dạng hẹp hơn `.` vì 35 tệp cũ chưa qua `ruff format` và `team.md` cấm một lần format toàn repo lẫn vào thay đổi chức năng; mã cũ dọn theo từng tệp khi có người sửa tới |
| Pipeline | `python -X utf8 -m src.pipeline run --stage all` | Mã thoát 0; `QualityGate` và `KpiReconciler` xanh | Có | Có (xem §2) |
| Bộ test nhanh | `python -X utf8 -m pytest -m "not slow"` | Xanh | Có | Có |
| Bộ test chậm | `python -X utf8 -m pytest -m slow` | Xanh | Có, trước khi phát hành | **Không** (Q2 = B) |
| Độ phủ | `python -X utf8 -m pytest --cov=src --cov-fail-under=80` | ≥ 80% | Có, trước khi phát hành | **Không** — lý do ngay dưới bảng |
| Kiểm bằng mắt | `python -X utf8 -m src.dashboard`, mở tab "Tích hợp" | Vùng `don-theo-thang` hiện đúng số liệu và trạng thái | Có, trước khi phát hành | Không thể |

Thống nhất một cách gọi Python trong cả bảng: `python -X utf8` (trên Windows, `.venv\Scripts\python.exe` là thứ `python` trỏ tới sau khi kích hoạt venv; ghi cứng đường dẫn chỉ để dễ đọc, không phải yêu cầu kỹ thuật).

**Vì sao cổng độ phủ 80% chỉ chạy ở local, không vào CI.** Ngưỡng 80% là điều kiện của bước xác nhận trước khi phát hành, và nó cần cả bộ `slow` để có nghĩa — bộ `slow` bị Q2 = B loại khỏi CI. Đưa `--cov-fail-under` vào CI mà chỉ chạy bộ nhanh sẽ đo độ phủ trên một nửa số test và tạo ra một con số khác với con số đã chốt; như thế tệ hơn là không đo. Đánh đổi đã ghi ở `memory.md`: CI có thể xanh trong khi độ phủ tụt, bù lại ngưỡng nằm trong lệnh bắt buộc chạy tay trước mỗi mốc phát hành.

Thứ tự chạy local là thứ tự đã chốt trong `team.md` mục Deployment: bộ nhanh → pipeline → mở dashboard, dừng ngay ở bước đỏ đầu tiên.

## 2. Workflow CI (Q2 = B)

Tệp: `.github/workflows/ci.yml`. Kích hoạt: `push` và `pull_request` trên `main` và `feature/update-ui-ux`. Một job duy nhất trên `windows-2022` (ghim phiên bản, không dùng nhãn trôi `windows-latest`).

| Bước | Việc làm | Vì sao |
|---|---|---|
| 1. Checkout | `actions/checkout` | — |
| 2. Python | `actions/setup-python` với `3.13`, cache theo `requirements.txt` | Cùng phiên bản với máy phát triển |
| 3. Cài đặt | `pip install -r requirements.txt` | Mọi phụ thuộc đã ghim; **bước này chỉ chạy được sau khi `ruff` được ghim vào `requirements.txt`** (việc của bước sinh mã, TS-U1-3) — nếu workflow lên trước, bước 4 đỏ ngay vì không có `ruff` |
| 4. Lint | `ruff check .` và `ruff format --check <phạm vi hẹp ở §1>` | NFR3.1; hỏng nhanh, dưới 30 giây. `ruff check` chạy toàn repo; phần định dạng chỉ chạy trên phạm vi trong `ruff.toml` — mã cũ dọn theo từng tệp |
| 5. Dựng dữ liệu | `python -X utf8 -m src.pipeline run --stage all` | **Bắt buộc**, xem khung dưới; không truyền `--refresh-ibge`. Nếu cache IBGE đã commit hợp lệ thì bước này không gọi mạng; nếu cache mất/hỏng thì nó sẽ gọi IBGE (và ghi lại cache), nên CI cần mạng đúng trong trường hợp đó |
| 6. Test nhanh | `python -X utf8 -m pytest -m "not slow"` | Đúng lựa chọn Q2 = B |

```yaml
# .github/workflows/ci.yml (rút gọn, phần còn lại là cấu hình chuẩn)
jobs:
  ci:
    runs-on: windows-2022
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.13', cache: pip }
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: ruff format --check src/integration tests/unit/test_integration_*.py tests/unit/test_log_pruning.py
      - run: python -X utf8 -m src.pipeline run --stage all
      - run: python -X utf8 -m pytest -m "not slow"
```

**Vì sao có bước 5 — nói rõ vì nó không nằm trong phương án bạn đã chọn.** Bộ test nhanh hiện **không hermetic** (nợ kỹ thuật `TD-09`): năm test trong `tests/unit/test_dashboard_smoke.py` và `test_cli.py::test_main_analyze_stage` cần `warehouse/olist.duckdb` và `data/marts/` đã tồn tại, mà hai thư mục đó bị `.gitignore`. Trên một bản clone sạch, `pytest -m "not slow"` sẽ **đỏ ngay** — CI sẽ đỏ vĩnh viễn và bị bỏ qua, tệ hơn là không có CI.

Ba cách xử lý, và lý do chọn cách 2:

| Cách | Đánh đổi |
|---|---|
| 1. Sửa `TD-09` để bộ nhanh tự dựng fixture | Đúng nhất về lâu dài, nhưng là thay đổi mã ngoài phạm vi lát cắt (năm test + `load_config()`); phải chốt phạm vi trước |
| 2. CI chạy pipeline rồi mới chạy test **(chọn)** | CI chậm thêm khoảng 1–2 phút, nhưng không sửa mã nào và biến CI thành chỗ kiểm luôn `QualityGate`/`KpiReconciler` |
| 3. Bỏ CI | Trái lựa chọn Q2 = B |

Cách 2 cũng là cách duy nhất trong ba cách mà **không** che giấu `TD-09`: nó đặt đúng điều kiện mà bộ nhanh cần, và khi `TD-09` được sửa thì chỉ cần xoá bước 5.

**Vì sao `windows-2022`, không phải `ubuntu-latest`.** Sản phẩm chỉ chạy trên Windows; hai chế độ hỏng của đơn vị này — khoá tệp tạm thời (`reliability-design.md` ADR-U1-R1) và bảng mã console cp1252 — là đặc thù Windows. Chạy CI trên Linux sẽ xanh cho mã có thể đỏ trên máy thật. Ba hệ quả, ghi bằng con số chứ không bằng cảm giác:

- **Chi phí:** runner Windows bị tính **gấp đôi** phút so với runner Linux trên repo riêng tư. Với job khoảng 3–5 phút và vài lần đẩy mỗi ngày, đây vẫn là mức không đáng kể; nếu vượt hạn mức miễn phí thì đó là lúc xem lại, không phải bây giờ.
- **Không cùng hệ điều hành với máy phát triển:** `windows-2022` là Windows **Server** 2022, không phải Windows 10/11. Khác biệt thực tế với đơn vị này là bảng mã console và cách khoá tệp — chấp nhận được vì mã không phụ thuộc tính năng nào chỉ có trên bản desktop.
- **Nhãn trôi:** `windows-latest` đổi image dưới chân pipeline. Vì vậy ghim `windows-2022`, đổi khi cần và đổi có chủ đích, ghi vào `CHANGELOG.md`.

## 3. Phát hành (Q1 = C)

| Khía cạnh | Quyết định |
|---|---|
| Định danh phiên bản | Tag annotate `v0.<n>.<m>` trên nhánh `feature/update-ui-ux` sau khi merge về `main` |
| `CHANGELOG.md` | Ở gốc repo; mỗi mốc một mục `## v0.<n>.<m> — YYYY-MM-DD` với ba nhóm `Thêm`, `Sửa`, `Nội bộ` |
| Khi nào ghi | Trong cùng thay đổi tạo tag; không có tag nào thiếu mục tương ứng |
| Nội dung mục | Viết cho người đọc, không phải danh sách commit: cái gì thay đổi với người dùng trước, chi tiết kỹ thuật sau |
| Mốc nộp | `v0.1.0` là mốc của đợt nâng cấp này; không cần tag cho từng Unit |
| Số phiên bản trong giao diện | Không hiện. Tag và `CHANGELOG.md` là nguồn; thêm số vào masthead là thay đổi giao diện không ai yêu cầu |

Ba quy tắc để tag còn nghĩa: tag chỉ đặt trên commit đã xanh đủ bộ cổng ở §1; tag không bao giờ bị di chuyển sau khi đẩy lên; nếu phải sửa một mốc đã phát hành thì tạo `v0.<n>.<m+1>` chứ không sửa lịch sử.

## 4. Triển khai và quay lui

Chiến lược: **recreate** — dừng tiến trình cũ, dựng lại từ mã nguồn, chạy lại. Không blue-green, không canary, không rolling: những chiến lược đó cần hai môi trường và lưu lượng để chia, cả hai đều không có.

| Bước | Lệnh | Ghi chú |
|---|---|---|
| 1. Dừng | `Ctrl+C` ở cửa sổ dashboard | Bắt buộc trước khi chạy `integrate`: cùng một tệp `warehouse/olist.duckdb` |
| 2. Cập nhật mã | `git checkout <tag>` (hoặc `git pull` trên nhánh làm việc) | — |
| 3. Cài lại | `pip install -r requirements.txt` nếu tệp đổi | — |
| 4. Dựng dữ liệu | `python -X utf8 -m src.pipeline run --stage all` | Sinh `data/`, `warehouse/`, `logs/` |
| 5. Chạy | `python -X utf8 -m src.dashboard` | Bind `127.0.0.1:8050` |
| 6. Kiểm tra khói | Mở tab "Tích hợp", bấm "Chạy truy vấn", thấy vùng `don-theo-thang` hiện số liệu | Nếu vùng báo lỗi, xem bước 4 |

Quay lui: `git checkout <tag trước>` → xoá `data/`, `warehouse/`, `logs/`, `inbox/` → chạy lại bước 4–5. Không có migration cơ sở dữ liệu nào phải đảo, vì mọi thứ trong `warehouse/` đều dẫn xuất từ `dataset/`.

## 5. Bí mật trong CI/CD

Không có. Workflow chỉ dùng `GITHUB_TOKEN` mặc định để checkout; không khai `secrets.*` nào, không có khoá API, không có tệp `.env`. Nếu sau này cần một bí mật, nó phải vào GitHub Secrets chứ không vào `config.yaml`, và phải ghi lý do vào `security-design.md` trước.

Hai `uses:` duy nhất (`actions/checkout`, `actions/setup-python`) được ghim theo major tag. Ghi nhận rủi ro chuỗi cung ứng: muốn chặt hơn thì ghim theo SHA commit; đánh đổi là phải cập nhật tay khi bản mới ra. Chọn major tag để CI còn bảo trì được, và ghi điểm này vào `CHANGELOG.md` khi đổi.

## 6. Điều không dựng

| Không dựng | Vì sao |
|---|---|
| Container / Dockerfile | Một máy, một tiến trình Python; đóng gói thêm một tầng phải bảo trì |
| Artifact registry / bản phát hành đóng gói | "Phát hành" = chạy từ mã nguồn; tag là mốc |
| Môi trường staging/production | Không có môi trường thứ hai (`team.md`) |
| Feature flag | Không có người dùng để bật/tắt dần |
| Triển khai tự động khi merge | Mốc phát hành là việc có chủ đích, không phải hệ quả của một lần push |

## 7. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Repo có thể đẩy lên GitHub | Giả định — nếu chỉ chạy local thì tệp workflow vô hại và chưa bao giờ chạy; đường local vẫn là đường chính |
| A2 | `dataset/` được commit trong repo nên CI có sẵn dữ liệu nguồn | Giả định — cần kiểm khi dựng workflow; nếu `dataset/` không có trong repo, bước 5 phải thêm cách lấy dữ liệu, và đó là quyết định mới |
| A3 | CI chạy dưới 5 phút kể cả bước dựng dữ liệu | Chưa đo; theo dõi ở 10 lần chạy đầu, ghi vào `CHANGELOG` nếu vượt |
| Q1 | Tag đặt trên `main` hay trên nhánh `feature/update-ui-ux`? | Thiết kế chọn **sau khi merge về `main`**, vì tag trên nhánh làm việc dễ trỏ vào commit sẽ bị squash. Nếu bạn muốn tag trước khi merge thì phải nói, vì nó đổi cách ghi lịch sử |
