# CI/CD Pipeline — u2-model

Nguồn: `../nfr-design/logical-components.md`, `../nfr-design/security-design.md`, `../functional-design/functional-spec.md`, `../../../inception/contract-design/contract-summary.md`, `../../../inception/domain-design/components.md`, `.github/workflows/ci.yml`, `aidlc/spaces/default/memory/project.md` (`## Deployment`).

`components.md` giao `model-module` cho đơn vị này và giao `stats-stage` của U1 làm điểm ghép nối duy nhất — vì vậy U2 không có bước CI riêng, chỉ có thay đổi tệp cấu hình và phụ thuộc.

## Hiện trạng

Không có môi trường triển khai: dự án chạy từ mã nguồn trên máy người làm, GitHub Actions là cổng tự động duy nhất. U1 đã mở đường trong `ci.yml`: thêm nhánh vào cả hai danh sách trigger, thêm tầng `stats` vào hai nơi khai danh sách tầng, và đặt bước `--stage stats` sau `--stage all`.

## Thay đổi đơn vị này cần

| # | Thay đổi | Vì sao | Ai làm |
|---|---|---|---|
| CI-1 | Thêm mọi tệp nguồn mới của U2 vào danh sách `ruff format --check` | Danh sách khai tay; tệp không có trong danh sách thì không ai kiểm định dạng (NFR4.1) | Code Generation, cùng lúc với việc tạo tệp |
| CI-2 | Ghim `scikit-learn==1.6.1` trong `requirements.txt` **trước** khi viết `import sklearn` | CI cài từ tệp đó; thiếu dòng ghim thì bước cài không có gói và test đỏ ngay ở lần chạy đầu | Code Generation, bước đầu tiên |
| CI-3 | Chạy đủ phép kiểm trôi phụ thuộc của `tech-stack-decisions.md` § "Điều còn phải xác nhận khi cài" — không chỉ quan sát: `pip show numpy scipy joblib threadpoolctl`; nếu `numpy` khác 2.2.1 thì **ghim lại `numpy==2.2.1`** kèm lý do, rồi chạy lại toàn bộ bộ `slow` của U1 | `numpy` không được ghim trực tiếp; CI cài lại từ `requirements.txt` trên runner sạch, nên một lần xác nhận trên máy local không bảo đảm gì cho CI, và `scikit-learn` có thể kéo bản `numpy` khác làm lệch số của U1 | Code Generation, ngay sau khi cài, và lặp lại trong CI |
| CI-4 | Không thêm bước CI mới cho mô hình | Bước mô hình chạy **bên trong** tầng `stats` mà U1 đã nối vào CI; thêm bước riêng là chạy hai lần cùng một việc | — |
| CI-5 | Cập nhật `README.md` mục Test và `CHANGELOG.md` cho mốc mô hình | Tài liệu phải khớp hành vi | Code Generation, cùng thay đổi |

## Thứ tự bước và hai cái bẫy

Bước `--stage stats` đã nằm sau `--stage all` và trước bước test. U2 chạy trong chính bước đó, nên **không** đổi thứ tự CI.

- **Bẫy 1 — thời gian.** Bộ test `slow` hiện chạy khoảng 3 phút; huấn luyện mô hình thêm vào đó, và test tái lập còn huấn luyện thêm hai lần. Nếu tổng vượt thời gian chịu đựng của job, cách xử lý là **nới `timeout-minutes` của job** hoặc rút gọn tập kiểm tra của chính test đó — **không** đụng vào lưới ngưỡng. BR2.5 chốt lưới 19 điểm và C3 bắt buộc `threshold_method = "max_f1_on_test_grid005"`; giảm số điểm là đổi ngưỡng, đổi cả bốn chỉ số đã làm tròn, và biến chuỗi metadata thành lời nói dối. Đó cũng đúng là kiểu "hạ ngưỡng để cho một bước pass" mà quy tắc nhóm cấm.
- **Bẫy 2 — bộ nhanh.** Không test nào của U2 được đọc `data/reports/analysis.json` hay `warehouse/olist.duckdb` của repo; test dựng dữ liệu trong `tmp_path`, test cần dữ liệu thật mang marker `slow`. Đây là cùng lỗ hổng `TD-09`, và U2 không được làm nó nặng thêm.

## Không thay đổi

- **Không thêm job, không tách workflow.** Một job đang chạy ổn.
- **Không thêm cổng mới.** Cổng phủ 80% và `ruff` đã đủ.
- **Không có bước deploy.** Không có môi trường để deploy tới.
- **Không lưu mô hình.** Không có tệp mô hình nào để đóng gói hay phân phối.

## Chuỗi xác nhận cục bộ

CI không thay chuỗi bốn bước của nhóm: bộ test nhanh → `--stage all` → `--stage stats` (nay gồm cả mô hình) → mở dashboard.

## Điều phải kiểm khi viết mã

- Một test đọc `ci.yml` và khẳng định mỗi tệp nguồn mới của U2 có mặt trong danh sách `ruff format --check`.
- Một test đọc `requirements.txt` và khẳng định `scikit-learn` có mặt kèm số phiên bản chính xác.
