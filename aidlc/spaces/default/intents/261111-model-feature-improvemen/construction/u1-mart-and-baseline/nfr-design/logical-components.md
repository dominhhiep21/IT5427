# Logical Components — u1-mart-and-baseline

Đơn vị: `u1-mart-and-baseline` (kind `library`). Nguồn: `security-design.md`, `../nfr-requirements/tech-stack-decisions.md`, `../functional-design/functional-spec.md`, `../../../inception/domain-design/components.md`, mã thật `src/integrate/pipeline.py`.

Tài liệu này là **inventory thành phần logic** — chỗ nào có mặt trong luồng chạy, ranh giới ở đâu, khi một chỗ hỏng thì cái gì hỏng theo. Ở dự án này không có hạ tầng triển khai nào, nên phần "hạ tầng" là **rỗng có chủ đích**.

## Dòng chạy thật của `integrate_all` (`src/integrate/pipeline.py:68-100`)

```
 load_cleaned                        (:68)
   → IbgeClient.fetch_states         (:70-71)  ← chỗ DUY NHẤT ghi vào dataset/ (cache)
   → RegionMapper.validate           (:72-76)  ← chặn: ExternalSourceError
   → DimensionBuilder.build_all      (:78)
   → FactBuilder.build_all           (:79)
   → Aggregator.build_all            (:80)
   → StarSchemaValidator.enforce     (:84)     ← chặn
   → KpiReconciler.enforce           (:88)     ← chặn
   → AtomicWriter → temp marts       (:90-94)
   → os.replace từng bảng            (:96-98)
   → DuckDbCatalog.create            (:100)    ← tạo lại 11 view SAU khi ghi
```

Đơn vị này chạm **hai** mắt xích: `FactBuilder` (thêm cột) và `measure_state_baseline` (thành phần mới, nằm ngoài dòng trên).

## Inventory

| # | Thành phần | Vai trò | Đơn vị này sửa? |
|---|---|---|---|
| L1 | `FactBuilder` | dựng `fact_orders`, `fact_order_items`; gắn ba cột mới | **Có** |
| L2 | `DimensionBuilder` | dựng `dim_seller`; nguồn của `seller_state` | Đọc |
| L3 | `RegionMapper` | gắn `region` từ `state`; chạy **trước** `L1` | Đọc |
| L4 | `IbgeClient` | gọi HTTPS API IBGE, ghi cache vào `dataset/external/ibge/` | Đọc — nhưng là chỗ duy nhất ghi vào `dataset/` |
| L5 | `Aggregator` | dựng `agg_sales_daily` và các bảng tổng hợp, nối `dim_customer` (`state`) | Đọc — và là nạn nhân nếu tên cột mới là `state` |
| L6 | `StarSchemaValidator` | 9 check số dòng, chặn trước khi ghi | Đọc |
| L7 | `KpiReconciler` | 5 KPI + 5 dung sai, chặn trước khi ghi | Đọc |
| L8 | `AtomicWriter` | ghi Parquet qua tệp tạm rồi thay | Đọc |
| L9 | `DuckDbCatalog` | tạo lại 11 view trên Parquet, **sau** khi ghi | Đọc |
| L10 | `AppConfig` | cấu hình bất biến, nguồn duy nhất của đường dẫn | Đọc |
| L11 | `measure_state_baseline` | hàm thuần đo baseline một đặc trưng | **Có** — thành phần mới |

**Hai thành phần được sửa hoặc tạo:** `L1` và `L11`. Chín thành phần còn lại là **ràng buộc hoặc bối cảnh**, không phải chỗ sửa — đó là lý do đơn vị này xếp cỡ M.

**Chỗ đặt `L11`:** `src/analytics/model.py`, theo hợp đồng C1. Tệp đó U2 cũng sửa; đơn vị này **chỉ thêm một hàm**, không đổi chữ ký nào đang có — nếu U2 cần đổi, đó là thay đổi của U2 và phải giữ hàm này chạy được.

## Ranh giới thật

1. **`L1` ↔ `L2`/`L5`**: `L1` đọc `dim_seller` nhưng không sở hữu nó; `L5` nối `dim_customer` có cột `state`. Đây là ranh giới **mỏng nhất** của đơn vị: đổi tên một cột ở `L2` hoặc đặt sai tên ở `L1` là `L5` gãy. `BR1.7` tồn tại để canh đúng chỗ này.
2. **`L1` → `L6`/`L7`**: một chiều. Hai cổng không sửa dữ liệu, chỉ đọc rồi ném — nên một cổng không thể làm hỏng dữ liệu.
3. **`L8`/`L9`**: ghi mart rồi mới tạo view. Đây là **trạng thái nửa vời duy nhất** mà luồng có thể để lại: mart mới cạnh view cũ nếu `L9` hỏng.
4. **`L11` ↔ mọi thứ**: hàm thuần, không chạm `L1`–`L10`, không đĩa, không kết nối. Ranh giới sạch nhất của đơn vị (ADR-008).

**Về trạng thái nửa vời:** mart được ghi vào thư mục tạm rồi `os.replace` **từng bảng một** (`:93-98`), không phải thay cả thư mục. Nên nếu lần ghi hỏng giữa vòng lặp, trên đĩa có thể có **một số bảng mới cạnh một số bảng cũ**. Còn view thì không "cũ" theo nghĩa nội dung: chúng là `read_parquet` trên đúng đường dẫn tuyệt đối, nên đọc lại là thấy nội dung mới. Rủi ro thật là lệch giữa các bảng, không phải view cũ.

## Bán kính ảnh hưởng

| Hỏng ở | Ảnh hưởng | Cổng nào bắt? |
|---|---|---|
| `L1` sai số dòng | 5 KPI lệch, mọi báo cáo sai | **`L6`, `L7`** — chặn trước khi ghi |
| `L1` sai dtype hoặc miền giá trị | mart sai kiểu; tầng trên đọc sai | **Không cổng nào** — test đơn vị + data-quality bắt |
| `L2` đổi tên `state` | `L1` gãy, hoặc `L5` sinh `state_x`/`state_y` | **Không** — `L6` chỉ đếm dòng, không thấy cột |
| `L9` hỏng | mart mới cạnh 11 view cũ | **Không** — trạng thái nửa vời |
| `L4` (IBGE) lỗi mạng | `region` thiếu | Fallback: dùng cache; đây là lý do `SD2` có ngoại lệ |
| `L11` hỏng | `baseline_auc` sai ⇒ phép so với mô hình vô nghĩa | **Không** — test đơn vị của U1 |

**Đọc bảng này theo chiều nguy hiểm:** bốn trong sáu dòng **không** tự dừng pipeline. Đó là lý do mỗi dòng có test riêng, và là lý do đơn vị này không thể chỉ dựa vào `StarSchemaValidator`.

## Tài nguyên chia sẻ

| Tài nguyên | Ai dùng chung | Rủi ro |
|---|---|---|
| `warehouse/olist.duckdb` | mọi tầng đọc; `integrate` ghi | Khoá tệp khi dashboard đang mở — đóng dashboard trước khi chạy `integrate` (`docs/runbook.md`) |
| `data/marts/*.parquet` | `L8` ghi, `L9` tạo view trên đó | View chứa **đường dẫn tuyệt đối** (`as_posix()`); chuyển thư mục repo phải chạy lại `integrate` |
| `dataset/external/ibge/` | `L4` ghi, `integrate` đọc | Cache dùng chung giữa các lần chạy; **không phải** dữ liệu gốc, nên nằm ngoài phép kiểm hash |

## Điều tài liệu này không có: hạ tầng

Không có service, không có container, không có bộ cân bằng tải, không có vùng sẵn sàng, không có scheduler. Dự án chạy từ mã nguồn trên máy một người; "triển khai lại từ đầu" nghĩa là xoá bốn thư mục sinh ra rồi chạy lại pipeline. Vì vậy phần hạ tầng của inventory này **rỗng có chủ đích**, không phải thiếu sót — và Infrastructure Design ở stage sau ghi đúng như thế.

**Một ngoại lệ cần nói:** có **một** phụ thuộc mạng ra ngoài là API IBGE, gọi từ `L4` trong cùng dòng chạy. Nó không phải "hạ tầng của dự án" (không có gì để triển khai), nhưng nó là lời gọi mạng thật, có cache và fallback — và đó là lý do `SD2` phải có ngoại lệ cho `dataset/external/ibge/`.
