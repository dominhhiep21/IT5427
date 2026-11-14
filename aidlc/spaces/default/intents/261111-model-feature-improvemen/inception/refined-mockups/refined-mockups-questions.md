# Câu hỏi — Refined Mockups

Không có câu hỏi nào để hỏi bạn: mọi lựa chọn thiết kế ở stage này đã bị chốt bởi quyết định trước đó hoặc bởi token đang chạy.

## Vì sao

| Lựa chọn thường phải hỏi | Đã bị chốt bởi |
|---|---|
| Màu cho kết quả cảnh báo | `BR3.9` — không thêm token màu; và đợt này chốt phân biệt bằng chữ |
| Cỡ chữ, khoảng cách, bán kính | `assets/style.css` — bảy thang `--space`, bốn `--radius` |
| Bố cục lưới | tab đã có khuôn: một cột ở hẹp, hai cột ở rộng; mốc 1280px là mốc đã kiểm |
| Có biểu đồ hay không | `wireframes.md` — không biểu đồ |
| Vị trí khối | `Q1 = A` của Rough Mockups — mục thứ tư |

## Consolidated Summary Confirmation

Bốn artifact đã viết. Bản tóm tắt:

- **`mockups.md`**: bố cục cuối (header → fieldset bảy ô → hai nút → mục kết quả), thang kích thước lấy **đúng** token đang có, và quyết định **không đổi màu** cho kết quả cảnh báo — phân biệt bằng chữ `CẢNH BÁO` / `KHÔNG cảnh báo`.
- **`interaction-spec.md`**: sáu trạng thái và chuyển tiếp, hành vi từng điều khiển (validate khi blur, nút Dự đoán **không** bị chặn khi có ô lỗi), thứ tự tab, và năm tương tác **bị từ chối có chủ đích** (không dự đoán tự động, không thanh trượt, không tooltip, không "xem thêm", không lịch sử).
- **`design-system-mapping.md`**: mỗi thành phần dựng bằng `html.*`/`dcc.*` như ba mục hiện có; **một** khối CSS mới cho `fieldset`, chỉ dùng token có sẵn; và ba chỗ phải sửa ngoài khối (`TEXTS["model_caption"]`, `README.md`, test hình dạng).
- **`accessibility-checklist.md`**: 14 mục WCAG 2.1 AA, mỗi mục có cách kiểm; ba chỗ dễ hỏng nhất khi viết mã; và giới hạn thật — không có trình đọc màn hình trong môi trường này, nên các mục cấu trúc kiểm bằng cây thành phần.

- Looks correct
- Request changes

[Answer]: Looks correct
