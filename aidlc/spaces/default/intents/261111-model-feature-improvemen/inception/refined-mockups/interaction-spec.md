# Interaction Spec — khối "Dự đoán"

Nguồn: `mockups.md`, `../../ideation/rough-mockups/user-flow.md`, `../user-stories/stories.md` (US2.2, US2.4, US2.5), `../requirements-analysis/requirements.md` (FR3).

## Sáu trạng thái, và chuyển tiếp giữa chúng

```
[1] không có khối        ← báo cáo rong | loi
      │ (chạy --stage stats rồi mở lại)
      ▼
[2] chưa dự đoán    ──bấm Dự đoán──▶ [3] đang tính ──xong──▶ [4] có kết quả, có ngưỡng
      ▲                                   │                    │
      │                                   └──lỗi──▶ [5] có kết quả, chưa có ngưỡng
      └───────── Đặt lại mặc định ────────┘
                                          │
[6] mô hình chưa sẵn  ◀── thiếu data/models/ (chặn từ [2], không vào [3])
```

| # | Trạng thái | Vào bằng | Ra bằng | Người dùng thấy |
|---|---|---|---|---|
| 1 | không có khối | `report.status ∈ {rong, loi}` | chạy `--stage stats` | không có mục thứ tư; thông báo của tab nói lệnh cần chạy |
| 2 | chưa dự đoán | báo cáo `day-du` hoặc `mot-phan` | bấm **Dự đoán** | mười một giá trị nhập, **không** có số nào, một dòng nhắc bấm |
| 3 | đang tính | bấm Dự đoán | xong hoặc lỗi | spinner **có sẵn** của `dcc.Loading` đang bọc thân tab; nút **không** bị khoá, và kết quả cũ vẫn hiện (xem ghi chú dưới) |
| 4 | có kết quả, có ngưỡng | tính xong, `report.model` có ngưỡng | đổi ô rồi bấm lại | xác suất · so ngưỡng · quyết định · ba đóng góp |
| 5 | có kết quả, chưa ngưỡng | tính xong, `report.model` là `None` | như trên | xác suất · "chưa có ngưỡng để so" · ba đóng góp; **không** có câu cảnh báo |
| 6 | mô hình chưa sẵn | bấm Dự đoán khi `data/models/` vắng | chạy `--stage stats` | câu hướng dẫn có **nguyên văn** lệnh và đường dẫn; không ném |

## Hành vi từng điều khiển

| Điều khiển | Hành vi | Ghi chú |
|---|---|---|
| Mười một giá trị nhập | validate khi rời ô (blur), không khi gõ | tránh báo lỗi giữa lúc đang nhập |
| Ô ngày đặt | chọn ngày; tháng và thứ **suy ra**, không nhập | FR3.1 |
| Bốn trường mặc định | **có điều khiển sửa được**, hiện đúng bốn giá trị đã chốt (`credit_card`, `1`, `true`, `true`) | đổi một trường rồi dự đoán lại **phải** cho xác suất khác |
| **Dự đoán** | bấm được cả khi có ô lỗi; lỗi hiện tại ô | không chặn nút — chặn nút làm người dùng không biết vì sao |
| **Đặt lại mặc định** | trả **mười một** điều khiển về giá trị mẫu, xoá kết quả, về trạng thái 2 | không đụng dữ liệu báo cáo |
| Kết quả | chỉ hiện khi có; không có placeholder số | |

## Bàn phím

| Bước | Phần tử | Hành vi |
|---|---|---|
| Tab 1…11 | **mười một** điều khiển: bảy trường lõi rồi bốn trường mặc định, theo thứ tự khai báo | thứ tự đọc = thứ tự tab |
| Tab 12 | **Dự đoán** | Enter/Space kích hoạt |
| Tab 13 | **Đặt lại mặc định** | |
| Kết quả | **không** nhận focus | đọc lên qua vùng thông báo của tab (xem dưới) |
| Escape | trong ô nhập | không đóng gì; không có hộp thoại nào |

Không `tabIndex` dương ở bất kỳ đâu — đây là ràng buộc đã có của tab (NFR5.3) và có test canh.

## Thông báo cho trình đọc màn hình

- **Một** vùng thông báo duy nhất: `RESULT_BODY_ID` của tab. **Lưu ý quan trọng:** vùng đó bọc **toàn bộ panel** (`analysis_tab.py:519-528`), nên thay con trực tiếp của nó sẽ khiến trình đọc màn hình đọc lại **cả tab**. Khối phải ghi kết quả vào một **nút con riêng** bên trong panel (một `div` có `id` riêng, không có `aria-live`), và chỉ nút con đó được cập nhật khi có kết quả mới. Không đặt `aria-live` thứ hai.
- Mỗi ô nhập có `<label for>`; `fieldset` có `<legend>`.
- Lỗi tại ô gắn bằng `aria-describedby` trỏ tới phần tử lỗi.
- Câu kết luận dùng chữ, không dùng màu: `KHÔNG cảnh báo` / `CẢNH BÁO: dòng hàng này có nguy cơ trễ`.

## Tương tác bị từ chối có chủ đích

| Không làm | Vì sao |
|---|---|
| Dự đoán tự động mỗi khi đổi ô | mỗi lần đổi sẽ ghi đè kết quả người dùng đang đọc |
| Thanh trượt cho xác suất | gợi ý thang tuyệt đối; và nó mời người dùng "chỉnh" một đầu ra |
| Tooltip cho ba đóng góp | nội dung quan trọng không giấu sau hover (không dùng được bằng bàn phím) |
| Nút "xem thêm" cho 12 đóng góp | ba là đủ cho câu hỏi "vì sao đơn này"; thêm là mời đọc bảng số |
| Lưu lịch sử dự đoán | nằm ngoài phạm vi; thêm trạng thái phải kiểm mà không ai yêu cầu |

## Điều spec này không nói

Nó không nói cách vẽ biểu đồ — không có biểu đồ. Nó không nói màu cho kết quả — không đổi màu. Nó không nói cỡ chữ tuyệt đối ngoài ba mức đã nêu trong `mockups.md`.
