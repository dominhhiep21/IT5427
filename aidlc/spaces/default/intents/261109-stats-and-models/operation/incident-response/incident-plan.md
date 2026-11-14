# Incident Plan

Nguồn: `runbooks.md`, `../observability-setup/alarms.md`, `aidlc/spaces/default/memory/phases/operation.md` (`## Incident Response`).

## Không có on-call, nên định nghĩa "sự cố" phải khác

Một sự cố thường được định nghĩa bằng tác động lên người dùng và đo bằng MTTD/MTTR. Ở đây người dùng là người chạy, nên họ phát hiện tức thì và họ là người sửa. Không có ca trực, không có thời gian phát hiện.

## Phân loại dùng thật

| Mức | Nghĩa | Ví dụ | Ai xử |
|---|---|---|---|
| **P1** | Kết quả sai mà không ai biết | baseline KPI lệch, báo cáo ghi sai số | người làm, ngay |
| **P2** | Không chạy được | `--stage all` hỏng, tab `loi` | người làm, ngay |
| **P3** | Chạy được nhưng kém | AUC tụt, một phép kiểm định bị bỏ | người làm, khi có thời gian |

Điểm quan trọng: **P1 không phải "hệ thống sập" mà là "hệ thống nói sai"**. Với một dự án phân tích, số sai tệ hơn số thiếu — số thiếu thì người đọc biết, số sai thì không.

## Quy trình ba bước

1. **Dừng.** Không chạy tiếp để "xem còn gì nữa" — kết quả sau đó đo trên dữ liệu chưa đúng.
2. **Đọc tín hiệu.** Exit code nói bước nào; nhật ký nói vì sao; tab nói trạng thái tệp.
3. **Tra runbook.** `runbooks.md` có bảy mục; nếu không khớp mục nào thì đó là sự cố mới và phải viết mục thứ tám.

## Sau sự cố

Không có postmortem chính thức vì không có tổ chức để chia sẻ. Nhưng có một bước bắt buộc: **nếu sự cố lặp lại được, thêm một test hoặc một mục runbook**. Một sự cố không để lại gì là một sự cố sẽ tái diễn.

Ba sự cố trong đợt này đã để lại thứ cụ thể: `test_ci_config.py` canh danh sách khai tay, `test_pipeline_stages.py` canh hai nơi khai tầng, và `test_analysis_tab_contrast.py` canh tương phản.

## Điều không có

Không có kênh thông báo, không có cầu nối, không có người trực thứ hai. Không có ai để leo thang tới.
