# Build Instructions

Nguồn: `../../../inception/requirements-analysis/requirements.md`, `aidlc/spaces/default/memory/project.md` (`## Deployment`), `.github/workflows/ci.yml`, `requirements.txt`, `README.md`.

## Không có bước build

Dự án chạy từ mã nguồn. Không có biên dịch, không đóng gói, không container. "Build" ở đây là **chuẩn bị môi trường và dữ liệu**, và đó là toàn bộ.

| Bước | Lệnh | Thời gian |
|---|---|---|
| 1. Môi trường | `python -m venv --system-site-packages .venv` rồi `.venv\Scripts\python -m pip install -r requirements.txt` | một lần |
| 2. Dữ liệu | `python -X utf8 -m src.pipeline run --stage all` | ~3 phút trên 99.441 đơn |
| 3. Báo cáo | `python -X utf8 -m src.pipeline run --stage stats` | ~1 giây |
| 4. Chạy | `python -X utf8 -m src.dashboard` → `127.0.0.1:8050` | — |

## Ràng buộc đã biết

- Mọi lệnh Python phải chạy `-X utf8`; đường dẫn workspace có ký tự tiếng Việt và dữ liệu có ký tự Bồ Đào Nha.
- `dataset/` chỉ đọc. Bước 2 ghi vào `data/`, `warehouse/`, `logs/` — cả bốn đều bị `.gitignore`.
- Phải đóng dashboard trước khi chạy lại bước 2, vì nó giữ khoá `warehouse/olist.duckdb`.
- View DuckDB chứa đường dẫn tuyệt đối tới Parquet; chuyển thư mục repo thì phải chạy lại bước 2.
- `scikit-learn==1.6.1` đã ghim; `numpy` phải vẫn 2.2.1. Nếu `pip install` nâng `numpy`, ghim lại và chạy lại bộ `slow` trước khi tin bất kỳ con số nào.

## Không có bước deploy

Không có môi trường staging hay production. "Phát hành" là chạy bốn bước trên sau khi CI xanh, đúng chuỗi xác nhận của nhóm.
