# E-Commerce Order Analytics System

An intern mini-project: generate messy multi-source e-commerce data, clean
it in Python, load it into SQLite, and run a full suite of SQL analytics
(basic → intermediate → advanced window-function/CTE queries), plus a
command-line reporting tool and an edge-case test suite.

## Project Structure

```
ecommerce_analytics/
├── 01_data_generation.py     # Part 1: generates 4 messy CSVs into data/
├── 02_data_cleaning.py       # Part 2: cleans data, writes data/cleaned/ + report
├── 03_load_to_sqlite.py      # loads cleaned CSVs into ecommerce.db
├── 04_sql_queries.sql        # Part 3: all 16 SQL analysis queries
├── 05_report_cli.py          # Part 4: interactive/CLI summary report tool
├── 06_test_edge_cases.py     # Part 5: edge-case test functions
├── 07_run_sql_report.py      # helper: runs 04_sql_queries.sql, saves output
├── run_all.py                # runs the whole pipeline in one command
├── requirements.txt
├── data/                      # created by 01_data_generation.py
│   ├── customers.csv, products.csv, orders.csv, order_items.csv   (raw, messy)
│   └── cleaned/               (cleaned versions of the same 4 files)
├── reports/                   # created by 02_data_cleaning.py / 07_run_sql_report.py
│   ├── data_quality_report.txt
│   └── sql_query_results.txt
└── ecommerce.db               # created by 03_load_to_sqlite.py
```

`data/`, `reports/`, and `ecommerce.db` are **not included in the zip** —
they're generated output, created fresh the first time you run the
pipeline (see Quick Start below).

## Quick Start

```bash
pip install -r requirements.txt

# Run everything in order (generate -> clean -> load -> SQL -> tests)
python run_all.py

# Then try the interactive report tool
python 05_report_cli.py
# or non-interactively:
python 05_report_cli.py --type monthly --start 2024-06-01 --end 2024-06-30
```

Each numbered script can also be run individually, in order (01 → 02 → 03 →
07 → 06). `04_sql_queries.sql` is meant to be read and/or run through any
SQLite client — `07_run_sql_report.py` executes it for you and saves the
output.

## Part 1 — Data Generation

`01_data_generation.py` uses `Faker` to build ~600 customers, 250 products,
3,000 orders and ~7,500 order_items (well above the 500-row minimum on every
file). Referential integrity between `orders` and `order_items` is correct
by construction (item rows are generated *from* real order_ids), **except**
for 15 intentionally-added orphan rows used to exercise the integrity check.

**Intentional data-quality issues injected on purpose:**

| File | Issue | Rate |
|---|---|---|
| `orders.csv` | missing/empty `customer_id` | ~5% |
| `orders.csv` | `order_date` in `DD-MM-YYYY` instead of `YYYY-MM-DD HH:MM:SS` | ~8% |
| `order_items.csv` | negative `quantity` (returns) | ~3% |
| `order_items.csv` | `order_id` not present in `orders.csv` | 15 rows |
| `order_items.csv` | `discount_percent` > 100 | a handful |
| `products.csv` | extra whitespace / inconsistent case in `product_name` | ~15% |
| `customers.csv` | invalid email (no `@` or no domain) | ~2% |

## Part 2 — Data Cleaning

`02_data_cleaning.py` implements exactly the four functions requested:

- **`clean_orders()`** — parses both date formats into proper timestamps,
  converts blank `customer_id` to a real NULL (kept as NULL, not guessed).
- **`clean_products()`** — trims whitespace, collapses double spaces, and
  title-cases `product_name`.
- **`validate_emails()`** — returns the list of `customer_id`s with an
  invalid email (regex-based check for `local@domain.tld`).
- **`check_referential_integrity()`** — returns every `order_items` row
  whose `order_id` doesn't exist in `orders`; these rows are then dropped
  from the cleaned `order_items.csv` since they can never be joined to a
  real order.

It also clips out-of-range `discount_percent` values into `[0, 100]` and
flags (without dropping) negative and zero quantities. Every finding is
written to `reports/data_quality_report.txt`, along with counts and affected
IDs.

## Part 3 — SQL Analysis

`04_sql_queries.sql` (SQLite dialect) contains all 16 requested queries,
organized exactly as specified:

**Basic:** total revenue per category · top 10 customers by order value ·
month-wise order count for the last 12 months.

**Intermediate:** customers with orders but zero deliveries · products with
more returns than purchases · return rate per category.

**Advanced (window functions / CTEs):**
1. Running totals of revenue per region (`SUM() OVER`)
2. `DENSE_RANK()` of products by revenue within category (ties share a rank)
3. `LAG()` to compute days between a customer's consecutive orders, plus an
   "At Risk" flag (avg gap > 30 days)
4. Multi-level CTE: monthly revenue per customer → High/Medium/Low bucket →
   customer counts per bucket per month
5. `NTILE(4)` customer segmentation into Platinum/Gold/Silver/Bronze
6. Year-over-year revenue comparison with `LEFT JOIN` to handle missing
   prior-year data
7. `FIRST_VALUE()` / `LAST_VALUE()` to find each customer's first vs. most
   recent purchased category, with a `category_shift` flag
8. Cumulative revenue distribution (running % of total revenue) to answer
   "what % of revenue comes from the top N% of customers"
9. Multi-level cohort-retention analysis (registration-month cohorts,
   retention in months 0–3)
10. Self-join on `orders` (via `ROW_NUMBER()`) comparing each order's value
    to the customer's immediately preceding order

Revenue is computed consistently everywhere as:
`quantity * unit_price * (1 - discount_percent / 100.0)`
(a negative `quantity` — a return — naturally subtracts value, which is the
desired business behavior).

`07_run_sql_report.py` executes every query and saves real output to
`reports/sql_query_results.txt` so results can be reviewed without opening a
SQLite client.

## Part 4 — Python + SQL Integration (CLI tool)

`05_report_cli.py` is a **stdlib-only** (`sqlite3`, `argparse`, `datetime` —
no pandas) command-line tool. It:

1. Asks for report type (daily / weekly / monthly)
2. Asks for a date range
3. Connects to `ecommerce.db`
4. Prints total orders, revenue, unique customers, top 3 products, and a %
   change comparison against the immediately preceding period of equal
   length.

Supports both interactive prompts and `--type/--start/--end` flags for
scripting.

## Part 5 — Edge Case Handling

`06_test_edge_cases.py` has one test function per required case, each
asserting *and documenting* the system's actual behavior:

1. **Orphan `order_id`** in `order_items` → detected, reported, and excluded
   from the cleaned dataset (can never be joined to a real order).
2. **`discount_percent` > 100** → clipped to 100 and flagged (never allowed
   to push revenue negative).
3. **`quantity == 0`** → valid, contributes $0 revenue, no crash — but
   flagged for manual review since it's unusual for a real order line.
4. **Future `order_date`** → detected via a date-vs-now check; not silently
   trusted in trend/time-series calculations.

Run with `python 06_test_edge_cases.py`.

## Notes / Design Decisions

- SQLite was chosen as "any SQL database" per the spec — it needs no server
  and the generated `ecommerce.db` file is portable.
- Cleaning is intentionally conservative: rows with unresolvable problems
  (e.g. orphan order_items) are **removed** from the cleaned dataset, while
  rows with fixable or informative problems (bad date format, out-of-range
  discount, missing customer_id) are **fixed or flagged, not deleted** —
  deleting an entire order because its customer_id is missing would throw
  away real revenue data.
- All money/revenue figures use the same formula everywhere so results are
  comparable across every query and report.
