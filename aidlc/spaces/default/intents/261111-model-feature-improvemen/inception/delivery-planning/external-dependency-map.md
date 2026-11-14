# External Dependency Map — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `bolt-plan.md`, `delivery-planning-questions.md` (Q4 = A), `../requirements-analysis/requirements.md`, `../domain-design/components.md`.

## Kết luận ngắn

**Không có mục nào bên ngoài chặn kế hoạch.** Không có API bên thứ ba bắt buộc, không có cửa sổ dữ liệu, không có phê duyệt ngoài, không có bàn giao từ team khác. Vì vậy tài liệu này ngắn — và ngắn ở đây là **đúng**, không phải thiếu sót.

## Bảng

| Hạng mục bên ngoài | Ai sở hữu | Thời gian | Bolt bị chặn | Nếu trượt thì sao |
|---|---|---|---|---|
| API IBGE (bang/thành phố) | Bên thứ ba | Không chặn — đã có **cache** trên đĩa và **fallback** khi gọi lỗi | Không Bolt nào | Không ảnh hưởng: pipeline chạy bằng cache; chỉ mất phần làm mới nhãn địa lý |
| `dataset/` — 9 CSV Olist | Trong repo, bất biến | Có sẵn | Không | Không áp dụng: không bao giờ sửa, chỉ đọc |
| GitHub Actions (`windows-2022`, Python 3.13) | Trong repo | Có sẵn | Không | Nếu CI không chạy được, cổng tự động duy nhất mất — xem mục dưới |
| `pip` — cài 12 gói đã ghim | PyPI | Vài phút | Không | Nếu PyPI không truy cập được, không Bolt nào build được; đây là phụ thuộc hạ tầng, không phải lịch |

## Ba ghi chú cần đọc kèm

**1. CI là cổng tự động duy nhất — và nó là phụ thuộc ngoài thật.** Repo không có môi trường staging/production, không Docker, không scheduler. Nếu GitHub Actions ngừng chạy (hết quota, sự cố), không còn cổng tự động nào; phần còn lại chỉ là test chạy tay trên máy. Điều này không chặn Bolt nào hôm nay, nhưng nó là lý do `team-allocation.md` nói thẳng "không ai soát chéo mã".

**2. Không có phụ thuộc vào dữ liệu của người khác.** Toàn bộ đầu vào là 9 CSV bất biến trong `dataset/`. Không có nguồn dữ liệu sống nào có thể đổi giữa hai lần chạy — nên kết quả đo là tái lập được, và đó là điều kiện để so AUC giữa các lần.

**3. Ngân sách thời gian không phải phụ thuộc ngoài.** 300 s cho tầng `stats` là hằng số **trong repo** (`tests/integration/test_u2_model_end_to_end.py` và `team.md`), không phải hạn mức của dịch vụ nào. Nếu grain dòng hàng đẩy thời gian lên, cách xử lý là đo lại và sửa hằng số **có chủ đích** — không phải chờ ai.
