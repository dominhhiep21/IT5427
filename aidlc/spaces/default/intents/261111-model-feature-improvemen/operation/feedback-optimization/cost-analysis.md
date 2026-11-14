# Cost Analysis — intent `261111-model-feature-improvemen`

## 1. Chi phí tiền

**0 đồng.** Không có tài nguyên đám mây, không dịch vụ trả phí, không kho artefact. Duy nhất một lời gọi mạng tuỳ chọn tới API IBGE (miễn phí) khi `--refresh-ibge`.

## 2. Chi phí thật của đợt: thời gian máy và thời gian người

| Hạng mục | Số đo | Ghi chú |
|---|---|---|
| Toàn bộ bộ test + phủ | **424 s**/lượt | 723 test, gồm 15 `slow` dựng lại pipeline |
| Bộ nhanh | 25 s | dùng hàng ngày |
| Tầng `stats` | ~28–30 s | ngân sách 300 s |
| Bước huấn luyện | ~24 s | ngân sách 240 s |
| Chạy lại từ đầu (`--stage all` + `stats`) | ~2 phút | khi cần tái lập artefact |

## 3. Cơ hội giảm chi phí (và vì sao chưa làm)

| Cơ hội | Lợi | Giá | Quyết định |
|---|---|---|---|
| Gộp `stats` vào `--stage all` (TD-11) | bớt một lệnh, bớt một lượt đọc mart | đổi hợp đồng CLI và ít nhất ba test hình dạng; CI đang tách hai bước có lý do | **để đợt sau**, đã ghi |
| Bỏ bước `--stage all` khi chỉ đổi dashboard | tiết kiệm ~90 s/lượt | mất kiểm hồi quy dữ liệu — đúng thứ đã cứu đợt này | **không** |
| Cache `load_model` trong tiến trình | tiết kiệm 0,33 ms/lần bấm | trả bản mô hình cũ sau khi huấn luyện lại | **không** (PD3.2) |
| Giảm số test `slow` | tiết kiệm vài phút CI | mất cổng trên dữ liệu thật | **không** |

## 4. Chi phí của chính quy trình

| Hạng mục | Ghi nhận |
|---|---|
| Ba vòng soát ở U2 (2 lần NOT-READY) | bắt được 1 Critical + 2 Major thật; nếu bỏ soát, lỗi sẽ nằm trong sản phẩm |
| Hai vòng soát ở U3 | bắt 1 Critical (đồ thị phụ thuộc không dựng được) + 1 Major (nhãn) |
| Viết lại tài liệu sau khi mã lệch | ~6 chỗ; rẻ hơn để tài liệu sai |

Kết luận: chi phí tiền bằng 0; chi phí thời gian tập trung ở bộ test `slow` và các vòng soát — cả hai đều đã trả lại giá trị cụ thể trong đợt này.
