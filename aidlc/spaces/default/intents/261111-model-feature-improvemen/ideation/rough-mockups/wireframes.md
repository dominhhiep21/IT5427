# Wireframes — khối dự đoán trong tab "Kết quả phân tích"

Nguồn: `../scope-definition/scope-document.md`, `../scope-definition/intent-backlog.md`, `../intent-capture/intent-statement.md`, `src/dashboard/analysis_tab.py`, `src/analytics/model.py`, `assets/style.css`.

## Nguyên tắc rút ra từ tab đang chạy

Tab hiện có ba mục theo thứ tự đọc **Tóm tắt → Thống kê → Mô hình**, bốn thẻ tóm tắt, và không có `tabIndex` dương. Khối mới **phải** theo cùng khuôn: một mục thứ tư đọc tiếp sau Mô hình, cùng cấp tiêu đề `html.H3` như ba mục kia.

| Ràng buộc | Ở đâu | Hệ quả cho khối mới |
|---|---|---|
| Mọi vùng nội dung mang `aria-label` hoặc heading ngữ nghĩa | `NFR5.2` | khối là `<section aria-label="Dự đoán">` có `H3` |
| Không `tabIndex` dương; thứ tự focus theo thứ tự đọc | `NFR5.3` | **bảy** ô nhập nhận focus theo thứ tự khai báo, không ô nào có `tabIndex` |
| Chữ dưới 16px dùng `--text-2`, không dùng `--text-3` (chỉ 3,85:1) | `NFR5.1` | mọi nhãn, chú thích, dòng đóng góp dùng `--text-2` |
| Không thêm token màu mới | `BR3.9` | hai kết quả phân biệt bằng **chữ**, không bằng màu |
| Bốn thẻ tóm tắt là hợp đồng | `test_dashboard_analysis_tab` | không thêm thẻ thứ năm |
| Tiêu đề mục là `html.H3` | `test_each_section_heading_is_a_real_heading` | khối mới cũng `H3`, không phải `H2` |

## Đơn vị dự đoán — câu dẫn bắt buộc phải có

Câu đầu của khối phải nói rõ: **"Dự đoán cho một dòng hàng — một món hàng trong một đơn, có người bán riêng."** Đây là thay đổi trung tâm của đợt (đơn vị từ đơn sang dòng hàng) và là thứ người dùng phải hiểu trước khi nhập.

## Biểu mẫu: bảy ô, và ô nào là đặc trưng thật

Q2 = A chốt **sáu trường** mạnh nhất. Khi vẽ ra, cần thêm **một ô ngày đặt hàng** để suy ra tháng và thứ trong tuần — nếu không, hai đặc trưng đó phải bịa một giá trị. Vậy biểu mẫu là **sáu trường đã chốt + một ô ngày**, và cả ba chỗ trong tài liệu này ghi đúng con số **bảy**.

| Ô | Đặc trưng mà nó cấp | Kiểu |
|---|---|---|
| Bang người bán | `seller_state` — đặc trưng tuyến đường duy nhất dữ liệu này có | chọn từ danh sách 27 bang |
| Bang người mua | `customer_state` (+ `customer_region` suy ra từ bang) | chọn từ danh sách 27 bang |
| Ngày đặt hàng | suy ra `purchase_month`, `purchase_weekday` | chọn ngày |
| Giá món hàng | `item_price_max` (và `item_total` nếu một dòng hàng) | số |
| Số ngày đặt → duyệt | đặc trưng dẫn xuất từ `order_approved_at` | số nguyên |
| Số ngày duyệt → bàn giao | đặc trưng dẫn xuất từ `order_delivered_carrier_date` | số nguyên |
| Số lượng món trong đơn | `item_count` | số nguyên |

Mặc định cho phần còn lại, và **hiện rõ** trên màn hình: `payment_type = credit_card`, `payment_installments = 1`, `has_items = true`, `has_payment = true`.

**Không có ô phí vận chuyển.** `freight_value` **không phải** đặc trưng của mô hình — không có trong bộ hiện tại (`src/analytics/model.py`) và không có trong danh sách mới của U2 (`intent-backlog.md`). Một ô nhập cho nó sẽ là ô không ảnh hưởng tới kết quả, đúng loại giao diện nói dối. Nếu sau này muốn dùng phí vận chuyển, nó phải được thêm vào **danh sách đặc trưng** trước, rồi mới thêm ô.

**Danh sách cuối cùng chốt ở Functional Design**, sau khi U2 cố định bộ đặc trưng. Bảy ô trên là những trường **chắc chắn** phải có mặt vì chúng là lõi của khung bàn giao; nếu Functional Design bỏ một trường khỏi bộ đặc trưng thì ô tương ứng cũng bị bỏ khỏi biểu mẫu, không giữ lại cho đẹp.

## Khung màn hình — trạng thái `day-du`, kết quả **không** cảnh báo

```
┌──────────────────────────────────────────────────────────────────────┐
│  Báo cáo phân tích và mô hình                                        │
│                                                                      │
│  ┌─ Tóm tắt ────────────────────────────────────────────────────┐    │
│  │  8,11%  ·  96.478  ·  0  ·  0,5133                           │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─ Thống kê ───────────────────────────────────────────────────┐    │
│  │  (năm phép kiểm định, dải skipped nếu có)                     │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─ Mô hình ────────────────────────────────────────────────────┐    │
│  │  AUC 0,5133 · ngưỡng 0,40 · precision 0,0866 · recall 0,2645  │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─ Dự đoán ────────────────────────────────────────────────────┐    │
│  │  Dự đoán cho một dòng hàng — một món hàng trong một đơn,      │    │
│  │  có người bán riêng.                                          │    │
│  │                                                              │    │
│  │  Bang người bán           [ SP ▾ ]  Bang người mua [ RJ ▾ ]   │    │
│  │  Ngày đặt hàng            [ 2018-03-14 ]                      │    │
│  │  Giá món hàng             [ 129,90 ]                          │    │
│  │  Số ngày đặt → duyệt      [   1     ]                         │    │
│  │  Số ngày duyệt → bàn giao [   3     ]                         │    │
│  │  Số lượng món trong đơn   [   1     ]                         │    │
│  │                                                              │    │
│  │  Mặc định, sửa được: payment_type=credit_card,               │    │
│  │  installments=1, has_items, has_payment                      │    │
│  │                                                              │    │
│  │            [ Dự đoán ]        [ Đặt lại mặc định ]            │    │
│  │                                                              │    │
│  │  ── kết quả ──────────────────────────────────────────────    │    │
│  │  0,37 · dưới ngưỡng 0,40 · **KHÔNG cảnh báo**                 │    │
│  │                                                              │    │
│  │  Ba đóng góp lớn nhất (log-odds, không phải tổng):           │    │
│  │    +  số ngày duyệt → bàn giao (3 ngày)        +0,18          │    │
│  │    +  bang người bán = SP                      +0,09          │    │
│  │    −  giá món hàng (129,90 BRL)                −0,04          │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

## Khung màn hình — cùng khối, kết quả **có** cảnh báo

```
│  │  ── kết quả ──────────────────────────────────────────────    │    │
│  │  0,61 · trên ngưỡng 0,40 · **CẢNH BÁO: dòng hàng này có       │    │
│  │  nguy cơ trễ**                                               │    │
│  │                                                              │    │
│  │  Ba đóng góp lớn nhất (log-odds, không phải tổng):           │    │
│  │    +  số ngày duyệt → bàn giao (9 ngày)        +0,54          │    │
│  │    +  bang người bán = SP                      +0,11          │    │
│  │    −  giá món hàng (129,90 BRL)                −0,03          │    │
```

Hai kết quả **không** khác nhau bằng màu: khác bằng chữ `KHÔNG cảnh báo` / `CẢNH BÁO: dòng hàng này có nguy cơ trễ`, bằng vị trí so với ngưỡng (dưới/trên), và bằng xác suất. Đó là ràng buộc "không thêm token màu" — và cũng là cách đúng cho người mù màu.

**Cả hai khung dùng cùng một khuôn câu về đơn vị dòng hàng**, để khi chép vào mã không có chỗ nào tự nhiên quay lại nói "đơn".

## Định nghĩa "mức đóng góp" — thứ khiến con số kiểm được

Mô hình là hồi quy logistic trên ma trận one-hot. Với một dự đoán:

```
z = β₀ + Σᵢ βᵢ · xᵢ            (log-odds)
p = 1 / (1 + e^(−z))          (xác suất hiện trên màn hình)
đóng góp của trường f = Σ βᵢ · xᵢ  trên mọi cột one-hot của f
```

| Điều | Quy tắc |
|---|---|
| Đơn vị | **log-odds**, không phải xác suất, không phải "%" |
| Dấu | dương = đẩy nguy cơ **lên** so với mốc 0; âm = kéo xuống. Không phải "so với trung bình" |
| Gộp one-hot | mọi cột của cùng một trường cộng lại thành **một dòng** trước khi chọn ba dòng lớn nhất |
| Tổng | ba dòng hiện ra **không** cộng thành 0,37; tổng đầy đủ gồm mọi trường **và** hệ số chặn β₀ |
| Chọn ba dòng | theo trị tuyệt đối của đóng góp sau khi gộp |
| Nhãn trên màn hình | "Ba đóng góp lớn nhất (log-odds, không phải tổng)" — chữ này là bắt buộc |

Vì sao phải gộp: `customer_state` có 27 mức one-hot, nên không gộp thì "ba đóng góp lớn nhất" có thể là ba **mức của cùng một trường**.

## Sáu trạng thái của khối

Hai trạng thái **#1** ("không có khối") và **#5** ("có kết quả, chưa có ngưỡng") là bổ sung so với bản tóm tắt đã xác nhận ở stage này; chúng xuất hiện vì lần soát thứ nhất chỉ ra rằng bốn trạng thái không khép kín. Trạng thái #6 ("mô hình chưa sẵn") thì đã có trong bản tóm tắt.

| # | Trạng thái | Điều kiện | Hiện gì |
|---|---|---|---|
| 1 | **Không có khối** | báo cáo `rong` hoặc `loi` | **không có mục thứ tư**; tab giữ nguyên hành vi hiện tại (`sections_for()` trả rỗng khi `view.report is None`), thông báo `rong` đã nói lệnh cần chạy |
| 2 | **Chưa dự đoán** | `day-du` hoặc `mot-phan`, chưa bấm | bảy ô, chưa có kết quả, một dòng nói bấm để xem |
| 3 | **Đang tính** | đã bấm, chưa xong | nút ở trạng thái chờ, kết quả cũ mờ đi |
| 4 | **Có kết quả, có ngưỡng** | `report.model` có ngưỡng | xác suất · so ngưỡng · quyết định · ba đóng góp |
| 5 | **Có kết quả, chưa có ngưỡng** | `mot-phan`: `report.model` là `None` | xác suất · **"chưa có ngưỡng để so"** · ba đóng góp; không có câu cảnh báo |
| 6 | **Mô hình chưa sẵn** | báo cáo `day-du` nhưng `data/models/` chưa có | "Chưa có mô hình đã lưu. Chạy `python -X utf8 -m src.pipeline run --stage stats` để sinh `data/models/`, rồi mở lại tab này." |

Trạng thái 5 là hệ quả của `mot-phan`: không có khối mô hình thì không có ngưỡng 0,40 để so, và khối không được bịa ra một ngưỡng. Trạng thái 6 **không** phải `rong`: `rong` là không có báo cáo, còn đây là có báo cáo mà thiếu tệp mô hình — hai nguyên nhân, hai câu chữ.

## AUC của mô hình cây — ở đâu, và vì sao không ở trên tab

Q4 = A chốt mô hình triển khai là hồi quy logistic. Mô hình cây vẫn được huấn luyện để **báo cáo** đánh đổi, nhưng con số của nó nằm ở:

| Nơi | Có AUC của cây? |
|---|---|
| `data/reports/analysis.json` — trong khối `model` | **có** |
| Record của đợt (`code-summary.md` của U2, `test-results.md`) | **có** |
| Tab "Kết quả phân tích" | **không** — mục Mô hình giữ đúng bốn số hiện tại |

Lý do: thêm dòng thứ năm vào mục Mô hình là sửa một mục đang có test canh, trong khi người đọc con số đó là chính người làm — và họ đọc record. Ghi rõ ở đây để không ai chờ thấy nó trên màn hình.

## Mốc 0,70 áp cho mô hình nào

Mốc ≥ 0,70 áp cho **mô hình logistic được triển khai** — mô hình duy nhất có mặt trong báo cáo dưới dạng `model.auc`. Nếu chỉ mô hình cây đạt 0,70 còn logistic thì không, **tiêu chí của đợt vẫn không đạt**; con số của cây được ghi vào record như bằng chứng của đánh đổi, không được dùng để đổi trạng thái đạt.

## Ba chỗ phải sửa cùng lúc với stage này

Q4 = A làm ba câu trong tài liệu đã duyệt trở nên sai và **phải** được sửa trong cùng thay đổi:

| Tệp | Câu cũ | Thay bằng |
|---|---|---|
| `../scope-definition/scope-document.md` — "Trong phạm vi", U2 | "chọn theo AUC" | "lưu hồi quy logistic; chạy mô hình cây **để báo cáo** đánh đổi" |
| `../scope-definition/scope-document.md` — "Tiêu chí xong", dòng 2 | "AUC của mô hình **chọn** ≥ 0,70" | "AUC của mô hình **logistic triển khai** ≥ 0,70" |
| `../scope-definition/intent-backlog.md` — U2 | "lưu mô hình **thắng** vào `data/models/`" | "lưu mô hình **logistic** vào `data/models/`; AUC của cây ghi vào record" |

## Ràng buộc tiếp cận cho từng vùng

| Vùng | Heading | Landmark | Điểm vào bàn phím |
|---|---|---|---|
| Khối dự đoán | `html.H3` "Dự đoán" (cùng cấp ba mục kia) | `<section aria-label="Dự đoán">` | ô đầu tiên (bang người bán) |
| Biểu mẫu | `html.H4` "Thông tin đầu vào" | `<fieldset>` có `<legend>` | Tab đi tuần tự qua **bảy** ô |
| Kết quả | `html.H4` "Kết quả" | **không** đặt `aria-live` riêng | không nhận focus |

**Vùng thông báo duy nhất:** tab đã có một vùng `aria-live="polite"` ở `RESULT_BODY_ID`. Khối dự đoán **không** thêm vùng thứ hai — hai vùng lồng nhau sẽ đọc kết quả hai lần với trình đọc màn hình.

## Điều khung này **không** làm

Không thêm thẻ tóm tắt thứ năm. Không thêm tab. Không thêm token màu. Không biểu đồ. Không `aria-live` thứ hai. Không thêm dòng nào vào mục Mô hình. Không có ô nhập cho `freight_value`. Không dùng SHAP hay thư viện giải thích mới — đóng góp tính từ hệ số của chính logistic.
