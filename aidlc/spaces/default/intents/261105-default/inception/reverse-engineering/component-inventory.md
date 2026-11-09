# Kiểm kê thành phần (Component Inventory)

## Gói ứng dụng

Không có. Không tồn tại mã nguồn, package, service hay entrypoint.

## Gói hạ tầng

Không có. Không có CDK, Terraform, CloudFormation, Docker, CI/CD.

## Gói dùng chung / tài sản dữ liệu

| Thành phần | Loại | Mục đích |
|---|---|---|
| `olist_orders_dataset.csv` | Data | Đầu mối vòng đời đơn hàng |
| `olist_customers_dataset.csv` | Data | Danh tính khách hàng |
| `olist_order_items_dataset.csv` | Data | Dòng hàng và doanh thu |
| `olist_order_payments_dataset.csv` | Data | Thanh toán |
| `olist_order_reviews_dataset.csv` | Data | Đánh giá |
| `olist_products_dataset.csv` | Data | Danh mục sản phẩm |
| `olist_sellers_dataset.csv` | Data | Người bán |
| `olist_geolocation_dataset.csv` | Data | Tọa độ theo zip |
| `product_category_name_translation.csv` | Data | Từ điển danh mục |
| `doc/*.pdf` | Documentation | Đề bài và slide bài giảng |
| `aidlc-wf/**` | Workflow rules | Quy tắc AI-DLC |
| `AGENTS.md` | Documentation | Hướng dẫn agent |

## Gói kiểm thử

Không có. Không có unit/integration/load test.

## Tổng hợp

- **Tổng gói phần mềm**: 0
- **Ứng dụng**: 0
- **Hạ tầng**: 0
- **Chia sẻ/dữ liệu**: 9 tệp dữ liệu + 8 tài liệu PDF
- **Kiểm thử**: 0
- **Dòng dữ liệu**: 1.550.922 dòng trên 9 CSV (bao gồm 1.000.163 dòng geolocation)
