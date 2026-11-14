# Runbooks

Nguồn: `../deployment-pipeline/rollback-runbook.md`, `../observability-setup/alarms.md`, `../../construction/build-and-test/test-results.md`, `../../construction/{u1-statistics,u2-model,u3-display}/nfr-design/reliability-design.md`, `../../construction/{u1-statistics,u2-model,u3-display}/infrastructure-design/infrastructure-specification.md`, `docs/runbook.md`.

## Bảy sự cố có thật, không phải giả định

Mỗi mục dưới đây đã xảy ra ít nhất một lần trong đời dự án, hoặc đã được ghi nhận là rủi ro có cơ chế rõ ràng. Không có runbook cho sự cố chưa từng xảy ra và không có cơ chế.

### RB-1 — `--stage all` hỏng vì khoá DuckDB

**Dấu hiệu:** lỗi mở `warehouse/olist.duckdb`, thường sau khi để dashboard mở.

**Nguyên nhân:** tiến trình dashboard giữ khoá tệp.

**Xử lý:** đóng dashboard, chạy lại `run --stage all`. Không xoá tệp khoá bằng tay.

**Phòng:** quy trình bắt buộc đóng dashboard trước khi chạy chuỗi.

### RB-2 — Tab hiện `loi` sau khi chạy lại

**Dấu hiệu:** tab báo tệp hỏng hoặc sai phiên bản.

**Nguyên nhân:** tệp báo cáo của phiên bản cũ, hoặc bị sửa tay.

**Xử lý:** `run --stage stats` sinh lại. Nếu vẫn `loi`, đọc thông điệp — nó nêu đường dẫn và phiên bản đọc được.

### RB-3 — Số KPI lệch sau khi cài phụ thuộc

**Dấu hiệu:** `KpiReconciler` đỏ, hoặc bộ `slow` đỏ ở các test baseline.

**Nguyên nhân:** `numpy` bị nâng khi cài `scikit-learn` — đã xảy ra thật và đã được chặn bằng ghim.

**Xử lý:** `pip show numpy` — phải là 2.2.1. Nếu khác, ghim lại trong `requirements.txt`, cài lại, chạy lại bộ `slow`.

### RB-4 — Báo cáo `mot-phan`

**Dấu hiệu:** tab hiện phần thống kê nhưng ghi "chưa chạy bước mô hình".

**Nguyên nhân:** bước mô hình chưa chạy hoặc đã hỏng.

**Xử lý:** chạy lại `run --stage stats`. Nếu bước mô hình hỏng, đọc `code-summary.md` của U2 để biết điều kiện nào không đạt (cỡ mẫu, tập kiểm tra một lớp, ngưỡng không hội tụ).

### RB-5 — AUC tụt hoặc `auc_below_target` bật

**Dấu hiệu:** tab hiện "không đạt mốc 0,70".

**Nguyên nhân:** hiện tại là trạng thái nền (0,5133), không phải sự cố mới.

**Xử lý:** không có — nó là nội dung báo cáo, không phải lỗi hệ thống. Nếu AUC **tụt thêm** so với 0,5133, đó mới là hồi quy: kiểm danh sách đặc trưng và cỡ mẫu.

### RB-6 — CI đỏ ở bước `ruff format --check`

**Dấu hiệu:** bước định dạng đỏ dù `ruff check` xanh.

**Nguyên nhân:** tệp mới chưa được thêm vào danh sách khai tay trong `ci.yml` và `NEW_FILES`.

**Xử lý:** thêm tệp vào **cả hai**, chạy lại. Test `test_ci_config.py` sẽ đỏ nếu chỉ sửa một nơi.

### RB-7 — Mọi lệnh hỏng ngay khi khởi động trên một checkout chỉ-đọc

**Dấu hiệu:** lỗi tạo thư mục hoặc lỗi ghi tệp **trước khi** tầng nào kịp chạy, thường nổ từ `load_config`.

**Nguyên nhân:** `load_config` tạo **11 thư mục** ở gốc workspace lúc khởi động — `data/`, `warehouse/`, `logs/`, `inbox/`, `dataset/external/ibge/` và các thư mục con. Yêu cầu về quyền ghi này là `INDU-1` trong `infrastructure-specification.md` của U3: tiến trình cần quyền ghi ở **gốc workspace**, không chỉ trong `logs/`.

**Xử lý:** cấp quyền ghi ở gốc workspace (hoặc chép sang thư mục ghi được), rồi chạy lại. Không sửa `load_config` để bỏ tác dụng phụ — tạo sẵn thư mục là chủ ý đã chốt.

**Phòng:** môi trường duy nhất là máy người làm (xem `../environment-provisioning/environment-inventory.md`), nên điều kiện này chỉ vỡ khi chạy trong container, CI runner lạ, hoặc thư mục chia sẻ chỉ-đọc.

## Điều không có runbook

Không có runbook cho sự cố mạng, dịch vụ ngoài, hoặc mất dữ liệu — ba loại đó không tồn tại trong hệ thống này.
