# CD Config — Olist integration upgrade

## 1. Không có môi trường triển khai

Đợt này **không có** staging, production, container, cloud hay scheduler. `team.md` mục Deployment ghi rõ: "chưa có môi trường triển khai"; `technology-stack.md` §5 ghi "CI/CD — Không có", "Đóng gói phát hành — Không có". Vì vậy mặc định "deploy on merge" của `org.md` **không áp dụng**.

Hệ quả: không có CD pipeline, không có promotion gate giữa các tầng môi trường, không có artifact registry.

## 2. "Phát hành" của đợt này là gì

Chạy từ mã nguồn trên máy local, theo đúng chuỗi xác nhận của `team.md` (Q7 = C):

1. `.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow"` — dừng nếu đỏ.
2. `.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all` — sinh `data/`, `warehouse/`, `logs/`.
3. `.venv\Scripts\python.exe -X utf8 -m src.dashboard` — mở, bấm "Chạy truy vấn" ở vùng `don-theo-thang`, thấy số liệu.

Không có bước build, không có bước copy artifact.

## 3. Định danh phiên bản

`team.md` ghi phiên bản = **commit hash**, không có tag. `cicd-pipeline.md` của U1 lại đề xuất tag `v0.x` + `CHANGELOG.md` (Q1 = C). Hai điều này **chưa được chốt thành một**: đợt này giữ commit hash làm định danh thật, còn tag/CHANGELOG là đề xuất chưa thực thi. Ghi nhận để người quyết.

## 4. Bí mật và cấu hình

Không có bí mật nào ở bất kỳ tầng nào: không `.env`, không `secrets.*`, `config.yaml` chỉ có đường dẫn, URL công khai và các ngưỡng số. Vì vậy không cần cơ chế phân phối bí mật cho môi trường.

## 5. Điều kiện để có CD thật (khi nào làm)

Chỉ đáng dựng khi có ít nhất một trong hai: (a) có người thứ hai dùng dashboard, (b) dữ liệu vượt một máy. Khi đó cần chốt trước: môi trường thứ hai là gì, ai được deploy, dữ liệu nguồn đặt ở đâu, và ai chịu trách nhiệm khi hỏng. Không có những câu trả lời đó thì CD chỉ thêm một tầng phải bảo trì.
