

import csv
import os
import random
from datetime import datetime, timedelta

from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# Config
N_CUSTOMERS = 600
N_PRODUCTS = 250
N_ORDERS = 3000          # gives us well over 500 rows, comfortably realistic
MAX_ITEMS_PER_ORDER = 4

CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]
ORDER_STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
# Weighted so DELIVERED dominates, like a real store
ORDER_STATUS_WEIGHTS = [0.10, 0.15, 0.55, 0.10, 0.10]

CATEGORIES = {
    "Electronics": ["Phones", "Laptops", "Audio", "Accessories"],
    "Clothing": ["Men", "Women", "Kids", "Footwear"],
    "Home": ["Kitchen", "Furniture", "Decor", "Bedding"],
    "Books": ["Fiction", "Non-Fiction", "Children", "Academic"],
}

REGIONS = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)


def random_date(start=START_DATE, end=END_DATE):
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)


# 1. customers.csv
def generate_customers(n=N_CUSTOMERS):
    rows = []
    for cid in range(1, n + 1):
        name = fake.name()
        email = fake.email()

        # 2% invalid emails: strip the @ or the domain part
        if random.random() < 0.02:
            broken_type = random.choice(["no_at", "no_domain"])
            if broken_type == "no_at":
                email = email.replace("@", "")
            else:
                email = email.split("@")[0] + "@"

        reg_date = random_date(START_DATE, END_DATE - timedelta(days=30))
        rows.append({
            "customer_id": cid,
            "customer_name": name,
            "email": email,
            "registration_date": reg_date.strftime("%Y-%m-%d"),
            "customer_type": random.choices(
                CUSTOMER_TYPES, weights=[0.65, 0.25, 0.10]
            )[0],
        })
    return rows


# 2. products.csv
def generate_products(n=N_PRODUCTS):
    rows = []
    for pid in range(1, n + 1):
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])
        base_name = f"{fake.word().capitalize()} {subcategory[:-1] if subcategory.endswith('s') else subcategory}"

        name = base_name
        # inject messy formatting into ~15% of product names
        if random.random() < 0.15:
            style = random.choice(["upper", "lower", "spaces", "both"])
            if style == "upper":
                name = name.upper()
            elif style == "lower":
                name = name.lower()
            elif style == "spaces":
                name = f"   {name}  "
            else:
                name = f"  {name.lower()}  "

        cost_price = round(random.uniform(3, 500), 2)
        rows.append({
            "product_id": pid,
            "product_name": name,
            "category": category,
            "subcategory": subcategory,
            "cost_price": cost_price,
        })
    return rows


# 3. orders.csv
def generate_orders(n=N_ORDERS, customer_ids=None):
    rows = []
    for oid in range(1, n + 1):
        order_dt = random_date()

        # date format issue: ~8% of rows use DD-MM-YYYY (no time component)
        if random.random() < 0.08:
            date_str = order_dt.strftime("%d-%m-%Y")
        else:
            date_str = order_dt.strftime("%Y-%m-%d %H:%M:%S")

        # 5% missing customer_id
        if random.random() < 0.05:
            cust_id = ""  # empty -> NULL
        else:
            cust_id = random.choice(customer_ids)

        region = random.choice(REGIONS)
        status = random.choices(ORDER_STATUSES, weights=ORDER_STATUS_WEIGHTS)[0]

        rows.append({
            "order_id": oid,
            "customer_id": cust_id,
            "order_date": date_str,
            "status": status,
            "region_code": region,
        })
    return rows, [r["order_id"] for r in rows]


# 4. order_items.csv
def generate_order_items(order_ids, product_rows):
    rows = []
    item_id = 1
    product_ids = [p["product_id"] for p in product_rows]
    price_lookup = {p["product_id"]: p["cost_price"] for p in product_rows}

    for oid in order_ids:
        n_items = random.randint(1, MAX_ITEMS_PER_ORDER)
        for _ in range(n_items):
            pid = random.choice(product_ids)
            cost = price_lookup[pid]
            # unit_price marked up 20%-80% over cost_price
            unit_price = round(cost * random.uniform(1.2, 1.8), 2)

            quantity = random.randint(1, 5)
            # 3% negative quantity -> represents a return
            if random.random() < 0.03:
                quantity = -abs(quantity)

            discount = random.choice([0, 0, 0, 5, 10, 15, 20, 25, 30])
            # occasionally inject an invalid discount > 100 to test edge-case handling
            if random.random() < 0.005:
                discount = random.choice([110, 150])

            rows.append({
                "order_item_id": item_id,
                "order_id": oid,
                "product_id": pid,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount_percent": discount,
            })
            item_id += 1

    # Referential integrity issue: add a few order_items pointing at
    # order_ids that were never generated in orders.csv
    max_oid = max(order_ids)
    for _ in range(15):
        fake_oid = max_oid + random.randint(1000, 5000)
        pid = random.choice(product_ids)
        cost = price_lookup[pid]
        rows.append({
            "order_item_id": item_id,
            "order_id": fake_oid,
            "product_id": pid,
            "quantity": random.randint(1, 3),
            "unit_price": round(cost * 1.4, 2),
            "discount_percent": random.choice([0, 10, 20]),
        })
        item_id += 1

    return rows


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {len(rows):>6} rows -> {path}")


def main():
    print("Generating e-commerce sample data (with intentional data-quality issues)...")
    os.makedirs("data", exist_ok=True)

    customers = generate_customers()
    customer_ids = [c["customer_id"] for c in customers]
    write_csv("data/customers.csv", customers,
              ["customer_id", "customer_name", "email", "registration_date", "customer_type"])

    products = generate_products()
    write_csv("data/products.csv", products,
              ["product_id", "product_name", "category", "subcategory", "cost_price"])

    orders, order_ids = generate_orders(customer_ids=customer_ids)
    write_csv("data/orders.csv", orders,
              ["order_id", "customer_id", "order_date", "status", "region_code"])

    order_items = generate_order_items(order_ids, products)
    write_csv("data/order_items.csv", order_items,
              ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])

    print("\nDone. Raw data is in ./data/")
    print("Known issues injected on purpose:")
    print(f"  - customers.csv : ~2% invalid emails")
    print(f"  - orders.csv    : ~5% missing customer_id, ~8% DD-MM-YYYY dates")
    print(f"  - order_items   : ~3% negative quantity, 15 rows with orphan order_id, a few discount_percent > 100")
    print(f"  - products.csv  : ~15% product_name with extra spaces / inconsistent case")


if __name__ == "__main__":
    main()
