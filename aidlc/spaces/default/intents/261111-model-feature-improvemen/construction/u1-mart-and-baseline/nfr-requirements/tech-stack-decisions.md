# Tech Stack Decisions — u1-mart-and-baseline

Đơn vị: `u1-mart-and-baseline`. Nguồn: `functional-spec.md`, `../../../inception/contract-design/contract-summary.md` (C1), `aidlc/spaces/default/codekb/Tich-hop-va-xu-li-du-lieu-lon/technology-stack.md`, `requirements.txt`, `ruff.toml`.

**Kết luận ngắn: đơn vị này không chọn công nghệ mới nào.** Ba cột thêm vào mart và một hàm đo baseline đều nằm trong ngăn xếp đã có. Tài liệu này ghi lại *vì sao* không cần gì mới — vì "không thêm gì" cũng là một quyết định phải bảo vệ được.

## Ngăn xếp đang dùng, và chỗ đơn vị này chạm vào

| Lớp | Công nghệ | Phiên bản | Đơn vị này dùng để |
|---|---|---|---|
| Ngôn ngữ | Python | 3.13 | toàn bộ |
| Xử lý dữ liệu | `pandas` | 2.2.3 | dựng cột, nối `dim_seller`, chia tập cho baseline |
| Kho phân tích | `duckdb` | đã ghim | mart và 11 view; đơn vị này không đổi câu SQL nào |
| Định dạng trung gian | Parquet (qua `pyarrow`) | đã ghim | mart ghi ra `data/marts/` |
| Học máy | `scikit-learn` | đã ghim | baseline một đặc trưng (một bộ ước lượng logistic) |
| Đo khoảng tin cậy | `scipy` | đã ghim | không dùng ở đơn vị này; dùng ở tầng thống kê |
| Lint/format | `ruff` | đã ghim | `ruff check .`, `ruff format --check` |
| Kiểm thử | `pytest` + `pytest-cov` | đã ghim | test đơn vị + `slow` |

## TS-U1.1 — Không thêm phụ thuộc nào

**Quyết định:** đơn vị này không thêm gói nào vào `requirements.txt`.

**Vì sao:** cả ba việc đều nằm trong thư viện đã có. Nối hai `DataFrame` là `pandas`; huấn luyện một bộ logistic là `scikit-learn`; đếm dòng là `pandas`. Thêm gói mới cho những việc này là thêm bề mặt bảo trì mà không đổi năng lực.

**Ràng buộc:** `project.md` `## Forbidden` cấm import bất kỳ thư viện bên thứ ba chưa ghim — kể cả `numpy`, vốn chỉ có mặt gián tiếp qua `pandas`. Mã mới của đơn vị này không được `import numpy` trực tiếp.

**Kiểm:** `requirements.txt` vẫn đúng 12 gói; test đơn vị khẳng định số gói và danh sách tên.

## TS-U1.2 — Baseline là logistic một đặc trưng, không phải một mô hình mới

**Quyết định:** baseline dùng `LogisticRegression` của `scikit-learn` với **một** đặc trưng phân loại one-hot, không chuẩn hoá.

**Vì sao không dùng cây hay mô hình khác cho baseline:** baseline phải là **mốc so sánh đơn giản nhất có nghĩa** — "nếu chỉ biết bang của khách thì đoán được bao nhiêu". Một baseline mạnh hơn sẽ làm mô hình triển khai trông tệ hơn thực tế, và làm phép so mất tính bảo thủ. Câu hỏi baseline trả lời là "mô hình có vượt được thứ ngớ ngẩn nhất không", không phải "mô hình có vượt được một mô hình khá không".

**Kiểm:** test đơn vị khẳng định ma trận đặc trưng của baseline có đúng một trường nguồn, và không có cột chuẩn hoá.

## TS-U1.3 — Giữ DuckDB + Parquet, không chuyển sang định dạng khác

**Quyết định:** mart vẫn là Parquet trên đĩa, đọc qua view DuckDB.

**Vì sao không đổi:** đổi định dạng lưu mart là thay đổi chạm 11 view, 9 bảng, toàn bộ test tích hợp và `StarSchemaValidator` — cho một đơn vị mà mục tiêu là *thêm ba cột*. Rủi ro lớn hơn lợi ích rất nhiều.

**Hệ quả phải biết:** view DuckDB chứa **đường dẫn tuyệt đối** vào Parquet (`docs/runbook.md`), nên chuyển thư mục repo hoặc dùng worktree khác phải chạy lại `integrate`. Điều này đã đúng trước đơn vị này và không đổi.

## TS-U1.4 — Kiểm kiểu tĩnh: vẫn không có

**Quyết định:** không thêm `mypy`/`pyright`.

**Vì sao:** đây là quyết định đã chốt của dự án (`project.md` `## Forbidden`), không phải thiếu sót. Type hint vẫn giữ theo quy ước hiện có (`from __future__ import annotations`, `list[str]`, `Path | None`) nhưng không phải cổng.

**Kiểm:** `requirements.txt` không có gói kiểm kiểu; `ci.yml` không có bước kiểm kiểu.

## TS-U1.5 — Python 3.13 và UTF-8, không đổi

**Quyết định:** mọi lệnh chạy `python -X utf8`; môi trường là `.venv` của repo.

**Vì sao:** đường dẫn workspace có ký tự tiếng Việt và dữ liệu có ký tự Bồ Đào Nha; thiếu `-X utf8` là `UnicodeEncodeError` khi in. Đây là ràng buộc đã thành luật trong `project.md` `## Mandated`, áp cho cả đơn vị này.

## Điều tài liệu này không quyết

Không quyết phiên bản Python mới hơn, không quyết dịch vụ đám mây, không quyết cơ sở dữ liệu khác. Dự án chạy từ mã nguồn trên máy một người; mọi lựa chọn hạ tầng nằm ngoài phạm vi đợt này.
