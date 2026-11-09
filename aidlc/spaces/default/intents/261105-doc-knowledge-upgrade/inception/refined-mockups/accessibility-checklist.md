# Accessibility Checklist — Tab "Tích hợp"

Mục tiêu: WCAG 2.1 AA. Mỗi mục ghi cách kiểm và nơi áp dụng.

## 1. Có thể nhận biết (Perceivable)

| Tiêu chí | Cách kiểm | Áp dụng |
|---|---|---|
| Tương phản chữ thường ≥ 4.5:1 | Đo bằng công cụ kiểm tương phản trên mọi cặp màu ở `design-system-mapping.md` | Toàn tab |
| Tương phản chữ lớn ≥ 3:1 | Như trên, cho tiêu đề 24px | Tiêu đề màn hình |
| Tương phản thành phần ≥ 3:1 | Viền thẻ khi focus, viền bảng, biểu tượng trạng thái | Thẻ, bảng, badge |
| Không dùng màu làm tín hiệu duy nhất | Mỗi badge trạng thái có chữ + biểu tượng | Badge trạng thái, cột "Được chọn", cột "Quyết định" |
| Nội dung không phải chữ có nhãn | Biểu tượng trang trí đặt `aria-hidden`; biểu tượng mang nghĩa có `aria-label` | Toàn tab |

## 2. Có thể thao tác (Operable)

| Tiêu chí | Cách kiểm | Áp dụng |
|---|---|---|
| Mọi chức năng dùng được bằng bàn phím | Rút chuột, đi hết 5 màn hình bằng Tab/Enter | Toàn tab |
| Thứ tự focus hợp lý | Đi Tab và ghi lại thứ tự; phải theo thứ tự đọc trên xuống | Mọi màn hình |
| Tiêu điểm thấy rõ | Quan sát viền focus ở mọi phần tử nhận focus, tương phản ≥ 3:1 | Toàn tab |
| Không có bẫy bàn phím | Tab qua mọi vùng, luôn thoát ra được | Bảng, phân trang |
| Bảng phân trang có nhãn | Kiểm `aria-label` của cụm nút phân trang | Màn hình B, D, E |
| Không giới hạn thời gian | Không có timeout tự động trên màn hình | Toàn tab |

## 3. Có thể hiểu (Understandable)

| Tiêu chí | Cách kiểm | Áp dụng |
|---|---|---|
| Ngôn ngữ trang được khai báo | Thuộc tính `lang="vi"` trên tài liệu | Toàn tab |
| Nhãn hiển thị cho mọi điều khiển | Ô chọn truy vấn, ô chọn đối tượng, chọn số dòng đều có nhãn chữ | Màn hình C, D, E |
| Thông báo lỗi nêu việc gì và cách sửa | Đọc thông báo lỗi của từng màn hình | Toàn tab |
| Điều hướng nhất quán | Breadcrumb và vị trí tiêu đề giống nhau ở mọi màn hình chi tiết | Màn hình B–E |
| Không tự đổi ngữ cảnh khi focus | Không có hành động tự chạy khi focus | Toàn tab |

## 4. Chắc chắn (Robust)

| Tiêu chí | Cách kiểm | Áp dụng |
|---|---|---|
| Cấu trúc tiêu đề đúng thứ bậc | h1 (dashboard) → h2 (màn hình) → h3 (khối/bảng) | Toàn tab |
| Vùng đất (landmarks) | `banner`, `navigation`, `main`, `contentinfo` có mặt | Khung |
| Vùng thông báo động | `aria-live="polite"` cho kết quả chạy truy vấn và đề xuất nguồn | Màn hình C, E |
| Bảng có chú thích | Mỗi `dmc.Table` có `<caption>` mô tả | Màn hình B, D, E |
| `prefers-reduced-motion` | Không có animation bắt buộc; hiệu ứng tải tôn trọng cài đặt giảm chuyển động | Toàn tab |

## 5. Kiểm thử thủ công trước khi duyệt

- [ ] Rút chuột, hoàn thành: mở tab → mở một thẻ → quay lại → mở cả bốn nhóm.
- [ ] Kiểm tương phản mọi cặp màu bằng công cụ, ghi lại kết quả. Viền tiêu điểm và viền bảng dùng token `focus` (`#0F766E`) và `border-strong` (`#64748B`), không dùng `border` (`#E2E8F0`) cho bất kỳ chỗ nào cần 3:1.
- [ ] Chạy trình đọc màn hình (NVDA trên Windows) qua màn hình tổng quan và màn hình viết lại truy vấn.
- [ ] Phóng to 200%, xác nhận không mất nội dung và không xuất hiện cuộn ngang.
- [ ] Kiểm với mô phỏng mù màu: trạng thái vẫn phân biệt được nhờ chữ và biểu tượng.

## 6. Ngoài phạm vi kiểm trong đợt này

- Điện thoại và máy tính bảng: tab chỉ hỗ trợ desktop/laptop, dưới 1024px hiện thông báo.
- Ba tab cũ: giữ nguyên hiện trạng, không thuộc phạm vi cải thiện tiếp cận của đợt này.
