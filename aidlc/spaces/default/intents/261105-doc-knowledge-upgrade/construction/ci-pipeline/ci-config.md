# CI Config — Olist integration upgrade

## 1. Tệp và kích hoạt

Tệp: `.github/workflows/ci.yml`. Kích hoạt: `push` và `pull_request` trên `main` và `feature/update-ui-ux`.

Một job duy nhất trên `windows-2022` (ghim image, không dùng `windows-latest`): sản phẩm chỉ chạy trên Windows và hai chế độ hỏng đã biết — khoá tệp tạm thời, bảng mã console cp1252 — là đặc thù Windows. CI trên Linux sẽ xanh cho mã có thể đỏ trên máy thật.

## 2. Các bước

| # | Bước | Lệnh | Vì sao |
|---|---|---|---|
| 1 | Checkout | `actions/checkout@v4` | — |
| 2 | Python | `actions/setup-python@v5`, `3.13`, cache `pip` | Cùng phiên bản với máy phát triển |
| 3 | Cài đặt | `pip install -r requirements.txt` | 10 gói đã ghim, gồm `ruff` |
| 4 | Lint + định dạng | `ruff check .` và `ruff format --check <danh sách 21 tệp>` | NFR3; phần format chỉ chạy trên mã của đợt này vì 35 tệp cũ chưa qua `ruff format` |
| 5 | Dựng dữ liệu | `python -X utf8 -m src.pipeline run --stage all` | Bắt buộc: bộ nhanh chưa hermetic (`TD-09`) cần `warehouse/` và `data/marts/`. Không truyền `--refresh-ibge` |
| 6 | Test nhanh | `python -X utf8 -m pytest -m "not slow"` | 375 test, ~14 giây |
| 7 | Phủ toàn bộ | `python -X utf8 -m pytest --cov=src --cov-fail-under=80` | Ngưỡng 80% chỉ có nghĩa trên toàn bộ bộ test; chạy trên bộ nhanh sẽ đỏ oan |
| 8 | Smoke cấu hình nguồn | `python -X utf8 -c "..."` | Bước duy nhất chứng minh `config/integration-sources.yaml` đã commit nạp được |

## 3. Điều CI **không** chạy

- **Không chạy bộ `slow`**: Q2 = B của đợt — bộ chậm cần dữ liệu thật và mất ~52 giây, chạy tay trước khi phát hành.
- **Không dựng môi trường, không deploy**: không có môi trường thứ hai (`team.md` — Deployment).
- **Không sinh artifact**: "phát hành" = chạy từ mã nguồn; tag là mốc, không có gói đóng.

## 4. Bí mật

Không có. Workflow chỉ dùng `GITHUB_TOKEN` mặc định để checkout; không khai `secrets.*`, không có `.env`. Hai `uses:` duy nhất (`actions/checkout`, `actions/setup-python`) ghim theo major tag; muốn chặt hơn thì ghim theo SHA, đánh đổi là phải cập nhật tay.

## 5. Chi phí

Runner Windows tính gấp đôi phút so với Linux trên repo riêng tư. Với job ~3–5 phút và vài lần đẩy mỗi ngày, đây là mức không đáng kể; vượt hạn mức miễn phí mới là lúc xem lại.
