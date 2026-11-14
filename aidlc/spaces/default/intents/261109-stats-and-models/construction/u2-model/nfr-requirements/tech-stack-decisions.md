# Tech Stack Decisions — u2-model

Nguồn: `../../../inception/requirements-analysis/requirements.md`, `../functional-design/rules.md`, `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`, `requirements.txt`, `functional-design-questions.md`.

## Quyết định

| # | Quyết định | Lý do | Phương án đã loại |
|---|---|---|---|
| TS-1 | Python 3.13, `pandas` 2.2, `numpy` **qua `pandas`** (không import trực tiếp) | Cả repo chạy trên đó; quy tắc dự án coi `numpy` là bám theo `pandas` | Ghim `numpy` trực tiếp: thêm một phụ thuộc chỉ vì vài phép mảng |
| TS-2 | Ghim `scikit-learn==1.6.1` cho mô hình phân loại | Cần AUC, đường cong precision/recall và cân trọng số lớp; tự viết là tự viết lại một thư viện. 1.6.1 chạy được trên Python 3.13/Windows và chấp nhận cặp `numpy 2.2.1` + `scipy 1.15.2` đang ghim | Tự viết logistic regression: đúng nhưng phải tự kiểm AUC và ngưỡng, gấp đôi bề mặt lỗi |
| TS-6 | Mã hoá biến phân loại bằng one-hot với **danh sách phạm trù cố định lấy từ tập huấn luyện**; phạm trù lạ thành vector 0 | `scikit-learn` từ chối chuỗi; one-hot cố định giữ cho ma trận đặc trưng có cùng số cột ở hai tập, và phạm trù chỉ xuất hiện ở tập kiểm tra không làm lệch số cột | `LabelEncoder`: tạo thứ tự giả giữa các bang; one-hot học từ dữ liệu gộp cả hai tập: rò rỉ thông tin tương lai vào tập huấn luyện |
| TS-7 | Năm cột **phân loại**, bốn cột **số**: phân loại là `payment_type`, `customer_state`, `customer_region`, `purchase_month`, `purchase_weekday`; số là `item_count`, `item_total`, `item_price_max`, `payment_installments` | Danh sách chín cột trong `entities.md` là bản có thẩm quyền. `purchase_month` và `purchase_weekday` mã hoá **one-hot**, không theo thứ tự — tháng 12 không "lớn hơn" tháng 1, và thứ Hai không "lớn hơn" Chủ nhật | Coi tháng/thứ là số thứ tự: tạo quan hệ giả mà mô hình sẽ học |
| TS-8 | Giá trị thiếu: cột phân loại thiếu thành **một phạm trù `unknown`**; cột số thiếu thành **0** kèm một cột cờ `has_*` tương ứng; **không bỏ dòng nào** | Đơn đã giao có thể không có dòng hàng hoặc không có dòng thanh toán; bỏ dòng sẽ phá BR2.1 và BR2.7 (96.478 đơn / 7.826 trễ) và làm lệch cỡ mẫu. `scikit-learn` từ chối NaN | Bỏ dòng thiếu: đổi cỡ mẫu; điền trung bình: che mất sự khác biệt giữa "không có" và "bằng 0" |
| TS-9 | Chuẩn hoá bốn cột số trước khi huấn luyện; `max_iter = 1000`; cảnh báo không hội tụ là lỗi, không phải ghi chú | `item_total` cỡ nghìn đứng cạnh dummy 0/1 làm bộ giải chậm hội tụ; không chuẩn hoá thì NFR1.3 (tái lập) và NFR1.1 (15 phút) đều không bảo đảm | Không chuẩn hoá: hệ số phụ thuộc thang đo, kết quả đổi khi thang đổi |
| TS-3 | Không dùng `statsmodels`, không dùng `xgboost`/`lightgbm` | `statsmodels` đã bị loại ở U1 (Q4); boosting thêm một phụ thuộc nặng cho một mô hình mà mục tiêu chỉ là AUC ≥ 0,70 | Boosting: cần thêm gói, thời gian huấn luyện dài hơn, khó giải thích hơn |
| TS-4 | Mô hình không tuần tự hoá ra đĩa | Chỉ số đi vào báo cáo; tệp mô hình là tài sản không ai đọc | Lưu `.joblib`: thêm một chỗ phải quản lý phiên bản |
| TS-5 | Đọc dữ liệu qua `AnalyticsService`, bổ sung phương thức đọc bảng đặc trưng | Quy tắc dự án: phân tích mới đọc mart có sẵn | Đọc Parquet trực tiếp: bỏ qua lớp đã kiểm |

## Hệ quả lên `requirements.txt`

Thêm đúng một dòng:

```
scikit-learn==1.6.1  # mô hình phân loại đơn trễ cho u2-model; xem tech-stack-decisions.md TS-2
```

`scikit-learn` hiện không có trong `requirements.txt`, và quy tắc dự án cấm import gói chưa ghim. Dòng trên là điều kiện để bước Code Generation được phép viết `import sklearn`.

## Điều còn phải xác nhận khi cài

Gói thật sự **trôi** trong phép cài này là `numpy`: nó không được ghim trực tiếp, chỉ có mặt gián tiếp qua `pandas`, và `scipy==1.15.2` đang được ghim *theo* `numpy 2.2.1` (`requirements.txt`). `scikit-learn` kéo thêm `joblib` và `threadpoolctl`.

Phép kiểm sau khi cài, theo đúng thứ tự:

1. `pip show numpy scipy joblib threadpoolctl` — `numpy` phải vẫn là **2.2.1**, `scipy` vẫn **1.15.2**; hai gói mới chỉ được thêm, không được thay bản cũ.
2. Nếu `numpy` bị nâng, ghim lại đúng `numpy==2.2.1` kèm lý do trong `requirements.txt`, rồi chạy lại toàn bộ bộ `slow` — nâng `numpy` có thể làm lệch số của các kiểm định U1 đã kiểm chứng.
3. Chạy lại bộ `slow` của U1 trước khi viết bất kỳ dòng mã mô hình nào.

## Tái lập kết quả

BR2.9 làm tròn 4 chữ số trước khi ghi, nên một khối mô hình không tái lập được sẽ trông như một khối khác. Vì vậy bộ phân loại phải chốt `random_state` cố định và dùng solver mặc định của `scikit-learn`; hai lần chạy trên cùng dữ liệu phải cho cùng `auc`, `threshold`, `precision`, `recall`.

## Yêu cầu phi chức năng của đơn vị này

Đơn vị này không sinh tệp `performance-requirements.md` riêng (xem `produces` của stage cho loại đơn vị này), nên các mốc dưới đây nằm ngay ở đây.

| Mã | Yêu cầu | Mốc | Cách kiểm |
|---|---|---|---|
| NFR1.1 | Thời gian huấn luyện | dưới 15 phút trên máy phát triển | Test `slow`, đo đồng hồ quanh bước huấn luyện |
| NFR1.2 | Thời gian toàn bước mô hình | dưới 15 phút, cùng mốc với NFR1.1 — không đặt mốc thứ hai khi yêu cầu gốc chỉ có một | Cùng test `slow`, đo quanh cả bước |
| NFR1.3 | Tái lập được | hai lần chạy trên cùng dữ liệu cho cùng `auc`, `threshold`, `precision`, `recall` sau khi làm tròn | Test `slow` chạy hai lần, so khối `model` |
| NFR2.1 | Độ phủ test | `pytest --cov=src --cov-fail-under=80` xanh trên toàn bộ bộ test | Cổng phủ trong chuỗi xác nhận và CI |
| NFR4.1 | Chất lượng mã | `ruff check .` và `ruff format --check` sạch; tệp mới có trong danh sách của `ci.yml` | Chạy trong chuỗi xác nhận và CI |

## Một quyết định chưa chốt, cố ý để lại

Mốc cắt thời gian giữa tập huấn luyện và tập kiểm tra **chưa được chốt**. Nó không phải lựa chọn kỹ thuật mà là lựa chọn về dữ liệu: mốc quyết định `train_n`/`test_n`, do đó quyết định AUC và việc mô hình có đạt 0,70 hay không. Ba ứng viên đã trình bày (2018-04-01, 2018-07-01, hoặc 80/20 trên trục thời gian). Nó phải được chốt ở cổng duyệt kế hoạch viết mã, trước khi huấn luyện lần đầu.
