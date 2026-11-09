# Logical Components — u6-integration-ui

Nguồn: `nfr-requirements/{performance-requirements,security-requirements,tech-stack-decisions}.md`, `nfr-design/security-design.md` (ADR-U6-S1..S5), `functional-design/{functional-spec,frontend-components}.md`.

## 1. Kiến trúc logic

```
app.layout
└── IntegrationTab ──► OverviewScreen (4 thẻ, trạng thái rỗng)
                       DetailScreen × 4 (khung rỗng)
                            │
      callback route ◄──────┤ người dùng bấm
                            v
      L1 đọc hợp đồng của màn hình (C5/C6/C7) ─► L2 dựng nội dung ─► L3 StateBlock
                            │
      callback run_query ───┴─► L4 gọi U5 (C3) → U3 run_template (C4) → vẽ hai bản SQL + KPI
      callback suggest_source ─► L5 gọi U5 select_source → vẽ lại bảng nguồn
```

<!-- Text fallback: layout chỉ dựng khung rỗng; khi người dùng bấm, callback đọc hợp đồng của màn hình, dựng nội dung, và bọc trong StateBlock; hai callback riêng gọi U5/U3 cho truy vấn và đề xuất nguồn. -->

## 2. Danh mục khối

| Mã | Khối | Trách nhiệm | Không làm gì | Sở hữu |
|---|---|---|---|---|
| L1 | Nạp hợp đồng theo màn hình | Đọc C5/C6/C7 **trong callback**; bắt lỗi đã khai (ADR-U6-S1) | Không đọc lúc dựng layout | `src/integration/tab.py` |
| L2 | Dựng nội dung | Bảng ánh xạ (C6), bảng cặp (C5), bảng nguồn (C7), kết quả KPI (C4) | Không tự tính số | `src/integration/tab.py` |
| L3 | Trạng thái | `StateBlock` với năm token hiện có; không số 0 giả; không traceback (ADR-U6-S3, ADR-U6-S4) | Không dùng màu làm tín hiệu duy nhất | `src/integration/tab.py` |
| L4 | Chạy truy vấn | Gọi U5 lấy C3 rồi U3 `run_template`; vẽ hai bản SQL, kế hoạch, kết quả, KPI | Không tự viết SQL | `src/integration/tab.py` |
| L5 | Đề xuất nguồn | Gọi U5 `select_source`; vẽ lại bảng nguồn | Không tự chọn nguồn | `src/integration/tab.py` |
| L6 | Điều hướng | `load_overview` (nạp bốn thẻ), `route`, `run_query`, `suggest_source`, `reload` và callback của vùng kết quả — **sáu** callback (thêm callback của vùng), mỗi callback một Output riêng: `overview-cards`, `screen-body`, `query-result`, `source-table`, `active-screen`, `don-theo-thang` (ADR-U6-S5) | Không đè callback của ba tab cũ; không hai callback cùng một Output | `src/integration/tab.py` |
| L7 | Cấu hình tab | `TabConfig.card_ids` và `result_region_ids` (bắt buộc chứa `don-theo-thang`) từ `config/integration-tab.yaml` (ADR-U6-S2) | Không còn `result_block_ids` | `src/integration/card.py` |

## 3. Phạm vi hỏng

| Vùng hỏng | Ảnh hưởng | Cô lập |
|---|---|---|
| C5 thiếu tệp | Màn hình ghép bản ghi rỗng | `StateBlock("rong")` kèm hướng dẫn chạy pipeline |
| C7 chưa đề xuất | Bảng nguồn ở trạng thái một phần | `partial_reason` từ C7 |
| Một hợp đồng lỗi | Chỉ màn hình đó lỗi | Callback bắt lỗi; ba tab cũ và các màn hình khác không bị |
| Gói DMC thiếu trong `.venv` | Tab mới không dựng được | Kiểm ở bước cài đặt; `requirements.txt` ghim phiên bản |
| Callback ném lỗi | Màn hình hiện thông báo | `StateBlock("loi")` + nút thử lại |

## 4. Luồng dữ liệu

| Bước | Ai gọi | Nhận | Trả |
|---|---|---|---|
| 1 | Người dùng mở tab | ngữ cảnh tab | Callback `load_overview` đọc C5/C6/C7 và trả bốn thẻ có số liệu + trạng thái |
| 2 | Bấm thẻ | `card_id` | Màn hình chi tiết (callback `route`) |
| 3 | Vào `schema` | C6 | Bảng ánh xạ + `GAV` |
| 4 | Vào `linkage` | C5 | Số liệu, bảng cặp, dòng "Bỏ qua" |
| 5 | Vào `sources` | C7 | Bảng nguồn |
| 6 | Bấm "Đề xuất nguồn" | C3 + C7 mới | Bảng nguồn cập nhật |
| 7 | Bấm "Chạy" ở `queries` | C3 + C4 | Hai bản SQL, kế hoạch, kết quả, KPI |

## 5. Đo lường tại chỗ

| Chỉ tiêu | Cách đo |
|---|---|
| NFR1.1–NFR1.4 | `time.perf_counter` quanh callback trong test dashboard; ghi số thật ở Build and Test |
| NFR4.1 | Rà cấu trúc: nút thật, nhãn, thứ tự tab, tương phản |
| NFR5.1/NFR5.2 | `test_dashboard_smoke.py` (4 thẻ + 1 vùng, 2 callback cũ + 6 callback mới = **8**) + `KpiReconciler` |
| SR-U6-8 | Test dựng layout khi C5/C6/C7 đều vắng: ba tab cũ vẫn dựng được |
