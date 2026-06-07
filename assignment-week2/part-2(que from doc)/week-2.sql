-- Databricks notebook source
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;

-- COMMAND ----------

CREATE TABLE customers (
    customer_id  INT,
    first_name   STRING,
    last_name    STRING,
    email        STRING,
    city         STRING,
    state        STRING,
    join_date    DATE,
    is_premium   BOOLEAN
) USING DELTA;

-- COMMAND ----------



-- COMMAND ----------

CREATE TABLE products (
    product_id   INT,
    product_name STRING,
    category     STRING,
    brand        STRING,
    unit_price   DECIMAL(10,2),
    stock_qty    INT
) USING DELTA;

-- COMMAND ----------

CREATE TABLE orders (
    order_id     INT,
    customer_id  INT,
    order_date   DATE,
    status       STRING,
    total_amount DECIMAL(12,2)
) USING DELTA;

-- COMMAND ----------

CREATE TABLE order_items (
    item_id      INT,
    order_id     INT,
    product_id   INT,
    quantity     INT,
    unit_price   DECIMAL(10,2),
    discount_pct DECIMAL(5,2)
) USING DELTA;

-- COMMAND ----------

INSERT INTO customers VALUES
(101,'Aarav','Sharma','aarav.s@email.com','Mumbai','Maharashtra','2024-01-15',true),
(102,'Priya','Patel','priya.p@email.com','Ahmedabad','Gujarat','2024-02-20',false),
(103,'Rohan','Gupta','rohan.g@email.com','Delhi','Delhi','2024-03-10',true),
(104,'Sneha','Reddy','sneha.r@email.com','Hyderabad','Telangana','2024-04-05',false),
(105,'Vikram','Singh','vikram.s@email.com','Jaipur','Rajasthan','2024-05-12',true),
(106,'Ananya','Iyer','ananya.i@email.com','Chennai','Tamil Nadu','2024-06-18',false),
(107,'Karan','Mehta','karan.m@email.com','Pune','Maharashtra','2024-07-22',true),
(108,'Divya','Nair','divya.n@email.com','Kochi','Kerala','2024-08-30',false);

-- COMMAND ----------

INSERT INTO products VALUES
(201,'Wireless Earbuds','Electronics','BoAt',1499.00,250),
(202,'Cotton T-Shirt','Clothing','Levis',799.00,500),
(203,'Smart Watch','Electronics','Noise',2999.00,150),
(204,'Running Shoes','Clothing','Nike',4599.00,120),
(205,'Bluetooth Speaker','Electronics','JBL',3499.00,200),
(206,'Bedsheet Set','Home','Spaces',1299.00,300),
(207,'Laptop Stand','Electronics','AmazonBasics',899.00,180),
(208,'Cushion Covers (Set)','Home','HomeCenter',599.00,400);

-- COMMAND ----------

INSERT INTO orders VALUES
(1001,101,'2024-08-01','Delivered',4498.00),
(1002,102,'2024-08-03','Delivered',799.00),
(1003,103,'2024-08-05','Shipped',7498.00),
(1004,101,'2024-08-10','Delivered',3499.00),
(1005,104,'2024-08-12','Cancelled',2999.00),
(1006,105,'2024-08-15','Delivered',5898.00),
(1007,106,'2024-08-18','Pending',1299.00),
(1008,103,'2024-08-20','Delivered',899.00),
(1009,107,'2024-08-25','Shipped',6098.00),
(1010,108,'2024-08-28','Delivered',1598.00);

-- COMMAND ----------

INSERT INTO order_items VALUES
(5001,1001,201,2,1499.00,0),
(5002,1001,207,1,899.00,10),
(5003,1002,202,1,799.00,0),
(5004,1003,203,1,2999.00,0),
(5005,1003,204,1,4599.00,5),
(5006,1004,205,1,3499.00,0),
(5007,1005,203,1,2999.00,0),
(5008,1006,201,1,1499.00,10),
(5009,1006,204,1,4599.00,5),
(5010,1007,206,1,1299.00,0),
(5011,1008,207,1,899.00,0),
(5012,1009,205,1,3499.00,0),
(5013,1009,208,2,599.00,15),
(5014,1010,206,1,1299.00,0),
(5015,1010,208,1,599.00,0);

-- COMMAND ----------

SELECT 'customers'  AS tbl, COUNT(*) AS rows FROM customers  UNION ALL
SELECT 'products',          COUNT(*)          FROM products   UNION ALL
SELECT 'orders',            COUNT(*)          FROM orders     UNION ALL
SELECT 'order_items',       COUNT(*)          FROM order_items;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Section A

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q1

-- COMMAND ----------

SELECT * FROM customers;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q2

-- COMMAND ----------

select first_name,last_name,city from customers;


-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q3

-- COMMAND ----------

select distinct category from products order by category;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q4

-- COMMAND ----------

-- Primary Keys:
-- customers  → customer_id
-- products   → product_id
-- orders     → order_id
-- order_items → item_id
--
-- A Primary Key must be UNIQUE so every row can be individually identified.
-- It must be NOT NULL because NULL means "unknown" — you cannot identify
-- a row with an unknown value. Together they guarantee every row has
-- a stable, unambiguous identity.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q5

-- COMMAND ----------

INSERT INTO customers VALUES (109,'Test','User','aarav.s@email.com','Delhi','Delhi','2024-09-01',false);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q6

-- COMMAND ----------

SELECT product_name, unit_price FROM products WHERE unit_price > 0;


-- COMMAND ----------

-- MAGIC %md
-- MAGIC Section-B

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q7

-- COMMAND ----------

SELECT * FROM orders WHERE status = 'Delivered';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q8

-- COMMAND ----------

SELECT product_id, product_name, brand, unit_price
FROM products
WHERE category = 'Electronics'
  AND unit_price > 2000
ORDER BY unit_price DESC;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q9

-- COMMAND ----------

SELECT customer_id, first_name, last_name, city, join_date
FROM customers
WHERE state = 'Maharashtra'
  AND join_date >= '2024-01-01'
  AND join_date <  '2025-01-01'
ORDER BY join_date;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q10

-- COMMAND ----------

SELECT order_id, customer_id, order_date, status, total_amount
FROM orders
WHERE order_date BETWEEN '2024-08-10' AND '2024-08-25'
  AND status <> 'Cancelled'
ORDER BY order_date;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q11

-- COMMAND ----------

SELECT order_id, customer_id, status, total_amount
FROM orders
WHERE order_date BETWEEN '2024-08-01' AND '2024-08-31';


-- COMMAND ----------

SELECT *
FROM customers
WHERE join_date >= '2024-01-01'
  AND join_date <  '2025-01-01';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Section C

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q13

-- COMMAND ----------

SELECT COUNT(*) AS total_orders FROM orders;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q14

-- COMMAND ----------

SELECT SUM(total_amount) AS delivered_revenue
FROM orders
WHERE status = 'Delivered';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q15

-- COMMAND ----------

SELECT category, ROUND(AVG(unit_price), 2) AS avg_unit_price
FROM products
GROUP BY category
ORDER BY avg_unit_price DESC;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q16

-- COMMAND ----------

SELECT status,
       COUNT(*)          AS order_count,
       SUM(total_amount) AS total_revenue
FROM orders
GROUP BY status
ORDER BY total_revenue DESC;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q17

-- COMMAND ----------

SELECT category,
       MAX(unit_price) AS most_expensive,
       MIN(unit_price) AS cheapest
FROM products
GROUP BY category
ORDER BY category;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q18

-- COMMAND ----------

SELECT category,
       ROUND(AVG(unit_price), 2) AS avg_price
FROM products
GROUP BY category
HAVING AVG(unit_price) > 2000
ORDER BY avg_price DESC;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Section D

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q19

-- COMMAND ----------

SELECT o.order_id, o.order_date,
       c.first_name, c.last_name,
       o.total_amount
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
ORDER BY o.order_date;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q20

-- COMMAND ----------

SELECT c.customer_id, c.first_name, c.last_name, c.city,
       o.order_id, o.order_date, o.status, o.total_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_id;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q21

-- COMMAND ----------

SELECT o.order_id,
       p.product_name,
       oi.quantity,
       oi.unit_price,
       oi.discount_pct,
       ROUND(oi.unit_price * oi.quantity * (1 - oi.discount_pct / 100), 2) AS line_total
FROM orders o
JOIN order_items oi ON o.order_id   = oi.order_id
JOIN products   p  ON oi.product_id = p.product_id
ORDER BY o.order_id;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q21

-- COMMAND ----------

SELECT o.order_id,
       p.product_name,
       oi.quantity,
       oi.unit_price,
       oi.discount_pct,
       ROUND(oi.unit_price * oi.quantity * (1 - oi.discount_pct / 100), 2) AS line_total
FROM orders o
JOIN order_items oi ON o.order_id   = oi.order_id
JOIN products   p  ON oi.product_id = p.product_id
ORDER BY o.order_id;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q22

-- COMMAND ----------

SELECT c.customer_id, c.first_name, o.order_id
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;

-- COMMAND ----------

SELECT c.customer_id, c.first_name, o.order_id
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q23

-- COMMAND ----------

SELECT o.order_id, o.customer_id, c.first_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Section E

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q24

-- COMMAND ----------

SELECT product_name,
       unit_price,
       CASE
           WHEN unit_price < 1000                THEN 'Budget'
           WHEN unit_price BETWEEN 1000 AND 3000 THEN 'Mid-Range'
           ELSE                                       'Premium'
       END AS price_tier
FROM products
ORDER BY unit_price;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q25

-- COMMAND ----------

SELECT
    SUM(CASE WHEN status = 'Delivered'  THEN 1 ELSE 0 END) AS delivered_count,
    SUM(CASE WHEN status <> 'Delivered' THEN 1 ELSE 0 END) AS not_delivered_count
FROM orders;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q26

-- COMMAND ----------

-- ACID Properties:
-- A - Atomicity:   All steps in a transaction succeed or ALL are rolled back.
--                  Bank transfer: if debit succeeds but credit fails → money vanishes.
--                  Atomicity ensures BOTH happen or NEITHER does.
--
-- C - Consistency: DB moves from one valid state to another. Rules always enforced.
--                  Total money before transfer = total money after transfer.
--
-- I - Isolation:   Concurrent transactions don't interfere with each other.
--                  Two clerks updating the same account see consistent balances.
--
-- D - Durability:  Once COMMITted, changes survive crashes/power cuts.
--                  Your confirmed bank transfer won't disappear after a reboot.
SELECT 'See comment above for ACID explanation' AS answer;


-- COMMAND ----------

-- MAGIC %md
-- MAGIC Q27
-- MAGIC

-- COMMAND ----------

INSERT INTO orders VALUES (1011, 102, CURRENT_DATE, 'Pending', 1598.00);


-- COMMAND ----------

INSERT INTO order_items VALUES (5016, 1011, 206, 1, 1299.00, 0);


-- COMMAND ----------

INSERT INTO order_items VALUES (5017, 1011, 208, 1, 599.00, 0);


-- COMMAND ----------

UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 206;


-- COMMAND ----------

UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 208;


-- COMMAND ----------

SELECT o.order_id, o.status, oi.product_id, oi.quantity, p.stock_qty
FROM orders o
JOIN order_items oi ON o.order_id   = oi.order_id
JOIN products   p  ON oi.product_id = p.product_id
WHERE o.order_id = 1011;