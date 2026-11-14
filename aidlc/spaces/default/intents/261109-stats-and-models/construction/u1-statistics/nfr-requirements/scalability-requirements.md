# Scalability Requirements — u1-statistics

Nguồn: `../functional-design/functional-spec.md`, `../functional-design/entities.md`, `../../../inception/requirements-analysis/requirements.md` (NFR1).

Đơn vị này chạy theo lô trên một máy, không có người dùng đồng thời. "Mở rộng" ở đây nghĩa là **chịu được dữ liệu lớn hơn**, không phải chịu tải truy cập.

| Mã | Yêu cầu | Mốc | Cách kiểm |
|---|---|---|---|
| NFR1.5 | Dữ liệu vào tăng 5 lần (khoảng 500.000 đơn) vẫn giữ mốc thời gian của NFR1.1 | vẫn dưới 5 phút | **Giả định**, chưa đo được: dữ liệu hiện chỉ có một cỡ và `dataset/` là bất biến. Ghi rõ để lần đo sau biết phải làm gì |
| NFR1.6 | Bộ nhớ đỉnh tăng tuyến tính theo số dòng | hệ số góc không đổi khi nhân đôi số dòng | Đo `tracemalloc` trên một bản sao dữ liệu trong bộ nhớ nhân đôi, ở test `slow` |
| NFR1.7 | Số nhóm của mọi bảng tổng hợp bị chặn bởi số bang và số tháng, không bởi số dòng | bang ≤ 27, tháng ≤ 36 | Test đơn vị trên dữ liệu thật |

## Ghi chú

- NFR1.7 chặn đúng loại phình to nguy hiểm nhất: gộp nhầm grain làm số nhóm tăng theo số dòng. Hai con số 27 và 36 là biên trên thật của dữ liệu Brazil 2016–2018, không phải con số tuỳ ý.
- NFR1.5 là **giả định**, không phải mốc đã đo. Nếu cỡ dữ liệu vượt 5 lần, mốc 5 phút phải đo lại chứ không được suy ra.
