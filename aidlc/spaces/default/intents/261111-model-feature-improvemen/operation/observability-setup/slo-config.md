# SLO / SLI Configuration — intent `261111-model-feature-improvemen`

## 1. Không có SLO phần trăm, và lý do

`phases/operation.md` đòi SLO lượng hoá theo % và cửa sổ thời gian **cho dịch vụ chạy liên tục**. Repo này không có dịch vụ như vậy: dashboard chạy khi người dùng mở, pipeline chạy khi người dùng gọi. Đặt "99,9% availability trong 30 ngày" cho một tiến trình bật-tắt theo tay là con số không đo được và không có nghĩa.

## 2. SLI đo được, thay cho SLO phần trăm

| SLI | Định nghĩa | Ngưỡng | Đo bằng |
|---|---|---|---|
| SLI-1 Đúng dữ liệu | 5 KPI và số dòng khớp baseline | **tuyệt đối**, không dung sai tuỳ ý | `KpiReconciler`, `StarSchemaValidator` |
| SLI-2 Đúng mô hình | `beats_floor(auc, baseline_auc)` trên báo cáo thật | **true** | test `slow` U3 |
| SLI-3 Chấm điểm | `score_item` một dòng | **< 200 ms** | PR3.1 |
| SLI-4 Nạp mô hình | `load_model` | **< 2 s** | PR3.2 |
| SLI-5 Dựng khối | `build_prediction_body` | **< 300 ms** | PR3.3 |
| SLI-6 Báo cáo không mục | tỉ lệ lượt mở tab có `status = loi` | phải là **0** khi `--stage stats` vừa xanh | đọc `analysis.json` |

## 3. Error budget

Không có error budget phần trăm. Ngân sách thực tế là **thời gian**: 300 s cho tầng `stats`, 240 s cho bước huấn luyện. Vượt ngân sách là tín hiệu phải đo lại và sửa **có chủ đích**, không nới ngầm (`team.md` `## Deployment`).

## 4. Chính sách khi SLI đỏ

| SLI | Đỏ nghĩa là | Việc phải làm |
|---|---|---|
| SLI-1 | dữ liệu sai | dừng, sửa tầng dữ liệu; **không** cập nhật baseline để cho xanh |
| SLI-2 | mô hình thoái hoá | điều tra đặc trưng/dữ liệu; không hạ `MODEL_AUC_FLOOR` |
| SLI-3…5 | chậm bất thường | chạy lại khi máy rảnh để loại nhiễu; nếu vẫn đỏ, tìm I/O thêm trong callback |
| SLI-6 | báo cáo hỏng | chạy lại `--stage stats`, xem `logs/` |

Ngưỡng SLI-3…5 lấy từ `../construction/u3-prediction-ui/nfr-design/performance-design.md` (PR3.1–PR3.3, PD3.1–PD3.2); cách ly dữ liệu nhật ký theo `security-design.md` SD3.5; vòng đời tệp báo cáo/mô hình theo `infrastructure-specification.md` INF3.3–INF3.4.
