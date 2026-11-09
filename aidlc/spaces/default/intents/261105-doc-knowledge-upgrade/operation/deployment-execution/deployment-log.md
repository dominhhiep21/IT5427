# Deployment Log — local release 2026-11-09

## 1. Bối cảnh

Đợt này không có môi trường triển khai từ xa. "Triển khai" = chạy chuỗi phát hành trên máy local, đúng định nghĩa ở `operation/deployment-pipeline/deployment-strategy.md`. Bản ghi này là bằng chứng của lần chạy thật, không phải kịch bản.

## 2. Chuỗi đã chạy

| # | Bước | Lệnh | Kết quả |
|---|---|---|---|
| 1 | Cổng test nhanh | `.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow" -q` | 375 passed, 13,94 s |
| 2 | Cổng test chậm | `.venv\Scripts\python.exe -X utf8 -m pytest -m slow -q` | 9 passed, 52,26 s |
| 3 | Cổng phủ | `.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80 -q` | 384 passed, 90,69% |
| 4 | Lint + định dạng | `ruff check .` và `ruff format --check` (28 tệp) | 0 vi phạm, 28 tệp đúng |
| 5 | Dựng dữ liệu | `.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all` | `success=True`, 6/6 tầng, `run=20261109T042432-42e24658` |
| 6 | Chạy sản phẩm | `.venv\Scripts\python.exe -X utf8 -m src.dashboard` | bind `127.0.0.1:8050` |

## 3. Thời điểm và phạm vi

- Ngày: 2026-11-09, máy phát triển.
- Không có downtime cần thông báo: một người dùng local.
- Không có thay đổi cơ sở dữ liệu cần migration; mọi thứ trong `warehouse/` dẫn xuất từ `dataset/`.

## 4. Việc chưa làm

- **Kiểm bằng mắt trên trình duyệt** (bước 3 của chuỗi xác nhận `team.md`) chưa chạy trong phiên tự động này: cần người mở dashboard và bấm "Chạy truy vấn" ở vùng `don-theo-thang`. Đây là bước duy nhất của chuỗi phát hành chưa có bằng chứng máy.
- Không có tag phát hành: định danh là commit hash (xem `deployment-pipeline/cd-config.md` §3).

## 5. Kết luận

Chuỗi phát hành local **đạt** ở mọi cổng máy kiểm được. Điều kiện còn lại là một lần kiểm bằng mắt của người.
