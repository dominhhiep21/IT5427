# Entities — u3-display

Nguồn: `../../../inception/units-generation/unit-of-work.md`, `../../../inception/domain-design/components.md`, `../../../inception/contract-design/contract-summary.md` (C2), `../../../inception/requirements-analysis/requirements.md`, `../../../inception/user-stories/stories.md` (US4.1), `functional-design-questions.md`.

U3 là đơn vị **giao diện**: nó không tính toán, chỉ đọc `ReportView` rồi dựng tab. Thực thể ở đây là thực thể giao diện, không phải dữ liệu nghiệp vụ.

```yaml
entities:
  - name: ResultTabState
    description: Trạng thái hiển thị của tab kết quả, suy ra từ ReportView
    attributes:
      - { name: token, type: string, required: true, allowed: ["rong", "day-du", "mot-phan", "loi", "chua-chay"] }
      - { name: notice, type: string, required: false, note: "câu chữ tiếng Việt; rỗng khi day-du" }
      - { name: command_hint, type: string, required: false, note: "lệnh cần chạy; có ở rong, và ở chỗ khối thiếu của mot-phan" }
    constraints:
      - "token lấy thẳng từ ReportView.status; chỉ chua-chay do giao diện tự sinh"
      - "đúng một token tại một thời điểm"
      - "day-du thì không có notice, không có command_hint"

  - name: SummaryCard
    description: Một thẻ trong dải tóm tắt
    attributes:
      - { name: card_id, type: string, required: true, allowed: ["ti-le-tre", "so-don", "so-bo-qua", "auc"] }
      - { name: label, type: string, required: true }
      - { name: value, type: string, required: true, note: "đã định dạng theo kiểu Brazil" }
      - { name: status_note, type: string, required: false, note: "chỉ thẻ auc dùng: 'đạt' hoặc 'không đạt mốc 0,70'" }
    constraints:
      - "số thẻ phụ thuộc dữ liệu có nguồn: ba thẻ đầu cần khối stats, thẻ auc cần khối model"
      - "thẻ auc chỉ mang status_note khi có khối model; thiếu khối thì ghi 'chưa có' và không có dấu"
      - "không thẻ nào được tính ra một con số không có trong tệp báo cáo"

  - name: ReportSection
    description: Một khối nội dung trong tab, theo thứ tự đọc
    attributes:
      - { name: section_id, type: string, required: true, allowed: ["tom-tat", "thong-ke", "mo-hinh"] }
      - { name: heading, type: string, required: true }
      - { name: items, type: "list[str]", required: false }
    constraints:
      - "thứ tự cố định: tom-tat, thong-ke, mo-hinh"

  - name: SkippedBanner
    description: Dải liệt kê kiểm định không chạy được
    attributes:
      - { name: entries, type: "list[tuple[str, str]]", required: true, note: "(tên phép, lý do) đọc từ StatsBlock.skipped" }
    constraints:
      - "rỗng thì không dựng dải; có phần tử thì mỗi phần tử một dòng"
      - "chỉ dựng ở token day-du và mot-phan"
```

## Tóm tắt tập thực thể

| Thực thể | Vai |
|---|---|
| `ResultTabState` | Ánh xạ trạng thái hợp đồng sang trạng thái giao diện |
| `SummaryCard` | Bốn thẻ của dải tóm tắt |
| `ReportSection` | Ba khối nội dung theo thứ tự đọc |
| `SkippedBanner` | Dải cảnh báo cho kiểm định bị bỏ |

## Quan hệ

- `ResultTabState` quyết định dựng gì: `rong` chỉ có thông điệp và lệnh; `day-du` dựng đủ ba khối; `mot-phan` dựng thiếu khối và ghi rõ phần thiếu; `loi` chỉ có thông điệp lỗi kèm đường dẫn.
- `SummaryCard` và `ReportSection` chỉ tồn tại ở `day-du` và `mot-phan`.
- `SkippedBanner` chỉ tồn tại khi `StatsBlock.skipped` không rỗng.
