# Deployment Pipeline — câu hỏi

Không có câu hỏi mới cần người trả lời ngay. Ba điểm đã chốt từ trước và vẫn đúng:

1. **Không có môi trường thứ hai** (`team.md` — Deployment): phát hành = chạy từ mã nguồn trên máy local.
2. **Chiến lược recreate** (`deployment-strategy.md`): dừng tiến trình, cập nhật mã, dựng lại dữ liệu, chạy lại.
3. **Không có bí mật** ở bất kỳ tầng nào.

## Ba điểm cần người chốt khi muốn đi xa hơn

| # | Câu hỏi | Ảnh hưởng nếu chưa chốt |
|---|---|---|
| 1 | **Định danh phát hành**: commit hash (như `team.md`) hay tag `v0.x` + `CHANGELOG.md` (như `cicd-pipeline.md` của U1)? | Hiện hai tài liệu nói hai cách; `CHANGELOG.md` đã có nhưng chưa gắn với tag nào |
| 2 | **Có cần môi trường thứ hai không** (máy khác, staging, hay chỉ một máy)? | Nếu có, phải chốt ai được deploy, dữ liệu nguồn đặt đâu, ai chịu trách nhiệm khi hỏng — chưa có câu trả lời nào |
| 3 | **Bật bảo vệ nhánh `main`** trên GitHub để CI thực sự chặn merge? | CI hiện chạy nhưng không chặn được gì; một người làm nên tự quyết |

Tôi không tự chọn ba điểm này: mỗi cái đổi cách ghi lịch sử hoặc thêm một tầng vận hành phải bảo trì.

## Consolidated Summary Confirmation

Tóm tắt những gì stage này chốt, để bạn xác nhận:

1. **Không có môi trường triển khai.** Không staging, không production, không container, không scheduler. Mặc định "deploy on merge" của `org.md` không áp dụng (`team.md` mục Deployment; `technology-stack.md` §5).
2. **"Phát hành" = chạy từ mã nguồn trên máy local**, theo chuỗi: `pytest -m "not slow"` → `pipeline run --stage all` → mở dashboard, dừng ngay ở bước đỏ đầu tiên.
3. **Chiến lược recreate**: dừng dashboard → `git checkout <commit>` → cài lại phụ thuộc nếu cần → dựng lại dữ liệu → chạy lại → kiểm tra khói bằng mắt trên vùng `don-theo-thang`. Dừng dashboard trước khi dựng lại là bắt buộc vì cùng tệp `warehouse/olist.duckdb`.
4. **Quay lui**: về commit trước, xoá `data/ warehouse/ logs/ inbox/`, chạy lại pipeline và dashboard. Không có migration nào phải đảo; `dataset/` không bao giờ bị chạm.
5. **Không có bí mật** ở bất kỳ tầng nào: không `.env`, không `secrets.*`, `config.yaml` chỉ có đường dẫn, URL công khai và ngưỡng số.
6. **Ba điểm để ngỏ, cần người quyết**: định danh phát hành (commit hash hay tag + CHANGELOG), có cần môi trường thứ hai không, và có bật bảo vệ nhánh `main` để CI thực sự chặn merge không.

Does this all look correct?

- A. Looks correct
- B. Request changes

[Answer]: Looks correct
