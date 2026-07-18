

import argparse
import sqlite3
import sys
from datetime import datetime, timedelta

DB_PATH = "ecommerce.db"


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d")


def get_period_stats(conn, start, end):
    """Returns a dict with total_orders, revenue, unique_customers, top_products
    for the half-open date range [start, end] (both inclusive, as dates)."""
    cur = conn.cursor()

    start_str = start.strftime("%Y-%m-%d 00:00:00")
    end_str = end.strftime("%Y-%m-%d 23:59:59")

    cur.execute("""
        SELECT COUNT(DISTINCT o.order_id), COUNT(DISTINCT o.customer_id),
               COALESCE(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 0)
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.order_date BETWEEN ? AND ?
    """, (start_str, end_str))
    total_orders, unique_customers, revenue = cur.fetchone()

    cur.execute("""
        SELECT p.product_name,
               SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS rev
        FROM order_items oi
        JOIN orders o ON o.order_id = oi.order_id
        JOIN products p ON p.product_id = oi.product_id
        WHERE o.order_date BETWEEN ? AND ?
        GROUP BY p.product_name
        ORDER BY rev DESC
        LIMIT 3
    """, (start_str, end_str))
    top_products = cur.fetchall()

    return {
        "total_orders": total_orders or 0,
        "unique_customers": unique_customers or 0,
        "revenue": revenue or 0.0,
        "top_products": top_products,
    }


def pct_change(new, old):
    if old in (0, None):
        return None
    return (new - old) / old * 100.0


def print_report(report_type, start, end, current, previous):
    print("\n" + "=" * 60)
    print(f"  E-COMMERCE SUMMARY REPORT  ({report_type.upper()})")
    print(f"  Period: {start.date()}  to  {end.date()}")
    print("=" * 60)

    print(f"\n  Total Orders     : {current['total_orders']}")
    print(f"  Total Revenue    : ${current['revenue']:,.2f}")
    print(f"  Unique Customers : {current['unique_customers']}")

    print("\n  Top 3 Products by Revenue:")
    if current["top_products"]:
        for i, (name, rev) in enumerate(current["top_products"], start=1):
            print(f"    {i}. {name:<30} ${rev:,.2f}")
    else:
        print("    (no sales in this period)")

    print("\n  Comparison with Previous Period:")
    for label, key in [("Orders", "total_orders"), ("Revenue", "revenue"),
                        ("Unique Customers", "unique_customers")]:
        change = pct_change(current[key], previous[key])
        change_str = f"{change:+.1f}%" if change is not None else "N/A (no prior data)"
        print(f"    {label:<18}: {current[key]:>12,.2f}  vs  {previous[key]:>12,.2f}   ({change_str})")

    print("=" * 60 + "\n")


def compute_previous_period(start, end):
    length = end - start
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - length
    return prev_start, prev_end


def run_report(report_type, start, end):
    conn = sqlite3.connect(DB_PATH)
    current = get_period_stats(conn, start, end)
    prev_start, prev_end = compute_previous_period(start, end)
    previous = get_period_stats(conn, prev_start, prev_end)
    print_report(report_type, start, end, current, previous)
    conn.close()


def interactive_mode():
    print("E-Commerce Order Analytics - Report Generator")
    print("-" * 45)
    report_type = ""
    while report_type not in ("daily", "weekly", "monthly"):
        report_type = input("Report type (daily/weekly/monthly): ").strip().lower()

    while True:
        try:
            start = parse_date(input("Start date (YYYY-MM-DD): ").strip())
            end = parse_date(input("End date   (YYYY-MM-DD): ").strip())
            if end < start:
                print("End date must be on/after start date. Try again.\n")
                continue
            break
        except ValueError:
            print("Invalid date format, please use YYYY-MM-DD.\n")

    run_report(report_type, start, end)


def main():
    parser = argparse.ArgumentParser(description="E-Commerce report CLI")
    parser.add_argument("--type", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--start", help="YYYY-MM-DD")
    parser.add_argument("--end", help="YYYY-MM-DD")
    args = parser.parse_args()

    if args.type and args.start and args.end:
        try:
            start = parse_date(args.start)
            end = parse_date(args.end)
        except ValueError:
            print("Invalid date format, use YYYY-MM-DD.")
            sys.exit(1)
        run_report(args.type, start, end)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
