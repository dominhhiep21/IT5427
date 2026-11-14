# Performance Requirements — u3-prediction-ui

Nguồn: `../functional-design/functional-spec.md` (§3, §7, §8), `../../../inception/requirements-analysis/requirements.md` (NFR1, NFR2, NFR6), `../../../inception/units-generation/unit-of-work.md` §U3.

Đơn vị này **không** thêm tầng dữ liệu nào: nó đọc một tệp JSON cục bộ và một tệp `pickle` cục bộ, rồi gọi một hàm thuần trên **một** dòng. Vì vậy ngân sách ở đây là ngân sách **tương tác**, không phải ngân sách lô.

| ID | Hạng mục | Mục tiêu | Đo bằng |
|---|---|---|---|
| NFR1.1 | Ngân sách tầng `stats` (**thuộc U2**, đơn vị này không đụng) | **< 300 s** — không đổi | test `slow` của U2 (`STAGE_BUDGET_SECONDS = 300`) |
| NFR2.1 | Ngân sách bước huấn luyện (**thuộc U2**, đơn vị này không đụng) | **< 240 s** — không đổi | test `slow` của U2 (`TRAIN_BUDGET_SECONDS = 240`) |
| NFR3.1 | Cổng phủ | giữ nguyên `--cov-fail-under=80`; không hạ, không đặt cờ lên riêng bộ nhanh | `ci.yml` bước phủ |
| NFR4.1 | Không hồi quy dữ liệu | 5 KPI, 9 bảng mart, 11 view không đổi | `KpiReconciler`, `StarSchemaValidator` (qua `--stage all` trong lệnh xác nhận) |
| NFR5.1 | Mốc sàn | `beats_floor(model.auc, model.baseline_auc)` xanh trên báo cáo thật | test `slow` mới của U3 |
| NFR6.1 | Tiếp cận | 100% vùng có nhãn; không `tabIndex` dương; chữ < 16px dùng `--text-2` ≥ 4,5:1 | test duyệt cây + `test_analysis_tab_contrast`; **thêm** một khẳng định CSS rằng `.field-error` dùng `var(--text-2)`, vì ca tương phản hiện có không thể đỏ khi thiếu lớp mới |

## Ngân sách tương tác (thêm bởi U3)

Ngưỡng dưới đây là **ngưỡng bắt thoái hoá**, không phải mục tiêu hiệu năng. Số đo trên **máy phát triển của đợt này** (Windows, Python 3.13, CPU desktop; 20 lần gọi, tệp `data/models/logistic.pkl` hiện **4,8 KB**): `score_item` trung bình **10,49 ms**, max **11,7 ms**; `load_model` **0,33 ms**; dựng cây **≈2 ms**. Dư địa không đều: PR3.1 rộng ~19 lần, PR3.3 ~150 lần, còn PR3.2 rộng ~6.000 lần — PR3.2 vì thế chỉ bắt được thoái hoá **thảm khốc** (đọc tệp từ mạng, quét cả thư mục); nó không phải cổng hiệu năng tinh.

| ID | Hạng mục | Ngưỡng | Đo bằng |
|---|---|---|---|
| PR3.1 | Chấm một dòng hàng | `score_item` trung bình **< 200 ms** qua 20 lần gọi | test đơn vị `time.perf_counter()` |
| PR3.2 | Nạp tệp mô hình | `load_model` **< 2 s** trên tệp do `save_model` sinh trong `tmp_path` | test đơn vị đo một lần nạp |
| PR3.3 | Dựng cây mục Dự đoán | `build_prediction_section(...)` **< 300 ms** qua 20 lần (không I/O) | test đơn vị |
| PR3.4 | Thời gian mở tab | không tăng quá **+20%** so với trước thay đổi trên cùng máy | đo tay một lần trước/sau, ghi số vào `code-summary.md` của U3 — **không** là test |
| PR3.5 | Một lần bấm | tối đa **một** `read_report` + **một** `load_model` mỗi lần bấm; không đọc lặp trong vòng lặp, không đọc `warehouse/` | đọc mã + test đơn vị đếm số lần gọi bằng giả lập |

Ghi chú: PR3.1–PR3.3 vẫn là đo đồng hồ thực nên có thể nhiễu; nếu một lần chạy vượt ngưỡng, ghi lại số đo và mở lại ngưỡng **có chủ đích** — không nới ngầm (cùng lý do đã ghi ở `team.md` `## Deployment`).

## Điều không đặt ra

- Không có ngân sách bộ nhớ riêng: khối dựng một cây Dash nhỏ, tệp mô hình đã nằm trong bộ nhớ tiến trình dashboard.
- Không có yêu cầu về độ trễ mạng: dashboard bind `127.0.0.1`.
- Không thêm bộ nhớ đệm (cache): một tệp JSON + một tệp pickle cục bộ, đo ở PR3.2 đã đủ nhanh; cache sẽ tạo trạng thái cũ khi `--stage stats` ghi bản mới.
