# Reverse Engineering Timestamp

## Run Record

- Date: 2026-11-05
- Commit: 41c422ffd7f3b27a2f78a67eaccc43a00d13c77e (`main`, "Remove aidlc v1")
- Repo: `Tich-hop-va-xu-li-du-lieu-lon` (workspace root, single-repo intent)
- Intent: `doc-knowledge-upgrade` — nâng cấp hệ thống Olist để thể hiện bốn nhóm kiến thức tích hợp
  dữ liệu (`doc/`) và thêm tab "Tích hợp"
- Depth: Standard · Test strategy: Standard · Scan breadth: FULL (`./`)
- Snapshot paths: `["./"]`
- Phương pháp: chỉ đọc mã và tài liệu; **không** chạy test, build hay chương trình của dự án.

### Tóm tắt lần quét

| Hạng mục | Kết quả |
|---|---|
| Tệp Python trong `src/` | 55 tệp, ~4.200 dòng |
| Tệp test | 25 mô-đun, 47 hàm test (6 hàm `slow`), `conftest.py` 320 dòng |
| Tài liệu đọc sâu | `README.md`, `AGENTS.md`, `docs/*` (3 tệp), `config.yaml`, `requirements.txt`, `pytest.ini`, `.gitignore` |
| Dữ liệu tham chiếu đọc sâu | `dataset/external/ibge/estados.json` (27 bang), `metadata.json` |
| Không mở | 9 CSV trong `dataset/`, PDF và quiz trong `doc/`, sản phẩm sinh ra (`data/`, `warehouse/`, `logs/`, `inbox/`) |
| Artifact tạo ra | 9 tệp CodeKB tại thư mục staging của intent (chưa công bố) + `developer-scan.md` |

### Ghi chú về phạm vi

- `kind: partial` vì lần quét **không** đọc nội dung 9 CSV nguồn (chỉ mô tả bố cục từ
  `src/ingest/schemas.py`, `AGENTS.md`, `docs/3v.md`) và không mở học liệu PDF trong `doc/`.
- Mọi kết luận về dữ liệu (số dòng, dị thường, grain) dựa trên hằng số trong mã và tài liệu dự án,
  không dựa trên việc chạy phân tích dữ liệu trong lần quét này.
- AI-DLC's own install (`.aidlc/`, `aidlc/`, `.opencode/`) không được quét và không nằm trong fingerprint.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: doc-knowledge-upgrade
fingerprint: 9b3ef37b940007e43054ef6c756296f70f6aad00
analyzed:
  paths:
    - src/
    - tests/
    - docs/
    - assets/style.css
    - config.yaml
    - requirements.txt
    - pytest.ini
    - README.md
    - AGENTS.md
    - .gitignore
    - dataset/external/ibge/
  components:
    - src.config
    - src.common
    - src.ingest
    - src.clean
    - src.quality
    - src.external
    - src.integrate
    - src.analytics
    - src.dashboard
    - src.pipeline
    - tests
    - docs
    - assets
shallow:
  paths:
    - dataset/
    - doc/
```
