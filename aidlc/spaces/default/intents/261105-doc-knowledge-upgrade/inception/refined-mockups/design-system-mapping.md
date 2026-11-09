# Design System Mapping — Tab "Tích hợp"

Ánh xạ từ thiết kế sang Dash Mantine Components (`dmc`), kèm token dùng chung cho cả tab.

## Token

### Màu

| Token | Giá trị | Dùng cho |
|---|---|---|
| `surface` | `#FFFFFF` | nền chính |
| `surface-subtle` | `#F8FAFC` | nền khối mã, nền thẻ khi hover |
| `border` | `#E2E8F0` | viền trang trí (không dùng để đạt 3:1) |
| `border-strong` | `#64748B` | viền bảng và đường phân cách khi cần tương phản ≥ 3:1 |
| `focus` | `#0F766E` | viền tiêu điểm bàn phím, tương phản ≥ 3:1 trên nền trắng |
| `text` | `#0F172A` | chữ chính |
| `text-muted` | `#475569` | nhãn, ghi chú |
| `status-ok` | `#0F766E` | trạng thái đạt |
| `status-partial` | `#B45309` | trạng thái một phần |
| `status-error` | `#B91C1C` | trạng thái lỗi |
| `status-empty` | `#64748B` | trạng thái rỗng |

Bảng màu này là bảng màu mới cho tab, đúng quyết định ở bước thiết kế; ba tab cũ giữ nguyên bảng màu hiện có và không bị đổi trong đợt này.

### Khoảng cách và chữ

| Token | Giá trị |
|---|---|
| spacing | 4, 8, 16, 24, 32, 48 px |
| font-size | 12, 14, 16, 20, 24 px |
| line-height | 1.5 cho thân, 1.25 cho tiêu đề |
| radius | 8px cho thẻ và khối mã, 4px cho badge |
| max-width | 1200px, canh trái |

## Ánh xạ thành phần

| Vùng thiết kế | Thành phần `dmc` | Ghi chú cấu hình |
|---|---|---|
| Tab "Tích hợp" | `dcc.Tab` (giữ shell hiện có) + nội dung bên trong bằng `dmc` | Ba tab cũ vẫn là `dcc.Tab` với nội dung cũ; tab thứ tư là `dcc.Tab` mới, phần thân dựng bằng `dmc`. Không thay shell `dcc.Tabs` để tránh đổi ba tab cũ. |
| Khung nội dung tab | `dmc.AppShell` (chỉ bên trong tab mới), `dmc.Container` | `Container` đặt `size="xl"`, canh trái |
| Thẻ nhóm | `dmc.Card`, `dmc.UnstyledButton`, `dmc.Group`, `dmc.Stack` | `UnstyledButton` bọc toàn thẻ, `aria-label` động |
| Nhãn trạng thái | `dmc.Badge` | `variant="light"`, `color` theo token trạng thái, kèm `dmc.ThemeIcon` |
| Số liệu trên thẻ | `dmc.Text` (nhãn 12px xám) + `dmc.Text` (giá trị 16px) | Không dùng `dmc.Stat` để giữ hai dòng gọn |
| Breadcrumb | `dmc.Anchor`, `dmc.Breadcrumbs` | `aria-label="Đường dẫn quay lại"` |
| Danh sách thực thể | `dmc.NavLink` | Mục đang chọn có `active` |
| Bảng | `dmc.Table`, `dmc.ScrollArea` | Tiêu đề cột chữ nhỏ, hàng sọc xen kẽ rất nhạt |
| Phân trang | `dmc.Pagination`, `dmc.Select` | `total` tính từ số dòng; chọn 25/50/100 |
| Ô chọn truy vấn | `dmc.Select` | Ba lựa chọn cố định |
| Nút hành động chính | `dmc.Button` | Một nút chính mỗi màn hình |
| Khối mã | `dmc.Code`, `dmc.CodeHighlight` | Chữ đơn cách 13px, nền `surface-subtle` |
| Thông báo | `dmc.Alert` | `variant="light"`, có `title` và biểu tượng |
| Trạng thái tải | `dmc.Skeleton` | Đúng hình dạng thẻ/bảng |
| Thông báo đọc lên | `dmc.Notification` + vùng `aria-live` | Dùng cho kết quả chạy truy vấn và đề xuất nguồn |

## Không dùng trong đợt này

- Không dùng `dmc.Modal`/`dmc.Drawer`: không có hành động phá huỷ hay form nhiều bước trong tab này.
- Không dùng `dmc.Slider` cho ngưỡng ghép: ngưỡng cố định 0,85 theo quyết định ở bước yêu cầu.
- Không thêm `dmc.DatePicker` hay ô tìm kiếm toàn cục: ngoài phạm vi đợt này.

## Ghi chú triển khai

- `dmc` chưa có trong môi trường hiện tại; sẽ được ghim vào `requirements.txt` ở bước sinh mã, kèm lý do.
- Ba tab cũ không bị thay đổi thành phần; chỉ tab mới dùng `dmc`, nên hai phần giao diện cùng tồn tại nhưng khác bảng màu có chủ đích.
- Mọi chuỗi hiển thị bằng tiếng Việt; số theo định dạng Việt Nam (dấu phẩy thập phân, dấu chấm phân cách nghìn).
