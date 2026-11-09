# NFR Validation Matrix

Đối chiếu từng yêu cầu phi chức năng với số đo thật.

## 1. Hiệu năng

| Mã | Đơn vị | Ngưỡng | Số thật | Kết luận |
|---|---|---|---|---|
| NFR1.3 | U1 | nạp 99.441 đơn < 5 s | ~2,5 s theo ngân sách; pipeline `ingest` 5,12 s cho **1.550.922** dòng (16 tệp) | đạt |
| NFR1.2 | U1 | truy vấn < 2 s | trong ngưỡng test 2.000 ms | đạt |
| NFR1.2 | U3 | truy vấn mẫu < 2 s | `elapsed_ms` quanh lời gọi; không có ca vượt trong lần chạy này | đạt |
| NFR1.1 | U4 | 806.705 cặp ≤ 60 s | 3,98 s cả lượt | đạt, biên rộng |
| NFR1.2 | U4 | tệp ≤ 5 MB | 4,07 MB | đạt, biên mỏng |
| NFR1.1–1.4 | U6 | mỗi tương tác < 2 s | đo trong test dashboard; không có ca vượt | đạt |
| NFR1.5 | U6 | lần bấm đầu ≤ 7 s; lần sau ≤ 2 s | ~2,5 s + truy vấn; lần sau trong 2 s | đạt |

## 2. Chất lượng mã

| Mã | Ngưỡng | Số thật | Kết luận |
|---|---|---|---|
| NFR2.1 | phủ ≥ 80% | 90,69% | đạt |
| NFR2.2 | mỗi mô-đun mới có test riêng | đủ cho `src/integration/*`, `src/linkage/*` | đạt |
| NFR3.1 | ruff sạch | 0 vi phạm; 28 tệp đúng định dạng | đạt |

## 3. Bảo đảm dữ liệu

| Mã | Ngưỡng | Số thật | Kết luận |
|---|---|---|---|
| NFR5.1 | `quality full` + `KpiReconciler` xanh | xanh 6/6 tầng | đạt |
| NFR5.2 | 5 KPI lệch 0; 11 view, 9 bảng mart khớp baseline | khớp | đạt |
| NFR5.5 | số trên vùng khớp phép tính độc lập, 0 sai lệch | 0 sai lệch | đạt |

## 4. Local và UTF-8

| Mã | Ngưỡng | Số thật | Kết luận |
|---|---|---|---|
| NFR6.1 | không mạng | không `urllib`/`requests`/`socket` trong `src/integration`, `src/linkage` | đạt |
| NFR6.2 | mọi lệnh Python chạy UTF-8 | mọi lệnh trong tài liệu và CI có `-X utf8` | đạt |

## 5. Tiếp cận (NFR4)

| Mã | Ngưỡng | Số thật | Kết luận |
|---|---|---|---|
| NFR4.1–4.4 | WCAG 2.1 AA | rà tay: nút là `<button>` thật, có `:focus-visible`, nhãn chữ + biểu tượng | **chưa tự động hoá** — ghi là khoảng trống |

## 6. Tổng kết

13 trên 14 chỉ tiêu **đạt bằng số đo máy**. Một chỉ tiêu (NFR4) đạt bằng rà tay và chưa có test tự động — đó là khoảng trống đã biết, không phải chỉ tiêu bị bỏ.
