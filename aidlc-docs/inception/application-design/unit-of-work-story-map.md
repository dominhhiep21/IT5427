# Bản đồ Story → Unit

## 1. Tổng hợp

| Unit | Số story | Story ID |
|---|---|---|
| U1 — Data Foundation | 7 | US-01 → US-07 |
| U2 — Integration & Analytics | 8 | US-08 → US-14, US-19 |
| U3 — Dashboard & Operations | 7 | US-15 → US-18, US-20 → US-22 |
| **Tổng** | **22** | **Không có story chưa gán** |

## 2. Bảng ánh xạ chi tiết

| Story | Tên | Epic | Persona | Ưu tiên | FR | Unit | Phụ thuộc |
|---|---|---|---|---|---|---|---|
| US-01 | Ingest 9 tệp + schema | E1 | P2 | Must | FR-01 | U1 | — |
| US-02 | Bảo vệ raw + log/hash | E1 | P2 | Must | FR-01 | U1 | US-01 |
| US-03 | Quality gate | E1 | P1 | Must | FR-08 | U1 | US-01, US-02 |
| US-04 | Timestamp/null/outlier | E2 | P1 | Must | FR-02 | U1 | US-01 |
| US-05 | Gộp geolocation | E2 | P1 | Must | FR-02 | U1 | US-01 |
| US-06 | Category fallback | E2 | P1 | Must | FR-02 | U1 | US-01 |
| US-07 | Giữ grain payment/review | E2 | P1 | Must | FR-02 | U1 | US-01 |
| US-08 | Star schema | E3 | P1 | Must | FR-03 | U2 | US-03 → US-07 |
| US-09 | Customer identity | E3 | P1 | Must | FR-03 | U2 | US-08 |
| US-10 | Geo/date/delivery dims | E3 | P1 | Must | FR-03 | U2 | US-05, US-08, US-19 |
| US-11 | Revenue trend | E4 | P1 | Must | FR-04 | U2 | US-08, US-10 |
| US-12 | Category/region | E4 | P1 | Must | FR-04 | U2 | US-08, US-10 |
| US-13 | Top product/seller | E4 | P1 | Should | FR-04 | U2 | US-08 |
| US-14 | Delivery KPI | E4 | P1 | Should | FR-04, FR-08 | U2 | US-08, US-10 |
| US-15 | KPI cards + filters | E5 | P1 | Must | FR-05 | U3 | US-11 → US-14 |
| US-16 | Trend/category/region charts | E5 | P1 | Must | FR-05 | U3 | US-11, US-12 |
| US-17 | Format/error/readability | E5 | P2 | Should | FR-05, NFR-05 | U3 | US-15, US-16 |
| US-18 | Micro-batch + replay | E6 | P2 | Must | FR-06 | U3 | US-08, US-20 |
| US-19 | IBGE download/cache/map | E6 | P1 | Must | FR-07 | U2 | US-01 |
| US-20 | CLI + docs | E7 | P2 | Must | FR-09, FR-10 | U3 | US-08 → US-19 |
| US-21 | Automated tests | E7 | P2 | Must | FR-08 | U3 | Tất cả story Must/Should |
| US-22 | ML late delivery | E7 | P1 | Could | FR-11 | U3 | US-08, US-14, US-21 |

## 3. Phân bổ theo epic

| Epic | Story | Unit chính |
|---|---|---|
| E1 — Ingestion & contract | US-01, US-02, US-03 | U1 |
| E2 — Cleaning | US-04, US-05, US-06, US-07 | U1 |
| E3 — Star schema | US-08, US-09, US-10 | U2 |
| E4 — Analytics/KPI | US-11, US-12, US-13, US-14 | U2 |
| E5 — Dashboard | US-15, US-16, US-17 | U3 |
| E6 — Micro-batch/IBGE | US-18 (U3), US-19 (U2) | U2, U3 |
| E7 — Operations/docs/ML | US-20, US-21, US-22 | U3 |

## 4. Kiểm tra phủ yêu cầu

| FR | Story | Unit |
|---|---|---|
| FR-01 | US-01, US-02 | U1 |
| FR-02 | US-04 → US-07 | U1 |
| FR-03 | US-08 → US-10 | U2 |
| FR-04 | US-11 → US-14 | U2 |
| FR-05 | US-15 → US-17 | U3 |
| FR-06 | US-18 | U3 |
| FR-07 | US-19 | U2 |
| FR-08 | US-03, US-14, US-21 | U1, U2, U3 |
| FR-09 | US-20 | U3 |
| FR-10 | US-20 | U3 |
| FR-11 | US-22 | U3 |

## 5. Kiểm tra tính đầy đủ

- [x] 22/22 story được gán unit.
- [x] Mỗi FR-01 → FR-11 có ít nhất một story.
- [x] Mỗi unit có ít nhất một story Must.
- [x] Không có story nào thuộc hai unit.
- [x] Thứ tự story trong U2/U3 tôn trọng dependency.
- [x] US-22 (Could) có thể bỏ mà không ảnh hưởng MVP.
