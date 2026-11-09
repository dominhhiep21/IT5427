# CI/CD Pipeline — u4-record-linkage

Nguồn: `nfr-design/security-design.md`, `nfr-design/logical-components.md`, `nfr-requirements/security-requirements.md`, `nfr-requirements/tech-stack-decisions.md` (TS-U4-6), `nfr-requirements/performance-requirements.md`, `functional-design/functional-spec.md`, `inception/contract-design/contract-summary.md` (C5), `inception/domain-design/components.md` (khối `RecordLinkage` mà đơn vị này hiện thực).

Đơn vị: `u4-record-linkage`. **Kết luận: đơn vị này không cần hạ tầng mới.** Nó là một gói thư viện chạy trong tiến trình pipeline đã có; không thêm dịch vụ, cổng, biến môi trường, gói phụ thuộc hay môi trường triển khai. Vì vậy tài liệu này chỉ nói phần thay đổi so với đường ống đã chốt ở `u1-thin-slice/infrastructure-design/cicd-pipeline.md`, và giữ nguyên mọi cổng đã có.

## 1. Cổng giữ nguyên, không thêm bước CI mới

| Cổng | Lệnh | Đạt khi | Thay đổi so với u1 |
|---|---|---|---|
| Lint | `ruff check .` | 0 vi phạm | Không |
| Định dạng | `ruff format --check src/integration tests/unit/test_integration_*.py tests/unit/test_log_pruning.py` | 0 tệp cần sửa | **Có — phải sửa `.github/workflows/ci.yml`**: dòng 33 đang liệt kê cứng phạm vi của u1, nên mã mới ở `src/linkage/` và test mới dưới `tests/unit/` sẽ **không** được kiểm định dạng. Thêm `src/linkage` và các tệp test của đơn vị này vào cùng lệnh, trong cùng thay đổi tạo mã |
| Pipeline | `python -X utf8 -m src.pipeline run --stage all` | Mã thoát 0; `QualityGate` + `KpiReconciler` xanh | **Có**: trong lần chạy này, pipeline gọi thêm bước ghép bản ghi (L5 ở `logical-components.md`) |
| Test nhanh | `python -X utf8 -m pytest -m "not slow"` | Xanh | Không (có thêm test của đơn vị) |
| Độ phủ | `python -X utf8 -m pytest --cov=src --cov-fail-under=80` | ≥ 80% | Không — chạy ở local trước phát hành, như u1 đã chốt |
| Kiểm bằng mắt | Mở `data/integration/linkage-customer.json`, đối chiếu vài cặp với nguồn | Tệp đọc được, `summary` khớp `len(pairs)` | Không — vẫn là bước cần người |
| Bộ chậm | `python -X utf8 -m pytest -m slow` | Xanh | Chỉ chạy ở lần xác nhận trước phát hành, như đã chốt |

Không thêm bước CI riêng cho ghép bản ghi: nó nằm trong `--stage all`, và một bước CI gọi riêng sẽ chạy đúng phép tính đó lần thứ hai. Nhưng **phạm vi định dạng trong `ci.yml` phải được mở rộng** — đó là thay đổi tệp CI duy nhất của đơn vị này.

## 2. Ảnh hưởng thời gian CI

| Hạng mục | Số đo / ước tính | Nguồn |
|---|---|---|
| Chấm điểm 806.705 cặp khách | ≈ 8,1 giây (10,0 µs mỗi cặp, đo trên 20.000 cặp city thật) | đo của reviewer ở bước NFR Design |
| Dựng chỉ mục từ 4 bảng nguồn | ≈ 1–2 giây (đọc CSV đã có trong bộ nhớ pipeline) | ước tính, sẽ đo ở Build and Test |
| Tổng thêm vào `--stage all` | **dưới 15 giây** (phần đã đo 8,1 giây; phần chỉ mục và bằng chứng thanh toán chưa đo) | tổng hai dòng trên, phần chưa đo ghi rõ |
| Ngân sách NFR1.1 | ≤ 60 giây | `performance-requirements.md` |

**Chưa đo tổng thời gian CI sau khi thêm đơn vị này.** Điều đã biết: phần so chuỗi city đo được 8,1 giây cho 806.705 cặp; phần dựng chỉ mục và tính Jaccard chưa đo. Job CI hiện tại chạy 3–5 phút, nên mục tiêu "dưới 5 phút" là **mục tiêu cần kiểm ở lần chạy CI đầu tiên**, không phải kết luận — nếu vượt, ghi vào `CHANGELOG.md` và xem lại `runs-on` hoặc cache.

## 3. Tệp sinh ra, cấu hình và vòng đời

**Một thay đổi cấu hình là cần thiết:** `config.yaml` `paths:` chưa có thư mục cho `data/integration` và `AppConfig` chưa có trường tương ứng, trong khi SR-U4-4 đòi đường dẫn ghi phải là hằng số lấy từ cấu hình. Quyết định: **thêm `paths.integration_dir: data/integration`** vào `config.yaml`, một trường `integration_dir` vào `AppConfig` **và một dòng trong `load_config`** để đọc khoá đó (cùng kiểu `_resolve` như các đường dẫn khác) — thay đổi cộng thêm, dùng chung với U6 (bên đọc cùng thư mục), không hardcode đường dẫn trong mã.

| Tệp | Sinh bởi | Commit? | Xoá/khôi phục |
|---|---|---|---|
| `data/integration/linkage-customer.json` | L3 trong `--stage all` và sau `run_stage("integrate")` | Không (`data/` bị `.gitignore`) | Xoá rồi chạy lại `--stage all` |
| `data/integration/linkage-seller.json` | như trên | Không | Như trên |
| `data/.tmp/<run_id>/` (bản tạm của `AtomicWriter`) | mọi lần ghi | Không | **Phải xoá cùng** — `write_json` để lại bản đầy đủ ở đây nếu lần chạy hỏng trước `os.replace` |
| `logs/<run_id>.jsonl` | nhật ký chung | Không | Giữ 10 tệp gần nhất (đã chốt ở u1) |

Không có bảng cơ sở dữ liệu nào để migrate: toàn bộ đầu ra là tệp dẫn xuất từ `dataset/`.

## 4. Phát hành và quay lui

- Đơn vị **không có tag riêng**: mốc phát hành là tag `v0.x` của cả đợt (Q1 = C đã chốt ở u1), và `CHANGELOG.md` có một dòng cho phần ghép bản ghi.
- Quay lui = `git checkout <tag trước>` → xoá `data/integration/`, `data/.tmp/` → chạy lại `--stage all`. Không có trạng thái nào cần đảo ngược.
- Lưu ý: `run_stage("integrate")` (lệnh runbook dùng sau khi chuyển thư mục repo) **cũng** sinh lại hai tệp kết quả, nên sau lệnh đó tệp khớp mart mới — không cần chạy thêm gì.
- Nếu bước ghép lỗi trong CI, pipeline đỏ và CI đỏ: sửa hoặc quay lui, không bỏ qua bước.

## 5. Bí mật

Không có. Workflow không khai `secrets.*`; đơn vị không đọc biến môi trường (SR-U4-2). Nếu sau này cần, phải vào GitHub Secrets và ghi lý do vào `security-design.md` trước.

## 6. Điều không dựng

| Không dựng | Vì sao |
|---|---|
| Dịch vụ/tiến trình riêng cho ghép bản ghi | Chạy trong tiến trình pipeline; một tiến trình cho một phép tính 8 giây là hạ tầng thừa |
| Bộ nhớ đệm kết quả ghép giữa các lần chạy | Kết quả phụ thuộc toàn bộ nguồn; cache sẽ phục vụ số liệu cũ |
| Bảng lưu kết quả trong `warehouse/` | C5 chốt giao qua tệp JSON; thêm bảng là đổi hợp đồng |
| Bước CI riêng | Trùng với `--stage all` |
| Biến môi trường cho ngưỡng/trọng số | Ngưỡng là hằng số theo BR4.6; biến môi trường sẽ tạo đường đổi ngưỡng ngoài quy trình |

## 7. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Bộ nhớ của runner CI đủ cho chỉ mục cộng 806.705 cặp | Giả định — ước tính dưới 400 MB; `windows-2022` có 7 GB |
| A2 | Thời gian thêm vào CI dưới 15 giây | Chưa đo; đo ở lần chạy CI đầu tiên, ghi vào `CHANGELOG.md` nếu vượt |
| Q1 | Có cần đưa `data/integration/` vào `.gitignore` một cách tường minh không? `data/` đã bị bỏ qua | Không chặn — `data/` đã bị `.gitignore`; thêm dòng riêng là thừa |
