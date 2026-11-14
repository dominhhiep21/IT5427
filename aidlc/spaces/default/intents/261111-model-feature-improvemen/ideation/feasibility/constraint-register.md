# Constraint Register

Nguồn: `../intent-capture/intent-statement.md`, `feasibility-assessment.md`, `aidlc/spaces/default/memory/project.md`, `aidlc/spaces/default/memory/team.md`, `requirements.txt`, `.github/workflows/ci.yml`.

## Ràng buộc kỹ thuật

| Mã | Ràng buộc | Vì sao | Kiểm bằng gì |
|---|---|---|---|
| **TC-01** | Không import thư viện chưa ghim trong `requirements.txt` | quy tắc dự án; `pyspark`/`xgboost`/`rapidfuzz` đều không có trong tệp | `requirements.txt` là danh sách đóng |
| **TC-02** | `dataset/` bất biến; mọi dữ liệu dẫn xuất vào `data/`, `warehouse/`, `logs/`, `inbox/` | quy tắc dự án | `.gitignore` + review diff |
| **TC-03** | 5 KPI baseline, số dòng 9 bảng nguồn, số dòng 11 bảng mart, 11 view DuckDB là hợp đồng cứng | `KpiReconciler` + `StarSchemaValidator` sẽ đỏ nếu lệch | `run --stage all` |
| **TC-04** | Chia tập theo `order_id`, không theo dòng hàng | nhãn là của đơn; chia theo dòng làm AUC bị thổi lên | test trên dữ liệu thật |
| **TC-05** | Chỉ chấm AUC trên đơn đã có `order_delivered_carrier_date` | khung dự đoán đặt tại chính thời điểm đó | truy vấn quần thể |
| **TC-06** | Độ phủ test ≥ 80%, đo trên **toàn bộ** bộ test, không hạ ngưỡng | cổng CI | `pytest --cov=src --cov-fail-under=80` |
| **TC-07** | Tệp nguồn mới phải được thêm vào danh sách `ruff format --check` trong `ci.yml` | danh sách khai tay | `test_ci_config.py` |
| **TC-08** | Mọi lệnh Python chạy UTF-8 | đường dẫn có ký tự tiếng Việt, dữ liệu có ký tự Bồ Đào Nha | `-X utf8` trong mọi khối lệnh |
| **TC-09** | Mô hình phải nạp lại được từ tệp đã lưu, cùng đầu vào cho cùng điểm | tiêu chí chất lượng thứ hai của `intent-statement` | phép kiểm lặp lại hai lần chạy |
| **TC-10** | Không thêm phụ thuộc kiểm tra kiểu tĩnh (`mypy`/`pyright`) | quyết định đã chốt | `requirements.txt` |

## Ràng buộc tổ chức

| Mã | Ràng buộc | Vì sao |
|---|---|---|
| **OC-01** | Một người làm, một người quyết định; không review chéo | team practice |
| **OC-02** | Làm trên nhánh `feature/analysis-and-models`; nhánh mới phải được thêm vào **cả** `on.push.branches` và `on.pull_request.branches` | team practice; nhánh ngoài danh sách là nhánh không ai kiểm |
| **OC-03** | "Xong" = chuỗi bốn bước xanh: bộ nhanh → `--stage all` → `--stage stats` → mở dashboard | team practice |
| **OC-04** | Không có môi trường thứ hai: không staging, không production, không Docker | `project.md` |
| **OC-05** | TDD: viết test trước cho hành vi mong muốn, thấy đỏ, rồi mới viết mã | team practice |

## Ràng buộc pháp lý

| Mã | Ràng buộc | Vì sao |
|---|---|---|
| **RC-01** | Không có yêu cầu tuân thủ nào áp dụng | dữ liệu công khai (Olist), không dữ liệu cá nhân thật, không khách hàng trả tiền, không xử lý thanh toán |

Không có PCI, HIPAA, SOC2 hay yêu cầu lưu trú dữ liệu nào ở đây — và ghi rõ là **không áp dụng**, không phải chưa xét.

## Ràng buộc do chính đợt này tạo ra

| Mã | Ràng buộc | Nguồn |
|---|---|---|
| **SC-01** | Danh sách cấm còn hiệu lực; chỉ nới đúng `order_approved_at` và `order_delivered_carrier_date`, và chỉ ở dạng số ngày | `intent-statement` |
| **SC-02** | Mốc 0,70 là mục tiêu, không phải cam kết; hạ mốc là lựa chọn chưa chốt | `intent-statement` |
| **SC-03** | Mốc sàn 0,55 trong CI là mốc **neo vào khung cũ**, phải được xem lại sau khi đo lại baseline | `intent-statement` |
| **SC-04** | Kết luận chỉ đúng cho giai đoạn 2016–2018 | `../market-research/market-trends.md` |
| **SC-05** | Đánh bại baseline đo lại là điều kiện; đánh bại mô hình hiện tại thì không | `../market-research/competitive-analysis.md` |
| **SC-06** | Nới mart **chỉ thêm cột**: `v_fact_orders` thêm 2 cột mốc, `v_fact_order_items` thêm `seller_state`; số dòng và số view không đổi | `feasibility-assessment.md` |
| **SC-07** | Mô hình lưu ở `data/models/` (đã bị `.gitignore`) kèm JSON mô tả đặc trưng và phiên bản thư viện | `feasibility-assessment.md` |
| **SC-08** | Mốc cắt giữ 2018-04-01 và chia theo **ngày đặt hàng**, dù dự đoán tại thời điểm bàn giao — sai lệch đã ghi ở R-08 | `feasibility-assessment.md`, `raid-log.md` |
