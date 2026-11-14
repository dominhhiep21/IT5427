# Incident Plan — intent `261111-model-feature-improvemen`

## 1. Bối cảnh

Một người làm, một máy local, không có người dùng ngoài. "Sự cố" ở đây không phải dịch vụ sập mà là **kết quả sai hoặc cổng đỏ** — thứ có thể khiến một quyết định dựa trên số sai.

## 2. Mức độ (đã hạ xuống cho quy mô một người)

| Mức | Định nghĩa | Ví dụ | Phản ứng |
|---|---|---|---|
| **P1** | Số liệu sai có thể dẫn tới quyết định sai, hoặc dữ liệu gốc bị đụng | `QualityGate`/`KpiReconciler` đỏ; `dataset/` bị sửa; báo cáo ghi AUC sai | dừng mọi việc khác, sửa ngay |
| **P2** | Bề mặt chính không dùng được | tab phân tích `loi`; khối Dự đoán luôn "mô hình chưa sẵn" dù tệp có | sửa trong ngày |
| **P3** | Cổng đỏ nhưng kết quả vẫn đúng | cổng phủ tụt; `ruff format` lệch | sửa trước lần hợp nhất kế tiếp |
| **P4** | Khó chịu, không ảnh hưởng kết quả | nhãn xấu, log thiếu trường | ghi lại, sửa khi có dịp |

## 3. Vòng đời

1. **Phát hiện:** cổng đỏ, `logs/` có `warning`/`error`, hoặc mắt thấy màn hình sai.
2. **Phân mức:** theo bảng trên. P1 ⇒ dừng, không "sửa tạm rồi tính sau".
3. **Khoanh vùng:** dùng RB tương ứng trong `runbooks.md`.
4. **Sửa:** sửa nguyên nhân; nếu phải đổi baseline/allowlist thì ghi lý do vào cùng thay đổi.
5. **Xác nhận:** bốn bước `scripts/verify_intent.ps1`.
6. **Ghi lại:** thêm một dòng vào `test-results.md` mục "Ca đỏ đã gặp" nếu là ca mới.

## 4. Điều cấm trong lúc xử lý sự cố

| Cấm | Vì sao |
|---|---|
| Hạ `--cov-fail-under` để cho xanh | biến cổng thành đồ trang trí |
| Cập nhật `BASELINE`/`allowlist` cho khớp số mới mà không ghi lý do | che hồi quy dữ liệu |
| Hạ `MODEL_AUC_FLOOR` khi AUC tụt | xoá cổng chống thoái hoá |
| Sửa `dataset/` để cho test xanh | dữ liệu gốc bất biến |
| Nới ngưỡng thời gian (300/240/60 s) ngầm | phải đo lại và sửa có chủ đích |

## 5. Sau sự cố

Với P1/P2: ghi một mục ngắn vào `test-results.md`: dấu hiệu, nguyên nhân gốc, test mới canh (nếu có), điều đã đổi. Không cần postmortem hình thức cho công cụ một người, nhưng **phải** có test canh nếu lỗi tái phát được — đó là bài học đã thành luật trong đợt này.
