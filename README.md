# Weekly Summary

## WEEK 1
1. I utilized pandas to import a shopping dataset (which I have downloaded from Kaggle) from a CSV file. Subsequently, I previewed the first and last five rows to understand the data.
2. I examined the shapes, column names and types of my dataset to get a better understanding of the data within it.
3. I acquired the initial row, followed by alternate rows, and eventually the first 7 rows.
4. I inspected the counts and percentages of the missing values in all the columns to see if any data is missing.
5. The total number of missing values in the dataset to visualize the distribution of missing values and duplicates.
6. Eliminated any repeated rows from the data.
7. Wherever missing, the size of the product was filled with "Not Applicable."
8. Price was imputed using median grouped by product.
9. Quantity, customer age, and rating were all filled with median value where applicable.
10. Filled the colour, payment method, customer gender, and location with the most frequent value.
11. Reformatted the purchase date column into proper date-time format.
12. Applied conditions to filter data in different situations such as price, category, location, gender, rating.
13. Organized garments according to their sales price and returned top 5 most expensive.
14. A new data column, total amount, was created by multiplying the price and quantity of Clothing. These values were rounded off to 2 digits after decimal.
15. The final cleaned dataset is exported as `cleaned_data.csv` for further usage.

## WEEK 2

### Part 1 — Superstore (Kaggle Dataset)
1. **Load Dataset** — I downloaded the Superstore CSV from Kaggle and loaded it into MySQL. The table has 21 columns and I successfully loaded 9,994 rows of sales data ranging from 2014 to 2017.
2. **Explore the Table** — I looked at the structure of the table using `DESCRIBE` to understand what columns exist and what type of data they hold. I also confirmed the total row count is 9,994.
3. **WHERE Filters** — I filtered the data in 4 different ways: by Region (only West region orders), by Category (only Technology products), by Date (only orders from 2017), and by Sales amount (only orders above $1000).
4. **GROUP BY Aggregations** — I grouped the data to find totals and averages. Technology had the highest total sales ($836K), Office Supplies had the most quantity sold (22,906 items), and Home Office customers had the highest average sales per order ($240).
5. **Sort & Limit** — I found the Top 10 products and top categories by sales. Canon imageCLASS Copier was the #1 product with $61,599 in sales. Phones was the top sub-category with $330,007 in sales.
6. **Use Cases** — I solved 3 business problems: Monthly trends showed sales peak every September and November. The top customer was Sean Miller with $25,043 in purchases. The duplicate check found 8 order-product combinations appearing more than once in the data.
7. **Validate Results** — I confirmed the data quality: total rows are 9,994, zero NULL values in all key columns, zero negative sales, zero invalid discounts, and the date range is correctly from January 2014 to December 2017.

### Part 2 — ShopEase (Document Questions)
1. **Section A — SQL Basics**: I created 4 tables (customers, products, orders, order_items) and loaded all the sample data. I retrieved all customer records, selected specific columns, and listed the 3 unique product categories available, which are Clothing, Electronics, and Home.
2. **Section B — Filtering & Indexes**: I filtered orders by status to get only Delivered orders, filtered Electronics products priced above ₹2000, found customers from Maharashtra who joined in 2024, and retrieved all non-cancelled orders placed between August 10 and August 25. I also explained how indexes make date-based searches faster by avoiding full table scans.
3. **Section C — Aggregation**: I counted a total of 10 orders and found that the total revenue from Delivered orders was ₹17,191. I calculated the average price per category and ranked all order statuses by revenue. Delivered orders led with ₹17,191 followed by Shipped at ₹13,596.
4. **Section D — Joins**: I combined data from multiple tables using INNER JOIN to show orders with customer names, LEFT JOIN to list all customers even those without any orders, and a 3-table JOIN connecting orders, order items, and products together. I also explained the difference between LEFT JOIN, RIGHT JOIN, and FULL OUTER JOIN with examples.
5. **Section E — Advanced Concepts**: I classified all products into Budget, Mid-Range, and Premium price tiers using a CASE statement. I counted 6 Delivered vs 4 Not Delivered orders displayed in a single row. I explained all 4 ACID properties using a real-world bank transfer example. Finally, I wrote a complete transaction that inserted a new order, added 2 order items, and updated the stock quantity — all wrapped safely with COMMIT and ROLLBACK to ensure data integrity.

## WEEK 3
1. Performed comprehensive customer sales analysis using SQL on a structured retail dataset.
2. Cleaned and transformed raw data into normalized tables for efficient querying.
3. Leveraged advanced SQL techniques including joins, subqueries, common table expressions (CTEs), and window functions.
4. Analyzed customer performance by identifying top 5 and bottom 5 customers based on total sales.
5. Explored customer behavior patterns by detecting customers with only a single transaction.
6. Evaluated revenue distribution by filtering customers with above-average sales contribution.
7. Derived key metrics such as highest order value per customer to highlight peak transactions.
8. Applied ranking and aggregation techniques to generate meaningful business insights.
9. Compiled all queries, outputs, and analytical findings into a single well-documented deliverable suitable for reporting and review.

## WEEK 4
1. **Task 1**: Created Resource Group `rg-adf-assignment`.
2. **Task 2**: Created Storage Account `stadfassign001`, uploaded CSV to `source-container`, made `destination-container`.
3. **Task 3**: Created ADF `adf-assignment-demo`, set up Linked Service + source/destination datasets, ran Get Metadata activity successfully.
4. **Task 4**: Built pipeline `pl_copy_csv` (Get Metadata → Copy Data).
5. **Task 5**: Ran pipeline via Debug — Succeeded, file confirmed in destination.
6. **Task 6**: Owner role already covers Reader/Contributor; assigned Storage Blob Data Contributor to ADF's managed identity for storage access.
7. **Mini Project**: Fully satisfied by the same pipeline — CSV copied end-to-end with metadata validated.

## WEEK 5
1. Set up PySpark 3.5.1 with Java 11 on Google Colab, created a SparkSession and loaded a 1000-row dataset with 13 columns.
2. Learned how Spark solves MapReduce limitations like disk I/O, no caching, and high latency using in-memory processing and DAG execution.
3. Simulated ML training with `cache()`, showing only the first iteration reads from disk and the rest read from RAM.
4. Removed duplicates using `dropDuplicates()` on specific columns and verified row counts before and after.
5. Handled nulls using `na.drop()` to delete rows and `na.fill()` to replace with defaults, knowing both give different aggregation results.
6. Chained `filter()`, `groupBy()`, and `agg()` to compute avg, min, max, and stddev across categories in a single pass.
7. Understood that DataFrames are immutable, so every transformation returns a new DataFrame and must be reassigned.
8. Learned that wide transformations like `groupBy()` and `join()` trigger a Shuffle, moving data across the network between executors.
9. Compared `inferSchema=True` vs explicit schema, saw silent null risks with mixed dates, and cast a string column to TimestampType.
10. Built a full pipeline removing duplicates, filling null prices with 0, and grouping by `store_id`, giving a grand total revenue of $709,924.32.

## WEEK 6
1. Loaded dataset with multiple columns and handled null values.
2. Learned Spark architecture (Driver, Executors, Cluster Manager).
3. Understood lazy evaluation and Catalyst Optimizer.
4. Performed transformations like select, filter, rename, and casting.
5. Cleaned data by removing nulls and creating new columns.
6. Compared CSV vs Parquet (Parquet is faster and optimized).
7. Used filtering and aggregation (sum, avg, count).
8. Wrote data to CSV after filtering.
9. Learned Spark writes multiple output files (part files).
10. Practiced optimization techniques like column selection and predicate pushdown.

## WEEK 7
1. Loaded the Superstore dataset into Delta Lake on Databricks.
2. Cleaned the data (checked/handled nulls and duplicates).
3. Simulated an incremental batch of updates and new records.
4. Used `MERGE INTO` to implement SCD Type 1 (overwrite).
5. Used `MERGE INTO` to implement SCD Type 2 (history tracking).
6. Validated results with row-count and duplicate checks.
7. Built a separate Pandas notebook to explore and clean the same dataset.
8. Created a derived `total_amount` column.
9. Exported a cleaned CSV file.
10. Prepared notebooks and outputs for GitHub submission.
