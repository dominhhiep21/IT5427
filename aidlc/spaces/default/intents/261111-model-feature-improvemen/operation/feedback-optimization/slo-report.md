# SLO Report — intent `261111-model-feature-improvemen`

Chu kỳ: 2026-11-11 → 2026-11-13 (ba Bolt). Không có SLO phần trăm (xem `../observability-setup/slo-config.md` §1); báo cáo dùng sáu SLI đo được.

## 1. Tuân thủ

| SLI | Ngưỡng | Kỳ này | Đạt? |
|---|---|---|---|
| SLI-1 Dữ liệu khớp baseline | tuyệt đối | 5 KPI, 9 bảng mart, 11 view khớp; `--stage all` xanh mỗi lượt | **đạt** |
| SLI-2 Mốc sàn mô hình | `beats_floor` true | 0,6482 ≥ max(0,55; 0,5297) | **đạt** |
| SLI-3 `score_item` | < 200 ms | 10,49 ms | **đạt** |
| SLI-4 `load_model` | < 2 s | 0,33 ms | **đạt** |
| SLI-5 Dựng khối Dự đoán | < 300 ms | ~2 ms | **đạt** |
| SLI-6 Báo cáo không `loi` sau `stats` | 0 lượt lỗi | 0 trong các lượt xác nhận | **đạt** |

## 2. Mục tiêu chất lượng không phải SLO

| Mục tiêu | Kết quả | Ghi chú |
|---|---|---|
| AUC ≥ 0,70 | **0,6482** | **không đạt**; vượt baseline (0,5297) và mốc sàn (0,55). Cờ `auc_below_target` bật đúng |
| Phủ ≥ 80% | 92,71% | đạt |
| Không hồi quy dữ liệu | 0 hồi quy | đạt |

## 3. Sự cố trong kỳ

| Sự cố | Mức | Xử lý | Test canh |
|---|---|---|---|
| `_serve_features` dùng sai 2/14 đặc trưng (vòng soát U2) | P1 (số sai) | sửa + test | có |
| `state_regions` khai mà không dùng | P1 | sửa + test vòng ghi-đọc | có |
| 12 `FIELD_LABELS` thiếu 6 trường (vòng soát U3) | P2 (hiển thị sai) | sửa + test tham số 14 nhãn | có |
| `test_linkage_score` đỏ do tải máy | P4 | chạy lại khi rảnh | không cần |
| Tài liệu lệch số (691 vs 694, 34 vs 50 mục) | P4 | sửa tài liệu | — |

Ba sự cố P1/P2 đều do **vòng soát bắt**, không do người dùng phát hiện — dấu hiệu tốt cho quy trình, và là lý do vòng soát phải giữ.

## 4. Kết luận

Sáu SLI đạt; mục tiêu AUC 0,70 **không đạt** và đã được ghi ở mọi nơi liên quan. Không có sự cố nào lọt ra ngoài.
