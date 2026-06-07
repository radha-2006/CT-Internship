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
