# Environment Inventory

Nguồn: `../../construction/{u1-statistics,u2-model,u3-display}/infrastructure-design/infrastructure-specification.md`, `../deployment-pipeline/cd-config.md`, `codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`.

## Chỉ có một môi trường, và nó đã tồn tại

Không có gì phải cấp phát: không tài khoản đám mây, không máy chủ, không cụm. Môi trường duy nhất là máy người làm, và nó đã ở đó trước khi dự án bắt đầu. Stage này vì vậy là **kiểm kê và xác nhận**, không phải tạo mới.

## Kiểm kê

| # | Thành phần | Ở đâu | Ai tạo ra | Trạng thái |
|---|---|---|---|---|
| E1 | Python 3.13 trong `.venv` | gốc repo | người làm, một lần | có |
| E2 | 10 gói ghim trong `requirements.txt` | `.venv` | `pip install -r` | có |
| E3 | `dataset/` — 9 CSV gốc | repo | có sẵn | **bất biến** |
| E4 | `data/` (cleaned, marts, reports) | gốc repo | `run --stage all`, `--stage stats` | sinh ra, bị `.gitignore` |
| E5 | `warehouse/olist.duckdb` | gốc repo | `run --stage integrate` | sinh ra |
| E6 | `logs/` — JSONL mỗi lần chạy | gốc repo | mọi tầng | sinh ra, giữ 10 tệp gần nhất |
| E7 | `inbox/`, `dataset/external/ibge/` | gốc repo | `load_config` lúc khởi động | sinh ra |
| E8 | Dashboard `127.0.0.1:8050` | tiến trình cục bộ | `python -m src.dashboard` | chạy khi mở |
| E9 | GitHub Actions `windows-2022` | GitHub | workflow | có |

## Điều kiện cấp phát

`load_config()` tạo **11 thư mục** lúc khởi động, nên tiến trình cần quyền ghi ở **gốc workspace**, không chỉ trong `logs/`. Đây là điều đã ghi ở `INDU-1` của U3 và là lý do một checkout chỉ-đọc sẽ hỏng ngay khi khởi động.

## Cấp phát lại từ đầu

Xoá `data/`, `warehouse/`, `logs/`, `inbox/` rồi chạy `run --stage all` — khoảng 3 phút trên 99.441 đơn. Ba thư mục kia tự sinh lại. `dataset/` không bao giờ bị đụng.

## Không có

Không có môi trường staging để giữ parity, không có production, không có drift detection — drift detection giả định có hạ tầng khai báo, ở đây hạ tầng là một thư mục.
