# Câu hỏi — Requirements Analysis

## Q1. AUC của mô hình cây có đi vào `analysis.json` không

Đã chốt ở Rough Mockups: con số đó **không** hiện trên tab, phải có trong record. Nhưng `analysis.json` là hợp đồng giữa các tầng — thêm một trường là đổi phiên bản hợp đồng (hiện `REPORT_VERSION = 2`).

- A. Thêm vào `analysis.json` → `REPORT_VERSION = 3`, khối `model` mang `auc` (logistic) và `auc_tree`; tab vẫn chỉ hiện một AUC
- B. Không đổi hợp đồng; AUC của cây chỉ nằm trong `code-summary.md` và record
- C. Thêm nhưng ở khối riêng `experiments`, không đụng khối `model`
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Mốc sàn 0,55 nằm ở đâu

- A. Một test đơn vị đọc `analysis.json` và khẳng định `auc ≥ 0,55` — chạy trong bộ nhanh, đỏ ngay khi mô hình thoái hoá
- B. Một kiểm tra trong tầng `stats`: AUC dưới 0,55 thì dừng và không ghi báo cáo
- C. Một bước riêng trong CI, không phải test
- D. Chưa xác định — để Functional Design
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Hai câu đã trả lời. Bản tóm tắt:

- **Hợp đồng báo cáo** [Q1 = A]: thêm `auc_tree` vào khối `model` của `analysis.json`, nâng `REPORT_VERSION` lên **3**; tab vẫn chỉ hiện **một** AUC (của logistic). Đọc tệp phiên bản 2 phải chịu được, không ném.
- **Mốc sàn 0,55** [Q2 = A]: một **test đơn vị** đọc `analysis.json` và khẳng định `auc ≥ 0,55`, chạy trong bộ nhanh. Tầng `stats` **không** dừng khi AUC thấp — nó vẫn ghi báo cáo, và test mới là thứ đỏ.
- **Hệ quả của Q2 = A:** một lần chạy `--stage stats` với mô hình 0,3 vẫn sinh báo cáo và dashboard vẫn hiển thị; cái chặn là CI. Đây là đánh đổi có chủ đích: giữ được khả năng thử một cấu hình kém mà không phá chuỗi bốn bước.
- **Sẽ sinh**: `requirements.md` (FR1 dữ liệu, FR2 mô hình, FR3 giao diện, NFR1–NFR6) và `traceability.json`.

- Looks correct
- Request changes

[Answer]: Looks correct
