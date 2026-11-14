# Functional Design — Câu hỏi (u1-mart-and-baseline)

**Không có câu hỏi mở.** Mọi quyết định mà bước này cần đã được chốt ở Inception và ghi trong record:

| Quyết định | Nguồn |
|---|---|
| Thêm **ba cột** vào mart, không đổi grain, không đổi lọc | `unit-of-work.md` U1; `contract-summary.md` C1 |
| `seller_state` lấy từ `dim_sellers`, không suy từ địa chỉ khách | `contract-summary.md` C1 (`shared-schema > v_fact_order_items`) |
| Hai cột mốc **chỉ** dùng ở dạng số ngày dẫn xuất; dạng ngày thô bị cấm làm đặc trưng | `project.md` `## Forbidden`; `contract-summary.md` C1 |
| Hàm baseline là hàm thuần, **grain-neutral**, chia trên `date_key` với `cut_date` cho trước | `contract-summary.md` C1 (`function`) |
| `CohortCounts` **thuộc U2** — U1 không sinh, không sở hữu bốn bộ đếm | `unit-of-work.md` U1 ranh giới; `contract-summary.md` C1 ghi chú |
| Lỗi của hàm baseline là `ModelError`, không phải `PipelineError` gốc | `contract-summary.md` C1 |
| 9 bảng mart + 11 view phải giữ nguyên số dòng; `StarSchemaValidator` và 5 KPI xanh | `team.md` `## Testing Posture`; `requirements.md` FR1.1 |

Chỗ duy nhất bước này tự quyết là **cách đặt tên và nhóm luật** (BR1.1–BR1.6) — không phải một lựa chọn nghiệp vụ, nên không cần hỏi.
