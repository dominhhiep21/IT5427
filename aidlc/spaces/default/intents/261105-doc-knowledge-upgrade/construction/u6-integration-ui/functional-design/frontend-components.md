# Frontend Components — u6-integration-ui

Nguồn: `functional-design/functional-spec.md` (W1–W5, bản đồ màn hình), `inception/requirements-analysis/requirements.md` (FR5.1–FR5.6, NFR1, NFR4), `inception/contract-design/contract-summary.md` (C1–C9), `inception/user-stories/stories.md` (US5.1–US5.3).

## 1. Cây thành phần

```
IntegrationTab                         tab_id="tich-hop"
├── ResultRegion × 1                    result_region_ids ("don-theo-thang"), callback riêng
├── OverviewScreen                    screen="overview"
│   └── CardGrid (4)
│       └── IntegrationCard × 4        card_id, state, metrics, on_open
├── DetailScreen                      screen in {schema, queries, linkage, sources}
│   ├── ScreenHeader                  title, on_back, on_reload
│   └── body theo màn hình
│       ├── SchemaPanel               C6: danh sách thực thể + bảng ánh xạ + nhãn GAV
│       ├── QueryPanel                C4: chọn mẫu, nút Chạy, hai bản SQL, kế hoạch, bảng kết quả
│       ├── LinkagePanel              C5: số liệu, bảng cặp, dòng "Bỏ qua"
│       └── SourcePanel               C7: bảng nguồn, nút "Đề xuất nguồn"
└── StateBlock                        state, message, items (dùng chung cho 5 trạng thái)
```

Mọi thành phần là hàm Python trả `dash.html`/`dmc` (không class), đúng mẫu `src/integration/card.py` đang dùng.

**Quan hệ với hiện trạng.** Tổng quan bốn thẻ **thay hẳn** phần thân tab đang có: `config/integration-tab.yaml` bỏ `result_block_ids`; **giữ và dựng `result_region_ids`** (`don-theo-thang`) cùng `card_ids` của C9; `build_integration_tab` dựng `OverviewScreen` thay cho ba khối, còn vùng kết quả (`ResultRegion`) nằm phía trên lưới thẻ; test `test_integration_tab_holds_the_three_result_blocks` được thay bằng test khẳng định **bốn** thẻ + một vùng và **sáu callback mới + hai callback cũ = 8** của ba tab báo cáo không đổi. `StateBlock` **dùng lại đúng bộ token hiện có** trong `src/integration/card.py` (`rong`, `dang-tai`, `day-du`, `mot-phan`, `loi`), không đặt bộ token thứ hai; tên tiếng Anh trong tài liệu này chỉ là nhãn đọc, `data-state` giữ nguyên giá trị tiếng Việt không dấu.

## 2. Props / state

| Thành phần | Props vào | State cục bộ | Ghi chú |
|---|---|---|---|
| `IntegrationTab` | `tab_id`, `cards` | `screen` | `screen` là state duy nhất của tab |
| `CardGrid` | `cards: list[CardSpec]` | — | Đúng bốn thẻ theo C9 |
| `ResultRegion` | `region_id`, `result`, `state` | — | Một vùng theo `result_region_ids` của C9, phía trên lưới thẻ; không phải `card_id` |
| `IntegrationCard` | `card_id`, `title`, `state`, `metrics` (hai dòng), `on_open`, `detail_id` | — | Nút có `data-testid=f"card-{card_id}-open"` |
| `DetailScreen` | `screen`, `title`, `on_back`, `on_reload` | — | Nút quay lại `data-testid="back-to-overview"` |
| `SchemaPanel` | `schema: MediatedSchemaViewForUi` (C6) | `entity_idx` | Chọn thực thể để xem bảng ánh xạ |
| `QueryPanel` | `templates: list[str]`, `result: QueryRunResult \| None`, `error` | `selected`, `running` | Nút Chạy `data-testid="run-query"` |
| `LinkagePanel` | `linkage: LinkageResultFile` (C5) | — | Dòng "Bỏ qua" `data-testid="linkage-skipped"` |
| `SourcePanel` | `catalogue: SourceCatalogueForUi` (C7), `selection` | `selected_query` | Nút đề xuất `data-testid="suggest-source"` |
| `StateBlock` | `state`, `message`, `items` | — | Năm trạng thái, `data-state` |

## 3. Luồng tương tác (callback)

| Callback | Kích hoạt | Làm gì | Trả |
|---|---|---|---|
| `route` | Bấm nút thẻ hoặc "quay lại" | Đổi `screen`, ẩn/hiện khối | `screen`, `children` |
| `run_query` | Bấm "Chạy" | Đặt `running`, gọi U5 → U3, dựng C4 | `state`, `children` |
| `suggest_source` | Bấm "Đề xuất nguồn" | Gọi U5 `select_source`, dựng lại bảng | `state`, `children` |
| `reload` | Bấm "Tải lại" | Gọi lại hợp đồng của màn hình | `state`, `children` |
| `run_region` | Bấm "Chạy truy vấn" trong vùng kết quả | Dựng lại vùng `don-theo-thang` của lát cắt | `children` của vùng |

Ba tab cũ giữ **nguyên** callback của chúng; tab mới có **6** callback của tab (bảng trên cùng callback nạp tổng quan), đặt tên khác để không đè `callback_id` cũ — tổng dashboard **8**.

## 4. Kiểm tra hợp lệ ở biên

- Chỉ bắt lỗi của những hợp đồng U6 **thật sự** tiêu thụ: C6 (`SchemaError`, `ConfigurationError`), C3 (`NoSourceAvailableError`, `SchemaError`), C4 (`QueryExecutionError`, `KpiMismatchError`), C5 (tệp hỏng), C7 (`NoSourceAvailableError`, `SchemaError`, `ConfigurationError`). C1/C2 đi qua U3/U5, không qua ranh giới giao diện.
- C5 **thiếu tệp** không phải lỗi: đó là trạng thái rỗng kèm hướng dẫn chạy `python -X utf8 -m src.pipeline run --stage all` (nhắc đóng dashboard trước khi chạy `integrate`). Chỉ tệp hỏng mới là `error`.
- Lỗi nào cũng dựng `StateBlock(state="error", message=<câu tiếng Việt>)`; không hiển thị traceback.
- `partial` dựng từ trường `partial` của hợp đồng tương ứng; không suy đoán.

## 5. Điểm tích hợp với các đơn vị khác

| Hợp đồng | Đơn vị cấp | Dùng ở màn hình |
|---|---|---|
| C1/C6 (lược đồ) | U2 | `schema` |
| C3 (nguồn đã chọn) | U5 | `queries`, `sources` — **U6 là consumer thứ hai của C3** (bảng hợp đồng ghi U3; C3 đã được cộng thêm `catalogue` với ghi chú "để U6 vẽ bảng nguồn", nên bảng hợp đồng cần cập nhật consumer cùng lúc) |
| C4 (kết quả truy vấn) | U3 | `queries` |
| C5 (kết quả ghép) | U4 | `linkage` |
| C7 (bảng nguồn) | U5 | `sources` |
| C9 (khung tab) | U1 | `IntegrationTab` |

## 6. Tiếp cận (NFR4)

- Mọi nút là `<button>` thật (không `div` giả lập), có `aria-label` khi nhãn rỗng.
- Tiêu điểm thấy rõ bằng `:focus-visible` với viền tương phản ≥ 3:1.
- Trạng thái không chỉ dựa vào màu: mỗi `StateBlock` có câu chữ.
- Thứ tự tab bàn phím đi theo thứ tự thị giác; không bẫy tiêu điểm.
