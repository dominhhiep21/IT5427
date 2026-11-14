# Tech Stack Decisions — u3-display

Nguồn: `../../../inception/requirements-analysis/requirements.md`, `../functional-design/rules.md`, `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`, `requirements.txt`, `assets/style.css`.

## Quyết định

| # | Quyết định | Lý do | Phương án đã loại |
|---|---|---|---|
| TSU-1 | Dùng **Dash + `dash-mantine-components`** (`dmc`) đã ghim trong repo | `requirements.txt` ghim `dash-mantine-components==2.8.1`; `src/integration/tab.py` và `src/dashboard/app.py` đều dùng `dmc.*` | Thêm bộ thành phần thứ hai (`dash_bootstrap_components`): hai hệ token song song, không ai dọn |
| TSU-2 | **Không** thêm phụ thuộc nào cho đơn vị này | Tab chỉ đọc JSON và dựng thành phần; mọi thứ cần đã có | Thêm `plotly-express` cho vài biểu đồ: chưa cần, và làm nặng bộ test |
| TSU-3 | Màu, khoảng cách, cỡ chữ lấy từ token trong `assets/style.css` | Quy tắc BR3.9 và NFR5 (tương phản như các tab hiện có) | Viết CSS mới trong tab: trôi khỏi hệ token |
| TSU-4 | Định dạng số dùng `src/dashboard/formatting.py` sẵn có | Một chỗ duy nhất biết định dạng Brazil (`1.234,56`, `%`) | Tự format trong tab: hai cách hiển thị cùng một số |
| TSU-5 | Đọc báo cáo qua `read_report` của U1, không mở tệp trực tiếp | C2 là hợp đồng; mở tệp trực tiếp là bỏ qua bốn trạng thái | `json.load` trong tab: mất `rong`/`mot-phan`/`loi` |

## Hệ quả lên `requirements.txt`

**Không thêm dòng nào.** Đơn vị này không có phụ thuộc mới.

## Cạm bẫy đã ghi

`late_rate.rate` là **phân số 0–1**, còn các KPI cũ dùng `late_rate_pct` 0–100. `format_percent` của dashboard **không** tự nhân 100. Truyền thẳng `rate` vào sẽ hiện "0,08%" thay vì "8,11%". Tab phải nhân 100 trước khi định dạng, và có một test khẳng định đúng con số 8,11.
