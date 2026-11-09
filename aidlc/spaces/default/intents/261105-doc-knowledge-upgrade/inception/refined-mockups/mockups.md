# Mockups (độ trung thực trung bình) — Tab "Tích hợp"

Nguồn: `ideation/rough-mockups/wireframes.md`, `ideation/rough-mockups/user-flow.md`, `inception/user-stories/stories.md`, `inception/requirements-analysis/requirements.md`, `inception/practices-discovery/team-practices.md`.

## Quyết định thiết kế đã chốt

| Chủ đề | Quyết định |
|---|---|
| Điểm vào thẻ | Cả thẻ là một liên kết; bỏ nút bên trong; Enter mở chi tiết |
| Thuật ngữ lý thuyết | Một dòng ghi chú dưới bảng dữ liệu của màn hình chi tiết |
| Mật độ | Cân bằng: màn hình A dùng đệm thẻ 24px, khoảng cách lưới 24px, tối đa 4 thẻ một hàng và không cần cuộn ở 1080px chiều cao; màn hình B–E dùng chiều cao hàng bảng 40px, 50 dòng mỗi trang, khoảng cách khối 16px |
| Bảng dài | Phân trang, chọn được số dòng mỗi trang |
| Màu | Bảng màu trung tính mới cho tab, ba màu trạng thái riêng |
| Thư viện | Plotly Dash + Dash Mantine Components (`dmc`) |
| Kích thước | Desktop/laptop, tối thiểu 1024px |
| Tiếp cận | WCAG 2.1 AA |

## Khung và thang thiết kế

- Khoảng cách: 4 / 8 / 16 / 24 / 32 / 48 px. Khoảng giữa nhóm > khoảng trong nhóm.
- Chữ: 12 (nhãn), 14 (phụ), 16 (thân), 20 (tiêu đề khối), 24 (tiêu đề trang).
- Nền `#FFFFFF`, nền phụ `#F8FAFC`, viền `#E2E8F0`, chữ chính `#0F172A`, chữ phụ `#475569`.
- Trạng thái: `#0F766E` (đạt), `#B45309` (một phần), `#B91C1C` (lỗi), luôn kèm biểu tượng và chữ.
- Bề rộng nội dung tối đa 1200px, canh trái; khối số liệu canh trái, không canh giữa.

## Màn hình A — Tổng quan bốn nhóm

```
+------------------------------------------------------------------+
| Tích hợp dữ liệu                              (h2, 24px)        |
| Bốn nhóm năng lực, mỗi nhóm một trạng thái.   (14px, xám)      |
|                                                                  |
| +------------------------+  +------------------------+          |
| | Lược đồ trung gian  [Đạt]  |  | Viết lại truy vấn   [Đạt]  |  |
| | 3 thực thể             |  | 3 truy vấn mẫu         |          |
| | 24 trường ánh xạ       |  | 0 truy vấn lỗi         |          |
| +------------------------+  +------------------------+          |
| +------------------------+  +------------------------+          |
| | Ghép bản ghi  [Một phần]   |  | Chọn nguồn          [Đạt]  |  |
| | 1 240 cặp vượt ngưỡng  |  | 4 nguồn ứng viên       |          |
| | ngưỡng 0,85            |  | 2 nguồn được chọn      |          || +------------------------+  +------------------------+          |
|                                                                  |
| Trạng thái tính từ lần chạy gần nhất.         (12px, xám)      |
+------------------------------------------------------------------+
```

- Lưới 2×2 ở 1024–1279px, 4 cột ở ≥ 1280px.
- Mỗi thẻ là một `dmc.Card` bọc `dmc.UnstyledButton` toàn chiều rộng, có `aria-label` = tên nhóm + trạng thái.
- Không có nút phụ bên trong thẻ.

## Màn hình B — Lược đồ trung gian

```
+------------------------------------------------------------------+
| ← Tích hợp / Lược đồ trung gian                                  |
| Lược đồ trung gian                                    (h2)      |
|                                                                  |
| +----------------+  +-------------------------------------------+ |
| | Thực thể       |  | GAV · áp cho thực thể "don_hang"           | |
| | • don_hang  ▸  |  | Trường trung gian | Nguồn        | Kiểu    | |
| | • mat_hang     |  | ma_don            | orders.order_id | chuỗi| |
| | • san_pham     |  | ngay_dat          | orders.order_purchase_timestamp | thời gian | |
| +----------------+  +-------------------------------------------+ |
+------------------------------------------------------------------+
```

- Danh sách thực thể dùng `dmc.NavLink`; bảng dùng `dmc.Table` + `dmc.Pagination` (50 dòng/trang mặc định).
- Dòng ghi chú `GAV` nằm **ngay trên bảng**, nêu tên thực thể đang xem — đúng AC1.2.1; câu trả lời Q2 đặt ghi chú dưới bảng, ở đây thu hẹp thành "ngay trên bảng" vì tiêu chí chấp nhận yêu cầu thấy nhãn ở phần đầu bảng. Nếu đổi lại vị trí dưới bảng thì phải sửa AC1.2.1 trước.

## Màn hình C — Viết lại truy vấn

```
+------------------------------------------------------------------+
| Lựa chọn: [ Doanh thu theo danh mục ▾ ]              [Chạy]      |
|                                                                  |
| Truy vấn trung gian               Kế hoạch viết lại              |
| +----------------------------+   +----------------------------+  |
| | select danh_muc,           |   | 1 don_hang → orders        |  |
| |   sum(gia_tri)             |   | 2 mat_hang → order_items   |  |
| | from don_hang              |   | 3 san_pham → products      |  |
| | join mat_hang using(ma_don)|   | 4 join trên mã đơn, mã SP  |  |
| +----------------------------+   +----------------------------+  |
|                                                                  |
| 0,42 s · 71 dòng · [Xem SQL nguồn]                               |
|                                                                  |
| Kết quả                                                          |
| +---------------------------+--------------------+              |
| | danh_muc                  | doanh_thu (BRL)    |              |
| | beleza_saude              | 1 258 681,27       |              |
| | relogios_presentes        | 1 203 362,55       |              |
| +---------------------------+--------------------+              |
| 71 dòng · trang 1/2                                              |
|                                                                  |
| GAV + query unfolding · mỗi truy vấn trung gian được mở thành   |
| truy vấn trên bảng nguồn.                            (12px)     |
+------------------------------------------------------------------+
```

- Hai khối `dmc.Code` cạnh nhau, chữ đơn cách 13px, nền xám rất nhạt; **bảng kết quả** nằm dưới, phân trang 50 dòng/trang.
- Khi chưa chạy lần nào, vùng kết quả ở trạng thái rỗng với câu "Chọn truy vấn và bấm Chạy".
- Số liệu định dạng theo quy ước Việt Nam: dấu phẩy thập phân, dấu chấm phân cách nghìn.
- Trạng thái đang chạy: nút chuyển `loading`, khối mã hiện khung tải và nhãn "kết quả lần trước".

## Màn hình D — Ghép bản ghi

```
+------------------------------------------------------------------+
| Đối tượng: [ Khách hàng ▾ ]        Ngưỡng đang dùng: 0,85 (cố định) |
|                                                                  |
| +---------------------+  +--------------------------------------+ |
| | 1 240 cặp vượt ngưỡng |  | Bản ghi A | Bản ghi B | Điểm | QĐ  | |
| | 318 nhóm trùng        |  | khach_01  | khach_77  | 0,93 | Ghép| |
| | 84,2% cặp ghép đúng   |  | khach_12  | khach_31  | 0,86 | Ghép| |
| | (mẫu số 1 240)        |  | khach_45  | khach_46  | 0,85 | Xem | |
| +---------------------+  +--------------------------------------+ |
|                                                                  |
| Bỏ qua: 37 cặp thiếu trường so khớp (thiếu thành phố hoặc prefix).|
| Khi không có cặp nào bị bỏ qua, dòng này ghi "không có".         |
|                                                                  |
| Blocking theo tiền tố mã bưu chính · so khớp thành phố + prefix. |
+------------------------------------------------------------------+
```

- Dòng "Bỏ qua" phục vụ US3.3: luôn hiện, kể cả khi bằng không, để người xem không nhầm là đã xét hết.

- Ngưỡng chỉ hiển thị, không có điều khiển chỉnh (đúng quyết định Q4 ở bước yêu cầu).
- Bảng phân trang; cột Quyết định có biểu tượng + chữ.

## Màn hình E — Chọn nguồn

```
+------------------------------------------------------------------+
| Truy vấn: [ Doanh thu theo danh mục ▾ ]        [Đề xuất nguồn]   |
|                                                                  |
| Nguồn              | Có dữ liệu | Chi phí (1–5) | Độ trễ | Được chọn    |
| olist_orders       | Có         | 1       | 80 ms  | Có           |
| olist_order_items  | Có         | 1       | 120 ms | Có           |
| ibge_cache         | Có         | 3       | 15 ms  | Không — thiếu cột |
| ibge_api (mô phỏng)| Không      | 5       | 900 ms | Không — không truy cập được |
|                                                                  |
| Chi phí là thang tương đối 1–5, ước tính theo số bảng phải đọc    |
| để trả lời truy vấn. Độ trễ là ước tính mô phỏng.                 |
|                                                                  |
| ibge_api chỉ là ứng viên mô phỏng; không có lệnh gọi mạng.       |
+------------------------------------------------------------------+
```

## Trạng thái trên mọi màn hình

| Trạng thái | Điều kiện kích hoạt | Biểu hiện |
|---|---|---|
| Rỗng | Nhóm chưa có dữ liệu | Khối giữa khung: biểu tượng, một câu, hướng dẫn chạy lệnh trong terminal |
| Đang tải | Đang đọc dữ liệu hoặc đang chạy truy vấn | Skeleton đúng hình dạng bảng/thẻ, không phủ toàn trang |
| Đầy đủ | Có dữ liệu | Nội dung bình thường |
| Lỗi | Đọc dữ liệu thất bại | Banner: biểu tượng cảnh báo, câu nêu việc hỏng, nút thử lại; không có mã lỗi thô |
| Một phần | Có dữ liệu nhưng thiếu một phần | Nhãn "Một phần" + tên phần thiếu; ô thiếu hiện "không có", không hiện 0 |

## Liên kết tới yêu cầu

Mỗi màn hình phục vụ các câu chuyện: A → US5.1, US5.2; B → US1.1, US1.2, US1.3; C → US2.1, US2.2, US2.3; D → US3.1, US3.2, US3.3; E → US4.1, US4.2; dòng "Bỏ qua" và trạng thái chung phục vụ US5.3; các ràng buộc không hồi quy và lớp ngữ nghĩa (US6.1, US6.2) không có màn hình riêng — chúng được kiểm bằng bộ test và bảng KPI, không phải bằng giao diện.
