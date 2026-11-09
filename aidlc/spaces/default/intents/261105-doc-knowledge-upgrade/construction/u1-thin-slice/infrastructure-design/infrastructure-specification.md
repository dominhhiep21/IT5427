# Infrastructure Specification — u1-thin-slice

Nguồn: `nfr-design/` (`performance-design.md`, `security-design.md`, `scalability-design.md`, `reliability-design.md`, `observability-design.md`, `logical-components.md`), `functional-design/functional-spec.md`, `inception/domain-design/components.md`, `inception/contract-design/contract-summary.md` (C8, C9).

Đơn vị: `u1-thin-slice`. Kết luận trước khi vào bảng: **đơn vị này không cấp phát tài nguyên đám mây nào.** Toàn bộ hạ tầng là một máy local, một tiến trình Python, một thư mục dữ liệu — nên tài liệu này chủ yếu ghi **cái gì không tồn tại và vì sao**, để bước sau không dựng thêm thứ không ai dùng.

## 1. Deployment

| Facet | Choice | Rationale |
|---|---|---|
| Compute model | Một tiến trình Python duy nhất chạy trong `.venv` của repo, gọi bằng `python -X utf8 -m src.dashboard` | Một người dùng, một máy; container hay serverless chỉ thêm tầng đóng gói mà không mua được gì (`scalability-design.md` ADR-U1-SC1) |
| Networking topology | Loopback `127.0.0.1:8050`, lấy `host`/`port` từ `config.yaml`; tab "Tích hợp" không có lời gọi mạng nào. **Ngoại lệ có điều kiện, nằm ở đường ống chứ không ở tab:** bước `integrate` của `--stage all` gọi `IbgeClient.fetch_states()`; nếu cache `dataset/external/ibge/` hợp lệ thì đó là lần đọc cache, nếu cache thiếu/hỏng hoặc chạy `--refresh-ibge` thì có **một** lời gọi HTTPS tới IBGE (timeout 10 giây, thử lại 2 lần) và ghi cache mới vào `dataset/external/ibge/` | `security-design.md` ADR-U1-S1 cho phần loopback; phần IBGE là hành vi có sẵn của pipeline, được ghi ở đây thay vì nói "không egress" cho gọn — xem quy tắc giữ `dataset/` bất biến ở §3 |
| Storage strategy | `dataset/` CSV chỉ đọc **trừ một ngoại lệ đã biết**: `dataset/external/ibge/` là cache tham chiếu do pipeline ghi khi cache thiếu hoặc khi chạy `--refresh-ibge`; `data/` Parquet, `warehouse/olist.duckdb`, `logs/` JSONL, `inbox/` là sản phẩm sinh ra và bị `.gitignore`; tab "Tích hợp" dùng DuckDB **in-memory**, không mở `warehouse/` | `performance-design.md` ADR-U1-P3; `logical-components.md` vùng hỏng D4; quy tắc bảo vệ `dataset/` ở §3 |
| Environments | **Một** môi trường local. Không dev/staging/production, không parity | `team.md` mục Deployment ghi rõ chưa có môi trường triển khai nào; thêm môi trường là thay đổi phạm vi |
| IaC approach | Không CDK/Terraform/CloudFormation. "Hạ tầng như mã" ở đây là `requirements.txt` (ghim phiên bản) + `config.yaml` + ba lệnh dựng môi trường trong `README.md` | Không có tài nguyên đám mây nào để mô tả bằng IaC; phần tái lập được là môi trường Python và thư mục dữ liệu |
| Dựng lại môi trường | `python -m venv --system-site-packages .venv` → `.venv/Scripts/pip install -r requirements.txt` → `python -X utf8 -m src.pipeline run --stage all` | `README.md` hiện có; `requirements.txt` hiện ghim 10 gói, trong đó có `ruff==0.17.4` và `dash-mantine-components==2.8.1` |
| Resource sizing | Máy 8 GB RAM, ổ cục bộ; đỉnh bộ nhớ của tab mới dưới 120 MB (ước tính ở `scalability-design.md` ADR-U1-SC3) | Một tiến trình, một bộ dữ liệu 99.441 dòng |
| Process supervision | Không service manager, không systemd/Task Scheduler. Chạy tay, dừng bằng `Ctrl+C` | Một người dùng; dịch vụ chạy nền là hạ tầng không ai bảo trì |
| Đồng hồ và múi giờ | Nhật ký ghi UTC (ISO-8601, hậu tố `Z`); giao diện hiện ngày theo giờ máy | Giữ đúng `src/common/logging.py` và masthead hiện có |

## 2. Infrastructure Services

| Service | Role | Configuration | Notes |
|---|---|---|---|
| Python 3.13 (`.venv`) | runtime | Venv tạo bằng `--system-site-packages`; `requirements.txt` hiện ghim 10 gói (có `ruff`, `dash`, `dash-mantine-components`) | Không cài gì vào môi trường Python toàn cục |
| DuckDB 2.0.0 (in-memory) | database | `duckdb.connect()` không đường dẫn; đăng ký DataFrame `don_hang`; đóng trong `finally` | Chỉ dùng cho truy vấn của tab mới; không khoá tệp, không trạng thái sống giữa hai lần chạy |
| DuckDB 2.0.0 (tệp `warehouse/olist.duckdb`) | database | View trỏ Parquet bằng đường dẫn tuyệt đối | **Không** thuộc đường của tab mới; ba tab cũ dùng; phải đóng dashboard trước khi chạy `integrate` |
| Hệ tệp cục bộ (NTFS) | storage | Đọc/ghi UTF-8 tường minh; `dataset/` chỉ đọc; sản phẩm vào `data/`, `warehouse/`, `logs/` | Bốn thư mục sinh ra bị `.gitignore`; "triển khai lại từ đầu" = xoá bốn thư mục và chạy lại `--stage all` |
| Dash dev server (Werkzeug) | web server | `run(host, port)` từ `config.yaml`; `debug=False`; không TLS | Không đặt sau reverse proxy; không cần vì chỉ loopback |
| pandas 2.2.3 | compute library | `read_csv` với `usecols` 4 cột và `dtype=str` | `performance-design.md` ADR-U1-P2 |
| ~~Cache (Redis/Memcached)~~ | cache | **Không dùng** | Bộ nhớ đệm nạp là biến cấp tiến trình (`performance-design.md` ADR-U1-P1); thêm Redis cho một tiến trình là hạ tầng thừa |
| ~~Message queue~~ | queue | **Không dùng** | Không có xử lý bất đồng bộ (`scalability-design.md` ADR-U1-SC4) |
| ~~CDN / DNS / load balancer~~ | network | **Không dùng** | Không có lưu lượng từ ngoài |
| ~~Secrets manager~~ | secrets | **Không dùng** | Không có bí mật nào (`security-design.md` SR-U1-2) |
| ~~Object storage / backup~~ | storage | **Không dùng** | Dữ liệu gốc bất biến và có thể tải lại; `reliability-design.md` ADR-U1-R4 |

## 3. Shared Infrastructure

Chỉ có tám tài nguyên dùng chung giữa các đơn vị; không có tài nguyên nào cần cấp phát.

| Shared Resource | Owner Unit | Consumer Units | Access Boundary |
|---|---|---|---|
| `config/mediated-schema.yaml` | U1 | U2 (đọc), U3 và U5 (gián tiếp qua U2) | Đọc; chỉ thêm thực thể/trường (C8), không đổi tên `don_hang` |
| `config/integration-tab.yaml` | U1 | U6 | Đọc; chỉ thêm thẻ/callback/vùng, không đổi `tab_id` hay `result_region_ids` đang có (C9) |
| `logs/` | Hạ tầng dự án (không đơn vị nào sở hữu riêng) | Pipeline và dashboard cùng ghi nối | Ghi nối một dòng một lời gọi; pipeline dọn còn 10 tệp gần nhất (§5) |
| `config.yaml` | Dự án | Mọi đơn vị | Chỉ đọc; đọc một lần thành `AppConfig` bất biến |
| `dataset/` (9 CSV nguồn) | Dự án (nguồn bất biến) | Pipeline, U1, U4 | **Chỉ đọc**; xem quy tắc bảo vệ dưới bảng |
| `dataset/external/ibge/` | Dự án (cache tham chiếu) | `integrate` của pipeline | Đọc khi có cache; **ghi** `estados.json` + `metadata.json` khi cache thiếu hoặc khi chạy `--refresh-ibge` |
| `.venv` + `requirements.txt` | Dự án | Mọi đơn vị | Chỉ đọc; mọi gói mới phải ghim kèm lý do |
| `data/marts/` và `warehouse/` | Pipeline (`integrate`) | Ba tab cũ, `KpiReconciler` | Chỉ `integrate` ghi; tab "Tích hợp" và toàn bộ đơn vị này không mở đường ghi nào vào đây |

**Quy tắc bảo vệ `dataset/`** — điều này phải nói chính xác, vì câu "không có đường ghi nào" là sai:

1. Chín tệp CSV nguồn trong `dataset/` là **bất biến**; không mã nào ghi vào chúng.
2. `dataset/external/ibge/` là **cache**, không phải dữ liệu nguồn, và là chỗ duy nhất trong `dataset/` được ghi. Hôm nay cache đã commit hợp lệ (27 bang, 5 vùng) nên `fetch_states(refresh=False)` là lần đọc cache và **không có** lời gọi mạng.
3. Trong CI, workflow **không** truyền `--refresh-ibge`, nên nó chỉ đọc cache đã commit. Diễn biến thật khi cache hợp lệ: `fetch_states(refresh=False)` trả cache, không có lời gọi mạng nào. Diễn biến khi cache **thiếu hoặc hỏng**: hàm này sẽ gọi HTTPS tới IBGE và ghi `estados.json` + `metadata.json` vào `dataset/external/ibge/`; nếu lời gọi đó thất bại, nó dùng lại cache cũ với một `WARNING`, và chỉ khi không còn cache dùng được thì pipeline mới đỏ. Vì vậy câu đúng là: **CI cần mạng chỉ khi cache đã commit mất hoặc hỏng**, và đó là tín hiệu đúng để người chạy xem lại cache chứ không phải lỗi cần che.
4. Việc chuyển `ibge_dir` ra khỏi `dataset/` (ví dụ sang `data/external/ibge/`) là thay đổi **đúng hướng nhưng nằm ngoài phạm vi lát cắt**: nó chạm `config.yaml`, `src/config.py`, `docs/runbook.md` và đường của ba tab cũ. Ghi thành việc cần làm ở `memory.md` của bước này, không tự làm trong đơn vị này.

## 4. Chi phí và giới hạn

Không có hoá đơn đám mây. Chi phí của đơn vị này là 0 đồng tăng thêm: nó chạy trên máy đã có, dùng thư viện đã cài, không tạo tài nguyên nào có thể phát sinh phí.

| Hạng mục | Hiện tại | Ngưỡng cần xử lý | Cách xử lý |
|---|---|---|---|
| Dung lượng `dataset/` | ≈ 120 MB, bất biến | — | Không tăng trong đợt này |
| Dung lượng `data/` + `warehouse/` | Vài chục MB, sinh lại được | Vượt 2 GB | Xoá và chạy lại `--stage all`; không có gì quý vì đều dẫn xuất |
| Dung lượng `logs/` | Vài MB cho 10 lần chạy | 10 tệp là mức giữ | Pipeline dọn còn 10 tệp gần nhất ở cuối mỗi lần chạy (Q3 = B) |
| Bộ nhớ tiến trình | Dưới 120 MB khi mở tab | 1 GB | Xem lại `scalability-design.md` ADR-U1-SC3 |

## 5. Vòng đời của `logs/` (Q3 = B)

| Khía cạnh | Quyết định |
|---|---|
| Ai dọn | Chính lần chạy pipeline, ở bước kết thúc (sau khi đã ghi sự kiện `summary`) |
| Giữ bao nhiêu | 10 tệp `logs/*.jsonl` mới nhất theo thời điểm sửa |
| Xoá gì | Tệp `.jsonl` cũ hơn ngưỡng; **không** xoá thư mục, không xoá tệp khác |
| An toàn | Không bao giờ xoá tệp mà lần chạy hiện tại đang ghi; nếu `logs/` có ít hơn 10 tệp thì không làm gì |
| Lỗi khi dọn | Ghi `WARNING integration.logs.prune_failed` và **không** làm hỏng lần chạy — dọn nhật ký là việc phụ, không phải kết quả |
| Quan sát | Sự kiện `integration.logs.pruned` với `kept`, `deleted` để biết đã dọn gì |

**Thay thế một quyết định trước đó:** Q3 = B đảo ngược câu "không xoay vòng tệp nhật ký tự động" trong `observability-design.md` ADR-U1-O1 (mục "Điều không làm"). Từ nay việc dọn là hành vi có chủ đích, nên ADR-U1-O1 được đọc lại theo nghĩa: *không* xoay vòng theo ngày/dung lượng, *có* giữ trần 10 tệp. Hai sự kiện `integration.logs.pruned` và `integration.logs.prune_failed` là hai sự kiện **bổ sung** cho danh mục mười sự kiện ở `observability-design.md` §2; chúng giữ đúng tiền tố `integration.` và sẽ được thêm vào danh mục đó ở bước sinh mã (tài liệu của bước trước đã đóng băng, nên phần bổ sung được khai ở đây).

**Tài liệu phải sửa trong cùng thay đổi** (nếu không, tài liệu vận hành sẽ nói sai):

| Tệp | Sửa gì |
|---|---|
| `README.md` | Thêm mục CI: workflow chạy gì, chạy ở đâu, và một dòng nói `logs/` chỉ giữ 10 lần chạy gần nhất |
| `docs/runbook.md` | Mục "Pipeline không chạy" đang trỏ người đọc tới tệp mới nhất trong `logs/`; thêm một câu rằng tệp cũ hơn bị dọn tự động nên không tìm lại được sau 10 lần chạy |
| `requirements.txt` | Ghim `ruff` kèm lý do (TS-U1-3) — điều kiện để bước lint của CI chạy được |
| `.github/workflows/ci.yml` | Tệp mới của Q2 = B (`cicd-pipeline.md` §2) |
| `CHANGELOG.md` | Mục `v0.1.0` cho mốc nộp (Q1 = C, `cicd-pipeline.md` §3) |

Ghi chú: dashboard ghi nối vào tệp mới nhất (`observability-design.md` ADR-U1-O1), và tệp mới nhất luôn nằm trong nhóm được giữ — nên việc dọn không cắt mất tệp đang được ghi.

## 6. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Máy đích là máy 8 GB đang dùng, ổ cục bộ, không có phần mềm diệt virus quét `logs/` liên tục | Giả định — nếu có, việc dọn có thể gặp `PermissionError` và được nuốt như §5 |
| A2 | Repo được đặt trong một thư mục mà đường dẫn có ký tự tiếng Việt | Đúng với workspace hiện tại; vì vậy mọi lệnh chạy `-X utf8` |
| Q1 | Có cần thêm `Task Scheduler`/`systemd` để tự chạy dashboard khi khởi động máy không? | Không — ngoài phạm vi đợt này và không ai yêu cầu; nếu cần thì là thay đổi phạm vi |
