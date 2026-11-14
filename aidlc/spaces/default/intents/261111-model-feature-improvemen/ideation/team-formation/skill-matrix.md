# Skill Matrix

Nguồn: `../scope-definition/intent-backlog.md`, `team-assessment.md`, `../../../261109-stats-and-models/` (record của đợt trước), `requirements.txt`.

## Kỹ năng cần cho từng đơn vị, đối chiếu với bằng chứng đã có

Cột "Bằng chứng" chỉ ghi thứ đọc được trong repo — không phải tự đánh giá.

| Kỹ năng | Cần cho | Bằng chứng trong repo | Trạng thái |
|---|---|---|---|
| Python 3.13, pandas, type hint hiện đại | U1, U2, U3 | 70 tệp trong `src/`, 537 test xanh ở đợt trước | **có** |
| DuckDB và lớp view/mart | U1 | `src/integrate/*`, `src/analytics/service.py`, 11 view đang chạy | **có** |
| Kiểm định thống kê, khoảng tin cậy, chọn ngưỡng | U2 | `src/analytics/statistics.py`, `src/analytics/model.py` (100% phủ) | **có** |
| `scikit-learn`: huấn luyện, AUC, precision/recall | U2 | mô hình 11 đặc trưng đã huấn luyện thật, AUC 0,5133 đo được | **có** |
| `HistGradientBoostingClassifier` | U2 | chưa dùng lần nào trong repo | **chưa chứng minh** — cùng API `fit`/`predict_proba`, rủi ro thấp |
| Lưu và nạp mô hình (`joblib`/`pickle`) | U2 | chưa có trong repo | **chưa chứng minh** — lần đầu làm |
| Dash, `dash-mantine-components` | U3 | tab thứ năm của đợt trước, có test canh hình dạng | **có** |
| Thiết kế thị giác (tương phản, nhịp, khoảng cách) | U3 | tab trước đúng chức năng, chưa có lượt soát thị giác | **một phần** |
| Đo phủ, đặt cổng CI | U1, U3 | `ci.yml`, `pytest-cov`, cổng 80% đang chạy | **có** |
| Review độc lập (người thứ hai) | mọi đơn vị | không có ai — team một người | **không có, và không thể có** |

## Ba khoảng trống, xếp theo mức thật sự đáng lo

| # | Khoảng trống | Đáng lo không | Cách bù |
|---|---|---|---|
| 1 | **Review độc lập** | **Có** — mọi lỗi phải do test hoặc do agent soát bắt; đợt trước hai lỗi thật đã bị bắt đúng bằng cách đó | agent soát ở các stage có reviewer; test end-to-end trên dữ liệu thật; không có cách nào khác |
| 2 | **Lưu/nạp mô hình** | Trung bình — lần đầu, và lỗi loại này im lặng (nạp đúng tệp nhưng sai phiên bản thư viện vẫn cho số khác) | JSON mô tả đặc trưng + phiên bản thư viện; phép kiểm lặp lại hai lần chạy |
| 3 | **Soát thị giác** | Thấp — tab có sẵn, chỉ thêm một vùng nhập | lượt `refactoring-ui` sau khi U3 xong, không gộp vào U3 |

## Điều bảng này không nói

Nó không nói người làm thiếu kỹ năng ở cột nào — hai dòng "chưa chứng minh" là **chưa có bằng chứng trong repo**, không phải "không biết". Nhưng với một team một người, khoảng cách giữa hai câu đó chính là chỗ rủi ro sống, nên tôi ghi đúng như nó là.
