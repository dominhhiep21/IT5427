# Logical Components — u3-display

Nguồn: `../functional-design/entities.md`, `../functional-design/rules.md`, `../nfr-requirements/*`, `../../../inception/domain-design/components.md`.

## Đối chiếu với danh mục thành phần của Domain Design

`components.md` khai `result-tab` cho đơn vị này và ghi rõ nó **không tính toán gì**. Hai điểm trong đó **lệch với thiết kế này**, và đây là ghi nhận trung thực thay vì im lặng:

- `components.md` xếp "bộ chọn ngưỡng" vào phần `result-tab` sở hữu. Thiết kế này **bỏ nó** (Q1 = A) vì hợp đồng C3 chỉ mang một ngưỡng đã chọn sẵn, không có dữ liệu để chọn lại. `components.md` và `unit-of-work.md` cần được sửa cho khớp.
- `components.md` trỏ tới `src/dashboard/analysis_tab.py`. Tệp đó **chưa tồn tại**; nó là tên dự kiến cho tab mới, không phải mã đang có.

Các thành phần dưới đây nằm trong `result-tab`; chúng là cách chia bên trong, không phải thành phần mới ở cấp kiến trúc.

| Thành phần nội bộ | Trách nhiệm | Quy tắc | Miền hỏng riêng |
|---|---|---|---|
| `tab-callback` | Nhận thao tác mở tab, gọi `read_report` đúng một lần, chọn nhánh dựng | BR3.1, NFR5.6 | Không — lỗi ở đây không dựng được gì |
| `loading-shell` | Bọc nội dung trong `dcc.Loading` với `custom_spinner` là khối trạng thái `chua-chay` | BR3.1 | Không |
| `state-mapper` | Ánh xạ `ReportView.status` thành token và thông điệp | BR3.1, BR3.5 | Không |
| `summary-strip` | Dựng các thẻ có nguồn dữ liệu, thẻ AUC kèm dấu đạt/không đạt | BR3.3 | Không |
| `stats-section` | Dựng năm mục thống kê, mục null hiện câu chữ kèm lý do | BR3.2, BR3.10 | Không |
| `skipped-banner` | Liệt kê kiểm định bị bỏ | BR3.6 | Không |
| `model-section` | Hiện AUC, ngưỡng, precision, recall như số đọc | BR3.7 | Không |
| `formatter` | Bọc `src/dashboard/formatting.py`, nhân 100 cho `late_rate.rate` | TSU-4 | Không |

## Ba quyết định tiếp cận (NFR5.2, NFR5.3, NFR5.4)

| Mã | Quyết định | Cách kiểm |
|---|---|---|
| NFR5.2 | Mỗi vùng nội dung mang một tiêu đề ngữ nghĩa (`dmc.Title` với `order`) **hoặc** `aria-label`; không vùng nào dựa vào hình thức để người đọc màn hình đoán ý | Test đơn vị duyệt cây và khẳng định mỗi `html.Div` cấp vùng có một trong hai |
| NFR5.3 | Tab này **không có phần tử tương tác nào** (SDU-1), nên không đặt `tabIndex` dương. Thứ tự đọc do thứ tự DOM quyết định, và thứ tự DOM là tóm tắt → thống kê → mô hình | Test khẳng định không có `tabIndex` dương, và thứ tự `children` khớp BR3.2 |
| NFR5.4 | Bố cục **một cột** ở mọi chiều rộng ≥ 1280px: dải tóm tắt là hàng thẻ có `wrap`, mỗi mục thống kê chiếm trọn chiều ngang. Không đặt chiều rộng cố định theo px cho khối chữ | Xem bằng mắt ở 1280px ở bước 4 chuỗi xác nhận, ghi kết quả vào `code-summary.md` |

Việc NFR5.3 không có `tabIndex` dương là kết luận, không phải thiếu sót: một tab chỉ đọc thì thứ tự DOM chính là thứ tự đọc, và thêm điểm dừng focus giả sẽ làm bàn phím khó dùng hơn.

## Tài nguyên dùng chung

| Tài nguyên | Ai dùng | Cách ly |
|---|---|---|
| `data/reports/analysis.json` | chỉ `tab-callback`, qua `read_report` | Không thành phần nào khác mở tệp |
| `assets/style.css` | `summary-strip`, `stats-section`, `model-section` | Chỉ đọc token; tab mới dùng `--text-2` cho chữ nhỏ (NFR5.1) |
| `src/dashboard/formatting.py` | `formatter` | Một chỗ duy nhất biết định dạng Brazil |

## Bán kính ảnh hưởng

| Hỏng ở | Ảnh hưởng | Vì sao dừng ở đó |
|---|---|---|
| `read_report` ném ngoại lệ | Không xảy ra — hàm đọc không ném (BR1.9) | Hợp đồng C2 |
| `state-mapper` | Tab hiện thông điệp chung, các mục không dựng | Không có dữ liệu để vẽ |
| Một mục thống kê null | Chỉ mục đó hiện câu chữ | BR3.10 |
| Bất kỳ thành phần nào của U3 | **Không** ảnh hưởng tầng ghi hay dữ liệu | U3 chỉ đọc, không ghi |

## Điều không có

Không có thành phần hạ tầng: không tiến trình nền, không hàng đợi, không bộ nhớ đệm, không gọi mạng. Tám thành phần trong một callback, và đó là toàn bộ.
