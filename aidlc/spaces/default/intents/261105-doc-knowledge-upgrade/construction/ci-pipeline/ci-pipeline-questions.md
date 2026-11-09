# CI Pipeline — câu hỏi

Không có câu hỏi mới. Hai quyết định của đợt đã chốt ở Infrastructure Design của U1 và vẫn giữ nguyên:

- **Q1 = C**: phát hành bằng tag `v0.x` + `CHANGELOG.md`, không có artifact đóng gói.
- **Q2 = B**: một workflow CI tối thiểu, **không** chạy bộ `slow`.

Các điểm đã chốt kèm lý do, ghi ở `ci-config.md` §3–§5 và `quality-gates.md`:

1. **Runner `windows-2022`, không `ubuntu-latest`** — sản phẩm chỉ chạy trên Windows; chạy CI trên Linux sẽ xanh cho mã có thể đỏ trên máy thật.
2. **Không chạy bộ `slow` trong CI** — cần dữ liệu thật và ~52 giây; chạy tay trước khi phát hành.
3. **Cổng phủ 80% chạy trên toàn bộ bộ test, không chỉ bộ nhanh** — bảy mô-đun chỉ có phần phủ đến từ bộ `slow`.
4. **CI chạy pipeline trước khi test** — vì bộ nhanh chưa hermetic (`TD-09`); khi `TD-09` được sửa thì xoá bước 5.
5. **`ruff check .` toàn repo nhưng `ruff format --check` chỉ trên mã của đợt** — 35 tệp cũ chưa qua `ruff format` và `team.md` cấm một lần format toàn repo lẫn vào thay đổi chức năng.

## Điều chưa chốt, cần người quyết khi có môi trường thật

- **Tag đặt ở đâu**: thiết kế chọn *sau khi merge về `main`*, vì tag trên nhánh làm việc dễ trỏ vào commit sẽ bị squash. Nếu muốn tag trước khi merge thì phải nói.
- **Ghim `uses:` theo SHA** thay vì major tag: chặt hơn về chuỗi cung ứng, đánh đổi là phải cập nhật tay khi có bản mới.
- **Bật nhánh bảo vệ trên GitHub** (bắt buộc CI xanh trước khi merge vào `main`): hiện chưa bật vì repo là một người làm, nhưng CI chỉ có nghĩa chặn khi nhánh `main` được bảo vệ.
