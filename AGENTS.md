# AGENTS.md

## Repo state

Greenfield data-engineering project for the Olist e-commerce dataset. There is **no application code, package manifest, test/lint config, CI, or git repo yet** — do not assume any exists or initialize one unprompted.

- `dataset/` — nine raw Olist CSVs. Treat as **immutable**; never overwrite or "clean in place". Write derived data/code to new directories.
- `doc/` — course material. `Projects.pdf` is the assignment brief (big-data integration/processing, ≥3V, storage, dashboard, analysis); the other PDFs are lecture slides on schema alignment, record linkage, query processing, source selection.
- `aidlc-wf/` — vendored AWS AI-DLC workflow template, not this project's code. Its `tech.md`/`structure.md` describe the upstream repo: paths like `.kiro/`, `.amazonq/`, `cliff.toml`, `README.md` and the `git cliff`/`cp` commands **do not apply here**. Its `core-workflow.md` mandates a welcome message and question files — follow that ritual only if the user explicitly asks for AI-DLC.

`doc/BT.pdf` is image-only slides; text extraction returns almost nothing, so read it visually if needed.

## Environment (verified)

- Windows, Python 3.13.5, pandas 2.2.3; also installed: numpy, matplotlib, seaborn, sqlalchemy, openpyxl, pdfplumber.
- **Not installed:** pyspark, duckdb, scikit-learn, pyarrow, jupyter. Don't write imports for them without installing.
- No venv, `requirements.txt`, or pinned versions. If you add dependencies, create a venv and a requirements file rather than installing globally.
- The workspace path contains Vietnamese characters and the console defaults to cp1252. Run Python with `python -X utf8` (or set `PYTHONUTF8=1`) or printing Portuguese/Vietnamese text raises `UnicodeEncodeError`.
- CSVs are UTF-8 (no BOM), comma-separated, all fields quoted; timestamps load as `object`, so parse explicitly.

## Dataset grain and traps

| File | Rows | Grain / key |
|---|---|---|
| `olist_orders_dataset.csv` | 99,441 | one row per `order_id` |
| `olist_customers_dataset.csv` | 99,441 | one row per `customer_id` |
| `olist_order_items_dataset.csv` | 112,650 | `(order_id, order_item_id)`; 98,666 orders |
| `olist_order_payments_dataset.csv` | 103,886 | `(order_id, payment_sequential)`; 99,440 orders |
| `olist_order_reviews_dataset.csv` | 99,224 | 98,410 unique `review_id`, 98,673 orders |
| `olist_products_dataset.csv` | 32,951 | one row per `product_id` |
| `olist_sellers_dataset.csv` | 3,095 | one row per `seller_id` |
| `olist_geolocation_dataset.csv` | 1,000,163 | many rows per zip prefix |
| `product_category_name_translation.csv` | 71 | one row per category |

- **`customer_id` is per-order, not per-person.** Use `customer_unique_id` (96,096 distinct) for repeat-purchase/customer analysis; joining orders to customers on `customer_id` is 1:1.
- **Never join geolocation directly.** It averages 52.6 rows per zip prefix and up to 5 city spellings per zip; a naive customer join explodes 99,441 rows to 15,083,455. Aggregate to one lat/lng per `zip_code_prefix` first. 278 customer zips and 7 seller zips have no geolocation row, and coordinates include clear outliers (lat up to 45, lng down to -101 for Brazil).
- **Payments and reviews are multi-row per order.** Aggregate before joining to item-level data; otherwise item revenue and review counts multiply. 547 order_ids have more than one review (551 extra review rows).
- **Payment totals disagree with item totals:** for 378 orders, summed `payment_value` differs from summed `price + freight_value` by more than 0.01. State which definition of revenue you use.
- 775 orders have no order items (mostly canceled/unavailable statuses); 1 order has no payment. All item `product_id`/`seller_id` resolve, but 610 products have null category and all their numeric attributes null too. 73 product categories exist vs 71 translations — `pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos` are missing, so an inner join silently drops them.
- Reviews: `review_comment_title` is null for 87,656 rows and `review_comment_message` for 58,247.
- Orders span 2016-09-04 to 2018-10-17; 96,478 of 99,441 are `delivered`. Filter by status explicitly for delivery/revenue analyses. `order_approved_at` (160 null), `order_delivered_carrier_date` (1,783), `order_delivered_customer_date` (2,965) are the only null timestamp columns.

## Working conventions

- Profile before transforming: `python -X utf8 -c "import pandas as pd; df=pd.read_csv('dataset/olist_orders_dataset.csv'); print(df.shape); print(df.dtypes); print(df.isna().sum())"`.
- Make join grain explicit (order / order-item / payment / review) before every merge, and validate row counts and key uniqueness after each join.
- Keep pipeline stages separate (ingest → clean → integrate → analyze) and make each rerunnable from the raw CSVs; do not hand-edit intermediate CSV output.
