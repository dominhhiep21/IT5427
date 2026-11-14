# Drift Report

Nguồn: `../deployment-execution/deployment-log.md`, `../deployment-execution/health-check-report.md`, `../performance-validation/test-results.md`, `../observability-setup/dashboards.md`, `../incident-response/incident-plan.md`, `../../construction/u3-display/infrastructure-design/infrastructure-specification.md`, `.github/workflows/ci.yml`, `README.md`, `docs/runbook.md`, `requirements.txt`, `pytest.ini`.

## Không có hạ tầng khai báo, nên "drift" phải định nghĩa lại

AWS Config phát hiện drift bằng cách so tài nguyên thật với một bản khai báo. Dự án này **không có bản khai báo nào** để so: hạ tầng là một thư mục và một `.venv`, không có CloudFormation, không có Terraform, không có trạng thái mong muốn.

Nhưng vẫn có thứ trôi được, và nó trôi thật: **tài liệu so với cấu hình**, và **dữ liệu sinh ra so với lần chạy trước**. Hai loại đó mới là drift có ý nghĩa ở đây.

## Bảy phép đối chiếu đã chạy

| # | Đối chiếu | Cách kiểm | Kết quả |
|---|---|---|---|
| D1 | `ci.yml` ↔ mục `## CI` của `README.md` | đọc cả hai, so từng bước và từng nhánh | **khớp** — 9 bước, 3 nhánh, thứ tự đúng |
| D2 | danh sách `ruff format --check` trong `ci.yml` ↔ khối lệnh ở mục `## Lint và định dạng` của `README.md` | đọc cả hai | **TRÔI** — xem bên dưới |
| D3 | `docs/runbook.md` ↔ hệ thống hiện có | tìm `stats`, `analysis.json`, tab thứ năm trong runbook | **TRÔI** — xem bên dưới |
| D4 | `pytest.ini` marker `slow` ↔ số test thật sự mang marker | `pytest -m "not slow"` báo 12 deselected | **khớp** |
| D5 | `requirements.txt` ↔ bản đang cài | `pip show numpy scipy scikit-learn` | **khớp** — numpy 2.2.1, scipy 1.15.2, scikit-learn 1.6.1 |
| D6 | dữ liệu sinh ra ↔ lần chạy trước | dựng lại `run --stage all` + `run --stage stats`, đọc lại báo cáo | **không trôi** — cả bốn con số giống hệt |
| D7 | danh sách tệp trong `ci.yml` ↔ tuple `NEW_FILES` của `tests/unit/test_ci_config.py` | chạy test | **khớp** — test canh, lệch là đỏ |

## DR-1 — `README.md` chỉ dẫn lệnh định dạng hẹp hơn CI

**Ở đâu:** `README.md` mục `## Lint và định dạng`, khối lệnh:

```
.\.venv\Scripts\ruff format --check src/integration
```

**Trong khi:** `ci.yml:35` chạy `ruff format --check` trên **34 mục** (hai trong đó là thư mục `src/integration` và `src/linkage`), gồm toàn bộ mã của đợt này — `src/analytics/report.py`, `statistics.py`, `model.py`, `service.py`, `src/dashboard/analysis_tab.py`, `src/common/kpis.py` và các test mới.

**Vì sao nguy hiểm:** người làm theo README sẽ thấy lệnh xanh trong khi ba mô-đun mới của đợt **chưa hề được kiểm định dạng**. Đây không phải lỗi đánh máy: dòng chú thích ngay dưới nói "chạy trên mã của đợt nâng cấp" — đúng ý định, sai danh sách, và danh sách đã mở rộng qua ba đợt mà khối lệnh thì không.

**Không CI nào bắt được:** `ruff check .` chạy toàn repo nên vẫn xanh; chỉ phần `format --check` bị thu hẹp, và nó chỉ đỏ nếu chạy đúng danh sách trong `ci.yml`.

**Sửa:** thay khối lệnh bằng đúng danh sách của `ci.yml`, hoặc tốt hơn — nói "xem danh sách trong `ci.yml:35`" thay vì chép lại, vì bản chép thứ hai chính là thứ vừa trôi.

## DR-2 — `docs/runbook.md` không có bước nào cho tầng `stats`

**Ở đâu:** `docs/runbook.md` có mục "Dashboard trống/lỗi" chỉ dẫn `run --stage integrate` để tạo mart/catalog. Không có mục nào nhắc `run --stage stats`, `data/reports/analysis.json`, hay tab "Kết quả phân tích".

**Vì sao nguy hiểm:** làm đúng runbook sẽ **không** làm tab hết `rong` — vì `--stage integrate` không sinh `analysis.json`. Người vận hành sẽ kết luận dashboard hỏng trong khi nó đang nói đúng sự thật: chưa có báo cáo.

**Đây là drift đã biết và bị bỏ lại:** người soát `infrastructure-specification.md` của U3 đã nêu đúng điểm này ở **R-07**, ở cả hai vòng soát, và nó vẫn ở trạng thái `Unresolved` khi đơn vị đóng. Ghi lại ở đây vì nó là ví dụ sạch nhất của loại trôi mà dự án này thật sự có: một phát hiện đúng, được ghi, rồi không ai đóng.

**Sửa:** thêm một mục vào `docs/runbook.md` cho trạng thái `rong` — chạy `run --stage stats` rồi tải lại — và một mục cho `mot-phan`.

## Không trôi — và bằng chứng

Ba thứ thường trôi ở dự án khác nhưng ở đây không:

| Thứ | Vì sao không trôi |
|---|---|
| **Dữ liệu** | Dựng lại toàn bộ từ `dataset/` cho ra đúng `late_rate 0,0811`, `auc 0,5133`, `threshold 0,4`, `64.322 + 32.156`. `KpiReconciler` khẳng định lại năm KPI trong cùng lần chạy |
| **Docker / môi trường** | Không có image, không có container, không có `environment.yml`. Ba bản đã ghim (`numpy`, `scipy`, `scikit-learn`) được kiểm bằng `pip show` |
| **Hạ tầng đám mây** | Không có hạ tầng để trôi. Một thư mục, một `.venv`, một quy trình |

## Hai mục này không phải "nợ kỹ thuật", chúng là tài liệu sai

Phân biệt quan trọng: `TD-09` là nợ kỹ thuật — mã đúng nhưng thiết kế chưa hermetic. DR-1 và DR-2 là **tài liệu chỉ dẫn sai**. Một tài liệu sai tệ hơn không có tài liệu: không có thì người ta đi tìm hiểu, có mà sai thì người ta làm theo và tin mình đã đúng.

Cả hai đều rẻ để sửa (một khối lệnh, một mục runbook) và cả hai đều **không** được canh bởi test nào. Ghi vào `feedback-loop.md` để đợt sau không mở lại từ đầu.
