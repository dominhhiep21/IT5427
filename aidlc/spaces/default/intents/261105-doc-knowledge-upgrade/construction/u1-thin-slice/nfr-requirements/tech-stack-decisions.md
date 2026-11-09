# Tech Stack Decisions — u1-thin-slice

Nguồn: `technology-stack.md`, `requirements.txt`, `team-practices.md`, `contract-summary.md`, `functional-design/functional-spec.md` (Workflow 1–3).

## Đã chốt ở cấp dự án

| Hạng mục | Lựa chọn | Ghi chú |
|---|---|---|
| Ngôn ngữ | Python 3.13 | Có sẵn |
| Xử lý dữ liệu | pandas | Có sẵn |
| Truy vấn | DuckDB | Có sẵn |
| Giao diện | Plotly Dash | Có sẵn; tab mới ở đơn vị này dựng bằng thành phần Dash lõi, `dmc` thay vào ở Bolt 6 |
| Kiểm thử | pytest + pytest-cov | Có sẵn |

## Yêu cầu chất lượng mã (NFR2, NFR3)

| Mã | Yêu cầu | Đo bằng |
|---|---|---|
| NFR2.1 | Độ phủ dòng tối thiểu 80% cho `src/`, không hạ ngưỡng để cho một bước pass | `pytest --cov=src`, báo cáo độ phủ trong lần chạy xác nhận |
| NFR2.2 | Mọi module mới của đơn vị này có test riêng, kể cả module chỉ nối dây | mỗi tệp trong `src/integration/` có tệp test tương ứng; phần giao diện (`src/integration/card.py` và vùng `don-theo-thang` trong `src/integration/tab.py`) được kiểm bằng `tests/unit/test_integration_card.py` và `tests/unit/test_dashboard_smoke.py` |
| NFR3.1 | `ruff check` và `ruff format --check` sạch trước khi coi là xong | hai lệnh chạy cạnh bộ test nhanh |

## Yêu cầu đúng đắn của lát cắt (NFR5.4–NFR5.6, bổ sung sau review)

Ba yêu cầu dưới đây **bổ sung** cho NFR5.1–NFR5.3 ở `reliability-requirements.md` (cổng chất lượng, KPI baseline, hình dạng dashboard); chúng mang dải mã riêng để không mã nào bị định nghĩa hai lần.

| Mã | Yêu cầu | Đo bằng |
|---|---|---|
| NFR5.4 | Đơn vị là **chỉ đọc**: không có thao tác ghi nào vào `data/marts` hay `warehouse/` (cơ chế bảo đảm cho NFR5.2 ở `reliability-requirements.md`) | rà mã: không có lời gọi ghi vào hai thư mục đó; và chạy `python -X utf8 -m src.pipeline run --stage all` để xác nhận NFR5.1/NFR5.2 vẫn xanh sau thay đổi |
| NFR5.5 | **Số trên vùng kết quả `don-theo-thang` phải khớp một phép tính độc lập, sai lệch 0, cho mọi trạng thái vùng hiển thị** | một test tính lại số đơn **theo từng `(tháng, trạng thái)`** trực tiếp từ `dataset/` bằng pandas (không dùng đường truy vấn của lát cắt), giới hạn đúng cửa sổ 12 tháng mà vùng hiển thị, rồi so từng nhóm, **tổng từng tháng** và tổng toàn kỳ với kết quả truy vấn; lệch một đơn ở bất kỳ trạng thái nào là test đỏ |
| NFR5.6 | Bộ lọc và phạm vi của truy vấn lát cắt phải tường minh và kiểm được | test khẳng định câu SQL nguồn (đọc từ `source_sql` của kết quả truy vấn, không qua giao diện) nêu rõ cột `trang_thai` trong `SELECT`/`GROUP BY` và không gộp mờ mọi trạng thái; cửa sổ 12 tháng là phép tính của tầng hiển thị, kiểm bằng `months` của kết quả chứ không nhét vào SQL |

**Vì sao thêm NFR5.5:** FR2.5 đặt chuẩn "sai lệch 0" cho số liệu; lát cắt không thuộc ba truy vấn mẫu nhưng cùng loại rủi ro. Nếu chỉ dựa vào "không ghi nên không đổi", một truy vấn sai vẫn qua cổng. Phạm vi là **mọi trạng thái** vì thẻ hiển thị số theo từng trạng thái (BR1.5); một phép đối chiếu chỉ cho `delivered` sẽ bỏ lọt sai lệch ở bảy trạng thái còn lại.

## Quyết định riêng cho đơn vị này

| Mã | Quyết định | Lý do |
|---|---|---|
| TS-U1-1 | Dùng `pandas` để đọc `olist_orders_dataset.csv`, không dùng DuckDB cho bước nạp | Bốn trường đọc từ một tệp; đọc thẳng đơn giản hơn và không cần dựng view |
| TS-U1-2 | Truy vấn chạy trên DuckDB in-memory, **nạp từ `dataset/` trong chính lần chạy**; số hiển thị trong **vùng kết quả `don-theo-thang` của tab "Tích hợp"** (khai ở C9 `result_region_ids`), không đọc view mart | Chứng minh cơ chế viết lại xuống SQL mà không phụ thuộc `warehouse/`. **Một đường dữ liệu duy nhất:** vùng đọc kết quả truy vấn của lần chạy; trạng thái rỗng chỉ có nghĩa "chưa chạy lần nào", không mượn ý "hãy chạy pipeline" |
| TS-U1-5 | `TabConfig` đọc thêm `result_region_ids` từ `config/integration-tab.yaml`, **bắt buộc** chứa `don-theo-thang`; thiếu khoá hoặc thiếu vùng đó → `ConfigurationError`, và `_tab_config` trong `src/dashboard/app.py` dùng cấu hình mặc định thay vì làm sập dashboard | C9 nay khai vùng kết quả; không đọc khoá này thì U6 dựng lại thân tab sẽ làm mất vùng số liệu — đúng lỗi đã bị cổng nghiệm thu bắt |
| TS-U1-3 | Ghim `ruff` vào `requirements.txt` ngay ở đơn vị này | Thực hành đã chốt; mọi đơn vị sau đều dùng |
| TS-U1-4 | Không thêm thư viện nào khác | Giữ ràng buộc "chỉ thư viện nhỏ, mã nguồn mở" |

## Việc cần làm ở bước sinh mã

- Ghim `ruff` vào `requirements.txt` kèm lý do.
- Thêm cấu hình `ruff` ở gốc repo (một chỗ duy nhất).
- Tạo tệp test cho mọi module mới của đơn vị, gồm test đối chiếu số trên vùng ở NFR5.5 và test phạm vi truy vấn ở NFR5.6. Phần giao diện (vùng `don-theo-thang` trong `src/integration/tab.py`, thẻ trong `src/integration/card.py`) được kiểm bằng `tests/unit/test_dashboard_smoke.py` và `tests/unit/test_integration_card.py` — đây là phép đo của NFR2.2 cho nửa giao diện.
- Đọc `result_region_ids` từ `config/integration-tab.yaml` và bắt buộc có `don-theo-thang` (TS-U1-5); thêm khoá này vào tệp cấu hình theo C9.
- BR1.8 và `functional-spec.md` Workflow 3 đã được sửa cho khớp TS-U1-2 (trạng thái rỗng là "chưa chạy truy vấn lần nào" kèm nút chạy); không sửa lại lần nữa ở bước sinh mã.
- Bảo đảm thẻ đọc số từ kết quả truy vấn của chính lần chạy (TS-U1-2); trạng thái rỗng là "chưa chạy".
