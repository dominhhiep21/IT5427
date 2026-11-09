# Performance and Quality Requirements — u4-record-linkage

Nguồn: `nfr-requirements/tech-stack-decisions.md` (đã chuyển các chỉ tiêu đo được sang tệp này để chúng có mã yêu cầu đúng chuẩn), `inception/requirements-analysis/requirements.md` (NFR1–NFR6), `inception/units-generation/unit-of-work.md` §U4.

Đơn vị `u4-record-linkage` là `library`: stage NFR Requirements chỉ sinh `security-requirements.md` và `tech-stack-decisions.md`, nên các chỉ tiêu hiệu năng/chất lượng của đơn vị được chốt ở đây. Tệp này là **nguồn sự thật** cho các mã `NFRx.y` của đơn vị.

## Hiệu năng (NFR1)

| Mã | Yêu cầu | Ngưỡng | Đo bằng |
|---|---|---|---|
| NFR1.1 | Chặn và xét **806.705 cặp ứng viên** (chặn 5 chữ số) của khách trong một lần chạy pipeline; số cặp thực sự chấm (`pairs_scored`) nhỏ hơn vì bản ghi không có sản phẩm bị đẩy sang `pairs_skipped` | ≤ 60 giây cho cả lượt chạy | `elapsed_ms` của sự kiện `integration.linkage.completed`. **Phạm vi số đo là cả lượt**: mã đặt `started` trước khi đọc 4 CSV (`src/linkage/result.py:124`) và tính sau khi ghi tệp + kiểm lại (`:147`) — nên số đo gồm đọc, chấm, ghi, kiểm, không phải riêng phần chấm. Test hiệu năng hiện có (`tests/unit/test_linkage_score.py`) chỉ chấm ~200.000 cặp trong bộ nhanh; ngưỡng 60 giây cho lượt đầy đủ được xác nhận ở lần chạy `--stage all` |
| NFR1.2 | Kích thước tệp kết quả | Tệp ≤ 5 MB | `Path.stat().st_size` trong test (`tests/unit/test_linkage_result.py`). Trần 10.000 cặp (BR4.10) giới hạn `pairs`; **`skipped` không bị trần nào chặn**, nên khi số bản ghi thiếu sản phẩm tăng thì tệp có thể vượt ngưỡng — test phải đo cả hai phần |

## Chất lượng mã (NFR2, NFR3)

| Mã | Yêu cầu | Ngưỡng | Đo bằng |
|---|---|---|---|
| NFR2.1 | Độ phủ dòng toàn dự án | ≥ 80% (mục tiêu của dự án) | `pytest --cov=src` — **lưu ý:** `pytest.ini` hiện không có `--cov-fail-under`, nên ngưỡng này là cam kết, chưa phải cổng tự động; phải chạy lệnh có `--cov-fail-under=80` trước khi phát hành |
| NFR2.2 | Mỗi mô-đun mới có test riêng | 1 tệp test cho mỗi tệp nguồn mới | Rà `src/linkage/` và `tests/unit/` |
| NFR3.1 | Lint và định dạng | 0 vi phạm | `ruff check .` (toàn repo) và `ruff format --check src/linkage tests/unit` (phạm vi hẹp — 35 tệp cũ chưa qua `ruff format`, theo `team.md`) |

## Bảo đảm dữ liệu (NFR5)

| Mã | Yêu cầu | Ngưỡng | Đo bằng |
|---|---|---|---|
| NFR5.1 | `quality full` và `KpiReconciler` xanh sau khi thêm đơn vị | 0 vi phạm; 5 KPI lệch 0 | `python -X utf8 -m src.pipeline run --stage all` |
| NFR5.2 | Số dòng 11 view và 5 KPI baseline không đổi | Khớp chính xác | `KpiReconciler` + test tích hợp hiện có |

## Chạy local (NFR6)

| Mã | Yêu cầu | Ngưỡng | Đo bằng |
|---|---|---|---|
| NFR6.1 | Không có lời gọi mạng | 0 | Rà mã `src/linkage/`: không import `urllib`, `http`, `requests`, `socket` — **đây là danh sách duy nhất**, `tech-stack-decisions.md` chỉ tham chiếu mã này |

## Không áp dụng

NFR4 (tiếp cận WCAG 2.1 AA) **không áp dụng** cho đơn vị này vì nó không hiển thị gì; yêu cầu đó thuộc `u6-integration-ui`.
