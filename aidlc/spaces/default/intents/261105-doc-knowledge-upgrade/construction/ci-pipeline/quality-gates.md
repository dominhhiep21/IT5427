# Quality Gates — Olist integration upgrade

## 1. Cổng chặn hợp nhất (CI, mỗi lần push/PR)

| Cổng | Ngưỡng | Đo bằng | Khi đỏ |
|---|---|---|---|
| Lint | 0 vi phạm | `ruff check .` | chặn |
| Định dạng | 0 tệp lệch trong phạm vi | `ruff format --check` trên 21 tệp của đợt | chặn |
| Test nhanh | 375 test xanh | `pytest -m "not slow"` | chặn |
| Độ phủ | ≥ 80% dòng `src/` | `pytest --cov=src --cov-fail-under=80` (toàn bộ bộ test) | chặn |
| Pipeline | `QualityGate` + `KpiReconciler` xanh | `src.pipeline run --stage all` | chặn |
| Cấu hình nguồn | nạp được, đúng ba hồ sơ | smoke ở bước 8 | chặn |

## 2. Cổng chạy tay trước phát hành (không vào CI)

| Cổng | Ngưỡng | Lý do không tự động |
|---|---|---|
| Bộ `slow` | 9 test xanh | cần dữ liệu thật, ~52 giây; Q2 = B loại khỏi CI |
| Kiểm bằng mắt trên dashboard | vùng `don-theo-thang` hiện số liệu sau khi bấm nút | cần người; bước 3 trong chuỗi xác nhận của `team.md` |
| Tương phản màu, thứ tự tiêu điểm | WCAG 2.1 AA | chưa có công cụ đo tự động trong repo |

## 3. Cổng đúng đắn dữ liệu của lát cắt

`tests/unit/test_integration_correctness.py` (marker `slow`): số đơn theo `(tháng, trạng thái)` trên vùng `don-theo-thang` phải khớp **0 sai lệch** với phép tính độc lập bằng pandas từ `dataset/`. Lệch một đơn là đỏ. Đây là cổng duy nhất chứng minh cơ chế viết lại truy vấn không làm đổi ngữ nghĩa.

## 4. Điều cổng **không** bắt được (đã biết)

| Lỗ hổng | Vì sao | Bù bằng |
|---|---|---|
| `bang_giao` luôn `None` | lược đồ khai `loaded: true` nhưng bộ nạp chỉ đọc bảng khoá | ghi nợ `TD-16`; bộ nạp ghi sự kiện `integration.load.skipped` |
| Hai bảng `agg_*` không có baseline số dòng | test chỉ khẳng định 11 view tồn tại + 9 bảng mart | `KpiReconciler` vẫn so 5 KPI |
| Bộ nhanh không hermetic (`TD-09`) | 5 test dashboard cần `warehouse/` + `data/marts/` | CI chạy pipeline trước khi test |
| Không test C5 thật (U4 → tab) | tab được test bằng payload dựng tay | ghi ở `build-and-test/integration-test-instructions.md` §3 |

## 5. Nguyên tắc

- **Không nới ngưỡng để cho qua.** Nếu phần mới làm tụt phủ, viết thêm test — không hạ `--cov-fail-under`.
- **Cổng đỏ thì dừng.** Bỏ qua một cổng là sự cố, không phải mẹo tắt.
- **Cổng phải có người đọc được.** Mỗi cổng ở §1 in ra đúng một con số so với ngưỡng của nó.
