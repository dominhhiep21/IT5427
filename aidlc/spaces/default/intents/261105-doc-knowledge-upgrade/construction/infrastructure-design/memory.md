<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-11-06T09:52:00Z [unit u1-thin-slice] — "Infrastructure Design" của một hệ chạy local được hiểu là: ghi rõ cái **không** cấp phát (cloud, container, queue, cache, secrets store) kèm lý do, rồi mới mô tả cái có. Bảng "dịch vụ không dùng" được giữ lại thay vì xoá, vì nó là thứ ngăn bước sau dựng thêm hạ tầng.
- 2026-11-06T09:52:00Z [unit u1-thin-slice] — Q3 = B ("pipeline tự dọn, giữ 10 lần chạy") chỉ áp cho tệp `logs/*.jsonl`; không dọn `inbox/` hay thư mục khác, vì người dùng chưa nói tới.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-11-06T09:52:00Z [unit u1-thin-slice] — workflow CI có thêm một bước **chạy pipeline** (`--stage all`) trước `pytest -m "not slow"`, bước này không nằm trong phương án B đã chốt. Lý do kiểm chứng được: bộ test nhanh không hermetic (`TD-09`, năm test cần `warehouse/` và `data/marts/` bị `.gitignore`), nên CI trên bản clone sạch sẽ đỏ vĩnh viễn. Cách này không sửa mã nào và còn kiểm được `QualityGate`/`KpiReconciler`; đã ghi rõ ba phương án và lý do chọn ở `cicd-pipeline.md` §2 để người đọc quyết lại nếu muốn sửa `TD-09` thay thế.
- 2026-11-06T09:52:00Z [unit u1-thin-slice] — chọn `windows-2022` cho CI thay vì `ubuntu-latest` mặc định, vì sản phẩm chỉ chạy trên Windows và hai chế độ hỏng của đơn vị (khoá tệp, cp1252) là đặc thù Windows.
- 2026-11-06T10:20:00Z [unit u1-thin-slice] — sau review vòng 1: bỏ hẳn câu "không egress" và "dataset/ không có đường ghi". Sự thật là `integrate` gọi `IbgeClient.fetch_states()`, ghi cache vào `dataset/external/ibge/` và có thể gọi HTTPS tới IBGE; hôm nay cache đã commit nên nhánh đó không chạy. Tài liệu nay ghi đúng là **có điều kiện**, kèm quy tắc 4 dòng ở §3 (CSV nguồn bất biến; chỉ cache được ghi; CI không truyền `--refresh-ibge`).
- 2026-11-06T10:20:00Z [unit u1-thin-slice] — Q3 = B thay thế câu "không xoay vòng tệp nhật ký tự động" của ADR-U1-O1; điều này được ghi tường minh ở `infrastructure-specification.md` §5 thay vì để hai tài liệu nói ngược nhau. Hai sự kiện `integration.logs.pruned` / `integration.logs.prune_failed` giữ tiền tố `integration.` như quy ước.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-11-06T09:52:00Z [unit u1-thin-slice] — cổng độ phủ 80% (NFR2.1) chỉ chạy ở local, không đưa vào CI, để giữ workflow đúng ba bước như phương án B và dưới 5 phút. Đánh đổi: CI có thể xanh trong khi độ phủ tụt; bù lại ngưỡng nằm trong lệnh xác nhận bắt buộc trước khi phát hành.
- 2026-11-06T09:52:00Z [unit u1-thin-slice] — tag phát hành đặt trên `main` sau khi merge, không trên nhánh làm việc: tag trên nhánh dễ trỏ vào commit sẽ bị squash-merge, làm mốc thành vô nghĩa.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-11-06T09:52:00Z [unit u1-thin-slice] — `dataset/` có thật sự được commit trong repo không, để CI có dữ liệu nguồn cho bước chạy pipeline? Chưa kiểm trong bước này; nếu không có, bước 5 của workflow phải thêm cách lấy dữ liệu và đó là quyết định mới cần chốt.
- 2026-11-06T10:20:00Z [unit u1-thin-slice] — đã kiểm: `git ls-files dataset` trả 11 tệp (9 CSV + `external/ibge/estados.json` + `metadata.json`), nên bước 5 của CI có dữ liệu nguồn. Giả định A2 của `cicd-pipeline.md` được nâng thành sự kiện đã kiểm.
- 2026-11-06T10:20:00Z [unit u1-thin-slice] — còn mở, ngoài phạm vi lát cắt: chuyển `ibge_dir` khỏi `dataset/` (ví dụ `data/external/ibge/`) để `dataset/` bất biến tuyệt đối. Chạm `config.yaml`, `src/config.py`, `docs/runbook.md` và đường của ba tab cũ — cần chốt phạm vi trước, không tự làm.
- 2026-11-06T09:52:00Z [unit u1-thin-slice] — tag `v0.1.0` đặt trên `main` (theo thiết kế) hay trên `feature/update-ui-ux` (nếu người làm muốn mốc trước khi merge)? Đã nêu ở `cicd-pipeline.md` §7 Q1.
- 2026-11-07T11:25:00Z [unit u2-mediated-schema] Don vi kieu library chi sinh cicd-pipeline.md + traceability.json. Khong hoi cau nao: khong co ha tang moi, va team da chot moi truong local. Da doi chieu ci.yml that trong repo (5 buoc, windows-2022) thay vi tin codekb (codekb quet truoc khi ci.yml ton tai) - phat hien G1 (CI khong chay --cov-fail-under=80) va G2 (ruff format --check liet ke tay tung tep test).
