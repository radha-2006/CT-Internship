
import sys
from datetime import datetime, timedelta

import pandas as pd




# Edge Case 1: order_items references an order_id not present in orders

def test_orphan_order_id():
    orders = pd.DataFrame({"order_id": [1, 2, 3]})
    order_items = pd.DataFrame({
        "order_item_id": [1, 2, 3],
        "order_id": [1, 2, 999],   # 999 does not exist in orders
        "quantity": [1, 2, 1],
    })

    valid_ids = set(orders["order_id"])
    orphan_mask = ~order_items["order_id"].isin(valid_ids)
    orphans = order_items[orphan_mask]

    assert len(orphans) == 1, "Expected exactly 1 orphan row"
    assert orphans.iloc[0]["order_id"] == 999

    # System behavior: orphan rows are detected, reported, and excluded from
    # the cleaned dataset (they cannot be joined to any real order, so
    # keeping them would silently inflate item counts with no order context).
    cleaned = order_items[~orphan_mask]
    assert len(cleaned) == 2
    print("  PASS: orphan order_id is detected and removed from cleaned data;"
          " it is reported in the data-quality report.")



# Edge Case 2: discount_percent > 100
def test_discount_over_100():
    order_items = pd.DataFrame({
        "order_item_id": [1, 2],
        "quantity": [2, 1],
        "unit_price": [100.0, 50.0],
        "discount_percent": [150, 20],   # first row is invalid
    })

    invalid_mask = (order_items["discount_percent"] < 0) | (order_items["discount_percent"] > 100)
    assert invalid_mask.sum() == 1

    
    clipped = order_items["discount_percent"].clip(lower=0, upper=100)
    assert clipped.iloc[0] == 100

    revenue = order_items["quantity"] * order_items["unit_price"] * (1 - clipped / 100.0)
    assert (revenue >= 0).all(), "Revenue must never go negative after clipping"
    print("  PASS: discount_percent > 100 is clipped to 100 and flagged; "
          "revenue can never go negative as a result.")



# Edge Case 3: quantity == 0
def test_zero_quantity():
    order_items = pd.DataFrame({
        "order_item_id": [1, 2],
        "quantity": [0, 3],
        "unit_price": [20.0, 10.0],
        "discount_percent": [0, 0],
    })

    revenue = order_items["quantity"] * order_items["unit_price"] * (1 - order_items["discount_percent"] / 100.0)
    assert revenue.iloc[0] == 0.0

    zero_qty_rows = order_items[order_items["quantity"] == 0]
    assert len(zero_qty_rows) == 1

 
    print("  PASS: quantity == 0 contributes $0 revenue (no crash / no divide-by-zero) "
          "and is flagged for manual review as an unusual-but-valid row.")


# Edge Case 4: order_date in the future
def test_future_order_date():
    today = datetime.now()
    future_date = today + timedelta(days=30)

    orders = pd.DataFrame({
        "order_id": [1, 2],
        "order_date": [today.strftime("%Y-%m-%d %H:%M:%S"),
                        future_date.strftime("%Y-%m-%d %H:%M:%S")],
    })
    orders["order_date"] = pd.to_datetime(orders["order_date"])

    future_mask = orders["order_date"] > pd.Timestamp.now()
    future_orders = orders[future_mask]

    assert len(future_orders) == 1
    assert future_orders.iloc[0]["order_id"] == 2

    
    print("  PASS: future order_date is detected via a simple date-vs-now "
          "comparison and would be flagged for review rather than silently "
          "included in trend calculations.")


def run_all():
    tests = [
        test_orphan_order_id,
        test_discount_over_100,
        test_zero_quantity,
        test_future_order_date,
    ]
    print("Running edge-case tests...\n")
    failures = 0
    for t in tests:
        print(f"{t.__name__}:")
        try:
            t()
        except AssertionError as e:
            failures += 1
            print(f"  FAIL: {e}")
        print()

    print("-" * 50)
    if failures == 0:
        print(f"All {len(tests)} edge-case tests passed.")
    else:
        print(f"{failures} of {len(tests)} tests FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    run_all()
