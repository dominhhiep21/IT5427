# Design System Mapping

Nguồn: `assets/style.css` (token hiện có) và `refined-mockups-questions.md` Q4 = B: được thêm token mới nhưng không thêm bộ thành phần thứ hai.

## Token dùng lại

| Thành phần | Token hiện có |
|---|---|
| Nền trang, bề mặt thẻ | `--paper`, `--surface` |
| Chữ chính, phụ, mờ | `--text`, `--text-2`, `--text-3` |
| Viền thường và đậm | `--border`, `--border-strong` |
| Màu nhấn và cảnh báo | `--accent`, `--accent-soft`, `--clay`, `--clay-soft` |
| Bo góc | `--radius-sm`, `--radius` |
| Bóng đổ | `--shadow-xs`, `--shadow-sm` |
| Thang khoảng cách | `--space-1` … `--space-6` |

## Token thêm mới (được phép)

| Token đề nghị | Giá trị | Dùng cho |
|---|---|---|
| `--chart-grid` | `#eceee9` | Lưới biểu đồ trong khối mô hình nếu có |
| `--signal-flag` | `#a94a2b` | Nhãn "bị gắn cờ" trong bảng phân bố |

Hai token này đặt trong `:root` của `assets/style.css`, không tạo tệp CSS thứ hai.

## Thành phần dùng lại

- Khung thẻ: `.integration-card` và các biến thể hiện có.
- Bảng: `.integration-table` cho bảng trong tab.
- Trạng thái: khối trạng thái hiện có với `data-state` (`chua-chay`, `dang-tai`, `day-du`, `mot-phan`, `loi`).
- Nhãn viên thuốc: `.integration-status` cho trạng thái khối.

## Điều không được làm

- Không thêm bộ thành phần thứ hai (không kéo thêm thư viện UI, không tạo bảng riêng).
- Không đổi token hiện có để phục vụ riêng tab này.
- Không đặt màu trực tiếp trong mã Python; mọi màu đi qua token.
