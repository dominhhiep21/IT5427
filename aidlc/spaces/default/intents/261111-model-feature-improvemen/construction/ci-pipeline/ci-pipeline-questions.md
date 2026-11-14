# CI Pipeline — Câu hỏi

> **Trạng thái:** người làm yêu cầu tiếp tục mà không chọn phương án. Bốn câu dưới đây đang được
> **tạm áp dụng phương án A (đề xuất)** để stage không bị chặn; đây **không** phải câu trả lời của
> người làm. Đổi được ở cổng duyệt của stage, hoặc sửa `[Answer]:` rồi nhắn lại.

Bốn câu, mỗi câu có một phương án **đề xuất** dựa trên bằng chứng trong repo. Nếu đồng ý cả bốn, trả lời **"1"** (hoặc điền `[Answer]: A` cho từng câu rồi nhắn "Xong").

---

## Q1 — Công cụ CI

Hiện repo dùng **GitHub Actions** (`.github/workflows/ci.yml`, 9 step, chạy xanh trên `windows-2022`).

- **A. Giữ GitHub Actions** *(đề xuất)* — không đổi hạ tầng, không có yêu cầu nào đòi đổi.
- B. Chuyển sang công cụ khác (Jenkins/CodeBuild/GitLab) — cần lý do và một đợt riêng.
- C. Khác: …

`[Answer]:`

---

## Q2 — Chiến lược nhánh

`team.md` ghi: một người làm, một nhánh dài hơi của đợt (`feature/analysis-and-models`), không review chéo, CI là cổng duy nhất.

- **A. Giữ nguyên: nhánh dài hơi, hợp nhất một lần khi CI xanh** *(đề xuất)* — đúng thực hành đã chốt.
- B. Chuyển sang nhánh ngắn hạn + pull request bắt buộc — cần người thứ hai review, hiện không có.
- C. Khác: …

`[Answer]:`

---

## Q3 — Cổng chất lượng trước khi hợp nhất

Tám cổng đang chạy: `ruff check`, `ruff format --check` (50 mục), `--stage all`, `--stage stats`, bộ nhanh 708 test, phủ **≥ 80%** trên toàn bộ bộ test (đo 92,71%), smoke cấu hình, và mốc sàn mô hình (test `slow`).

- **A. Giữ đúng tám cổng này, không thêm** *(đề xuất)* — đã phủ lint, dữ liệu, test, phủ, cấu hình, chất lượng mô hình.
- B. Thêm cổng mới (nêu rõ: quét phụ thuộc? kiểm tra kiểu tĩnh? chạy trên Linux?) — mỗi cái là thay đổi phạm vi.
- C. Bớt một cổng (nêu rõ cổng nào và vì sao) — sẽ phải sửa luật `team.md`, không nên làm ngầm.
- D. Khác: …

`[Answer]:`

---

## Q4 — Kho artefact / versioning

Repo **không** có ECR/CodeArtifact/S3; artefact dữ liệu (`data/`, `warehouse/`, `data/models/`) bị `.gitignore` và mỗi máy sinh lại. Version = commit hash + mốc `CHANGELOG.md` (nay `v0.5.0`).

- **A. Giữ nguyên: không kho artefact, không git tag** *(đề xuất)* — đúng mô hình "phát hành = chạy từ mã nguồn".
- B. Thêm git tag cho mỗi mốc `CHANGELOG` — rẻ, nhưng cần một quy ước đánh số.
- C. Thêm kho artefact (S3/ECR) — chỉ có nghĩa nếu sau này có môi trường triển khai.
- D. Khác: …

`[Answer]:`
