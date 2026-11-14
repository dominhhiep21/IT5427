# Rules — u2-model

Nguồn: `../../../inception/requirements-analysis/requirements.md` (FR2.1–FR2.4), `../../../inception/contract-design/contract-summary.md` (C1, C3), `functional-design-questions.md`, và `entities.md`.

`category` chỉ dùng năm giá trị: `validation`, `authorization`, `constraint`, `calculation`, `policy`. `source` chỉ trỏ tới FR/NFR; quyết định từ câu hỏi thiết kế nằm ở `decided_by`.

```yaml
rules:
  - id: BR2.1
    category: validation
    statement: Quần thể huấn luyện chỉ gồm đơn đã giao, lọc tường minh
    applies_to: TrainingFrame
    trigger: Khi dựng bảng đặc trưng
    logic: "IF is_delivered = true THEN giữ dòng; ELSE loại. `is_late` của mart không null ở cả đơn chưa giao, nên lọc theo 'có nhãn' sẽ kéo 2.963 đơn chưa giao vào tập huấn luyện với nhãn sai. Cỡ mẫu kỳ vọng là 96.478 đơn và 7.826 đơn trễ."
    violation: "Cỡ mẫu khác 96.478 thì dừng: đã lọc sai quần thể"
    source: FR2.2

  - id: BR2.2
    category: calculation
    statement: Chia tập theo thời gian, tập huấn luyện đứng trước tập kiểm tra, không xáo trộn
    applies_to: TrainingFrame.split
    trigger: Sau BR2.1
    logic: "IF chọn mốc cắt THEN mọi đơn có ngày đặt TRƯỚC 2018-04-01 vào tập huấn luyện, từ 2018-04-01 trở đi vào tập kiểm tra (đơn rơi đúng ngày cắt thuộc tập kiểm tra, để không mất mẫu); không lấy mẫu ngẫu nhiên; ghi train_start, train_end, test_start, test_end, train_n, test_n; kiểm train_n + test_n = 96.478"
    violation: "Nếu một trong hai tập rỗng, hoặc tổng hai cỡ mẫu khác 96.478, thì dừng và không ghi khối mô hình"
    source: FR2.2

  - id: BR2.3
    category: validation
    statement: Danh sách đặc trưng là danh sách cột cụ thể, không chứa thông tin chỉ có sau khi giao
    applies_to: TrainingFrame.features
    trigger: Khi dựng bảng đặc trưng
    logic: "IF cột nằm trong tập cấm THEN loại; danh sách cuối cùng là hằng số có tên trong mã, gồm đúng 11 cột: 9 cột ở entities.md § Danh sách đặc trưng, cộng has_items và has_payment (hai cờ sẵn có trong mart, dùng cho TS-8)"
    violation: "Không huấn luyện nếu danh sách còn cột bị cấm; đây là rò rỉ nhãn, không phải một lựa chọn"
    source: FR2.1

  - id: BR2.4
    category: calculation
    statement: Huấn luyện với trọng số lớp cân bằng ở mức thuật toán
    applies_to: Bước huấn luyện
    trigger: Khi gọi huấn luyện
    logic: "IF huấn luyện THEN bật cân trọng số theo tần suất lớp (với scikit-learn là class_weight='balanced'); không lấy mẫu lại, không đổi dữ liệu"
    violation: "Không huấn luyện khi chưa cân trọng số"
    source: FR2.1
    decided_by: Q3 (Functional Design)

  - id: BR2.5
    category: calculation
    statement: Ngưỡng cảnh báo là ngưỡng làm F1 cao nhất trên tập kiểm tra, xét trên một lưới ngưỡng xác định
    applies_to: ModelBlock.threshold và ModelBlock.counts.threshold_method
    trigger: Sau khi có điểm số dự đoán trên tập kiểm tra
    logic: "IF duyệt lưới THEN lưới là 0.05, 0.10, …, 0.95 (bước 0.05, 19 điểm); với mỗi ngưỡng tính precision, recall, f1; chọn ngưỡng có f1 lớn nhất; hoà thì chọn ngưỡng cao hơn; threshold_method = 'max_f1_on_test_grid005'"
    violation: "Không chọn được ngưỡng (một lớp vắng mặt ở tập kiểm tra) thì dừng và không ghi khối mô hình"
    source: FR2.4
    decided_by: Q2 (Functional Design)

  - id: BR2.6
    category: validation
    statement: AUC dưới 0,70 được ghi rõ là không đạt, không ẩn đi
    applies_to: ModelBlock.counts.auc_below_target
    trigger: Sau khi tính AUC trên tập kiểm tra
    logic: "IF auc < 0.70 THEN auc_below_target = true; ELSE auc_below_target = false"
    violation: "Không được bỏ trường này khỏi báo cáo, kể cả khi đạt"
    source: FR2.3

  - id: BR2.7
    category: constraint
    statement: Số đếm trên tập kiểm tra khớp nhau và khớp cỡ mẫu
    applies_to: ModelBlock.counts
    trigger: Trước khi ghi khối mô hình
    logic: "IF flagged + not_flagged != total OR total != split.test_n THEN dừng, không ghi"
    violation: "Ba con số lệch nhau là báo cáo sai, không phải báo cáo gần đúng"
    source: FR2.4

  - id: BR2.8
    category: policy
    statement: Model-module trả khối ModelBlock cho tầng stats; việc ghép vào tệp báo cáo thuộc tầng stats của U1
    applies_to: ModelBlock — ranh giới giao cho U1
    trigger: Cuối bước mô hình
    logic: "IF bước mô hình xong THEN trả ModelBlock; tầng `stats` của U1 đọc tệp cũ, giữ khối stats và gọi write_report. U2 không đọc và không ghi data/reports/analysis.json"
    violation: "Không được để model-module mở tệp báo cáo; làm vậy là vượt ranh giới mà components.md và unit-of-work.md đã chốt"
    source: FR3.1

  - id: BR2.9
    category: calculation
    statement: Số thực trong khối mô hình được làm tròn khi ghi — AUC, ngưỡng, precision, recall 4 chữ số — và ngưỡng đã làm tròn vẫn nằm trong (0, 1)
    applies_to: Mọi trường số thực của ModelBlock
    trigger: Trước khi ghi tệp
    logic: "round(auc, 4); round(threshold, 4); round(precision, 4); round(recall, 4); IF không còn 0 < threshold < 1 sau khi làm tròn THEN dừng"
    violation: "Không làm tròn thì không ghi; ngưỡng tròn thành 0 hoặc 1 là lỗi, không phải giá trị hợp lệ"
    source: FR2.4
```

## Tóm tắt quy tắc

| Mã | Loại | Một dòng |
|---|---|---|
| BR2.1 | validation | Chỉ đơn đã giao, lọc tường minh; kỳ vọng 96.478/7.826 |
| BR2.2 | calculation | Chia theo thời gian, không xáo trộn |
| BR2.3 | validation | Danh sách cột cụ thể, không cột nào có sau khi giao |
| BR2.4 | calculation | Cân trọng số lớp, không lấy mẫu lại |
| BR2.5 | calculation | Ngưỡng = F1 cao nhất trên lưới 19 điểm |
| BR2.6 | validation | AUC dưới 0,70 được ghi rõ |
| BR2.7 | constraint | Ba con số đếm khớp nhau |
| BR2.8 | policy | Giữ khối thống kê khi ghi; mô hình chạy sau U1 |
| BR2.9 | calculation | Làm tròn 4 chữ số, ngưỡng vẫn trong (0,1) |

## Kiểm tra ràng buộc

| Mã | Kiểm bằng | Ở đâu |
|---|---|---|
| BR2.1 | Mọi dòng huấn luyện có `is_delivered = true`; cỡ mẫu 96.478; số trễ 7.826 | Test `slow` trên dữ liệu thật |
| BR2.2 | `train_end < test_start`; không dòng nào nằm cả hai tập | Test đơn vị |
| BR2.3 | Danh sách đặc trưng không giao với tập cột bị cấm | Test đơn vị đọc hằng số |
| BR2.4 | Tham số cân trọng số được truyền | Test đơn vị |
| BR2.5 | Với bộ điểm số dựng sẵn, ngưỡng chọn đúng là điểm trên lưới có F1 lớn nhất | Test đơn vị |
| BR2.6 | AUC 0,69 → `true`; 0,70 → `false` | Test đơn vị |
| BR2.7 | Ba con số lệch nhau thì có ngoại lệ | Test đơn vị |
| BR2.8 | Chạy mô hình trên tệp có sẵn khối thống kê thì khối đó còn nguyên | Test đơn vị với thư mục tạm |
| BR2.9 | Số trong tệp ghi ra có đúng 4 chữ số; ngưỡng sau làm tròn vẫn trong (0,1) | Test đơn vị |
