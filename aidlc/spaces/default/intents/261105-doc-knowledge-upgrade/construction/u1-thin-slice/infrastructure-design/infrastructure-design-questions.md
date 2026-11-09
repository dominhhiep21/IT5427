# Infrastructure Design — u1-thin-slice

Bối cảnh: đơn vị này chạy trên **một máy local**, một người dùng, không có cloud, không có môi trường staging/production (`team.md` mục Deployment; `scalability-design.md`). Phần lớn hạ tầng vì vậy đã được chốt từ trước: Python 3.13 trong `.venv`, DuckDB in-memory, `dataset/` chỉ đọc, `data/` + `warehouse/` + `logs/` là sản phẩm sinh ra và bị `.gitignore`.

Ba câu dưới đây là ba điểm **thật sự còn phải chọn** — mỗi câu đổi một thứ sẽ phải làm trong đợt này.

## Q1. [Phát hành] Đánh dấu mốc phát hành bằng gì?

Hiện tại "phiên bản" chỉ là commit hash; `team.md` ghi điểm này **chưa xác định** cho mốc nộp.

- A. Giữ nguyên: chỉ commit hash, không tag, không CHANGELOG
- B. Thêm tag `v0.x` cho mốc nộp, không viết CHANGELOG
- C. Thêm tag `v0.x` **và** một `CHANGELOG.md` ngắn (chỉ mục "Thay đổi" theo mốc)
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: C

## Q2. [CI/CD] Có thêm một pipeline CI tối thiểu không?

`team.md` ghi rõ hiện **không có CI**, và chuỗi xác nhận là chạy tay trên máy: `pytest -m "not slow"` → `python -m src.pipeline run --stage all` → mở dashboard.

- A. Không thêm CI; giữ đúng chuỗi chạy tay đã chốt
- B. Thêm một workflow GitHub Actions tối thiểu: cài từ `requirements.txt`, chạy `ruff check`, `ruff format --check`, `pytest -m "not slow"`
- C. Thêm CI như B **và** chạy cả bộ `slow` trong CI (cần `dataset/` đi kèm hoặc tải về)
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Q3. [Vận hành] Nhật ký `logs/*.jsonl` được dọn thế nào?

Mỗi lần chạy pipeline sinh một tệp; tab "Tích hợp" ghi nối vào tệp của lần chạy gần nhất. `logs/` bị `.gitignore` và hiện không có cơ chế dọn.

- A. Không tự dọn: để nguyên, dọn tay khi thấy cần (thêm một dòng vào `docs/runbook.md`)
- B. Pipeline tự dọn: giữ 10 lần chạy gần nhất, xoá tệp cũ hơn ở cuối mỗi lần chạy
- C. Xoay vòng theo dung lượng: khi `logs/` vượt 50 MB thì xoá tệp cũ nhất
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Ghi chú

- Không có câu hỏi về bí mật, mạng, hay cân bằng tải: đơn vị không có cả ba (`security-design.md` §1, `scalability-design.md` §1).
- Nếu chọn B hoặc C ở Q2, cần thêm một tệp workflow và một ghi chú trong `README.md`; đó là thay đổi phạm vi nhỏ nhưng phải kể vào đợt này.

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Mốc phát hành: thêm tag `v0.x` cho mốc nộp kèm một `CHANGELOG.md` ngắn.
- CI: thêm một workflow GitHub Actions tối thiểu — cài từ `requirements.txt`, chạy `ruff check`, `ruff format --check`, `pytest -m "not slow"`; không chạy bộ `slow`.
- Nhật ký: pipeline tự dọn `logs/`, giữ 10 lần chạy gần nhất.

Cách làm cho phần còn lại của hạ tầng: một tiến trình Python chạy trên máy local trong `.venv` (không cloud, không container, không môi trường staging); `dataset/` chỉ đọc còn `data/`, `warehouse/`, `logs/` là sản phẩm sinh ra và bị `.gitignore`; theo dõi bằng nhật ký JSONL đã thiết kế, không metric tập trung, không tracing, không alerting; không có bí mật nào để quản lý.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
