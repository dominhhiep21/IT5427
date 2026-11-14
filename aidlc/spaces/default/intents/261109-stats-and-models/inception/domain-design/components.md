# Components — Kiểm định thống kê và mô hình dự báo

Nguồn: `../requirements-analysis/requirements.md` (FR1–FR5, NFR1–NFR5), `../user-stories/stories.md`, và `domain-design-questions.md`.

```yaml
components:
  - name: stats-module
    kind: library
    path: src/analytics/stats.py
    owns: [khoảng tin cậy, kiểm định hai tỉ lệ, tương quan, so sánh nhóm, phân rã mùa vụ]
    depends_on: [analytics-service]
  - name: model-module
    kind: library
    path: src/analytics/model.py
    owns: [dựng đặc trưng, chia dữ liệu theo thời gian, huấn luyện, chọn ngưỡng]
    depends_on: [analytics-service]
  - name: report-writer
    kind: library
    path: src/analytics/report.py
    owns: [kiểu báo cáo dùng chung, ghi tệp JSON]
    depends_on: []
  - name: report-reader
    kind: library
    path: src/analytics/report.py
    owns: [đọc và kiểm cấu trúc tệp báo cáo]
    depends_on: [report-writer]
  - name: stats-stage
    kind: service
    path: src/pipeline/stages.py
    owns: [tầng stats trong chuỗi run --stage]
    depends_on: [stats-module, model-module, report-writer]
  - name: result-tab
    kind: ui
    path: src/dashboard/analysis_tab.py
    owns: [tab kết quả, dải tóm tắt, bộ chọn ngưỡng]
    depends_on: [report-reader]
```

## Sơ đồ

```
          ┌──────────────────┐
          │ analytics-service│  (đọc DuckDB, có sẵn)
          └───────┬──────────┘
        ┌─────────┴─────────┐
        ▼                   ▼
 ┌─────────────┐     ┌─────────────┐
 │ stats-module│     │ model-module│
 └──────┬──────┘     └──────┬──────┘
        └─────────┬─────────┘
                  ▼
          ┌──────────────┐
          │ report-writer│
          └──────┬───────┘
                 ▼  (tệp JSON)
          ┌──────────────┐
          │ report-reader│
          └──────┬───────┘
                 ▼
          ┌──────────────┐
          │  result-tab  │
          └──────────────┘

 stats-stage gọi stats-module, model-module, report-writer
```

## Tóm tắt trách nhiệm

- `stats-module` chỉ tính, không ghi tệp, không đọc tệp. [Q1][Q2]
- `model-module` chỉ dựng đặc trưng và huấn luyện, không ghi tệp. [Q1][Q2]
- `report-writer` và `report-reader` nằm cùng một mô-đun nhưng hai trách nhiệm rõ ràng: một ghi, một đọc và kiểm. [Q3][Q4]
- `stats-stage` là điểm ghép nối duy nhất gọi cả hai phần. [Q3]
- `result-tab` không tính toán gì; mọi con số đến từ tệp báo cáo. [Q5]

## Vì sao tách hai mô-đun

Thống kê và mô hình có nhịp thay đổi khác nhau và phụ thuộc khác nhau; gộp chúng làm một tệp sẽ khiến mọi thay đổi ở mô hình chạm vào phần kiểm định đã ổn định. [Q1]
