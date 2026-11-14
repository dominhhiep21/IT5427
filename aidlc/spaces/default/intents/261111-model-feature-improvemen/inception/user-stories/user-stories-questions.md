# Câu hỏi — User Stories (story plan)

## Q1. Persona: một hay hai

Người dùng của hệ thống là **một người** (Q2 = D ở Intent Capture). Nhưng họ đóng hai vai rất khác nhau trong đợt này.

- A. **Hai persona**: "người chạy pipeline" (chạy `--stage stats`, đọc record, quyết định giữ/hạ mốc) và "người dự đoán" (mở tab, nhập bảy ô, đọc kết quả và ba đóng góp)
- B. **Một persona** duy nhất là "người phân tích", gộp cả hai vai
- C. Ba persona, tách thêm "người đọc báo cáo" (chỉ xem số, không chạy gì)
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Cách chia truyện

- A. **Theo hành trình người dùng**: mở tab → nhập → xem kết quả → đọc vì sao; cộng nhóm truyện cho người chạy pipeline
- B. **Theo ba đơn vị U1/U2/U3** của scope
- C. Theo yêu cầu (mỗi FR một nhóm truyện)
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Hai câu đã trả lời. Bản tóm tắt kế hoạch truyện:

- **Persona** [Q1 = A]: **hai** persona — "người chạy pipeline" và "người dự đoán" — dù chỉ có một người, vì hai vai có tiêu chí "xong" khác nhau.
- **Cách chia** [Q2 = A]: **theo hành trình người dùng** (mở tab → nhập → xem kết quả → đọc vì sao), cộng một nhóm cho người chạy pipeline.
- **Sẽ sinh**: `personas.md`, `stories.md` (US1.x cho người chạy pipeline, US2.x cho hành trình dự đoán, US3.x cho đọc kết quả), `traceability.json` phủ mọi FR/NFR.
- **Không có truyện** cho U1/U2 thuần kỹ thuật (thêm cột, huấn luyện, ghi tệp): chúng vào vai **điều kiện tiên quyết** và **tiêu chí nghiệm thu**, không phải truyện riêng.

- Looks correct
- Request changes

[Answer]: Looks correct
