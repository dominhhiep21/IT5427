# Deployment Strategy

Nguồn: `cd-config.md`, `../../construction/u1-statistics/infrastructure-design/infrastructure-specification.md`, `aidlc/spaces/default/memory/project.md` (`## Deployment`), `aidlc/spaces/default/memory/phases/operation.md`.

## Chiến lược: thay thế tại chỗ, không có lưu lượng để chuyển

Không có người dùng đồng thời, không có phiên bản chạy song song, không có lưu lượng để chia. Mọi chiến lược triển khai dần dần (blue/green, canary, rolling) giả định có hai phiên bản cùng phục vụ — giả định đó sai ở đây.

Cách "triển khai" là: dừng dashboard, cập nhật mã và phụ thuộc, chạy lại chuỗi xác nhận bốn bước, mở lại dashboard.

## Ba thứ thay đổi, ba cách xử lý

| Thay đổi | Cách đưa vào | Vì sao |
|---|---|---|
| Mã nguồn | `git pull` trên nhánh đang làm, rồi chạy lại chuỗi | Không có build, không có artefact |
| Phụ thuộc | `pip install -r requirements.txt` trong `.venv` | Sau khi cài phải chạy lại bộ `slow` của U1 — nâng `numpy` làm lệch số |
| Dữ liệu dẫn xuất | `run --stage all` rồi `run --stage stats` | Hai thư mục sinh ra bị `.gitignore`; không có bản sao lưu, sinh lại là cách duy nhất |

## Cửa sổ rủi ro

Dashboard đang mở thì giữ khoá `warehouse/olist.duckdb`, nên `--stage all` sẽ hỏng. Quy trình bắt buộc: **đóng dashboard trước**, chạy chuỗi, rồi mở lại. Đây là điều đã ghi trong `docs/runbook.md` và đã gây lỗi thật một lần.

## Môi trường

Chỉ một: máy người làm, `127.0.0.1:8050`. Không có parity để giữ, vì không có môi trường thứ hai. "Triển khai lại từ đầu" = xoá `data/`, `warehouse/`, `logs/`, `inbox/` rồi chạy `--stage all` — khoảng 3 phút trên 99.441 đơn.

## Điều không làm

- **Không đặt tag phát hành.** Phiên bản là commit hash; tag là thứ phải bảo trì mà không ai đọc.
- **Không đóng gói.** Không có artefact để đóng gói.
- **Không giữ bản sao lưu dữ liệu dẫn xuất.** Chúng sinh lại được bằng một lệnh; bản sao lưu chỉ tạo thêm một trạng thái phải đồng bộ.
