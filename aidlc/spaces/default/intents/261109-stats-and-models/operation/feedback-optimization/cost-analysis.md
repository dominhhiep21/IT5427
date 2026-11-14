# Cost Analysis

Nguồn: `../deployment-execution/deployment-log.md`, `../performance-validation/test-results.md`, `../observability-setup/alarms.md`, `../incident-response/runbooks.md`, `codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`.

## Hoá đơn đám mây là 0 — nên "chi phí" phải định nghĩa lại

Không có tài khoản đám mây, không có máy chủ thuê, không có dịch vụ trả tiền. Nếu báo cáo này dừng ở "chi phí = 0" thì nó vô dụng, vì dự án **có** chi phí thật — chỉ là chi phí không hiện trên hoá đơn.

Ba loại chi phí thật, đo được:

| Loại | Đơn vị | Đo được |
|---|---|---|
| Dung lượng đĩa | MB | có |
| Thời gian CI | giây/phút mỗi lần push | có |
| Thời gian người làm mỗi chuỗi xác nhận | phút | có |

## Dung lượng đĩa

| Thư mục | Dung lượng | Số tệp | Bản chất |
|---|---|---|---|
| `data/` | **139,25 MB** | 40 | sinh ra, bị `.gitignore` |
| `dataset/` | **120,34 MB** | 11 | gốc, bất biến, **có** trong git |
| `warehouse/` | 0,26 MB | 1 | sinh ra (một tệp DuckDB) |
| `logs/` | 0,01 MB | 10 | sinh ra, tự dọn còn 10 tệp |
| `inbox/` | 0 MB | 0 | rỗng khi không có batch |
| **Tổng trên đĩa** | **~260 MB** | — | — |

Điều đáng chú ý: `data/` (139 MB) **lớn hơn** dữ liệu gốc (120 MB) — bản làm sạch và mart chiếm nhiều hơn nguồn. Nhưng `data/` là sinh ra và dựng lại được trong 28,86 s, nên chi phí lưu trữ thật của repo trong git chỉ là **120 MB** (`dataset/`, trong đó `dataset/external/ibge/` là cache 27 bang).

Không có đề xuất nén hay xoá: 139 MB trên một máy là không đáng kể, và mọi phép nén đều đổi lấy thời gian dựng lại.

## Thời gian CI — chi phí lớn nhất, và nó nằm ở một chỗ

| Bước | Thời gian | Chiếm |
|---|---|---|
| `pytest --cov=src --cov-fail-under=80` (toàn bộ) | **281,85 s** | **~80%** |
| `run --stage all` | 28,86 s | ~8% |
| `pytest -m "not slow"` | 18,62 s | ~5% |
| `run --stage stats` | 3,5 s | ~1% |
| `ruff check` + `ruff format --check` | ~2 s | <1% |
| Nạp `config/integration-sources.yaml` (smoke) | ~3 s | <1% |
| **Một lần push** | **~340 s ≈ 5,7 phút** | 100% |

Một quan sát: **bộ nhanh chạy hai lần** — một lần riêng (18,62 s, để fail nhanh) và một lần nữa bên trong lệnh đo phủ. Đó là **18,62 s trùng lặp**, khoảng 5% tổng thời gian CI.

## Đề xuất tối ưu, kèm giá phải trả

| # | Đề xuất | Tiết kiệm | Giá phải trả | Khuyến nghị |
|---|---|---|---|---|
| C-1 | Bỏ bước `pytest -m "not slow"` riêng, chỉ chạy lệnh đo phủ | 18,6 s (~5%) | mất fail-fast: một test đỏ phải chờ hết 282 s mới biết | **Không làm.** 18 giây không đáng mất phản hồi nhanh |
| C-2 | Sửa `TD-09` để bộ nhanh hermetic, bỏ được bước `run --stage all` | 28,9 s (~8%) | phải sửa 6 test dashboard để tự dựng dữ liệu thay vì đọc `warehouse/` | **Nên làm ở đợt sau**, không phải vì 29 s mà vì trên máy mới clone bộ "nhanh" hiện vẫn đỏ |
| C-3 | Giảm thời gian bộ `slow` (281 s) | phần lớn nhất | mỗi test `slow` chạy cả pipeline trên dữ liệu thật; cắt bớt là bớt chốt hồi quy | **Không làm.** Đây là chốt hồi quy dữ liệu, không phải chi phí lãng phí |
| C-4 | Cache `data/marts/` bằng `actions/cache` | ~10 s | cache sai làm CI xanh trên dữ liệu cũ — đúng loại lỗi tệ nhất | **Không làm.** Rủi ro lớn hơn lợi ích |

Tổng tiết kiệm khả dĩ nếu làm cả bốn: **~60 s**, tức CI từ 340 s xuống 280 s. Đổi lại là mất fail-fast hoặc thêm một nguồn trạng thái có thể cũ. **Kết luận: không tối ưu.** 5,7 phút mỗi lần push là chi phí chấp nhận được, và ba trong bốn đề xuất đều đổi một chốt đúng lấy vài giây.

## Thời gian người làm mỗi chuỗi xác nhận

Chuỗi bốn bước của `project.md` (`## Deployment`), đo trên lần chạy thật:

| Bước | Thời gian |
|---|---|
| `pytest -m "not slow"` | 18,62 s |
| `run --stage all` | 28,86 s |
| `run --stage stats` | 3,5 s |
| Mở dashboard và xem bằng mắt | ~60 s (thao tác người) |
| **Tổng** | **~1,9 phút**, trong đó 85% là thời gian chờ máy |

Một điểm đáng giữ: người làm dành **1,9 phút mỗi lần** cho chuỗi này, nhưng phần lớn là chờ. Nếu chuỗi này chạy ba lần mỗi ngày thì đó là **6 phút/ngày** — nhỏ. Đừng tự động hoá nó: tự động hoá sẽ lấy đi đúng bước 4 (nhìn bằng mắt), là bước duy nhất bắt được lỗi giao diện.

## Điều không có, và không cần có

Không AWS Cost Explorer, không Trusted Advisor, không right-sizing (không có instance để chỉnh), không savings plan, không tag chi phí. Không có gì để phân bổ — chỉ có một máy và một người.
