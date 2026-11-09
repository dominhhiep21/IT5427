# Logical Components — u1-thin-slice

Nguồn: `nfr-requirements/` (sáu tệp yêu cầu của đơn vị), `functional-design/functional-spec.md`, `contract-design/contract-summary.md` (C4, C8, C9), `inception/domain-design/components.md` (khối MediatedSchema, QueryRewriter, IntegrationUI).

Đơn vị: `u1-thin-slice`. Tài liệu này là cầu nối giữa các quyết định NFR ở bốn tệp trước và bước Infrastructure Design: nó nói **khối nào tồn tại**, **khối nào hỏng thì ai chịu**, và **khối nào dùng chung**.

## 1. Kiến trúc logic của lát cắt

```
config/mediated-schema.yaml  ──►  L1 nạp don_hang  ──►  L2 truy vấn  ──►  L3 vùng số liệu
        (C8, do U1 sở hữu)          (đọc CSV)            (DuckDB RAM)      (trong tab, Dash)
                                          │                   │             ▲
                                          └─────► logs/ ◄─────┘             │
                                              (L5, dùng chung)              │
                              config/integration-tab.yaml ──────────────────┘
                                        (C9, id ổn định)
```

<!-- Text fallback: tệp lược đồ nuôi bước nạp; bước nạp nuôi bước truy vấn; bước truy vấn nuôi vùng số liệu; tệp cấu hình tab cấp id cho thẻ và vùng; cả bước nạp và bước truy vấn ghi vào nhật ký dùng chung. -->

## 2. Danh mục khối

| Mã | Khối | Trách nhiệm | Không làm gì | Sở hữu |
|---|---|---|---|---|
| L1 | Bước nạp `don_hang` | Đọc 5 cột nguồn theo ánh xạ trong lược đồ; kiểm mã đơn duy nhất, ngày, trạng thái; trả tập bản ghi và số bị loại kèm lý do | Không ghi đĩa, không biết gì về giao diện, không tự sửa ánh xạ | `src/integration/` phần nạp; dữ liệu `LoadResult` |
| L2 | Bước chạy truy vấn | Kiểm điều kiện trạng thái tường minh; sinh kế hoạch viết lại; chạy SQL trên DuckDB in-memory; trả `QueryRunResult` **kèm** `total_orders`, `months` (12 tháng gần nhất) và `partial` (tháng/trạng thái thiếu + lý do) | Không đọc CSV trực tiếp (nhận DataFrame từ L1), không đụng `warehouse/` | `src/integration/` phần truy vấn; `QueryRunResult` |
| L3 | Vùng số liệu trong tab "Tích hợp" (id `don-theo-thang`) | Định dạng và bố cục những gì L2 đã trả: sáu trạng thái (chưa chạy, đang tải, rỗng, đầy đủ, một phần, lỗi), tổng, bảng theo tháng và trạng thái, `elapsed_ms`, nhãn "kết quả lần trước" | Không đọc dữ liệu, không gọi DuckDB, **không tính lại** tổng hay tự suy phần thiếu — cả hai đã có trong `QueryRunResult` | `src/integration/` phần giao diện; vùng nằm trong thân tab U6 |
| L4 | Tệp lược đồ đầu tiên | Khai báo thực thể `don_hang` theo đúng hình dạng §2.1: ánh xạ từng trường tới bảng/cột nguồn, kiểu dữ liệu, cờ `loaded`, `schema_kind: GAV` | Không chứa logic; không chứa bí mật | `config/mediated-schema.yaml` — hợp đồng C8 bàn giao cho U2 |
| L5 | Nhật ký | Ghi sự kiện JSONL của L1 và L2 | Không phải nơi lưu kết quả; không chứa giá trị bản ghi | Dùng lại `src/common/logging.py` (dùng chung) |
| L6 | Cấu hình | `host`, `port`, đường dẫn dữ liệu, đường dẫn lược đồ | Không chứa bí mật | `config.yaml` (dùng chung) |
| L7 | Tệp cấu hình tab | `tab_id`, nhãn, bốn `card_ids` của tổng quan, `result_region_ids` (vùng kết quả `don-theo-thang`), `callback_ids` — id ổn định cho U6 | Không chứa bố cục hay chuỗi hiển thị dài; không chứa bí mật | `config/integration-tab.yaml` — phần "tệp cấu hình" của hợp đồng C9 |

Ba khối L1–L3 nằm trong **một** gói `src/integration/`, không phải ba dịch vụ. Lý do: chúng luôn thay đổi cùng nhau trong lát cắt, và tách tiến trình cho một người dùng là thêm chỗ hỏng (nguyên tắc "least coupling" không có nghĩa là chia nhỏ vô ích).

### 2.1 Hình dạng tệp `config/mediated-schema.yaml` (hợp đồng C8)

Tệp này là thứ U2 sẽ đọc, nên hình dạng của nó phải chốt ở đây chứ không để người viết mã tự phát minh. C8 nay khai đúng hình dạng này (`entities` và `fields` là danh sách bản ghi), nên tệp dưới đây là **hiện thực của C8**, không phải phần mở rộng tự phát; các đơn vị sau chỉ thêm thực thể/trường theo `change_policy` của C8.

```yaml
schema_kind: GAV
entities:
  - name: don_hang
    description: Một dòng cho mỗi đơn hàng
    source_tables:
      - olist_orders_dataset
      - olist_customers_dataset
    fields:
      - field_name: ma_don
        source_table: olist_orders_dataset
        source_column: order_id
        data_type: string
        loaded: true
      - field_name: ngay_dat
        source_table: olist_orders_dataset
        source_column: order_purchase_timestamp
        data_type: timestamp
        loaded: true
      - field_name: trang_thai
        source_table: olist_orders_dataset
        source_column: order_status
        data_type: string
        loaded: true
      - field_name: ma_khach
        source_table: olist_orders_dataset
        source_column: customer_id
        data_type: string
        loaded: true
      - field_name: bang_giao
        source_table: olist_customers_dataset
        source_column: customer_state
        data_type: string
        loaded: false      # bản bàn giao của lát cắt; tệp hiện tại đã là true sau khi đơn vị sau bật nạp
```

Ba quy tắc đi kèm, để tệp không mơ hồ:

1. `loaded: true` là trường **duy nhất** được đưa vào `usecols` và vào `DonHang` (`performance-design.md` ADR-U1-P2); `loaded: false` chỉ bị kiểm tiêu đề.
2. `data_type` thuộc tập đóng `string | integer | decimal | timestamp` — cùng tập C1 dùng, để U2 không phải dịch.
3. Bảng nguồn và cột nguồn phải qua `checked_identifier` và có thật trong CSV (`security-design.md` ADR-U1-S2); tệp sai thì từ chối phục vụ, không tự sửa.

Phần bổ sung này được ghi trong `memory.md` của bước này và phải được nêu khi bàn giao C8 cho U2 — nếu U2 muốn hình dạng khác, sửa tệp lược đồ là đủ, không phải sửa mã.

## 3. Phạm vi hỏng (failure domains) và bán kính ảnh hưởng

| Vùng hỏng | Chứa gì | Hỏng thì ai chịu | Cơ chế cô lập |
|---|---|---|---|
| **D1 — Tiến trình dashboard** | L1, L2, L3 và ba tab cũ | Nếu tiến trình chết: cả dashboard. Nếu một khối ném lỗi: chỉ vùng số liệu của tab mới | Lỗi trong L1/L2 được bắt trong callback của vùng; callback này **riêng**, không gộp với callback 9 output (`reliability-design.md` ADR-U1-R3) |
| **D2 — Dữ liệu nguồn `dataset/`** | 9 tệp CSV, chỉ đọc | Chỉ L1; ba tab cũ không dùng đường này | Không có đường ghi; lỗi đọc → trạng thái lỗi của thẻ |
| **D3 — `logs/`** | Nhật ký dùng chung | Chỉ mất khả năng chẩn đoán, **không** mất số liệu | Ghi nhật ký lỗi được nuốt và in ra console; không bao giờ làm hỏng đường dựng thẻ |
| **D4 — `warehouse/olist.duckdb`** | View cho ba tab cũ và bộ lọc | **Không ảnh hưởng tab mới** | L2 dùng DuckDB in-memory, không mở tệp này (`tech-stack-decisions.md` TS-U1-2) |
| **D5 — Tiến trình DuckDB in-memory của L2** | Kết nối sống trong một lần chạy | Chỉ lần chạy đó | Mở và đóng trong `finally` (`scalability-design.md` ADR-U1-SC2) |

Hệ quả đáng chú ý: tab mới là phần **duy nhất** của dashboard chạy được khi `warehouse/` chưa được dựng, vì nó chỉ cần `dataset/` và bộ nhớ. Đây là lý do lát cắt chọn truy vấn in-memory thay vì đọc view.

## 4. Tài nguyên dùng chung và tranh chấp

| Tài nguyên | Ai dùng | Tranh chấp có thể xảy ra | Cách xử lý |
|---|---|---|---|
| `config.yaml` | Dashboard, pipeline | Không (chỉ đọc) | Đọc một lần thành `AppConfig` bất biến |
| `logs/` | Pipeline, dashboard | Hai tiến trình ghi nối cùng tệp | Ghi một dòng một lời gọi; rủi ro đã ghi ở `observability-design.md` §5 |
| `dataset/` | Pipeline, L1 | Không (chỉ đọc) | Chỉ `open("r")`/`read_csv` |
| `warehouse/olist.duckdb` | Ba tab cũ, `integrate` | Có khoá khi `integrate` đang chạy | Tab mới **không** tham gia; quy tắc "đóng dashboard trước khi integrate" vẫn giữ cho ba tab cũ |
| Tệp lược đồ `config/mediated-schema.yaml` | L1 (đọc), U2 về sau (đọc) | Không | U1 sở hữu; chỉ thêm trường (C8 `change_policy`) |

### 4.1 Mã hoá tệp và lệnh chạy

Mọi khối đọc/ghi tệp bằng UTF-8 tường minh (`encoding="utf-8"`, `read_csv(..., encoding="utf-8-sig")` như `src/common/io.py` đang làm), và mọi lệnh Python trong tài liệu, trong test và trong lệnh xác nhận chạy dưới `python -X utf8` — đường dẫn workspace có ký tự tiếng Việt và dữ liệu có ký tự Bồ Đào Nha, thiếu cờ này sẽ `UnicodeEncodeError` (NFR6.2, luật dự án đã chốt).

## 5. Ranh giới với các đơn vị sau

Lát cắt cố ý chỉ dựng **phần xương** của ba khối trong `domain-design/components.md`, và bàn giao đúng hai hợp đồng:

| Hợp đồng | Đơn vị này bàn giao gì | Đơn vị sau mở rộng gì |
|---|---|---|
| C8 → U2 | `config/mediated-schema.yaml` có **một** thực thể `don_hang`, năm trường ánh xạ đầy đủ tới bảng/cột nguồn, `schema_kind: GAV` (§2.1) | Thêm `mat_hang`, `san_pham` và ánh xạ đầy đủ; không đổi tên `don_hang` |
| C9 → U6 | `config/integration-tab.yaml` với `tab_id`, nhãn, **bốn** `card_ids` ổn định của màn hình tổng quan, `result_region_ids` (`don-theo-thang`), và `callback_ids`; cộng hàm dựng khung tab đọc các id đó | Dựng ba thẻ tổng quan còn lại và bốn màn hình chi tiết; **phải dựng mọi vùng trong `result_region_ids`** (C9); thêm callback; không đổi `tab_id` và không đổi tên id đã có |

Payload C9 bàn giao, cụ thể (id đặt theo tên nhóm trong `inception/refined-mockups/mockups.md`, màn hình A):

```yaml
tab_id: tich-hop
tab_label: Tích hợp
card_ids:                       # bốn thẻ tổng quan — C9 khai đủ ngay từ lát cắt
  - luoc-do-trung-gian          # màn hình B
  - viet-lai-truy-van           # màn hình C
  - ghep-ban-ghi                # màn hình D
  - chon-nguon                  # màn hình E
result_region_ids:               # vùng kết quả — C9 khai khoá này
  - don-theo-thang               # vùng số liệu của lát cắt (nằm trong thân tab, không phải thẻ)
callback_ids:
  - tich-hop-cap-nhat
```

Vì sao khai đủ bốn `card_ids` dù lát cắt chỉ dựng một vùng: C9 tồn tại để U6 không phải tự đặt tên, và một danh sách id trong tệp cấu hình không tốn gì. Cái **chưa** dựng là ba thẻ tổng quan và các màn hình chi tiết — chúng thuộc U6. Vùng `don-theo-thang` là khoá `result_region_ids` của C9, **không** đếm vào `card_ids`; nút "Chạy truy vấn" của vùng cần một callback riêng, nên hình dạng đích của dashboard là **4 tab, 8 callback, 4 thẻ + 1 vùng**.

| Khối trong domain-design | Đơn vị này có dựng? | Ghi chú |
|---|---|---|
| MediatedSchema | **Một phần** — chỉ tệp khai báo và bước kiểm ánh xạ dùng cho `don_hang` | Phần đọc lược đồ tổng quát thuộc U2 |
| QueryRewriter | **Một phần** — đúng một truy vấn mẫu, kế hoạch viết lại một bước, đối chiếu KPI chưa có | Đối chiếu KPI (`kpi_comparison`) thuộc U3 |
| IntegrationUI | **Một phần** — khung tab và một vùng kết quả | Ba thẻ và bốn màn hình chi tiết thuộc U6 |
| RecordLinkage, SourceSelector, SemanticLayer | **Không** — ngoài phạm vi lát cắt | Thuộc U4, U5, U6 |

Mọi mở rộng ngoài bảng này là thay đổi phạm vi, phải chốt lại (`team.md` — "Phạm vi do một người chốt").

## 6. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Ba khối L1–L3 đủ nhỏ để nằm chung một gói mà vẫn tách được bằng test riêng từng tệp | Giả định — `tech-stack-decisions.md` NFR2.2 buộc mỗi tệp có test riêng, nên ranh giới vẫn kiểm được |
| A2 | Không có nhu cầu chạy L2 khi chưa chạy L1 trong cùng phiên | Đúng theo Workflow 3 (vùng đọc kết quả đã có) |
| Q1 | C8 để mở "đặt trong `config/` hay cạnh `config.yaml` ở gốc" | Đã chốt cho đơn vị này: `config/mediated-schema.yaml`, đúng như C8 ghi. Nếu U2 muốn khác thì đổi đường dẫn trong `config.yaml`, không đổi mã — nhưng phải nói với U1 vì C8 do U1 sở hữu |
