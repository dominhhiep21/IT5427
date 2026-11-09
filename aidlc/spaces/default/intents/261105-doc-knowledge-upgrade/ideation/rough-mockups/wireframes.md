# Wireframes — Tab "Tích hợp"

Bối cảnh: `intent-statement.md`, `scope-document.md`, `intent-backlog.md` (PB-01…PB-07). Độ trung thực: wireframe cấu trúc (không màu thật, không dữ liệu thật).

## Quyết định thiết kế

| Hạng mục | Quyết định | Nguồn |
|---|---|---|
| Thư viện | Plotly Dash + Dash Mantine Components (`dmc`), giữ nhãn tiếng Việt | Q3, Q7 |
| Tổ chức | Một tab "Tích hợp": màn hình tổng quan bốn nhóm, bấm vào mở chi tiết | Q1 |
| Luồng chính | Xem tổng quan trạng thái → đi sâu nhóm cần xem | Q2 |
| Kích thước | Desktop/laptop, bề rộng tối thiểu 1024px | Q4 |
| Tiếp cận | WCAG 2.1 AA đầy đủ | Q5 |
| Thuật ngữ | Hiện thuật ngữ lý thuyết, không kèm giải thích trên màn hình | Q6 |

Nguyên tắc thị giác áp dụng: dựng bằng thang xám trước, chỉ dùng màu cho trạng thái; thang khoảng cách 4/8/16/24/32/48; thang chữ 12/14/16/20/24/30; nhãn nhỏ và nhạt hơn giá trị.

## Thang thiết kế

- **Khoảng cách**: 4, 8, 16, 24, 32, 48 px. Khoảng giữa nhóm > khoảng trong nhóm.
- **Chữ**: 12 (nhãn), 14 (phụ), 16 (thân), 20 (tiêu đề khối), 24–30 (tiêu đề trang).
- **Màu**: nền `#FFFFFF`, nền phụ `#F8FAFC`, viền `#E2E8F0`, chữ chính `#0F172A`, chữ phụ `#475569`. Trạng thái: xanh `#0F766E` (đạt), vàng `#B45309` (một phần), đỏ `#B91C1C` (lỗi) — luôn kèm biểu tượng và nhãn chữ, không chỉ màu.
- **Tương phản**: chữ thân ≥ 4.5:1, chữ lớn ≥ 3:1, viền component ≥ 3:1.

## Khung ứng dụng

```
+--------------------------------------------------------------------------------+
|  Olist Data Integration                                           [Tổng quan]  |  <- h1 (24px)
|  Tổng quan  |  Danh mục  |  Giao vận  |  Tích hợp  (đang chọn)                  |  <- role=navigation
+--------------------------------------------------------------------------------+
|                                                                                |
|   <vùng nội dung>                                                              |  <- role=main
|                                                                                |
+--------------------------------------------------------------------------------+
|  Dữ liệu: data/marts · Cập nhật: 05/11/2026 14:30                               |  <- role=contentinfo
+--------------------------------------------------------------------------------+
```

- Điều hướng bằng tab của `dmc.Tabs`, tab đang chọn có gạch chân và `aria-selected`.
- Tab "Tích hợp" nằm cuối, giữ nguyên ba tab cũ.
- Điểm vào bàn phím: `Skip to content` là phần tử focus đầu tiên.

## Màn hình 1 — Tổng quan tích hợp

```
+--------------------------------------------------------------------------------+
|  Tích hợp dữ liệu                                                              |  <- h2 (20px)
|  Bốn nhóm năng lực, mỗi nhóm một trạng thái.                                  |  <- chữ phụ 14px
|                                                                                |
|  +------------------+  +------------------+  +------------------+  +---------+ |
|  | Lược đồ trung gian|  | Viết lại truy vấn|  | Ghép bản ghi     |  | Chọn    | |
|  | [Đạt]            |  | [Đạt]            |  | [Một phần]       |  | nguồn   | |
|  | 8 thực thể       |  | 5 truy vấn mẫu   |  | 1 240 cặp khớp   |  | [Đạt]   | |
|  | 9 nguồn ánh xạ   |  | 0 truy vấn lỗi   |  | ngưỡng 0.85      |  | 2 nguồn | |
|  | [Xem chi tiết →] |  | [Xem chi tiết →] |  | [Xem chi tiết →] |  | [Chi    | |
|  |                  |  |                  |  |                  |  | tiết →] | |
|  +------------------+  +------------------+  +------------------+  +---------+ |
|                                                                                |
|  Ghi chú: trạng thái tính từ lần chạy gần nhất.                               |  <- 12px, xám
+--------------------------------------------------------------------------------+
```

- Bốn thẻ `dmc.Card` trong `dmc.SimpleGrid` 4 cột, mỗi thẻ cao bằng nhau.
- Mỗi thẻ: tiêu đề nhóm (16px, đậm), `dmc.Badge` trạng thái, 2 dòng số liệu (nhãn 12px xám + giá trị 16px), một nút phụ "Xem chi tiết".
- Toàn bộ thẻ là một vùng bấm được; thẻ có `role="link"`, `tabindex="0"`, Enter/Space mở chi tiết.
- Trạng thái: rỗng (chưa chạy pipeline), đang tải (skeleton 4 thẻ), lỗi (banner đỏ có biểu tượng), một phần (badge "Một phần" + dòng lý do).

## Màn hình 2 — Lược đồ trung gian

```
+--------------------------------------------------------------------------------+
|  ← Tích hợp / Lược đồ trung gian                                               |  <- breadcrumb
|  Lược đồ trung gian                                             [Tải lại]      |
|                                                                                |
|  +---------------------------+  +--------------------------------------------+ |
|  | Thực thể (8)              |  | Ánh xạ của "don_hang"                      | |
|  | • don_hang      (chọn)    |  | +------------------+-------------+---------+ | |
|  | • mat_hang                |  | | Trường trung gian| Nguồn       | Kiểu    | | |
|  | • khach_hang              |  | +------------------+-------------+---------+ | |
|  | • nguoi_ban               |  | | ma_don           | orders.     | chuỗi   | | |
|  | • san_pham                |  | |                  | order_id    |         | | |
|  | • thanh_toan              |  | | ngay_dat         | orders.     | thời    | | |
|  | • danh_gia                |  | |                  | order_      | gian    | | |
|  | • dia_ly                  |  | |                  | purchase_ts |         | | |
|  |                           |  | +------------------+-------------+---------+ | |
|  +---------------------------+  +--------------------------------------------+ |
|                                                                                |
|  Nguồn tham gia: olist_orders · olist_order_items · ibge_cache                 |  <- 12px
+--------------------------------------------------------------------------------+
```

- Hai cột: danh sách thực thể (trái, chọn được) và bảng ánh xạ (phải).
- Bảng `dmc.Table` có tiêu đề cột nhỏ, chữ thường; hàng có sọc xen kẽ rất nhạt.
- Bấm một thực thể cập nhật bảng bên phải, không tải lại trang (`aria-live="polite"` báo số dòng mới).

## Màn hình 3 — Viết lại truy vấn

```
+--------------------------------------------------------------------------------+
|  ← Tích hợp / Viết lại truy vấn                                                |
|  Chọn truy vấn mẫu: [ Doanh thu theo danh mục  v ]        [Chạy]              |
|                                                                                |
|  Truy vấn trên lược đồ trung gian          Kế hoạch viết lại                   |
|  +----------------------------------+      +---------------------------------+ |
|  | select danh_muc, sum(gia_tri)    |      | 1. don_hang  -> olist_orders    | |
|  | from don_hang                    |      | 2. mat_hang  -> olist_order_    | |
|  | join mat_hang using (ma_don)     |      |    items                        | |
|  | group by danh_muc                |      | 3. san_pham  -> olist_products  | |
|  +----------------------------------+      | 4. join trên ma_don, ma_san_pham| |
|                                            | 5. gộp nhóm tại DuckDB          | |
|                                            +---------------------------------+ |
|                                                                                |
|  Thời gian chạy: 0.42 s · Số dòng: 71             [Xem SQL nguồn]             |
+--------------------------------------------------------------------------------+
```

- Hai khối code cạnh nhau, chữ đơn cách 13px, nền xám rất nhạt, có thể chọn và sao chép.
- "Chạy" là hành động chính duy nhất trên màn hình; trong lúc chạy nút chuyển sang trạng thái chờ có xoay.
- Lỗi truy vấn hiện ngay dưới ô chọn, nêu truy vấn nào và lỗi gì, kèm nút thử lại.

## Màn hình 4 — Ghép bản ghi

```
+--------------------------------------------------------------------------------+
|  ← Tích hợp / Ghép bản ghi                                                     |
|  Ngưỡng tương đồng: [ 0.85 ]   Khoá chặn: [ tiền tố mã bưu chính v ]          |
|                                                                                |
|  +-------------------------+  +----------------------------------------------+ |
|  | 1 240 cặp vượt ngưỡng   |  | Cặp tiêu biểu                                | |
|  | 318 nhóm trùng          |  | +----------+----------+-------+-----------+ | |
|  |                         |  | | Bản ghi A| Bản ghi B| Điểm  | Quyết định| | |
|  |                         |  | +----------+----------+-------+-----------+ | |
|  |                         |  | | khach_01 | khach_77 | 0.93  | Ghép      | | |
|  |                         |  | | khach_12 | khach_31 | 0.86  | Ghép      | | |
|  |                         |  | | khach_45 | khach_46 | 0.85  | Xem lại   | | |
|  |                         |  | +----------+----------+-------+-----------+ | |
|  +-------------------------+  +----------------------------------------------+ |
+--------------------------------------------------------------------------------+
```

- Thanh trượt ngưỡng cập nhật bảng ngay; số liệu tóm tắt bên trái là `dmc.Stat`.
- Điểm số hiển thị 2 chữ số thập phân; cột "Quyết định" dùng nhãn chữ + biểu tượng.
- Bảng cuộn trong khung riêng, giữ tiêu đề cột khi cuộn.

## Màn hình 5 — Chọn nguồn dữ liệu

```
+--------------------------------------------------------------------------------+
|  ← Tích hợp / Chọn nguồn                                                       |
|  Truy vấn: [ Doanh thu theo danh mục v ]                    [Đề xuất nguồn]    |
|                                                                                |
|  +------------------+----------+----------+------------+---------------------+ |
|  | Nguồn            | Có dữ liệu| Chi phí | Độ trễ ước | Được chọn            | |
|  +------------------+----------+----------+------------+---------------------+ |
|  | olist_orders     | Có       | 1        | 80 ms      | Có                  | |
|  | olist_order_items| Có       | 1        | 120 ms     | Có                  | |
|  | ibge_cache       | Có       | 3        | 15 ms      | Không (thiếu cột)   | |
|  | ibge_api         | Không    | 5        | 900 ms     | Không (không truy   | |
|  |                  |          |          |            | cập được)           | |
|  +------------------+----------+----------+------------+---------------------+ |
+--------------------------------------------------------------------------------+
```

- Bảng có sắp xếp theo cột; hàng bị loại có chữ xám và lý do bằng chữ.
- Nút "Đề xuất nguồn" là hành động chính; kết quả cập nhật bảng và đọc lên bằng `aria-live`.

## Trạng thái màn hình (áp dụng cho cả 5)

| Trạng thái | Biểu hiện |
|---|---|
| Rỗng | Khối giữa khung: biểu tượng + một câu giải thích + nút hành động chính (ví dụ "Chạy pipeline để có dữ liệu") |
| Đang tải | Skeleton đúng hình dạng nội dung (thẻ/bảng), không dùng vòng xoay toàn trang |
| Đầy đủ | Trạng thái bình thường với số liệu thật |
| Lỗi | Banner trong vùng nội dung: biểu tượng cảnh báo, câu nêu việc gì hỏng, nút thử lại; không hiện mã lỗi thô |
| Một phần | Nhãn "Một phần" + dòng nêu phần nào thiếu; số liệu thiếu hiện "không có" chứ không hiện 0 |

## Tiếp cận (WCAG 2.1 AA) theo màn hình

| Màn hình | Cấp tiêu đề | Vùng vai trò | Điểm vào bàn phím |
|---|---|---|---|
| Khung | h1 = tên dashboard | banner, navigation, main, contentinfo | Skip to content → tab điều hướng → nội dung |
| Tổng quan | h1 → h2 → h3 (tên thẻ) | main | Tab vào từng thẻ, Enter/Space mở chi tiết |
| Lược đồ trung gian | h1 → h2 → h3 (tên bảng) | main | Tab vào danh sách thực thể, phím mũi tên đổi mục, Tab sang bảng |
| Viết lại truy vấn | h1 → h2 → h3 (hai khối) | main | Tab tới ô chọn, nút Chạy, rồi vùng mã |
| Ghép bản ghi | h1 → h2 → h3 (bảng) | main | Tab tới thanh trượt (mũi tên tăng giảm), rồi bảng |
| Chọn nguồn | h1 → h2 → h3 (bảng) | main | Tab tới ô chọn, nút, rồi bảng sắp xếp được |

- Mọi trạng thái có thay đổi động đều nằm trong vùng `aria-live="polite"`.
- Tiêu điểm bàn phím hiện rõ (viền 2px, tương phản ≥ 3:1), không bao giờ tắt outline mà không thay thế.
- Không dùng màu làm tín hiệu duy nhất: mọi badge có chữ đi kèm.

## Thành phần dmc dùng lại

| Vùng | Thành phần |
|---|---|
| Khung | `dmc.AppShell`, `dmc.Tabs`, `dmc.Text`, `dmc.Group` |
| Tổng quan | `dmc.SimpleGrid`, `dmc.Card`, `dmc.Badge`, `dmc.Stat`, `dmc.Button` |
| Danh sách + bảng | `dmc.NavLink`, `dmc.Table`, `dmc.ScrollArea` |
| Truy vấn | `dmc.Select`, `dmc.Code`, `dmc.LoadingOverlay`, `dmc.Alert` |
| Ghép bản ghi | `dmc.Slider`, `dmc.NumberInput`, `dmc.Table` |
| Chọn nguồn | `dmc.Table` (sắp xếp), `dmc.Button`, `dmc.Alert` |
