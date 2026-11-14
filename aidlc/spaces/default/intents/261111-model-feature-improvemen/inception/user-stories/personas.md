# Personas

Nguồn: `../user-stories-assessment.md`, `../requirements-analysis/requirements.md`, `../../ideation/intent-capture/stakeholder-map.md`.

## Vì sao hai persona cho một người

Chỉ có một người dùng, nhưng họ đóng hai vai có **tiêu chí "xong" khác nhau**, và gộp lại thì vai thứ hai dễ bị bỏ. Đây là quyết định Q1 = A của stage này.

| | **P1 — Người chạy pipeline** | **P2 — Người dự đoán** |
|---|---|---|
| Vai | chạy `run --stage stats`, đọc record, quyết định giữ hay hạ mốc | mở tab, nhập thông tin, đọc kết quả |
| Mục tiêu | biết mô hình mới có **thực sự tốt hơn** baseline, không phải chỉ "khác" | biết **một dòng hàng cụ thể** có nguy cơ trễ không, và **vì sao** |
| Nỗi đau hiện tại | con số AUC 0,5133 không nói được gì vì thấp hơn baseline một cột | tab hiện chỉ đọc; muốn biết một trường hợp cụ thể phải tự viết mã |
| Thời điểm dùng | sau mỗi lần đổi đặc trưng, một vài lần mỗi Bolt | bất cứ lúc nào muốn kiểm một trường hợp |
| Tiêu chí "xong" của họ | baseline đo lại, AUC vượt baseline, quyết định về mốc 0,70 được ghi | cùng đầu vào → cùng một điểm; ba đóng góp giải thích được |
| Họ đọc gì | `data/reports/analysis.json` và record | tab "Kết quả phân tích", mục "Dự đoán" |

## Thứ tự ưu tiên

**P1 trước, P2 sau.** Không phải vì P2 ít giá trị, mà vì **P2 không có gì để đọc nếu P1 chưa xong**: khối dự đoán cần một tệp mô hình đã lưu, và tệp đó chỉ có sau khi U2 huấn luyện và lưu. Thứ tự này khớp với ba Bolt đã chốt.

## Điều hai persona này **không** có

Không có persona "quản trị viên", "người vận hành", "khách hàng" — không ai trong số đó tồn tại trong hệ thống này. Cũng không có persona "giảng viên": người chấm không dùng hệ thống, họ đọc báo cáo của người học.

**Nhóm truyện US3 ("đọc kết quả") cũng thuộc P1, không phải persona thứ ba.** Đó là cùng người chạy pipeline, đọc lại kết quả của chính mình. Ghi rõ ở đây vì một bản nháp trước đã tách nhóm đó thành persona riêng, tạo ra một vai không tồn tại.
