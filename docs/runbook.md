# Runbook

## Pipeline không chạy

1. Kiểm tra Python: `.\.venv\Scripts\python.exe --version` (3.13).
2. Kiểm tra dependency: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
3. Chạy `run --stage all` và xem log mới nhất trong `logs/`.
   `logs/` chỉ giữ **10 tệp gần nhất** — cuối mỗi lần chạy pipeline dọn tệp cũ hơn, nên log của
   một lần chạy đã qua 10 lần khác thì không tìm lại được. Chép ra ngoài nếu cần giữ.

## Lỗi `SchemaError`

- Tệp CSV thiếu cột hoặc sai thứ tự.
- So sánh với `src/ingest/schemas.py`.
- Không sửa `dataset/`; sửa tệp batch/nguồn.

## Lỗi `QualityGateError`

- Xem `data/reports/quality-report.json`.
- Các check fail có `expected`/`actual`.
- Không tự sửa số liệu; kiểm tra nguồn hoặc allowlist.

## Lỗi IBGE

- API IBGE có thể timeout.
- Cache hợp lệ nằm ở `dataset/external/ibge/estados.json`.
- Chỉ dùng `--refresh-ibge` khi có mạng.
- Nếu cache hỏng: khôi phục 27 bang từ `dataset/external/ibge/`.

## DuckDB bị khóa

- Đóng dashboard trước khi chạy `integrate`.
- Dashboard dùng read-only; pipeline dùng write.
- Nếu vẫn lỗi, đóng tiến trình Python đang giữ `warehouse/olist.duckdb`.

## Dashboard trống/lỗi

1. Chạy `run --stage integrate` để tạo mart/catalog.
2. Kiểm tra `warehouse/olist.duckdb` tồn tại.
3. Mở `http://127.0.0.1:8050`.
4. Nếu port bận, đổi `dashboard.port` trong `config.yaml`.

## Tệp kết quả ghép bản ghi bị cũ

- Dấu hiệu: `data/integration/linkage-customer.json` hoặc `linkage-seller.json` mang `run_id` /
  `computed_at` không khớp lần chạy gần nhất, hoặc tệp không tồn tại sau khi nâng cấp đơn vị U4.
- Xử lý: chạy lại `run --stage all` (hoặc `run --stage integrate` — lệnh này cũng làm mới cả hai tệp).
  Không chép tay tệp kết quả và không sửa `summary` trong tệp.
- Kiểm chứng: xem sự kiện `integration.linkage.completed` trong `logs/<run_id>.jsonl` của lần chạy mới.

## UnicodeEncodeError trên Windows

- Luôn chạy `python -X utf8` hoặc đặt `PYTHONUTF8=1`.

## Micro-batch lỗi

- Kiểm tra `inbox/manifest.json` để biết batch/file fail.
- Tệp phải cùng schema 9 bảng nguồn.
- Batch lỗi không promote; chạy lại sau khi sửa.
- Batch đã success sẽ bị skip theo hash.

## Replay

- `replay --batches N` tạo batch từ N tháng gần nhất.
- Nếu muốn chạy lại, xóa `inbox/replay/` và `inbox/replay/manifest.json`.

## Test

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow"
.\.venv\Scripts\python.exe -X utf8 -m pytest
```
