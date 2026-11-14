# Integration Test Instructions

Nguồn: `cross-unit-traceability.md`, `../../../inception/contract-design/contract-summary.md`, ba thư mục `../../{u1-statistics,u2-model,u3-display}/code-generation/`.

## Ba biên cần kiểm

| Biên | Hợp đồng | Ca tích hợp |
|---|---|---|
| U1 → U2 | C1: U2 đọc khối `stats` U1 ghi, ghi lại cùng tệp với khối `model` | `tests/integration/test_u2_model_end_to_end.py` |
| U1 → U3 | C2: `read_report` trả bốn trạng thái, U3 ánh xạ thành token | `tests/unit/test_dashboard_analysis_tab.py` (năm mẫu) |
| U2 → U3 | C3: bảy trường `ModelBlock`, thẻ AUC đọc `counts.auc_below_target` | `tests/integration/test_u3_end_to_end.py` |

## Chuỗi end-to-end

`tests/integration/test_u1_stats_end_to_end.py`, `test_u2_model_end_to_end.py`, `test_u3_end_to_end.py` — mỗi tệp chạy toàn pipeline trên dữ liệu thật, mang marker `slow`.

Chuỗi phải chứng minh **theo thứ tự**: `--stage all` dựng mart → `--stage stats` sinh báo cáo có cả hai khối → tab đọc được và hiện đúng.

## Điều phải khẳng định lại sau mỗi thay đổi

- 5 KPI baseline: doanh thu 15.419.773,75 BRL; 96.478 đơn delivered; AOV 159,83; 7.826 đơn trễ; 8,11%.
- 9 bảng nguồn, 11 bảng mart, 11 view giữ nguyên số dòng và tên.
- `quality` chế độ `full` và `KpiReconciler` xanh.
- Báo cáo `day-du` với `train_n + test_n = 96.478` và `flagged + not_flagged = total`.

## Không kiểm bằng máy được

Mốc 1280px và bố cục tổng thể: xem bằng mắt ở bước 4 chuỗi xác nhận. Repo chỉ có `pytest`, không có trình duyệt trong CI.
