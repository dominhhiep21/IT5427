# Alarms — intent `261111-model-feature-improvemen`

## 1. Không có alarm, và vì sao

Không có kênh thông báo (không email/Slack/PagerDuty), không có người trực, không có dịch vụ chạy nền. Một alarm không có người nhận là nhiễu, không phải giám sát.

## 2. Cái đóng vai alarm: các cổng chặn

| "Alarm" | Kích hoạt khi | Hành động |
|---|---|---|
| `QualityGate` (21 + 9 + 10 check) | cấu trúc/số dòng/dị thường lệch | pipeline dừng, CLI trả mã thoát 1 |
| `KpiReconciler` (5 KPI) | doanh thu/đơn/AOV/tỉ lệ trễ lệch dung sai | pipeline dừng |
| Cổng phủ CI | phủ < 80% | chặn hợp nhất |
| Test `slow` mốc sàn | `beats_floor` sai trên báo cáo thật | chặn hợp nhất |
| `predict` với payload hỏng | `ModelError` | giao diện hiện câu hướng dẫn, ghi `prediction.model_unavailable` |

Đây là alarm **pull** (ai chạy mới thấy), đúng với công cụ chạy tay. Không có alarm **push**.

## 3. Khi nào mới đáng thêm alarm

Khi có môi trường chạy tự động theo lịch (cron/scheduler). Khi đó ba alarm tối thiểu:

1. **Lượt chạy đỏ liên tiếp ≥ 2** → báo người.
2. **Thời gian tầng `stats` > 300 s** (ngân sách NFR1) hai lượt liền.
3. **`prediction.model_unavailable` xuất hiện > 0** trong 24 giờ.

Ngưỡng đặt dưới mức SLO để còn thời gian sửa — đúng `phases/operation.md` `## Observability`.
