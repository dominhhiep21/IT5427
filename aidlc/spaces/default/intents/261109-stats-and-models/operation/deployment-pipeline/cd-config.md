# CD Configuration

Nguồn: `../../construction/ci-pipeline/ci-config.md`, `../../construction/ci-pipeline/quality-gates.md`, `../../construction/u1-statistics/infrastructure-design/infrastructure-specification.md`, `aidlc/spaces/default/memory/project.md` (`## Deployment`).

## Không có CD pipeline, và đó là quyết định

Dự án không có môi trường triển khai: không staging, không production, không container, không dịch vụ đám mây. Vì vậy **không có** cấu hình CD để viết — viết một pipeline triển khai cho một môi trường không tồn tại là bịa ra hạ tầng.

## "Triển khai" của dự án này là gì

Chạy từ mã nguồn trên máy người làm, sau khi CI xanh:

```
1. pytest -m "not slow"                    bộ nhanh phải xanh
2. run --stage all                         dựng mart, qua QualityGate + KpiReconciler
3. run --stage stats                       sinh báo cáo, khớp những gì dashboard đọc
4. mở dashboard, xem bằng mắt              hình dạng giao diện là một phần của "chạy đúng"
```

Dừng ngay ở bước đỏ đầu tiên. Bước 3 đứng trước bước 4 vì mở dashboard khi báo cáo chưa sinh lại là xem một màn hình có thể đang đọc tệp cũ.

## Phiên bản và phát hành

| Mục | Cách làm |
|---|---|
| Phiên bản | commit hash; không có git tag |
| Ghi mốc | `CHANGELOG.md` theo ba nhóm **Thêm / Sửa / Nội bộ** |
| Artefact | không có — mã nguồn là artefact |
| Đăng ký gói | không có — không phát hành gói nào |

## Điều không tồn tại, nên không cấu hình

- Không blue/green, không canary, không feature flag: không có môi trường để chuyển lưu lượng.
- Không migration cơ sở dữ liệu: mart sinh lại được từ `dataset/`.
- Không secret, không biến môi trường: mọi cấu hình nằm trong `config.yaml` và `config/*.yaml`.
- Không health check, không synthetic monitor: dashboard là tiến trình cục bộ, không có ai gọi từ ngoài.

## Cổng duy nhất trước khi coi là phát hành

CI xanh trên nhánh đang làm. Không có cổng thứ hai, vì không có bước thứ hai.
