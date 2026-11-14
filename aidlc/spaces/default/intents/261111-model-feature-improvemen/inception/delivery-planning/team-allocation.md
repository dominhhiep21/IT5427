# Team Allocation — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `../ideation/team-formation/` (đã chạy), `bolt-plan.md`, `../units-generation/unit-of-work.md`.

**Mob** ở đây là nhóm thực thi một Bolt. Với dự án này, "nhóm" là **một người cộng các agent AI-DLC**, không phải một team nhiều người — nên tài liệu này ngắn, và trung thực về điều đó.

## Bối cảnh đội

`team-formation` (Ideation) đã chốt: **một người làm, một người quyết định**; không review chéo, không người phê duyệt thứ hai; cổng tự động duy nhất là **CI** trên GitHub Actions (9 bước, `windows-2022`, Python 3.13). Vì vậy không có "Program Board" nhiều nhóm — có một đường thực thi và một bộ cổng.

## Phân công theo Bolt

| Bolt | Unit | Mob | Vai trò |
|---|---|---|---|
| 1 | `u1-mart-and-baseline` | `aidlc-developer-agent` (AI) + người làm | Developer dựng mart + hàm baseline; người làm chạy xác nhận bốn bước và quyết định ở cổng |
| 2 | `u2-features-and-models` | `aidlc-developer-agent` (AI) + người làm | Developer dựng khung, đặc trưng, hai mô hình, lưu mô hình, báo cáo v3; người làm đo thời gian và chốt ngân sách |
| 3 | `u3-prediction-ui` | `aidlc-developer-agent` (AI) + người làm | Developer dựng bề mặt và callback thứ mười; người làm kiểm bằng mắt trên dashboard thật |

Không có chuyển giao giữa các nhóm: cùng một người, cùng một agent, ba lượt. Điều này **không** phải thiếu phân công — nó là mô hình đã chốt từ Team Formation và đã được xác nhận lại ở Practices Discovery.

## Chuyên môn cần cho từng Bolt

| Bolt | Cần biết | Có sẵn? |
|---|---|---|
| 1 | DuckDB, Parquet, grain của 9 bảng mart, `StarSchemaValidator`, 5 KPI | Có — toàn bộ nằm trong repo và đã có test |
| 2 | `scikit-learn` (logistic + `HistGradientBoosting`), chia tập theo khoá nhóm, chống rò rỉ đặc trưng, `pickle` | Có — `requirements.txt` đã ghim `scikit-learn`; `pickle` là thư viện chuẩn |
| 3 | Dash (callback, `Output`, `dcc.Loading`), a11y (tương phản, `aria-live`), token CSS | Có — `dash==4.4.1` đã ghim; `assets/style.css` đã có token |

Không có khoảng trống kỹ năng nào cần lấp bằng người ngoài hay công cụ mới.

## Nhịp và cổng

- **Nhịp**: mỗi Bolt một lượt, theo thứ tự `u1 → u2 → u3`; không chạy song song.
- **Cổng tự động**: CI trên ba nhánh đã khai (`main`, `feature/update-ui-ux`, `feature/analysis-and-models`), 9 bước, gồm cổng phủ 80% trên **toàn bộ** bộ test.
- **Cổng người**: mỗi Bolt có một cổng duyệt ở cuối; Plan Approval của Code Generation là cổng riêng, không gộp.
- **Xác nhận trước khi coi một Bolt là xong**: chuỗi bốn bước đã chốt — `pytest -m "not slow"` → `run --stage all` → `run --stage stats` → mở dashboard; dừng ở bước đỏ đầu tiên.

## Điều tài liệu này không hứa

Một người làm ba Bolt nghĩa là **không có ai soát chéo mã**. Bù lại: mỗi đơn vị có test end-to-end riêng trên dữ liệu thật, và hình dạng bề mặt được canh bằng test ở ba tệp. Đó là toàn bộ cơ chế bắt lỗi — không có gì thêm, và không nên giả vờ có.
