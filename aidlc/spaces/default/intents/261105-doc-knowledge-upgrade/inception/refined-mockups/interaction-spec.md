# Interaction Spec — Tab "Tích hợp"

Định dạng theo `.aidlc/knowledge/aidlc-design-agent/component-spec-template.md`. Mỗi thành phần mô tả trạng thái, đầu vào, hành vi bàn phím và cách đọc màn hình.

---

## GroupCard (thẻ nhóm trên tổng quan)

| Field | Value |
|---|---|
| Component | GroupCard |
| Description | Thẻ hiển thị trạng thái và hai dòng số liệu của một nhóm chủ đề; cả thẻ là điểm vào chi tiết |
| Category | navigation |

### States

| State | Description | Trigger |
|---|---|---|
| default | Thẻ hiện tên nhóm, badge trạng thái, hai dòng số liệu | tải xong dữ liệu |
| hover | Viền đậm hơn, con trỏ bàn tay | trỏ chuột |
| focus | Viền 2px tương phản ≥ 3:1 quanh toàn thẻ | Tab |
| active | Nền xám rất nhạt | giữ chuột |
| empty | Badge "Rỗng" thay cho số liệu | nhóm chưa có dữ liệu |
| partial | Badge "Một phần" + tên phần thiếu | nhóm thiếu một phần dữ liệu |
| loading | Badge xám "Đang tải", hai dòng số liệu là skeleton | đang đọc dữ liệu |
| error | Badge đỏ "Lỗi", dòng số liệu thay bằng câu "không tải được" | đọc dữ liệu thất bại |

### Props / Inputs

| Prop | Type | Required | Default | Description |
|---|---|---|---|---|
| title | string | yes | — | Tên nhóm |
| status | enum (`dat`, `mot-phan`, `loi`, `rong`) | yes | `rong` | Trạng thái hiển thị |
| metrics | array of {label, value} | yes | [] | Hai dòng số liệu |
| href | string | yes | — | Đích khi mở |

### Responsive Behaviour

| Breakpoint | Behaviour |
|---|---|
| < 1024px | Không hỗ trợ; hiện thông báo cần màn hình rộng hơn |
| 1024–1279px | Lưới 2×2 |
| ≥ 1280px | Lưới 4 cột |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `link` (thẻ là một `dmc.UnstyledButton` bọc ngoài) |
| keyboard interaction | Tab để focus, Enter để mở; không dùng Space vì đây là liên kết |
| Label / aria-label | `aria-label` = "<tên nhóm>, trạng thái <trạng thái>" |
| Contrast ratio | Chữ 4.5:1, viền 3:1 |
| Screen reader | Đọc tên nhóm, trạng thái, rồi hai dòng số liệu theo thứ tự |
| Focus management | Mở chi tiết thì focus vào tiêu đề màn hình chi tiết |

---

## DataTable (bảng dữ liệu có phân trang)

| Field | Value |
|---|---|
| Component | DataTable |
| Description | Bảng dữ liệu dùng cho ánh xạ, cặp ghép, nguồn; phân trang và sắp xếp được |
| Category | display |

### States

| State | Description | Trigger |
|---|---|---|
| default | Hiện trang đầu, 50 dòng/trang | tải xong |
| loading | Skeleton 5 dòng | đang tải |
| empty | Khối rỗng có câu giải thích và lý do | không có dòng |
| error | Banner lỗi phía trên bảng | tải thất bại |

### Props / Inputs

| Prop | Type | Required | Default | Description |
|---|---|---|---|---|
| columns | array of {key, label, type} | yes | — | Cột và kiểu hiển thị |
| rows | array of object | yes | [] | Dữ liệu |
| pageSize | number | no | 50 | Số dòng mỗi trang |
| caption | string | yes | — | Mô tả bảng cho trình đọc màn hình |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `table` gốc của `dmc.Table`, có `<caption>` |
| Keyboard interaction | Tab vào bảng; nút phân trang nhận Tab |
| Label / aria-label | `aria-label` cho nhóm nút phân trang: "Phân trang <tên bảng>" |
| Contrast ratio | Tiêu đề cột 4.5:1; viền hàng dùng token `border-strong` (3:1) |
| Screen reader | Đọc caption, số dòng, trang hiện tại và tổng số trang |
| Focus management | Đổi trang giữ focus ở nút phân trang vừa bấm |

**Sắp xếp:** không hỗ trợ trong đợt này. Bảng chỉ sắp theo thứ tự cố định do lớp truy vấn trả về; nếu sau này thêm sắp xếp thì phải có `aria-sort` trên ô tiêu đề và hành vi Enter/Space trên tiêu đề cột.

---

## Select (ô chọn đối tượng và ô chọn truy vấn)

| Field | Value |
|---|---|
| Component | Select |
| Description | Chọn một giá trị trong danh sách cố định (đối tượng ghép, truy vấn mẫu, số dòng mỗi trang) |
| Category | input |

### States

| State | Description | Trigger |
|---|---|---|
| default | Hiện giá trị đã chọn | tải xong |
| open | Danh sách xổ xuống | Enter hoặc bấm |
| disabled | Không chọn được khi dữ liệu chưa tải | đang tải hoặc lỗi |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `combobox` |
| Keyboard interaction | Mũi tên di chuyển, Enter chọn, Escape đóng |
| Label / aria-label | Luôn có nhãn chữ phía trên: "Đối tượng", "Truy vấn mẫu", "Số dòng mỗi trang" |
| Screen reader | Đọc nhãn, giá trị đang chọn, số lựa chọn |

---

## ActionButton (nút Đề xuất nguồn, Xem SQL nguồn, Chạy)

| Field | Value |
|---|---|
| Component | ActionButton |
| Description | Nút hành động chính hoặc phụ trên màn hình C và E |
| Category | input |

### States

| State | Description | Trigger |
|---|---|---|
| default | Nút bật | dữ liệu sẵn sàng |
| loading | Nút ở trạng thái chờ, không bấm lại được | hành động đang chạy |
| disabled | Nút mờ, `aria-disabled="true"` | thiếu điều kiện (chưa chọn truy vấn) |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `button` |
| Keyboard interaction | Enter và Space đều kích hoạt |
| Label / aria-label | Nhãn chữ rõ nghĩa, không dùng biểu tượng đơn lẻ |
| Screen reader | Khi xong, vùng `aria-live` đọc kết quả; focus giữ ở nút |

---

## InlineNotice (thông báo trong trang)

| Field | Value |
|---|---|
| Component | InlineNotice |
| Description | Câu thông báo cho các tình huống không nguồn nào đủ trường, đề xuất nguồn xong, lỗi đọc dữ liệu |
| Category | feedback |

### States

| State | Description | Trigger |
|---|---|---|
| info | Nền xám nhạt, biểu tượng thông tin | đề xuất nguồn xong |
| warning | Nền vàng nhạt, biểu tượng cảnh báo | không nguồn nào đủ trường |
| error | Nền đỏ nhạt, biểu tượng cảnh báo | đọc dữ liệu thất bại |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `status` cho info, `alert` cho warning/error |
| Keyboard interaction | Không nhận focus; nội dung đọc qua `aria-live` |
| Label / aria-label | Câu đầy đủ, nêu việc gì và bước tiếp theo |
| Screen reader | Đọc ngay khi xuất hiện (polite cho info, assertive cho error) |

---

## StatusBadge

| Field | Value |
|---|---|
| Component | StatusBadge |
| Description | Nhãn trạng thái đạt / một phần / lỗi / rỗng |
| Category | feedback |

### States

| State | Description | Trigger |
|---|---|---|
| dat | Nền xanh nhạt, chữ xanh đậm, biểu tượng dấu kiểm | trạng thái đạt |
| mot-phan | Nền vàng nhạt, chữ nâu đậm, biểu tượng nửa vòng tròn | trạng thái một phần |
| loi | Nền đỏ nhạt, chữ đỏ đậm, biểu tượng cảnh báo | trạng thái lỗi |
| rong | Nền xám nhạt, chữ xám đậm, biểu tượng gạch ngang | trạng thái rỗng |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `status` |
| Label / aria-label | Luôn có chữ, không chỉ biểu tượng |
| Contrast ratio | Chữ trên nền nhạt đạt ≥ 4.5:1 |
| Screen reader | Đọc đúng nhãn trạng thái bằng tiếng Việt |

---

## QueryRunner (khối chọn và chạy truy vấn)

| Field | Value |
|---|---|
| Component | QueryRunner |
| Description | Chọn một trong ba truy vấn mẫu, chạy, và hiển thị hai khối mã cùng số liệu chạy |
| Category | input |

### States

| State | Description | Trigger |
|---|---|---|
| default | Đã chọn truy vấn, nút Chạy bật | tải xong |
| loading | Nút Chạy ở trạng thái chờ; hai khối mã phủ skeleton | bấm Chạy |
| success | Hai khối mã và số liệu thời gian/số dòng | chạy xong |
| error | Thông báo dưới ô chọn: tên truy vấn + lỗi + nút thử lại | chạy lỗi |
| stale | Kết quả cũ được ghi rõ "kết quả lần trước" | chạy lỗi sau lần thành công |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `combobox` cho ô chọn, `button` cho nút Chạy |
| Keyboard interaction | Mũi tên chọn truy vấn, Enter chạy, Tab sang khối mã |
| Label / aria-label | Nhãn hiển thị "Truy vấn mẫu" gắn với ô chọn |
| Screen reader | Khi chạy xong, vùng `aria-live="polite"` đọc "Xong, <số> dòng, <thời gian> giây" |
| Focus management | Sau khi chạy xong, focus giữ ở nút Chạy |

---

## PageHeader (đầu màn hình chi tiết)

| Field | Value |
|---|---|
| Component | PageHeader |
| Description | Breadcrumb quay lại, tiêu đề màn hình, và dòng ghi chú thuật ngữ dưới bảng |
| Category | navigation |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `navigation` cho breadcrumb |
| Keyboard interaction | Tab tới breadcrumb, Enter quay lại tổng quan |
| Label / aria-label | Breadcrumb có `aria-label="Đường dẫn quay lại"` |
| Focus management | Khi vào màn hình chi tiết, focus vào `h2` của màn hình |

---

## Chuyển màn hình

| Từ | Tới | Hành động | Focus sau khi chuyển |
|---|---|---|---|
| Tổng quan | Chi tiết nhóm | Enter trên thẻ | `h2` của màn hình chi tiết |
| Chi tiết nhóm | Tổng quan | Enter trên breadcrumb | Thẻ của nhóm vừa xem |
| Tab khác | Tab "Tích hợp" | Bấm/Enter trên tab | Thẻ đầu tiên |
| Bất kỳ | Bất kỳ | Escape không dùng để điều hướng (không có hộp thoại) | — |
