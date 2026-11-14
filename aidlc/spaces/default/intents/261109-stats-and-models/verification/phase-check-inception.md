# Phase Check — Inception sang Construction

**Kết luận: PASS.** Ba bảng truy vết của Inception không còn khoảng trống, không có đích không hợp lệ, và mọi mã yêu cầu thượng nguồn đều có nơi bao phủ. Hai ghi chú ở mục 4 không chặn bàn giao.

Kiểm tra chạy sau khi hợp đồng báo cáo lên phiên bản 2, trên các tệp truy vết hiện có trong record.

## 1. Yêu cầu → Câu chuyện (`inception/user-stories/traceability.json`)

`upstream_ids` khai 22 mã: FR1.1–FR1.5, FR2.1–FR2.4, FR3.1–FR3.2, FR4.1–FR4.3, FR5.1–FR5.3, NFR1–NFR5.

| Câu chuyện | Bao phủ | Số mã |
|---|---|---|
| US1 | FR1.1, FR1.2, FR1.3, FR1.4, FR1.5 | 5 |
| US2 | FR2.1, FR2.2, FR2.3, FR2.4 | 4 |
| US3 | FR3.1, FR3.2 | 2 |
| US4 | FR4.1, FR4.2, FR4.3, NFR5 | 4 |
| US5 | FR5.1, FR5.2, FR5.3, NFR1, NFR2, NFR3, NFR4 | 7 |

Tổng 22 mã, không trùng, phủ đúng danh sách thượng nguồn. **Không có GAP, không có ORPHAN.**

## 2. Yêu cầu → Thành phần (`inception/domain-design/traceability.json`)

Mười mã thượng nguồn (FR1–FR5, NFR1–NFR5) đều có thành phần bao phủ:

| Thành phần | Bao phủ |
|---|---|
| `stats-module` | FR1 |
| `model-module` | FR2 |
| `report-writer` | FR3 |
| `report-reader` | FR3, FR4 |
| `stats-stage` | FR5, NFR1 |
| `result-tab` | FR4, NFR5 |

Mọi thành phần đều trỏ tới một mã có thật trong `requirements.md`. **Không có đích không hợp lệ, không có thành phần mồ côi.**

## 3. Câu chuyện → Đơn vị (`inception/units-generation/traceability.json`)

Năm câu chuyện được giao đủ, mỗi câu chuyện đúng một đơn vị, không đơn vị nào không có câu chuyện:

| Câu chuyện | Đơn vị |
|---|---|
| US1.1 | U1 |
| US2.1 | U2 |
| US3.1 | U1 |
| US4.1 | U3 |
| US5.1 | U1 |

**Không có GAP, không có ORPHAN.**

## 4. Ghi chú (không chặn)

1. **Nhãn câu chuyện trong tệp truy vết của `user-stories` còn dùng mã cũ.** Tệp ghi `US1`…`US5`, trong khi `stories.md` và tệp truy vết của `units-generation` dùng `US1.1`…`US5.1`. Việc phủ không đổi — mỗi nhãn cũ ánh xạ một-một sang nhãn mới — nên đây là lệch nhãn, không phải lệch nội dung. Tệp của `units-generation` là bản đúng; tệp của `user-stories` đã được duyệt và không sửa lại trong đợt này.
2. **Truy vết của `domain-design` ở mức nhóm yêu cầu** (`FR1`…`FR5`), không xuống mức `FR1.1`. Vì vậy nó không phát hiện được thiếu hụt trong một nhóm; phần đó do truy vết của `user-stories` gánh, và ở đó cả 22 mã đều có nơi bao phủ.
3. **Contract Design không sinh `traceability.json`** — bước này sở hữu hợp đồng hình thức chứ không sở hữu độ phủ yêu cầu, nên không tham gia bảng nào ở trên. Ảnh hưởng của nó lên bàn giao nằm ở chỗ khác: mọi đơn vị đọc chung một hợp đồng phiên bản 2, và ba hợp đồng C1/C2/C3 đều có chủ sở hữu rõ ràng.
