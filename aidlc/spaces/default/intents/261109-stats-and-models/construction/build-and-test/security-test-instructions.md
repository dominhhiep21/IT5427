# Security Test Instructions

Nguồn: `../../u1-statistics/nfr-requirements/security-requirements.md`, `../../u2-model/nfr-requirements/security-requirements.md`, `../../u3-display/nfr-requirements/security-requirements.md`, `../../../inception/contract-design/contract-summary.md`, `aidlc/spaces/default/memory/project.md`.

## Bối cảnh

Không có bề mặt mạng, không có xác thực, không có người dùng thứ hai. Rủi ro thật của đợt này là **rò rỉ nhãn** trong mô hình và **rò rỉ định danh** trong báo cáo — không phải tấn công từ ngoài.

## Phép kiểm đã có

| Mã | Phép kiểm | Tệp |
|---|---|---|
| SEC-1 / SEC-U3-1 | Truy vấn dựng từ tham số, không nối chuỗi; tab không có ô nhập | `tests/unit/test_analytics_statistics.py`, `test_dashboard_analysis_tab.py` |
| SEC-2 / SEC-U3-2 | Chỉ đọc view trong `VIEW_TABLES`; đường dẫn từ `AppConfig` | test `slow` của U1, U2 |
| SEC-3 / SEC-U3-3 | Báo cáo và khối mô hình không chứa `customer_id`, `customer_unique_id`, địa chỉ, mã bưu chính | `test_u1_stats_end_to_end.py`, `test_dashboard_analysis_tab.py` |
| SEC-4 / SEC-U3-4 | Không bí mật trong mã; không `dangerously_allow_html`; không gọi mạng | rà `ruff` + test cây thành phần |
| SEC-U3-5 | Không tài nguyên ngoài trong tab | `test_dashboard_analysis_tab.py` |
| **Rò rỉ nhãn** | Danh sách 11 đặc trưng và tập 10 cột cấm rời nhau; **khung đặc trưng thật** chỉ chứa đúng 11 tên | `tests/unit/test_analytics_model.py` |

## Phép kiểm quan trọng nhất của đợt

Rò rỉ nhãn không làm chương trình hỏng: nó chạy, cho AUC cao, và trả lời sai câu hỏi. Không ai phát hiện bằng cách nhìn kết quả — chỉ phát hiện bằng cách kiểm danh sách đặc trưng. Vì vậy nó có test riêng, kiểm trên **khung dữ liệu thật** chứ không chỉ trên hằng số.

`has_review` nằm trong tập cấm vì nó là cột hậu giao cùng họ `has_*` với hai cờ được dùng.

## Không kiểm

- Không có kiểm thâm nhập, quét phụ thuộc CVE, hay SAST — không có bề mặt mạng và không có phụ thuộc chạy trên máy chủ.
- Không có kiểm mã hoá: không có dữ liệu nhạy cảm rời khỏi máy người dùng.
