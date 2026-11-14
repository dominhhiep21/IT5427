# User Flow — khối dự đoán

Nguồn: `wireframes.md`, `../intent-capture/intent-statement.md`, `../scope-definition/scope-document.md`, `src/dashboard/analysis_tab.py`.

## Luồng chính — một lần dự đoán

```
Mở dashboard (127.0.0.1:8050)
   │
   ├─ chọn tab "Kết quả phân tích"
   │     │
   │     ├─ callback đọc data/reports/analysis.json  (đúng một lần)
   │     │
   │     ├─ báo cáo `rong`  ──▶ tab hiện thông báo "chưa có báo cáo" + lệnh cần chạy
   │     │                      KHÔNG có mục Dự đoán (giữ nguyên quy tắc hiện tại)   [dừng]
   │     ├─ báo cáo `loi`   ──▶ tab hiện lý do + đường dẫn
   │     │                      KHÔNG có mục Dự đoán                                  [dừng]
   │     └─ báo cáo `day-du` hoặc `mot-phan`
   │            ──▶ dựng các mục hiện có, cộng mục "Dự đoán" ở trạng thái "chưa dự đoán"
   │
   ├─ nhập bảy ô (bang bán, bang mua, ngày đặt, giá món, số lượng món, hai ô số ngày)
   │     │
   │     └─ thiếu/sai định dạng ──▶ lỗi ngay tại ô, nút Dự đoán vẫn bấm được
   │
   ├─ bấm [Dự đoán]
   │     │
   │     ├─ tệp mô hình chưa có ──▶ "Chưa có mô hình đã lưu" + lệnh `--stage stats`
   │     │                          + đường dẫn `data/models/`                        [dừng]
   │     ├─ tệp mô hình không nạp được ──▶ lý do (hỏng, sai phiên bản)                [dừng]
   │     └─ nạp được ──▶ tính xác suất ──▶ hiện kết quả
   │
   └─ đọc kết quả
         ├─ có ngưỡng (report.model ≠ None) ──▶ xác suất · so ngưỡng · quyết định · ba đóng góp
         └─ chưa có ngưỡng (mot-phan)       ──▶ xác suất · "chưa có ngưỡng để so" · ba đóng góp
```

## Bốn nhánh thoát, và vì sao mỗi nhánh phải có

| Nhánh | Khi nào | Người dùng thấy gì |
|---|---|---|
| Không có báo cáo (`rong`) | chưa chạy `--stage stats` | thông báo sẵn có của tab + lệnh cần chạy; **không** có mục Dự đoán |
| Báo cáo hỏng (`loi`) | tệp sai phiên bản hoặc bị sửa tay | lý do + đường dẫn tệp; **không** có mục Dự đoán |
| Báo cáo `mot-phan` | có khối thống kê, thiếu khối mô hình | vẫn dự đoán được, nhưng **không** có câu cảnh báo — chỉ "chưa có ngưỡng để so" |
| Chưa có tệp mô hình | báo cáo `day-du` mà `data/models/` chưa có | "Chưa có mô hình đã lưu" + lệnh sinh tệp + đường dẫn |

Nhánh thứ ba và thứ tư trông giống nhau ở chỗ "chưa so được với ngưỡng", nhưng khác nguyên nhân: một bên là báo cáo thiếu khối mô hình, một bên là báo cáo đủ mà tệp mô hình chưa sinh. Hai câu chữ khác nhau, không gộp.

## Vì sao mục Dự đoán **không** xuất hiện khi báo cáo `rong`

Hiện tại `sections_for()` trả danh sách rỗng khi `view.report` là `None`, nên tab không dựng mục nào. Giữ nguyên quy tắc đó là cách rẻ nhất và đúng nhất: khi chưa có báo cáo thì chưa có gì để dự đoán — và thông báo `rong` đã nói đúng lệnh cần chạy. Dựng thêm một mục Dự đoán trống trong trạng thái đó sẽ là hứa một việc mà nút bấm không làm được.

## Vòng lặp thử nhiều lần

Người dùng sẽ đổi một ô để xem xác suất nhảy thế nào. Luồng phải chịu việc này mà **không** đọc lại báo cáo và **không** nạp lại mô hình mỗi lần bấm:

```
đổi ô ──▶ bấm [Dự đoán] ──▶ dùng lại mô hình đã nạp trong phiên ──▶ kết quả mới
```

Đó là lý do chọn "lưu mô hình ra đĩa": nạp một lần, dự đoán nhiều lần. Nếu huấn luyện lại mỗi lần bấm, mỗi lần thử mất vài giây và người dùng sẽ thôi thử.

## Ràng buộc tất định, nhìn từ luồng

Cùng **bảy ô** + cùng mặc định **phải** cho cùng một xác suất: qua nhiều lần bấm, qua hai lần chạy dashboard, và sau khi khởi động lại. Đây không chỉ là yêu cầu kỹ thuật — một mô hình cho 0,37 rồi 0,42 với cùng đầu vào thì không con số nào dùng được.

## Điều luồng này không có

Không đăng nhập, không lưu lịch sử dự đoán, không xuất kết quả ra tệp, không chia sẻ, không so sánh nhiều lần nhập cạnh nhau. Một người dùng, một phiên, một màn hình — thêm bất kỳ thứ nào trong số đó là thêm trạng thái phải kiểm mà không ai yêu cầu.
