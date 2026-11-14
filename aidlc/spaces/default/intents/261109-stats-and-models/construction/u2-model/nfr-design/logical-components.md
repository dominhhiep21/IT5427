# Logical Components — u2-model

Nguồn: `../functional-design/entities.md`, `../functional-design/rules.md`, `../nfr-requirements/*`, `../../../inception/domain-design/components.md`.

## Đối chiếu với danh mục thành phần của Domain Design

`components.md` khai `model-module` cho đơn vị này. Các thành phần nội bộ dưới đây **nằm trong** `model-module`; chúng là cách chia bên trong để cách ly lỗi, không phải thành phần mới ở cấp kiến trúc.

| Thành phần nội bộ | Trách nhiệm | Quy tắc | Miền hỏng riêng |
|---|---|---|---|
| `model-orchestrator` | Điều phối: dựng đặc trưng → **chia tập** → mã hoá → huấn luyện → chọn ngưỡng → trả khối `ModelBlock` | BR2.1, BR2.2 | Không — lỗi ở đây không có khối mô hình |
| `feature-builder` | Đọc mart, gộp về grain đơn, dựng 11 cột, gắn nhãn `is_late` | BR2.1, BR2.3 | Không — dừng cả bước |
| `splitter` | Chia theo mốc 2018-04-01, không xáo trộn, kiểm tổng cỡ mẫu | BR2.2 | Không |
| `encoder` | One-hot với phạm trù cố định **khớp trên tập huấn luyện**, điền `unknown`, chuẩn hoá cột số bằng tham số **khớp trên tập huấn luyện** | TS-6, TS-7, TS-8, TS-9 | Không |
| `trainer` | Huấn luyện với trọng số lớp cân bằng, `random_state` cố định | BR2.4 | Không |
| `threshold-picker` | Duyệt lưới 19 điểm, chọn F1 lớn nhất, hoà chọn cao hơn | BR2.5 | Không |
| `metrics-reporter` | AUC, cờ `auc_below_target`, đếm ba con số, làm tròn | BR2.6, BR2.7, BR2.9 | Không |

`model-module` **trả về** một `ModelBlock` và dừng ở đó. Việc đọc tệp cũ, giữ khối `stats` và gọi `write_report` thuộc **`stats-stage` của U1** — `components.md` ghi rõ `model-module` chỉ dựng đặc trưng và huấn luyện, không ghi tệp, và `unit-of-work.md` giao `stats-stage` làm điểm ghép nối duy nhất. U2 không sở hữu một thành phần ghi tệp nào.

## Tài nguyên dùng chung

| Tài nguyên | Ai dùng | Cách ly |
|---|---|---|
| `AnalyticsService` trên DuckDB | `feature-builder` | Một kết nối mỗi lời gọi, do lớp dịch vụ tự quản |
| `data/reports/analysis.json` | **`stats-stage` của U1**, không phải U2 | U2 chỉ trả khối; lần đọc và ghi duy nhất nằm ở tầng `stats` |
| Logger JSONL | mọi thành phần | Cùng `run_id` với tầng `stats` **khi** tầng truyền writer đã có; gọi mặc định sẽ sinh `run_id` mới |

## Bán kính ảnh hưởng

| Hỏng ở | Ảnh hưởng | Vì sao dừng ở đó |
|---|---|---|
| `feature-builder` | Không có khối mô hình; tệp báo cáo không đổi | Không có gì để huấn luyện |
| `trainer` hoặc `threshold-picker` | Không có khối mô hình; tệp không đổi | Khối chỉ được trả về, chưa ai ghi |
| Bất kỳ thành phần nào của U2 | **Không** ảnh hưởng khối `stats` | U2 không đọc và không ghi tệp; nó trả một khối cho tầng `stats` |

## Điều không có

Không có thành phần hạ tầng: không tiến trình nền, không hàng đợi, không bộ nhớ đệm, không dịch vụ, không tệp mô hình. Tám thành phần trong một tiến trình, và đó là toàn bộ.
