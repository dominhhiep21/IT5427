# Tổng quan nghiệp vụ — Olist E-commerce Data Pipeline

> Phạm vi: repo `Tich-hop-va-xu-li-du-lieu-lon`. Lần quét **tập trung** ngày 2026-11-11 tại commit
> `ea77bdf88d1431de11c36e1b739972bd594063f0` (cây làm việc có thay đổi chưa commit — xem
> `reverse-engineering-timestamp.md`) cập nhật phần nghiệp vụ liên quan tới `src/analytics/`,
> `src/integrate/`, `src/dashboard/`, `src/pipeline/` và `tests/`; phần còn lại giữ nguyên từ lần quét
> trước (**chưa xác minh lại** — xem khối Scope of Analysis).
> Chi tiết kỹ thuật: `architecture.md`, `component-inventory.md`, `code-quality-assessment.md`.

## 1. Bối cảnh nghiệp vụ

Hệ thống phục vụ bài toán **tích hợp và xử lý dữ liệu lớn** trên bộ dữ liệu công khai
**Olist Brazilian E-Commerce** (Brazil, 09/2016 – 10/2018). Đây là đồ án môn học: thư mục
`doc/` chứa đề bài (`doc/Projects.pdf`) và slide bài giảng về bốn nhóm kiến thức tích hợp
dữ liệu (đồng nhất lược đồ và lược đồ trung gian, ghép bản ghi, xử lý truy vấn, chọn nguồn).

Dữ liệu mô tả **một sàn thương mại điện tử**: đơn hàng, khách hàng, người bán, sản phẩm,
dòng hàng, thanh toán, đánh giá, vị trí địa lý theo mã bưu chính (CEP) và bảng dịch danh mục.
Sản phẩm bàn giao là **pipeline batch chạy cục bộ** biến 9 tệp CSV thô thành **star schema**
trong Parquet + DuckDB, kèm **dashboard Plotly Dash tiếng Việt** để đọc KPI, và — từ đợt
`261109-stats-and-models` — một **tầng `stats`** chạy năm phép kiểm định thống kê cùng một **bộ
phân loại đơn giao trễ**, ghi kết quả vào `data/reports/analysis.json`.

## 2. Mục đích hệ thống

| Mục tiêu | Cách hệ thống đáp ứng | Bằng chứng |
|---|---|---|
| Tích hợp nhiều nguồn lệch lược đồ | Hợp đồng lược đồ tường minh cho 9 bảng ở tầng ingest, cộng **lược đồ trung gian khai báo được** (`config/mediated-schema.yaml`) và bảng ánh xạ nguồn→thực thể | `src/ingest/schemas.py`, `src/integration/schema.py`, `src/integration/models.py` |
| Bảo đảm chất lượng dữ liệu | Cổng chất lượng 21 check cấu trúc; chế độ `full` thêm 9 check số dòng và 10 dị thường có allowlist | `src/quality/gate.py`, `src/quality/allowlist.py` |
| Mô hình hóa phân tích | 5 dimension, 4 fact, 2 aggregate; kiểm tra grain và khóa duy nhất | `src/integrate/dimensions.py`, `src/integrate/facts.py`, `src/integrate/aggregates.py`, `src/integrate/validate.py` |
| Truy vấn phân tích | 11 view DuckDB trên Parquet; dịch vụ truy vấn chỉ đọc **9 phương thức** (5 KPI cũ + 4 phục vụ tầng `stats`) | `src/integrate/catalog.py`, `src/analytics/service.py` |
| Kiểm định thống kê | Năm phép: tỉ lệ trễ kèm khoảng Wilson; so sánh hai bang; tương quan giá–phí kèm khoảng Fisher; kiểm định vùng × trễ; phân rã mùa vụ cộng tính chu kỳ 12 | `src/analytics/statistics.py` |
| Dự báo đơn giao trễ | Hồi quy logistic có cân trọng số lớp trên **khung grain đơn** (11 đặc trưng), chia theo thời gian tại `2018-04-01`, ngưỡng chọn theo F1, AUC kèm cờ "dưới 0,70" | `src/analytics/model.py` |
| Viết lại & đối chiếu truy vấn | 3 mẫu truy vấn khai báo, kế hoạch viết lại trên lược đồ trung gian, so KPI với tham chiếu trong dung sai 0,01 BRL | `src/integration/rewrite.py`, `src/common/kpis.py` |
| Ghép bản ghi (record linkage) | Sinh kết quả ghép theo hai đối tượng (khách hàng, người bán) vào `data/integration/` | `src/linkage/*`, `src/linkage/result.py` |
| Chọn nguồn dữ liệu | Hồ sơ nguồn + chọn nguồn theo độ phủ trường, chi phí, độ trễ | `src/integration/selector.py` |
| Trình bày kết quả | Dashboard **5 tab** (Tổng quan, Danh mục, Giao vận, Tích hợp, Kết quả phân tích), **9 callback** | `src/dashboard/app.py`, `src/dashboard/analysis_tab.py`, `config/integration-tab.yaml` |
| Mô phỏng vận tốc dữ liệu | Micro-batch theo `inbox/<batch_id>/<table>.csv`, manifest SHA-256 idempotent, replay theo tháng | `src/pipeline/micro_batch.py`, `src/pipeline/replay.py` |

## 3. Chức năng chính (theo lát cắt người dùng)

1. **Chạy toàn bộ pipeline** bằng một lệnh CLI: `python -m src.pipeline run --stage all`
   (ingest → clean → quality → integrate → linkage → analyze). **Lưu ý**: `stats` **không** nằm trong
   `--stage all` dù có tên trong `STAGES` (`src/pipeline/stages.py:24` so với `:91-179`).
2. **Chạy từng tầng** riêng lẻ để gỡ lỗi (`--stage ingest|clean|integrate|analyze|stats`).
3. **Sinh báo cáo phân tích + huấn luyện mô hình** bằng `--stage stats`: một lần ghi duy nhất
   `data/reports/analysis.json` chứa cả khối `stats` và khối `model`.
4. **Nạp dữ liệu tăng dần** từ hộp thư `inbox/`, upsert theo khóa tự nhiên, bỏ qua batch đã
   xử lý theo hash.
5. **Replay lịch sử**: cắt dữ liệu đã làm sạch theo tháng gần nhất để tạo batch và xử lý tuần tự.
6. **Xem KPI và biểu đồ** theo bộ lọc ngày/bang/vùng/danh mục/trạng thái đơn (ba tab báo cáo).
7. **Xem bốn thẻ của tab "Tích hợp"**: lược đồ trung gian, viết lại truy vấn, ghép bản ghi, chọn nguồn —
   mỗi thẻ mở một màn hình chi tiết; vùng `don-theo-thang` chạy truy vấn đã viết lại trên nguồn CSV.
8. **Xem báo cáo phân tích trên tab thứ năm** ("Kết quả phân tích"): bốn thẻ tóm tắt (tỉ lệ trễ, số đơn,
   số kiểm định bị bỏ, AUC kèm dấu đạt/không đạt 0,70), mục thống kê năm phép kiểm định, mục mô hình bốn
   số đọc. Tab **không tính toán gì**: mọi con số đến từ `analysis.json`.

## 4. Chỉ số nghiệp vụ chuẩn (KPI baseline)

Các con số dưới đây là **hợp đồng hồi quy** của hệ thống: `src/integrate/reconcile.py` chặn
pipeline nếu lệch quá dung sai, và test tích hợp khẳng định lại chúng.

| KPI | Giá trị | Định nghĩa |
|---|---|---|
| Doanh thu đơn `delivered` | 15.419.773,75 BRL | Tổng `price + freight_value` của dòng hàng thuộc đơn đã giao |
| Số đơn `delivered` | 96.478 | `COUNT(DISTINCT order_id)` trên dòng hàng đã giao |
| AOV | 159,83 BRL | Doanh thu / số đơn giao được |
| Đơn giao trễ | 7.826 | `delivered_customer_date > estimated_delivery_date` |
| Tỷ lệ giao trễ | 8,11% | Đơn trễ / đơn đã giao |

Nguồn: `src/integrate/reconcile.py` (`BASELINE` ở `:8-14`, `TOLERANCE` ở `:16-22`), `README.md`,
`docs/3v.md`; được test tích hợp khẳng định lại tại `tests/integration/test_u2_end_to_end.py:29-41`,
`test_u3_end_to_end.py:76-77` và `test_u1_stats_end_to_end.py:64-103`.
Doanh thu ở đây **gồm phí vận chuyển**; tổng `payment_value` không khớp tuyệt đối
(378 đơn lệch > 0,01 BRL — xem `reconcile_payments` trong `src/ingest/reports.py`, khẳng định ở
`tests/integration/test_u1_end_to_end.py:65`).

Định nghĩa doanh thu còn được khai **một lần** trong sổ KPI dùng chung `src/common/kpis.py`
(`REVENUE_DEFINITION = "price + freight_value của đơn delivered"`, dòng 11), nơi mọi KPI kiểu tiền bị
**từ chối** nếu thiếu định nghĩa này (`validate_ledger`), và `src/analytics/report.py` ghi lại chính
định nghĩa đó vào khối `seasonal` của báo cáo.

### Chỉ số chất lượng của mô hình (mới, chưa phải KPI baseline)

| Chỉ số | Giá trị hiện tại trên dữ liệu thật | Ở đâu |
|---|---|---|
| Đích | `is_late` trên đơn `delivered` | `src/analytics/model.py:19` |
| Quần thể | 96.478 đơn đã giao, 7.826 đơn trễ | `model.py:22-23` |
| Mốc chia tập | `2018-04-01` (đơn rơi đúng ngày cắt thuộc tập kiểm tra) | `model.py:20`, `:140-156` |
| AUC | **0,5133** — dưới mốc 0,70 nên cờ `auc_below_target = true` | `tests/integration/test_u3_end_to_end.py:116-117` |
| Ngưỡng cảnh báo | 0,40 (lưới 19 điểm, chọn theo F1 trên tập kiểm tra) | `tests/unit/test_dashboard_analysis_tab.py:461` |
| Precision / Recall | 0,0866 / 0,2645 | `tests/unit/test_dashboard_analysis_tab.py:462-463` |

Những con số này **không** thuộc `BASELINE` của `KpiReconciler` và **không** bị cổng chất lượng chặn;
chúng chỉ được ghi vào báo cáo và hiển thị. Đây đúng là vùng mà intent
`261111-model-feature-improvemen` muốn cải thiện (baseline so sánh: một đặc trưng `customer_state`
duy nhất đạt AUC 0,5333 — theo `ideation/scope-definition/scope-document.md` §"Mục tiêu của đợt").

## 5. Đối tượng sử dụng

| Vai trò | Nhu cầu | Bề mặt sử dụng |
|---|---|---|
| Kỹ sư dữ liệu / người vận hành | Chạy lại pipeline, xử lý batch lỗi, đọc log | CLI `src.pipeline`, `logs/<run_id>.jsonl` (giữ 10 tệp gần nhất), `docs/runbook.md` |
| Nhà phân tích nghiệp vụ | Xem doanh thu, danh mục, giao vận theo bộ lọc | Dashboard Dash tại `http://127.0.0.1:8050`, tab Tổng quan / Danh mục / Giao vận |
| Người đọc kết quả thống kê & mô hình | Biết tỉ lệ trễ, phép kiểm định nào chạy được, mô hình đạt hay không đạt mốc | Tab "Kết quả phân tích", `data/reports/analysis.json` |
| Người học tích hợp dữ liệu | Xem bốn nhóm kiến thức được cài đặt thật | Tab "Tích hợp" (4 thẻ + màn hình chi tiết) |
| Giảng viên / người chấm | Đối chiếu 3V, kiến trúc, bằng chứng chất lượng | `docs/3v.md`, `docs/data-dictionary.md`, báo cáo JSON trong `data/reports/` và `data/integration/` |
| Lập trình viên mở rộng | Thêm nguồn, thêm tab, đổi mô hình | `src/` theo tầng, `tests/` |

## 6. Ba đặc trưng dữ liệu lớn (3V) như hệ thống tuyên bố

- **Volume**: 1.550.922 dòng trên 9 CSV; riêng `geolocation` 1.000.163 dòng.
- **Variety**: grain khác nhau (đơn, dòng hàng, thanh toán, đánh giá), dữ liệu tham chiếu
  ngoài (IBGE 27 bang → 5 vùng), nhiều kiểu thuộc tính (giao dịch, vận chuyển, địa lý, văn bản).
- **Velocity**: batch đầy đủ + micro-batch + replay theo tháng; **không phải streaming thật**
  (không Kafka), đây là mô phỏng có chủ đích (`docs/3v.md`).

## 7. Ranh giới và giả định nghiệp vụ

- `dataset/` là **nguồn bất biến**; mọi dẫn xuất ghi vào `data/`, `warehouse/`, `logs/`, `inbox/`.
- Chỉ phân tích đơn `delivered` theo mặc định (`KpiFilters.order_status = "delivered"`); mọi phân tích
  doanh thu/giao vận phải lọc trạng thái **tường minh**.
- Không có xác thực/người dùng: dashboard chỉ chạy localhost, một người dùng.
- **Đã có kiểm định thống kê và mô hình** (từ đợt `261109-stats-and-models`): `src/analytics/` chứa
  `statistics.py` (scipy) và `model.py` (scikit-learn). Ghi chú cũ "chưa có mô hình ML / chưa có kiểm định"
  trong bản CodeKB trước **đã lỗi thời**; `README.md` cũng không còn câu "chưa triển khai" cho mục ML.
- **Mô hình không được lưu ra đĩa**: `README.md` mục "Lưu ý" ghi rõ mỗi lần `--stage stats` là một lần
  huấn luyện lại từ mart; `src/` không có `joblib`/`pickle`, `AppConfig` không có thư mục mô hình.
- Báo cáo phân tích là **tệp duy nhất** mang cả hai khối (`version: 2`), ghi nguyên tử và **chỉ** tầng
  `stats` ghi.
- Toàn bộ thông điệp hiển thị cho người dùng bằng **tiếng Việt**; dữ liệu gốc giữ nguyên tiếng Bồ Đào Nha;
  số hiển thị theo định dạng Brazil (`1.234,56`, `R$`, `%`).
- Định danh trong lớp tích hợp dùng **tiếng Việt không dấu** (`don_hang`, `trang_thai`, `ma_don`) và id
  kebab-case tiếng Việt cho thành phần giao diện (`tich-hop`, `don-theo-thang`, `phan-tich`,
  `tom-tat`/`thong-ke`/`mo-hinh`).

## 8. Thuật ngữ

| Thuật ngữ | Nghĩa trong hệ thống |
|---|---|
| **Grain** | Đơn vị một dòng: đơn (`order_id`), dòng hàng (`order_id, order_item_id`), thanh toán (`order_id, payment_sequential`), đánh giá (`review_id, order_id`) |
| **Mart** | Bảng Parquet dẫn xuất trong `data/marts/` (5 dim, 4 fact, 2 agg) |
| **Cleaned** | Tầng dữ liệu đã chuẩn hóa kiểu/chuỗi trong `data/cleaned/` |
| **Raw** | Bản sao Parquet của CSV gốc trong `data/raw/` |
| **Allowlist dị thường** | Bộ đếm dị thường được chấp nhận cho lô đầy đủ (`src/quality/allowlist.py`) |
| **Đơn trễ** | Đơn `delivered` có ngày giao thực tế muộn hơn ngày dự kiến (`is_late`, chỉ đúng khi `is_delivered`) |
| **Khung huấn luyện** | `AnalyticsService.training_frame()` — một dòng mỗi đơn, dựng bằng `TRAINING_FRAME_SQL` |
| **Đặc trưng cấm** | `FORBIDDEN_COLUMNS` trong `model.py`: mọi cột chỉ biết **sau** khi giao, gồm `is_late`, `delivery_days`, `is_delivered`, các cột review và `order_delivered_carrier_date` |
| **Khối `stats` / khối `model`** | Hai khối của `data/reports/analysis.json`; `read_report` trả `rong` (không có tệp), `mot-phan` (thiếu một khối), `day-du` (đủ hai), `loi` (không đọc được/ sai phiên bản) |
| **`chua-chay`** | Token **chỉ tồn tại trong giao diện** trong lúc tab đang đọc tệp; không phải trạng thái của báo cáo |
| **Batch** | Thư mục `inbox/<batch_id>/` chứa các CSV cùng lược đồ nguồn |
| **Lược đồ trung gian** | Ánh xạ khai báo được từ bảng/cột nguồn sang thực thể và trường dùng chung (`config/mediated-schema.yaml`) |
| **Sổ KPI** | `src/common/kpis.py`: mã, nhãn, công thức, định nghĩa doanh thu, đơn vị của từng chỉ số |
| **Vùng kết quả** | Khối hiển thị số liệu của lát cắt mỏng trong tab "Tích hợp" (`don-theo-thang`) |

## 9. Liên kết

- Cách các thành phần ráp lại và luồng một đơn hàng: `architecture.md`.
- Danh sách thành phần, trách nhiệm, phụ thuộc: `component-inventory.md`.
- Bề mặt lệnh, hàm, view, tệp, callback: `api-documentation.md`.
- Nợ kỹ thuật và rủi ro cho đợt nâng cấp: `code-quality-assessment.md`.
