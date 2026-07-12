# Delta Lake Incremental Processing Assignment

## Objective

In this assignment, I implemented incremental data processing using Delta Lake on Databricks. The goal was to load a dataset into Delta tables, perform data cleaning, simulate incremental data ingestion, and apply MERGE operations to handle both SCD Type 1 (overwrite) and SCD Type 2 (historical tracking).

## Project Structure

delta-lake-assignment/
│
├── data/
│ ├── customer_master.csv
│ └── customer_incremental.csv
│
├── notebooks/
│ └── delta_scd_assignment.py
│
├── screenshots/
│ ├── data_loading/
│ ├── data_cleaning/
│ ├── scd1/
│ ├── scd2/
│ ├── validation/
│ └── final_output/
│
├── report/
│ └── assignment_summary.pdf
│
└── README.md

## How I Ran This in Databricks

1. Uploaded the notebook via Workspace → Import and selected the source file.
2. Uploaded both CSV files using Data → Add Data → Upload File.
3. Stored files in a Unity Catalog volume and used the path:
   /Volumes/dbacademy/default/raw_data/
4. Set the data path in the notebook:

DATA_PATH = "/Volumes/dbacademy/default/raw_data/"

5. Attached compute and ran all cells.
6. Captured screenshots at each stage and organized them into respective folders.

## What I Implemented

### 1. Data Loading (Bronze Layer)

Loaded customer_master.csv into a Delta table named customers_bronze.

### 2. Data Cleaning (Silver Layer)

- Removed duplicate records
- Dropped rows with null primary keys
- Filled missing values (email, city)
- Converted date columns

Stored cleaned data in customers_silver.

### 3. Incremental Data Processing

Loaded customer_incremental.csv and identified updated and new records.

### 4. SCD Type 1 Implementation

Used MERGE with:

- whenMatchedUpdateAll()
- whenNotMatchedInsertAll()

This keeps only the latest data (no history).

### 5. SCD Type 2 Implementation

- Expired old records (is_current = false)
- Inserted new versions
- Maintained effective dates

This preserves full history.

### 6. Validation

- Checked row counts
- Ensured no duplicate keys
- Verified updates and inserts

### 7. Final Output

Displayed both SCD1 and SCD2 tables along with summary results.

## GitHub Upload

cd delta-lake-assignment
git init
git add .
git commit -m "Delta Lake incremental processing assignment (SCD1 + SCD2)"
git branch -M main
git remote add origin [https://github.com/](https://github.com/)<my-username>/<my-repo>.git
git push -u origin main

## Key Learnings

- Implemented Delta Lake MERGE operations
- Understood SCD Type 1 vs Type 2
- Worked with Unity Catalog volumes (/Volumes/...)
- Built an end-to-end incremental ETL pipeline
- Performed data validation and quality checks
