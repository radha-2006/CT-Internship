
-- 1. Total revenue per category
SELECT
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 2. Top 10 customers by total order value
SELECT
    c.customer_id,
    c.customer_name,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_order_value
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_order_value DESC
LIMIT 10;


-- 3. Month-wise order count for the last 12 months
SELECT
    strftime('%Y-%m', order_date) AS order_month,
    COUNT(DISTINCT order_id) AS order_count
FROM orders
WHERE order_date >= date((SELECT MAX(order_date) FROM orders), '-12 months')
GROUP BY order_month
ORDER BY order_month;


-- 4. Customers who placed orders but never had any item delivered
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name
HAVING SUM(CASE WHEN o.status = 'DELIVERED' THEN 1 ELSE 0 END) = 0
ORDER BY total_orders DESC;


-- 5. Products that were ordered but had more returns than purchases

SELECT
    p.product_id,
    p.product_name,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS units_purchased,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS units_returned
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
HAVING units_returned > units_purchased
ORDER BY units_returned DESC;


-- 6. Return rate (returned items / total items) per category
SELECT
    p.category,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS returned_units,
    SUM(ABS(oi.quantity)) AS total_units,
    ROUND(
        100.0 * SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END)
        / NULLIF(SUM(ABS(oi.quantity)), 0), 2
    ) AS return_rate_pct
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;


WITH daily AS (
    SELECT
        o.region_code,
        date(o.order_date) AS order_day,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY o.region_code, order_day
)
SELECT
    region_code,
    order_day AS order_date,
    ROUND(daily_revenue, 2) AS daily_revenue,
    ROUND(SUM(daily_revenue) OVER (
        PARTITION BY region_code ORDER BY order_day
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS running_total
FROM daily
ORDER BY region_code, order_date;



WITH product_revenue AS (
    SELECT
        p.category,
        p.product_name,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY p.category, p.product_name
)
SELECT
    category,
    product_name,
    ROUND(total_revenue, 2) AS total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM product_revenue
ORDER BY category, rank_in_category;



WITH ordered AS (
    SELECT
        o.customer_id,
        o.order_date,
        LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS previous_order_date
    FROM orders o
    WHERE o.customer_id IS NOT NULL
),
gaps AS (
    SELECT
        customer_id,
        order_date,
        previous_order_date,
        CASE
            WHEN previous_order_date IS NOT NULL
            THEN CAST(julianday(order_date) - julianday(previous_order_date) AS INTEGER)
            ELSE NULL
        END AS days_gap
    FROM ordered
)
SELECT * FROM gaps ORDER BY customer_id, order_date;

-- ... and the "At Risk" flag, aggregated per customer:
WITH ordered AS (
    SELECT
        o.customer_id,
        o.order_date,
        LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS previous_order_date
    FROM orders o
    WHERE o.customer_id IS NOT NULL
),
gaps AS (
    SELECT
        customer_id,
        CASE
            WHEN previous_order_date IS NOT NULL
            THEN julianday(order_date) - julianday(previous_order_date)
            ELSE NULL
        END AS days_gap
    FROM ordered
)
SELECT
    customer_id,
    ROUND(AVG(days_gap), 1) AS avg_days_gap,
    CASE WHEN AVG(days_gap) > 30 THEN 'At Risk' ELSE 'Healthy' END AS risk_flag
FROM gaps
WHERE days_gap IS NOT NULL
GROUP BY customer_id
ORDER BY avg_days_gap DESC;


WITH monthly_revenue AS (
    SELECT
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS order_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS monthly_rev
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id, order_month
),
categorized AS (
    SELECT
        customer_id,
        order_month,
        monthly_rev,
        CASE
            WHEN monthly_rev > 10000 THEN 'High'
            WHEN monthly_rev >= 5000 THEN 'Medium'
            ELSE 'Low'
        END AS revenue_category
    FROM monthly_revenue
)
SELECT
    order_month,
    revenue_category,
    COUNT(DISTINCT customer_id) AS customer_count
FROM categorized
GROUP BY order_month, revenue_category
ORDER BY order_month, revenue_category;



WITH customer_ltv AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_value
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
)
SELECT
    customer_id,
    ROUND(total_value, 2) AS total_value,
    NTILE(4) OVER (ORDER BY total_value DESC) AS quartile,
    CASE NTILE(4) OVER (ORDER BY total_value DESC)
        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        WHEN 4 THEN 'Bronze'
    END AS quartile_label
FROM customer_ltv
ORDER BY total_value DESC;



WITH monthly AS (
    SELECT
        CAST(strftime('%Y', o.order_date) AS INTEGER) AS yr,
        CAST(strftime('%m', o.order_date) AS INTEGER) AS mo,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY yr, mo
)
SELECT
    m.yr AS year,
    m.mo AS month,
    ROUND(m.revenue, 2) AS revenue,
    ROUND(p.revenue, 2) AS prev_year_revenue,
    CASE
        WHEN p.revenue IS NULL OR p.revenue = 0 THEN NULL
        ELSE ROUND(100.0 * (m.revenue - p.revenue) / p.revenue, 2)
    END AS yoy_growth_percent
FROM monthly m
LEFT JOIN monthly p ON p.yr = m.yr - 1 AND p.mo = m.mo
ORDER BY year, month;



WITH customer_category_orders AS (
    SELECT
        o.customer_id,
        o.order_date,
        p.category,
        FIRST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id ORDER BY o.order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS first_category,
        LAST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id ORDER BY o.order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_category
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.customer_id IS NOT NULL
)
SELECT DISTINCT
    customer_id,
    first_category,
    last_category,
    CASE WHEN first_category <> last_category THEN 'Yes' ELSE 'No' END AS category_shift
FROM customer_category_orders
ORDER BY customer_id;



WITH customer_revenue AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
),
totals AS (
    SELECT SUM(revenue) AS grand_total FROM customer_revenue
)
SELECT
    cr.customer_id,
    ROUND(cr.revenue, 2) AS revenue,
    ROUND(SUM(cr.revenue) OVER (ORDER BY cr.revenue DESC
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_revenue,
    ROUND(100.0 * SUM(cr.revenue) OVER (ORDER BY cr.revenue DESC
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / t.grand_total, 2) AS cumulative_percent
FROM customer_revenue cr, totals t
ORDER BY revenue DESC;

WITH cohorts AS (
    SELECT
        customer_id,
        strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
customer_orders AS (
    SELECT
        o.customer_id,
        o.order_date,
        c.cohort_month
    FROM orders o
    JOIN cohorts c ON c.customer_id = o.customer_id
    WHERE o.customer_id IS NOT NULL
),
order_month_offset AS (
    SELECT
        customer_id,
        cohort_month,
        -- month index relative to the cohort month (0 = registration month, 1 = next month, ...)
        (CAST(strftime('%Y', order_date) AS INTEGER) * 12 + CAST(strftime('%m', order_date) AS INTEGER))
        - (CAST(substr(cohort_month, 1, 4) AS INTEGER) * 12 + CAST(substr(cohort_month, 6, 2) AS INTEGER))
        AS month_offset
    FROM customer_orders
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS cohort_customers
    FROM cohorts
    GROUP BY cohort_month
),
cohort_activity AS (
    SELECT
        cohort_month,
        month_offset,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM order_month_offset
    WHERE month_offset BETWEEN 0 AND 3
    GROUP BY cohort_month, month_offset
)
SELECT
    ca.cohort_month,
    ca.month_offset,
    ca.active_customers,
    cs.cohort_customers,
    ROUND(100.0 * ca.active_customers / cs.cohort_customers, 2) AS retention_rate_pct
FROM cohort_activity ca
JOIN cohort_size cs ON cs.cohort_month = ca.cohort_month
ORDER BY ca.cohort_month, ca.month_offset;


WITH order_totals AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_date,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS order_value,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS seq
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.order_id, o.customer_id, o.order_date
)
SELECT
    curr.customer_id,
    curr.order_id AS current_order_id,
    curr.order_date AS current_order_date,
    ROUND(curr.order_value, 2) AS current_order_value,
    prev.order_id AS previous_order_id,
    ROUND(prev.order_value, 2) AS previous_order_value,
    CASE
        WHEN prev.order_value IS NULL THEN 'First Order'
        WHEN curr.order_value > prev.order_value THEN 'Increased'
        WHEN curr.order_value < prev.order_value THEN 'Decreased'
        ELSE 'Flat'
    END AS spend_trend
FROM order_totals curr
LEFT JOIN order_totals prev
    ON prev.customer_id = curr.customer_id
   AND prev.seq = curr.seq - 1
ORDER BY curr.customer_id, curr.order_date;
