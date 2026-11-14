# Câu hỏi — Units Generation

Ba đơn vị U1/U2/U3 đã được chốt từ scope-definition và approval-handoff, nên câu hỏi ở đây không hỏi lại việc chia đơn vị. Chúng hỏi ba chỗ mà thiết kế chưa tự quyết: **loại** từng đơn vị, **ranh giới U1/U2** ở chỗ phép đo baseline, và **cho phép song song** hay không.

## Q1. Loại (`kind`) của từng đơn vị là gì?

`kind` quyết định đơn vị phải mang theo bộ tài liệu thiết kế nào vào Construction: `service` là tiến trình chạy được, `ui` là bề mặt giao diện, `library` là mã dùng lại không có runtime riêng, `spec` là hợp đồng/schema dùng tại chỗ, `packaging` là artefact đóng gói.

- A. **U1 = `library`, U2 = `library`, U3 = `ui`** — đúng bản chất: hai đơn vị đầu là mã thư viện trong cùng tiến trình, đơn vị ba là bề mặt giao diện nên phải mang tài liệu thiết kế giao diện
- B. **Cả ba = `library`** — coi tab phân tích là mã thư viện như phần còn lại; gọn hơn nhưng bỏ mất phần thiết kế giao diện của U3
- C. **U1 = `library`, U2 = `service`, U3 = `ui`** — coi tầng mô hình là "dịch vụ" vì nó sinh ra tệp mô hình; không đúng: không có tiến trình riêng nào
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Ranh giới U1/U2 nằm ở đâu với phép đo baseline?

`FR1.4` đã chốt bộ số baseline mới **được thay ở U2, không phải U1**, vì `delivered_population` còn ở grain đơn cho tới khi `TRAINING_FRAME_SQL` đổi. Nhưng `ModelModule` lại sở hữu `BaselineMeasurement` và `beats_baseline`.

- A. **U1 chỉ giao mart + `CohortCounts` + hàm đo baseline (chưa ghi vào báo cáo); U2 mới nối `baseline_auc`/`beats_baseline` vào `analysis.json` v3** — giữ đúng `FR1.4`, mỗi đơn vị tự xanh trên dữ liệu thật của mình
- B. **U1 giao luôn `baseline_auc` và ghi báo cáo v3 sớm** — sớm thấy con số baseline, nhưng phải nâng phiên bản báo cáo ở U1 trong khi khối `model` mới chỉ có một phần, và `FR1.4` nói ngược lại
- C. **Tách phép đo baseline thành đơn vị thứ tư** — rõ ràng nhất về trách nhiệm, nhưng thêm một đơn vị và một vòng xác nhận cho một hàm thuần
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q3. U3 có được làm song song với U2 không?

`unit-of-work-dependency.md` chỉ mô tả thứ tự phụ thuộc; việc chọn đường đi kinh tế thuộc Delivery Planning. Nhưng DAG phải khai đúng: U3 có thật sự **cần** U2 xong mới bắt đầu được không?

- A. **Chuỗi thẳng `U1 → U2 → U3`** — U3 cần tệp mô hình và báo cáo v3 đã có để nối số; làm sau thì không phải làm lại
- B. **Cho U3 khởi động song song phần khung tĩnh** (mục thứ tư, CSS, sáu trạng thái) và chỉ chờ U2 ở phần nối số — nhanh hơn, nhưng DAG phải khai cạnh mềm và U3 có hai chặng
- C. **U3 độc lập hoàn toàn** — sai: không có báo cáo v3 và tệp mô hình thì vùng dự đoán không có gì để đọc
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Ba câu đã trả lời, và mô hình đơn vị mà chúng tạo ra:

- **Loại** [Q1 = A]: `U1 = library`, `U2 = library`, `U3 = ui`. Hai đơn vị đầu là mã thư viện trong cùng tiến trình; đơn vị ba là bề mặt giao diện nên mang theo bộ tài liệu thiết kế giao diện vào Construction.
- **Ranh giới U1/U2** [Q2 = A]: U1 giao **mart mở rộng + `CohortCounts` + hàm đo baseline** (hàm thuần, chưa ghi vào báo cáo). U2 mới nối `baseline_auc` và `beats_baseline` vào `analysis.json` v3, cùng lúc với khung huấn luyện grain dòng hàng — đúng `FR1.4` ("bộ số baseline mới thay ở U2"), nên không có đơn vị nào ghi baseline bằng khung cũ.
- **DAG** [Q3 = A]: chuỗi thẳng `u1-… → u2-… → u3-…`; U3 cần cả báo cáo v3 và tệp mô hình nên khai cạnh thật, không cạnh mềm.
- **Ba đơn vị, không thêm đơn vị thứ tư**: phép đo baseline nằm trong U1 dưới dạng hàm, phần nối vào hợp đồng nằm ở U2.
- **Mô hình triển khai**: một tiến trình duy nhất, không tách đơn vị triển khai — đúng hiện trạng repo (không có Docker/cloud/scheduler), nên không đơn vị nào là "standalone" theo nghĩa triển khai.

- Looks correct
- Request changes

[Answer]: Looks correct
