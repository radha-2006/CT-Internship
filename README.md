# Summary:
WEEK-1:
- I utilized pandas to import a shopping dataset(which i have downloaded it from kaggle) from a CSV file. Subsequently, I previewed the first and last five rows to understand the data.
- I examined the shapes, column names and types of my dataset to get a better understanding of the data within it.
- I acquired the initial row, followed by alternate rows, and eventually the first 7 rows.
- I inspected the counts and percentages of the missing value in all the columns to see if any data is missing
- The total number of missing values in the dataset to visualize the distribution of missing values and duplicates.
- Eliminated any repeated rows from the data.
- Wherever missing, the size of the product was filled with "Not Applicable".
- Price was imputed using median grouped by product.
- Quantity, customer age and rating were all filled with median value where applicable.
- Filled the colour, payment method, costumer gender and location with the most frequent value.
- Reformatted the purchase date column into proper date-time format.
- Applied condition to filter data in different situations such as price, category, location, gender, rating.
- Organized garments according to their sales price and returned top 5 most expensive.
- A new in data column total amount was created by multiplying the price and quantity of Clothing.  These values were rounded off to 2 digits after decimal.
- The final cleaned dataset is exported as cleaned_data.csv for further usage.

WEEK-2:
PART-1:
Superstore (Kaggle Dataset)

-Step 1 — Load Dataset

I downloaded the Superstore CSV from Kaggle and loaded it into MySQL. The table has 21 columns and I successfully loaded 9,994 rows of sales data ranging from 2014 to 2017.

-Step 2 — Explore the Table

I looked at the structure of the table using DESCRIBE to understand what columns exist and what type of data they hold. I also confirmed the total row count is 9,994.

-Step 3 — WHERE Filters

I filtered the data in 4 different ways — by Region (only West region orders), by Category (only Technology products), by Date (only orders from 2017), and by Sales amount (only orders above $1000).

-Step 4 — GROUP BY Aggregations

I grouped the data to find totals and averages. Technology had the highest total sales ($836K), Office Supplies had the most quantity sold (22,906 items), and Home Office customers had the highest average sales per order ($240).

-Step 5 — Sort & Limit

I found the Top 10 products and top categories by sales. Canon imageCLASS Copier was the #1 product with $61,599 in sales. Phones was the top sub-category with $330,007 in sales.

-Step 6 — Use Cases

I solved 3 business problems — Monthly trends showed sales peak every September and November. The top customer was Sean Miller with $25,043 in purchases. The duplicate check found 8 order-product combinations appearing more than once in the data.

-Step 7 — Validate Results

I confirmed the data quality — total rows are 9,994, zero NULL values in all key columns, zero negative sales, zero invalid discounts, and the date range is correctly from January 2014 to December 2017.

PART-2:
ShopEase(Document questions)

-Section A — SQL Basics

I created 4 tables (customers, products, orders, order_items) and loaded all the sample data. I retrieved all customer records, selected specific columns, and listed the 3 unique product categories available which are Clothing, Electronics, and Home.

-Section B — Filtering & Indexes

I filtered orders by status to get only Delivered orders, filtered Electronics products priced above ₹2000, found customers from Maharashtra who joined in 2024, and retrieved all non-cancelled orders placed between August 10 and August 25. I also explained how indexes make date-based searches faster by avoiding full table scans.

-Section C — Aggregation

I counted a total of 10 orders and found that the total revenue from Delivered orders was ₹17,191. I calculated the average price per category and ranked all order statuses by revenue. Delivered orders led with ₹17,191 followed by Shipped at ₹13,596.

-Section D — Joins

I combined data from multiple tables using INNER JOIN to show orders with customer names, LEFT JOIN to list all customers even those without any orders, and a 3-table JOIN connecting orders, order items, and products together. I also explained the difference between LEFT JOIN, RIGHT JOIN, and FULL OUTER JOIN with examples.

-Section E — Advanced Concepts

I classified all products into Budget, Mid-Range, and Premium price tiers using a CASE statement. I counted 6 Delivered vs 4 Not Delivered orders displayed in a single row. I explained all 4 ACID properties using a real-world bank transfer example. Finally I wrote a complete transaction that inserted a new order, added 2 order items, and updated the stock quantity — all wrapped safely with COMMIT and ROLLBACK to ensure data integrity.
