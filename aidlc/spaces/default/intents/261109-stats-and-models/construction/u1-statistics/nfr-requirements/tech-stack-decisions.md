# Tech Stack Decisions — u1-statistics

Nguồn: `../../../inception/requirements-analysis/requirements.md`, `../functional-design/rules.md`, `../../../../codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`, `requirements.txt`, và câu trả lời Q1–Q4 trong `nfr-requirements-questions.md`.

## Quyết định

| # | Quyết định | Lý do | Phương án đã loại |
|---|---|---|---|
| TS-1 | Python 3.13, `pandas` 2.2, `numpy` qua `pandas` | Cả repo đang chạy trên đó; dữ liệu vừa bộ nhớ | Không có lý do đổi |
| TS-2 | Ghim `scipy` cho phân phối và kiểm định | Cần phân phối chuẩn, chi-square, và hệ số tương quan Pearson; tự viết lại là nguồn lỗi số học | Không dùng thư viện thống kê nào: phải tự viết phân phối, sai số khó kiểm |
| TS-3 | **Không** ghim `statsmodels` | Q4 = A: phần phân rã mùa vụ tự viết theo BR1.5, nên `statsmodels` không còn việc nào; quy tắc dự án cấm ghim thư viện không có lý do | Q1 = C ban đầu (dùng `statsmodels` cho phân rã) — bị Q2 = A vô hiệu, và Q4 = A chốt bỏ |
| TS-4 | Phân rã mùa vụ tự viết bằng `pandas.Series.rolling(center=True, min_periods=…)`, không import `numpy` trực tiếp | `rolling` đã có đúng cơ chế cửa sổ thu hẹp ở hai đầu; dùng nó thì không phải ghim `numpy` thành phụ thuộc trực tiếp, đúng quy tắc dự án coi `numpy` là bám theo `pandas` | Dùng `statsmodels` rồi bọc lại; hoặc import `numpy` trực tiếp rồi phải ghim thêm một gói chỉ để làm một phép trung bình động |
| TS-5 | Đọc dữ liệu qua `AnalyticsService` trên view DuckDB | Quy tắc dự án: phân tích mới đọc mart sẵn có thay vì định nghĩa lại doanh thu | Đọc trực tiếp Parquet: bỏ qua lớp đã kiểm |
| TS-6 | Ghi tệp qua `AtomicWriter` | Đã là quy ước của repo | Ghi trực tiếp: để lại tệp dở |
| TS-7 | Nhật ký JSONL với đúng năm trường sẵn có | Q3 = A; lý do bỏ qua đã nằm trong tệp báo cáo | Thêm trường riêng cho tầng `stats` |

## Hệ quả lên `requirements.txt`

Thêm đúng một dòng:

```
scipy==<phiên bản ghim>  # kiểm định thống kê cho tầng stats (u1-statistics); xem tech-stack-decisions.md TS-2
```

Phiên bản cụ thể chốt tại Code Generation khi cài, nhưng **phải ghim đúng số**, không dùng khoảng. `statsmodels` không được thêm.

## Chất lượng mã

| Mã | Yêu cầu | Mốc | Cách kiểm |
|---|---|---|---|
| NFR4.1 | `ruff check .` và `ruff format --check` sạch trên mọi tệp của đơn vị | không lỗi, không cảnh báo | Chạy trong chuỗi xác nhận và trong CI |
| NFR4.2 | Mọi tệp nguồn mới được thêm vào danh sách `ruff format --check` của `ci.yml` cùng lúc với việc tạo tệp | danh sách khớp với tệp có thật | Đối chiếu thủ công trong cùng thay đổi; CI sẽ đỏ nếu lệch |

Không thêm `per-file-ignores` mới, và không có kiểm tra kiểu tĩnh — cả hai là quyết định đã chốt của dự án, không phải thiếu sót.

## Điều còn phải xác nhận khi cài
`scipy` kéo theo `numpy` với phiên bản tối thiểu riêng; nếu bản `numpy` mà `scipy` đòi cao hơn bản `pandas` đang dùng, phải nâng `pandas` và chạy lại toàn bộ bộ test trước khi coi là xong — đây là loại thay đổi có thể làm lệch số của KPI baseline.
