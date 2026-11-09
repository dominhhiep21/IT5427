# Monitoring Design — u1-thin-slice

Nguồn: `nfr-design/` (`observability-design.md` là nguồn sự thật cho lược đồ nhật ký; `reliability-design.md`, `performance-design.md`, `security-design.md`, `scalability-design.md`, `logical-components.md`), `functional-design/functional-spec.md`, `inception/contract-design/contract-summary.md` (C4), `inception/domain-design/components.md`.

Đơn vị: `u1-thin-slice`. Không có metric tập trung, không tracing, không alerting (`observability-design.md` ADR-U1-O4). Tài liệu này nói rõ **cái gì được đo, đo ở đâu, ngưỡng nào là đỏ, và tín hiệu đỏ đi tới ai** — với hệ một người dùng thì "đi tới ai" luôn là chính người đang chạy máy.

## 1. Metrics & KPIs

| Metric | Source | Threshold | Why it matters |
|---|---|---|---|
| `elapsed_ms` của truy vấn đếm đơn | `QueryRunResult.elapsed_ms`, sự kiện `integration.query.completed` | < 2.000 ms; vượt là `WARNING` | Ngưỡng NFR1.2; cảnh báo sớm trước khi người dùng thấy chậm |
| `elapsed_ms` của lần nạp | sự kiện `integration.load.completed` | < 5.000 ms | Ngưỡng NFR1.3; lần nạp chỉ xảy ra một lần mỗi tiến trình |
| `rows_loaded` / `rows_dropped` | sự kiện `integration.load.completed` | tỉ lệ loại > 1% số dòng nạp là đáng xem | Phát hiện ánh xạ sai hoặc dữ liệu nguồn đổi, trước khi thẻ hiện số lệch |
| `row_count` của kết quả | sự kiện `integration.query.completed` | 0 dòng → trạng thái rỗng, không phải 0 đơn | Phân biệt "không có dữ liệu" với "có dữ liệu bằng 0" (BR1.7) |
| Độ phủ dòng `src/` | `pytest --cov=src` | ≥ 80%, dưới là đỏ | NFR2.1; đo ở lệnh xác nhận, không đo trong sản phẩm |
| Số vi phạm `ruff` | `ruff check`, `ruff format --check` | > 0 là đỏ | NFR3.1 |
| Số tệp `logs/*.jsonl` | đếm thư mục ở cuối lần chạy | ≤ 10 | Giữ dung lượng ổ đĩa có trần (Q3 = B) |
| Thời gian một lần CI | GitHub Actions, thời lượng job | < 5 phút (mục tiêu, không phải cổng) | CI dài quá thì người ta bắt đầu bỏ qua nó |

## 2. Alerts

Không có kênh alerting tự động (không email, không chat, không pager). "Alert" ở đây là **cổng đỏ** — thứ chặn đường và bắt buộc phải nhìn:

| Alert | Condition | Severity | Routes to |
|---|---|---|---|
| Lệnh xác nhận đỏ | `pytest` hoặc `--cov-fail-under=80` thất bại | P1 — chặn | Người đang chạy máy; không được coi thay đổi là xong |
| `quality full` đỏ | `QualityGate` báo vi phạm cấu trúc/số dòng/dị thường | P1 — chặn | Người đang chạy; là bảo đảm NFR5.1 |
| `KpiReconciler` lệch | 5 KPI lệch khỏi baseline quá dung sai | P1 — chặn | Người đang chạy; là bảo đảm NFR5.2 |
| CI đỏ trên nhánh làm việc | Một trong ba bước của workflow thất bại | P1 — chặn merge | Người mở PR; nhánh `feature/update-ui-ux` |
| Truy vấn chậm | `integration.query.slow` xuất hiện trong nhật ký | P3 — ghi nhận | Chỉ nằm trong nhật ký; xem khi thấy thẻ chậm |
| Dọn nhật ký lỗi | `integration.logs.prune_failed` | P3 — ghi nhận | Nhật ký; không chặn lần chạy |

Vì sao không có alert tự động: không có dịch vụ chạy nền nào để gửi, và một hệ một người dùng không có ai trực ngoài giờ. Thêm pager sẽ là hạ tầng không có người nhận.

## 3. SLIs / SLOs

Giữ đúng định nghĩa ở `observability-design.md` ADR-U1-O4, và ghi rõ cửa sổ đo — đây là SLO của **một lần chạy xác nhận**, không phải cam kết vận hành liên tục:

| SLI | SLO target | Measurement window |
|---|---|---|
| Tỉ lệ nạp thành công trên dữ liệu nguồn hiện có | 100% | Mỗi lần chạy bộ test tích hợp của đơn vị |
| Tỉ lệ truy vấn dưới ngưỡng 2.000 ms | 100% | Mỗi lần chạy bộ test nhanh (NFR1.4) |
| Độ đúng của tổng số đơn và số dòng theo tháng | Lệch 0 so với phép đếm độc lập bằng pandas | Mỗi lần chạy bộ test nhanh |
| Tỉ lệ dựng vùng thành công khi dữ liệu đã nạp | 100% | Mỗi lần chạy bộ test nhanh |
| Tỉ lệ lần chạy CI xanh trên nhánh làm việc | ≥ 90% (mục tiêu theo dõi, không phải cổng) | 20 lần chạy gần nhất trên GitHub Actions |

## 4. Logs & Tracing

| Khía cạnh | Quyết định |
|---|---|
| Định dạng | JSONL, một sự kiện một dòng; trường bắt buộc `timestamp`, `level`, `run_id`, `stage`, `event` (`src/common/logging.py`) |
| Nơi ghi | `logs/<run_id>.jsonl` của lần chạy pipeline gần nhất; `stage="integration"` cho sự kiện từ dashboard (`observability-design.md` ADR-U1-O1) |
| Danh mục sự kiện | **Mười hai** sự kiện `integration.*` ở `observability-design.md` §2 — mười sự kiện gốc cộng hai sự kiện dọn nhật ký (`integration.logs.pruned`, `integration.logs.prune_failed`) do Q3 = B thêm vào ở bước sinh mã. Không có sự kiện nào khác |
| Truy vết | Không tracing phân tán. Chuỗi truy vết là `run_id` → `plan_id` → `template_id`, đều có trong bản ghi và trong `QueryRunResult` (C4) |
| Tổng hợp | Không có. Đọc bằng `jq`/pandas trên tệp JSONL; không có dịch vụ thu thập log |
| Lưu giữ | 10 tệp gần nhất; pipeline dọn ở cuối mỗi lần chạy (`infrastructure-specification.md` §5) |
| Bảo mật | Không ghi giá trị bản ghi, không ghi `ma_khach`; câu SQL nguồn chỉ ở `integration.query.started` (`security-design.md` §4) |

## 5. Bảng điều khiển (dashboard)

Không có dashboard giám sát riêng — dashboard sản phẩm **là** bề mặt quan sát, và nó phải tự nói trạng thái của mình:

| Bề mặt | Nội dung | Nguồn |
|---|---|---|
| Vùng `don-theo-thang` | Tổng số đơn, bảng theo tháng và trạng thái, `elapsed_ms`, số dòng | `QueryRunResult` (C4) |
| Nhãn trạng thái | Rỗng / Đang tải / Đầy đủ / Một phần / Lỗi — luôn kèm chữ và biểu tượng, không chỉ màu | `functional-spec.md`, NFR4.4 |
| Nhãn "kết quả lần trước" | Kèm giờ:phút:giây của lần chạy thành công gần nhất | `reliability-design.md` ADR-U1-R2 |
| Nút "Thử lại" / "Chạy truy vấn" | Nhận tiêu điểm bàn phím, nhãn chữ cố định | `reliability-design.md` ADR-U1-R5, NFR4.1 |

## 6. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Người đọc nhật ký có `jq` hoặc pandas; không cần giao diện xem log | Giả định — nếu cần, đó là đơn vị mới, không phải việc của lát cắt |
| A2 | GitHub Actions là nơi CI chạy (theo Q2 = B) | Giả định — repo phải được đẩy lên GitHub thì workflow mới chạy; chạy local vẫn là đường chính |
| Q1 | Có cần hiện `plan_id` trên thẻ để người dùng đối chiếu nhật ký không? | Không — `plan_id` đã có trong kết quả và trong nhật ký; hiện thêm sẽ làm thẻ chật. Mở lại nếu có người thật sự cần |
