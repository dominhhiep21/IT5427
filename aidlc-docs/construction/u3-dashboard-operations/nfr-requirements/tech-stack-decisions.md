# Tech Stack Decisions — U3 Dashboard & Operations

## 1. Quyết định

| Thành phần | Lựa chọn | Phiên bản | Lý do |
|---|---|---|---|
| Dashboard | Plotly Dash | Pin khi cài | Python-native, callback đơn giản |
| Chart | Plotly | Pin khi cài | Đi kèm Dash |
| CLI | argparse (stdlib) | 3.13 | Không thêm dependency |
| Data | pandas + DuckDB | Đã cài | Tái sử dụng U1/U2 |
| Test | pytest | 9.1.1 | Đã cài |
| Styling | CSS tokens + `assets/style.css` | — | Không cần Node/npm |
| Server | Dash dev server | — | Chạy localhost |

> Dash/Plotly sẽ được cài trong venv và pin chính xác trong `requirements.txt`.

## 2. Không sử dụng

| Công nghệ | Lý do |
|---|---|
| React/Next.js | Không cần; Dash đủ |
| Node/npm | Không có frontend build |
| Streamlit | Đã chốt Dash |
| Power BI/Tableau | Không chạy cục bộ/không tự động |
| Kafka | Micro-batch mô phỏng bằng thư mục |
| scikit-learn | ML trì hoãn |

## 3. Cấu trúc dashboard

```
src/dashboard/
  __init__.py
  app.py          # create_app, layout, callbacks
  components.py   # KPI card, charts, tables
  formatting.py   # BRL, date, number
assets/
  style.css       # design tokens
```

- `python -m src.dashboard` chạy `app.run(host=127.0.0.1, port=8050)`.
- `assets/` được Dash tự phục vụ.

## 4. Design tokens

```css
:root {
  --ink: #0B1F1A;
  --paper: #F6F7F2;
  --mist: #DCE8E0;
  --ochre: #D9A441;
  --clay: #B5532F;
  --muted: #5B6B63;
  --line: #C9D6CE;
}
```

- Heading: Georgia.
- Body: Segoe UI.
- Số nhỏ: Consolas.
- Không dùng card bo tròn đồng loạt; ưu tiên border mảnh, khoảng trắng.

## 5. CLI

- `src/pipeline/cli.py` + `__main__.py`.
- argparse subcommands: `run`, `micro-batch`, `replay`.
- `src/dashboard/__main__.py` cho dashboard.

## 6. Micro-batch

- `inbox/{batch_id}/{table}.csv`.
- Manifest JSON.
- Upsert cleaned + U2 rebuild.
- Không cần queue/broker.

## 7. Hệ quả

- Cần cài `dash`, `plotly` (và Flask/Werkzeug transitive).
- Không cần Node.
- Dashboard chạy localhost; không deploy cloud.
- Có thể test callback bằng Dash test client hoặc gọi hàm thuần.
