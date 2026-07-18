

import os
import re
import pandas as pd

DATA_DIR = "data"
CLEAN_DIR = os.path.join(DATA_DIR, "cleaned")
REPORT_PATH = "reports/data_quality_report.txt"

os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs("reports", exist_ok=True)

issues = []  # collects human-readable strings for the final report


def log(msg):
    print(msg)
    issues.append(msg)



def clean_orders(df):
    """
    Fixes:
      - order_date arriving in DD-MM-YYYY (no time) instead of YYYY-MM-DD HH:MM:SS
      - missing / empty customer_id -> pd.NA (kept, but flagged + counted)
    Returns the cleaned dataframe.
    """
    df = df.copy()

    def parse_date(value):
        value = str(value).strip()
        # Try the canonical format first
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return pd.to_datetime(value, format=fmt)
            except (ValueError, TypeError):
                pass
        # Fall back to DD-MM-YYYY
        try:
            return pd.to_datetime(value, format="%d-%m-%Y")
        except (ValueError, TypeError):
            return pd.NaT

    bad_format_mask = ~df["order_date"].astype(str).str.match(
        r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?$"
    )
    n_bad_format = int(bad_format_mask.sum())

    df["order_date"] = df["order_date"].apply(parse_date)
    n_unparseable = int(df["order_date"].isna().sum())

    log(f"[clean_orders] Reformatted {n_bad_format} order_date values that were "
        f"not in YYYY-MM-DD HH:MM:SS format (mostly DD-MM-YYYY).")
    if n_unparseable:
        log(f"[clean_orders] WARNING: {n_unparseable} order_date values could "
            f"not be parsed at all and were set to NaT.")

    # customer_id: blank strings / whitespace -> NA
    df["customer_id"] = df["customer_id"].replace(r"^\s*$", pd.NA, regex=True)
    n_missing_customer = int(df["customer_id"].isna().sum())
    log(f"[clean_orders] Found {n_missing_customer} orders with a missing "
        f"customer_id ({n_missing_customer/len(df):.1%} of all orders). "
        f"These rows are KEPT (an order can still be analyzed) but customer_id "
        f"is left NULL rather than guessed.")

    # keep customer_id as nullable integer where possible
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")

    return df


def clean_products(df):
    """
    Normalizes product_name: trims whitespace and applies Title Case.
    """
    df = df.copy()
    before = df["product_name"].copy()

    df["product_name"] = (
        df["product_name"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

    n_changed = int((before.astype(str) != df["product_name"]).sum())
    log(f"[clean_products] Normalized {n_changed} product_name values "
        f"(trimmed whitespace, collapsed internal spaces, applied Title Case).")

    return df


def validate_emails(customers_df):
    """
    Returns the list of customer_ids whose email address is invalid
    (missing '@' or missing/invalid domain part).
    """
    pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def is_valid(email):
        return bool(pattern.match(str(email).strip()))

    mask_valid = customers_df["email"].apply(is_valid)
    invalid_ids = customers_df.loc[~mask_valid, "customer_id"].tolist()

    log(f"[validate_emails] Found {len(invalid_ids)} customers with an invalid "
        f"email address ({len(invalid_ids)/len(customers_df):.1%} of all customers).")

    return invalid_ids


def check_referential_integrity(orders_df, order_items_df):
    """
    Returns the subset of order_items whose order_id does not exist in orders.
    """
    valid_order_ids = set(orders_df["order_id"])
    orphan_mask = ~order_items_df["order_id"].isin(valid_order_ids)
    orphans = order_items_df.loc[orphan_mask]

    log(f"[check_referential_integrity] Found {len(orphans)} order_items rows "
        f"referencing an order_id that does not exist in orders.csv. "
        f"Affected order_ids: {sorted(orphans['order_id'].unique().tolist())}")

    return orphans


def extra_validations(order_items_df):
    """Additional data-quality checks mentioned in the spec (edge cases)."""
    neg_qty = order_items_df[order_items_df["quantity"] < 0]
    log(f"[extra] {len(neg_qty)} order_items rows have negative quantity "
        f"(interpreted as returns, kept in data but flagged).")

    zero_qty = order_items_df[order_items_df["quantity"] == 0]
    log(f"[extra] {len(zero_qty)} order_items rows have quantity == 0 "
        f"(these contribute zero revenue; flagged for review).")

    bad_discount = order_items_df[
        (order_items_df["discount_percent"] < 0) | (order_items_df["discount_percent"] > 100)
    ]
    log(f"[extra] {len(bad_discount)} order_items rows have an out-of-range "
        f"discount_percent (<0 or >100). These will be CLIPPED to [0, 100] "
        f"in the cleaned file.")

    return bad_discount


def clean_order_items(df):
    df = df.copy()
    df["discount_percent"] = df["discount_percent"].clip(lower=0, upper=100)
    return df


def main():
    print("Loading raw CSVs...")
    customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
    products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
    orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"), dtype={"customer_id": "object"})
    order_items = pd.read_csv(os.path.join(DATA_DIR, "order_items.csv"))

    print("\nRunning cleaning + validation functions...\n")

    invalid_email_ids = validate_emails(customers)
    orphan_items = check_referential_integrity(orders, order_items)
    extra_validations(order_items)

    orders_clean = clean_orders(orders)
    products_clean = clean_products(products)
    order_items_clean = clean_order_items(order_items)

    # Drop orphan order_items from the cleaned dataset (referential integrity)
    order_items_clean = order_items_clean[
        order_items_clean["order_id"].isin(orders_clean["order_id"])
    ].copy()
    log(f"[main] Removed {len(orphan_items)} orphan order_items rows from the "
        f"cleaned dataset (they cannot be joined to any real order).")

    # Save cleaned files
    customers.to_csv(os.path.join(CLEAN_DIR, "customers.csv"), index=False)
    products_clean.to_csv(os.path.join(CLEAN_DIR, "products.csv"), index=False)
    orders_clean.to_csv(os.path.join(CLEAN_DIR, "orders.csv"), index=False)
    order_items_clean.to_csv(os.path.join(CLEAN_DIR, "order_items.csv"), index=False)

    print(f"\nCleaned files written to {CLEAN_DIR}/")

    # Write the data-quality report
    with open(REPORT_PATH, "w") as f:
        f.write("E-COMMERCE DATA QUALITY REPORT\n")
        f.write("=" * 60 + "\n\n")
        for line in issues:
            f.write(line + "\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"Invalid-email customer_ids ({len(invalid_email_ids)}): "
                 f"{invalid_email_ids}\n")

    print(f"Data quality report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
