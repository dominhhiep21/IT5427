# Runbooks

Bốn tình huống thật, mỗi cái có bước kiểm, bước sửa, và dấu hiệu phải dừng. Tất cả chạy trên máy local.

## RB-1 — Pipeline đỏ

**Nhận ra:** `pipeline.completed` với `success=False`, hoặc lệnh trả mã thoát 1.

```powershell
Get-Content (Get-ChildItem logs\*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1) |
  Select-String '"level":"ERROR"'
```

| Tầng hỏng | Kiểm | Sửa |
|---|---|---|
| `ingest` | tệp CSV còn trong `dataset/` không | không tự sửa `dataset/`; khôi phục từ git nếu thiếu |
| `clean` / `quality` | `data/reports/quality.json` | đọc check đỏ; nếu dữ liệu nguồn đổi thật thì cập nhật allowlist **có ghi lý do** |
| `integrate` | `warehouse/olist.duckdb` có bị dashboard giữ khoá | đóng dashboard, chạy lại |
| `linkage` | `data/integration/` có ghi được | kiểm quyền ghi; xem `integration.linkage.failed` |
| `analyze` | view có tồn tại | chạy lại `integrate` |

## RB-2 — KPI lệch

**Nhận ra:** `KpiReconciler` báo lệch, hoặc `quality` đỏ ở nhóm KPI.

1. Đọc `data/reports/` của lần chạy để biết KPI nào lệch và lệch bao nhiêu.
2. **Không** sửa baseline. Baseline là hợp đồng.
3. Kiểm dữ liệu đầu vào: số dòng 9 bảng nguồn có khớp `AGENTS.md` không.
4. Nếu dữ liệu nguồn đã đổi thật, đó là thay đổi phạm vi — dừng và chốt lại với người.

## RB-3 — Số trên vùng `don-theo-thang` sai

**Nhận ra:** cổng đối chiếu đỏ, hoặc người dùng thấy số khác lần trước.

```powershell
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_correctness.py -m slow -q
```

- Đỏ: số liệu **sai thật**. Không quay lui mù; đọc thông điệp test (nó nêu tháng, trạng thái, hai con số).
- Xanh mà người dùng vẫn thấy khác: kiểm xem họ đang nhìn "kết quả lần trước" hay kết quả mới (nhãn "Đang hiện kết quả lần trước").

## RB-4 — Dashboard không mở hoặc tab trắng

| Triệu chứng | Kiểm | Sửa |
|---|---|---|
| `Address already in use` | cổng 8050 đang bị giữ | dừng tiến trình cũ |
| Trang trắng | `logs/` có `integration.tab.*` không | chạy `pytest tests/unit/test_dashboard_smoke.py` để thấy lỗi cụ thể |
| Tab Tích hợp báo "Lỗi cấu hình" | `config/integration-tab.yaml` còn đủ `card_ids`, `callback_ids`, `result_region_ids` | khôi phục tệp từ git; `_tab_config` sẽ dùng mặc định nếu tệp hỏng |
| Bảng nguồn báo lỗi | `config/integration-sources.yaml` | chạy smoke cấu hình nguồn ở `ci-config.md` bước 8 |

## Nguyên tắc chung

- Sửa xong thì **chạy lại cả chuỗi**: bộ nhanh → pipeline → mở dashboard.
- Không bao giờ sửa `dataset/`, không sửa tay CSV trung gian.
- Mỗi lần dừng vì sự cố đều ghi một dòng vào `incident-plan.md` §nhật ký.
