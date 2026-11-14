# Frontend Components — u3-prediction-ui

Nguồn: `functional-spec.md` §2–§7, `rules.md` (BR3.11–BR3.31), `../../../inception/contract-design/contract-summary.md` (C3), `../../../inception/refined-mockups/` (bố cục mục thứ tư).

Khuôn: Dash + `dash_mantine_components`, dựng cây thuần trong Python, test bằng cách duyệt cây và đọc `props` — không mở trình duyệt.

## 1. Cây thành phần

```
PredictionSection                          (html.Section, data-section="du-doan")
├─ SectionHeader                           (_section_header — dùng lại)
│  ├─ H3 "Dự đoán"
│  └─ P  caption: "... MỘT DÒNG HÀNG ..."
├─ form (html.Fieldset, id="bieu-mau-du-doan")
│  ├─ legend "Thông tin một dòng hàng"
│  ├─ DropdownField x3     ids: o-bang-nguoi-ban, o-bang-nguoi-mua, o-thanh-toan
│  ├─ InputField x6        ids: o-ngay-dat, o-gia-mon, o-so-mon,
│  │                            o-tra-gop, o-ngay-duyet, o-ngay-ban-giao
│  ├─ ChecklistField       id:  o-co-hang        (hai mục: has_items, has_payment)
│  ├─ Button               id:  nut-du-doan      "Dự đoán"
│  └─ dcc.Loading(id="du-doan-dang-tai", custom_spinner=...)
│     └─ Div#du-doan-ket-qua
│        ├─ PendingNotice                        (chua-chay)
│        ├─ ModelMissingNotice                   (mo-hinh-chua-san)
│        ├─ FieldErrorList                       (loi nhập: data-field từng ô)
│        └─ OutcomeCard                          (day-du)
│           ├─ ProbabilityLine
│           ├─ ThresholdLine
│           ├─ VerdictLine
│           └─ ContributionList (3 x ContributionRow)
```

`PredictionSection` là **con** của `RESULT_BODY_ID` (`analysis-result`). Không đặt `aria-live` mới; vùng `RESULT_BODY_ID` là nơi thông báo duy nhất. Tiêu đề mục là `html.H3`; mọi vùng có `aria-label`.

## 2. Mười thành phần nhập, mười một giá trị

| # | Loại | `id` | Trường | Mặc định | Nhãn |
|---|---|---|---|---|---|
|---|---|---|---|---|---|
| 1 | `dcc.Dropdown` | `o-bang-nguoi-ban` | `seller_state` | `SP` | Bang người bán |
| 2 | `dcc.Dropdown` | `o-bang-nguoi-mua` | `customer_state` | `SP` | Bang người mua |
| 3 | `dcc.Dropdown` | `o-thanh-toan` | `payment_type` | `credit_card` | Hình thức thanh toán |
| 4 | `dcc.Input` (`type=text`) | `o-ngay-dat` | `order_date` | `2018-01-01` | Ngày đặt hàng (YYYY-MM-DD) |
| 5 | `dcc.Input` (`type=number`) | `o-gia-mon` | `item_price` | `100` | Giá món hàng (BRL) |
| 6 | `dcc.Input` (`type=number`) | `o-so-mon` | `item_count` | `1` | Số món trong đơn |
| 7 | `dcc.Input` (`type=number`) | `o-tra-gop` | `installments` | `1` | Số kỳ trả góp |
| 8 | `dcc.Input` (`type=number`) | `o-ngay-duyet` | `approval_days` | `1` | Số ngày đặt → duyệt |
| 9 | `dcc.Input` (`type=number`) | `o-ngay-ban-giao` | `handling_days` | `3` | Số ngày duyệt → bàn giao |
| 10 | `dcc.Checklist` | `o-co-hang` | `has_items`, `has_payment` | cả hai chọn | Dòng hàng có món / có thanh toán |

Nhãn: Dash 4.4.1 **từ chối** prop `aria-label` trên `dcc.Dropdown`/`dcc.Input`/`dcc.Checklist`, nên mỗi ô được bọc trong một `html.Label` thật (kèm `data-field`); nhãn ngữ nghĩa vẫn đạt BR3.12. Đây là chỗ mã khác chữ `aria-label` ban đầu của thiết kế, và chữ đã được sửa theo.

`STATE_CODES` là hằng **mới của U3**, 27 mã UF (hai chữ cái). Repo hiện **không** có danh sách này: `FittedModel.state_regions` được dựng từ `customer_state` sau khi nạp mô hình và **không** phủ `seller_state`, nên không dùng làm nguồn lựa chọn — dùng nó sẽ làm biểu mẫu phụ thuộc tệp mô hình, trái yêu cầu "biểu mẫu dựng được ở trạng thái mô hình chưa sẵn".

`PAYMENT_TYPES` cũng là hằng của U3: `credit_card`, `boleto`, `voucher`, `debit_card`, `not_defined`. U2 **không** kiểm miền này (giá trị lạ rơi vào `'unknown'` khi mã hoá), nên đây là ràng buộc **của giao diện**, không phải của hợp đồng.

## 3. Trạng thái và props

`PredictionViewState` (frozen dataclass, hàm thuần):

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `token` | `str` | `chua-chay`, `mo-hinh-chua-san`, `day-du` (ba token **render được**); `dang-tai` do `dcc.Loading` thể hiện, không phải token render; `loi` là token đóng của repo cho lỗi nhập/chấm điểm |
| `outcome` | `PredictionOutcome \| None` | kết quả của `score_item` (U2) |
| `threshold` | `float \| None` | ngưỡng đọc từ `report.model.threshold` (bắt buộc khi có khối) |
| `notice` | `str` | câu hướng dẫn hoặc thông điệp lỗi |
| `errors` | `dict[str, str]` | lỗi theo `id` ô |

Ánh xạ từ báo cáo: `rong`/`loi` ⇒ **không có** mục; `mot-phan` + `model is None` ⇒ không có mục; `mot-phan` + có `model` ⇒ như `day-du` (ngưỡng luôn có, xem `functional-spec.md` D-1).

Sáu nhãn trạng thái của FR3.2 ánh xạ vào ba token render + một spinner + hai nhánh không có mục. Không có trạng thái thứ bảy: lỗi khối dùng `mo-hinh-chua-san` với `notice` riêng.

## 4. Callback

Một callback mới, một `Output`:

| Thành phần | Giá trị |
|---|---|
| `Output` | `du-doan-ket-qua.children` |
| `Input` | `nut-du-doan.n_clicks` + **12 `Input`** cho 11 giá trị (hai cờ cùng khai `o-co-hang.value` hai lần — không thêm thành phần nào) |
| `prevent_initial_call` | `True` |
| `State` | không dùng — mọi thứ đến từ `Input` để test gọi trực tiếp được |

Luồng trong callback (thuần, chỉ hai lần đọc có kiểm soát):

1. `read_report(report_path(config))` — đọc **lại** tệp cục bộ mỗi lần bấm; đây là nguồn duy nhất của `report.model.threshold`. Không dùng `State` cho ngưỡng.
2. `report.model is None` (báo cáo vừa bị thay bằng bản thiếu khối) ⇒ trả `mo-hinh-chua-san`, **không** truy cập `None.threshold`.
3. `validate_form(values)` → `errors`. Có lỗi ⇒ trả cây lỗi (BR3.19), không chấm.
4. `load_model(config.models_dir)` → `None` hoặc `ModelError` ⇒ cây BR3.25.
5. `score_item(model, item, threshold=report.model.threshold)` — ngưỡng **luôn** từ báo cáo vừa đọc.
6. Dựng `OutcomeCard` + `ContributionList`.

Không tính lại chỉ số, không đọc DuckDB, không huấn luyện. "Đang tính" do `dcc.Loading` bọc vùng kết quả; nút **không** bị khoá (ADR-005).

## 5. Kiểm hợp lệ phía giao diện

`validate_form` là hàm thuần trả `dict[id, thông điệp]`:

| Ô | Điều kiện hợp lệ | Thông điệp |
|---|---|---|
| `o-bang-nguoi-ban`, `o-bang-nguoi-mua` | giá trị trong `STATE_CODES` | "Chọn bang người bán/người mua" |
| `o-thanh-toan` | giá trị trong `PAYMENT_TYPES` | "Chọn hình thức thanh toán" |
| `o-ngay-dat` | `pd.Timestamp` đọc được | "Ngày phải theo dạng YYYY-MM-DD" |
| `o-gia-mon` | số hữu hạn `>= 0` | "Giá phải là số không âm" |
| `o-so-mon` | số nguyên `>= 1` | "Số món phải là số nguyên từ 1" |
| `o-tra-gop` | số nguyên `>= 1` | "Số kỳ trả góp phải từ 1" |
| `o-ngay-duyet` | số trong `0…365` | "Số ngày đặt→duyệt phải trong 0…365" |
| `o-ngay-ban-giao` | số trong `0…365` | "Số ngày duyệt→bàn giao phải trong 0…365" |

Miền số và dạng mã bang **trùng** với `_serve_features` của U2 (`MAX_DAYS = 365`, `STATE_CODE_LENGTH = 2`, giá `>= 0`, số món `>= 1`, trả góp `>= 1`). Hai chỗ **khác** và có chủ đích: (a) `payment_type` do giao diện giới hạn 5 giá trị còn U2 nhận chuỗi bất kỳ; (b) U2 kiểm sau khi đã có dữ liệu, giao diện kiểm trước để đặt lỗi đúng ô. `ModelError` của U2 vẫn là lưới an toàn.

Lỗi hiện **trong vùng kết quả** (chỉ có **một** `Output`, nên không thể có Output thứ hai cho từng ô), mỗi dòng lỗi là `html.P(className="field-error", role="alert")` gắn `data-field` = id ô để người đọc và test biết lỗi thuộc ô nào; lớp `.field-error` được **thêm vào `assets/style.css`** trong cùng thay đổi (BR3.31).

## 6. Điểm tích hợp

| Điểm | Hướng | Ghi chú |
|---|---|---|
| `read_report(report_path(config))` | đọc | đường hiện có; không đọc lại trong callback con |
| `load_model(config.models_dir)` | đọc | C2b; `None` là trạng thái bình thường, `ModelError` là payload hỏng |
| `score_item(model, item, threshold=...)` | gọi | U2; hàm thuần, tất định; `threshold` bắt buộc |
| `beats_floor(...)` | chỉ test | U3 **không** gọi trong giao diện |
| `AUC_TARGET` | import | cho nhãn thẻ AUC (BR3.28); không dùng để suy cờ |
| `format_number` / `format_percent` | gọi | định dạng Brazil; `format_percent` **không** nhân 100 — truyền `probability * 100` |

## 7. Khả năng tiếp cận

- Tiêu đề mục `H3`, cùng cấp ba mục kia; mọi vùng có `aria-label`.
- `Fieldset` + `legend` cho biểu mẫu; nhãn gắn với ô bằng `aria-label`.
- Không `tabIndex` dương; thứ tự tab theo thứ tự DOM.
- Chữ dưới 16px dùng `--text-2` (tương phản ≥ 4,5:1), không thêm token màu.
- `dcc.Loading` có `aria-busy` sẵn; không đặt `aria-live` mới.

## 8. Móc kiểm thử

| Test | Đọc gì |
|---|---|
| `test_dashboard_analysis_tab.py` | `SECTION_IDS` = 4 mục, thứ tự; không ô nhập thứ mười một; **xoá** `test_auc_card_falls_back_to_the_value_when_the_flag_is_absent` |
| `test_dashboard_smoke.py` | `len(app.callback_map) == 10`; `build_dashboard_outputs` vẫn trả **9** |
| `test_u3_end_to_end.py` | 5 tab, 10 callback; cập nhật chỗ ghim chuỗi "0,70" ở `:119` |
| `test_u3_prediction_section.py` (mới) | 10 thành phần/11 giá trị, `len(STATE_CODES) == 27`, `len(PAYMENT_TYPES) == 5`, sáu trạng thái, lỗi tại ô, ba đóng góp, câu mô hình chưa sẵn, nhãn tiếng Việt của trường, `README.md` không còn câu "chỉ đọc" |
| `test_u3_floor_end_to_end.py` (mới, `slow`) | nhánh xanh trên tệp thật |

`beats_floor` hai nhánh **đã** được `tests/unit/test_analytics_baseline_block.py` phủ từ U2 — U3 không tạo tệp test trùng.

**Ba** đường dẫn mới (`src/dashboard/prediction_section.py`, `tests/unit/test_u3_prediction_section.py`, `tests/integration/test_u3_floor_end_to_end.py`) phải được thêm vào **cả hai** danh sách khai tay — `ci.yml:35` và `NEW_FILES` của `tests/unit/test_ci_config.py` — **cùng lúc** với việc tạo tệp (BR3.31).

## 9. Điều không thuộc đơn vị này

- Không sửa `src/analytics/model.py`; chỉ `import` `score_item`, `beats_floor`, `MODEL_AUC_FLOOR`, `AUC_TARGET`.
- Không đổi số tab, số thẻ tóm tắt, số `Output` của callback KPI.
- Không đọc `warehouse/` trực tiếp, không gọi `AnalyticsService`.
