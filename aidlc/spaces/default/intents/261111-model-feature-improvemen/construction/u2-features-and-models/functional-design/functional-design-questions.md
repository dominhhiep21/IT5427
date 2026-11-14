# Functional Design — Câu hỏi (u2-features-and-models)

**Không có câu hỏi mở.** Mọi quyết định đã chốt ở Inception; bảng dưới chỉ để người đọc sau không hỏi lại.

| Quyết định | Nguồn |
|---|---|
| Grain dự đoán là **dòng hàng**; nhãn kế thừa từ đơn; chia tập theo `order_id` | `components.md` ADR-003; `requirements.md` FR1.2, FR2.1 |
| Quần thể: `delivered` **và** có carrier date; bốn bộ đếm sinh từ **một** truy vấn | `contract-summary.md` C1; FR1.2 |
| Mô hình **triển khai là logistic**; `HistGradientBoosting` chỉ để báo cáo `auc_tree` | `components.md` ADR-004 |
| `analysis.json` **v3**: 11 trường khối `model`, `counts` **chín** khoá | `contract-summary.md` C2; FR2.5 |
| Lưu mô hình bằng `pickle` vào `data/models/`; `AppConfig.models_dir` là trường mới | FR2.4; Q3 = A |
| `assemble_report` là entry point duy nhất dựng `AnalysisReport` | `components.md` ADR-008 |
| Ba đóng góp log-odds **gộp theo trường**, không phải theo cột one-hot | FR3.3 |
| Không thêm phụ thuộc; `pickle` là thư viện chuẩn | `project.md` `## Mandatory` |
