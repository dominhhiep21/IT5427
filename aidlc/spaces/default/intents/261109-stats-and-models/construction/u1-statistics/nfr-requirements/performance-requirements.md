# Performance Requirements — u1-statistics

Nguồn: `../functional-design/functional-spec.md`, `../functional-design/rules.md`, `../../../inception/requirements-analysis/requirements.md` (NFR1), `../../../inception/contract-design/contract-summary.md`.

Bối cảnh đo: máy phát triển Windows, Python 3.13, dữ liệu thật 99.441 đơn và 112.650 dòng hàng. Mốc dưới đây đo trên lần chạy đầy đủ `python -X utf8 -m src.pipeline run --stage stats`, sau khi `--stage all` đã dựng mart.

| Mã | Yêu cầu | Mốc đo | Cách kiểm |
|---|---|---|---|
| NFR1.1 | Tổng thời gian tầng `stats` | dưới 5 phút | Đo đồng hồ trong test `slow`, khẳng định trên lần chạy thật |
| NFR1.2 | Thời gian một phép kiểm định | dưới 60 giây mỗi phép | Đo trong test đơn vị quanh từng hàm, **không** đọc từ nhật ký — nhật ký chỉ có sự kiện bắt đầu, kết thúc và mỗi lần bỏ qua |
| NFR1.3 | Bộ nhớ đỉnh | ngưỡng `quality.memory_fail_mb` hiện có trong `config.yaml` (2048 MB), không đặt con số thứ hai | Dùng lại `src/common/memory.py` (`MemoryProbe`) quanh lần chạy `stats` trong test `slow` |
| NFR1.4 | Chi phí phân rã mùa vụ | tuyến tính theo số tháng | Test đơn vị trên hai chuỗi dài khác nhau, so tỉ lệ thời gian với tỉ lệ độ dài |

## Phạm vi của NFR1 ở đơn vị này

NFR1 trong `requirements.md` gồm hai nửa: phần kiểm định dưới 5 phút, và **huấn luyện mô hình dưới 15 phút**. Nửa thứ hai thuộc `u2-model` theo `unit-of-work.md`, không thuộc đơn vị này. Ghi rõ ở đây để không ai đọc bảng trên mà tưởng U1 phủ cả NFR1 — nó chỉ phủ nửa thời gian chạy của tầng `stats`.

## Ghi chú

- Mốc 5 phút đo trên dữ liệu hiện có; biên mở rộng nằm ở `scalability-requirements.md` (NFR1.5).
- Trần bộ nhớ dùng lại đúng ngưỡng `quality.memory_fail_mb` của `config.yaml` qua `MemoryProbe`; tầng `stats` không đặt ngưỡng riêng, để cùng một con số không bị khai ở hai nơi.
