# Databricks notebook source
# MAGIC %md
# MAGIC Q1: Explain the roles of the Driver, Cluster Manager, and Executor in a Spark application. 

# COMMAND ----------

# MAGIC %md
# MAGIC ans: 
# MAGIC Driver: Runs the main() function, builds the DAG from your PySpark code, and schedules tasks.
# MAGIC Cluster Manager: Allocates CPU/memory across the cluster (YARN, Kubernetes, Standalone).
# MAGIC Executor: Runs the actual tasks on worker nodes and reports results back to the Driver.

# COMMAND ----------

# MAGIC %md
# MAGIC Q2: How does Spark’s Lazy Evaluation strategy improve performance when chain-processing large datasets? 

# COMMAND ----------

# MAGIC %md
# MAGIC ans: Spark delays execution of transformations until an action is called. This lets the Catalyst Optimizer view the entire chain at once and optimize it — reordering filters, pruning unused columns, and fusing steps into fewer passes over the data — before anything actually runs.

# COMMAND ----------

# MAGIC %md
# MAGIC Q3: Write a Spark command to read a CSV file located at "data/source.csv", ensuring the first row is treated as a header and inferSchema is enabled. 

# COMMAND ----------

df = spark.read \
    .option("inferSchema", "true") \
    .option("header", "true") \
    .csv("/Volumes/dbacademy/default/raw_data/week5_dataset_1000.csv")

# COMMAND ----------

df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC Q4: What is the difference between CSV and Parquet in terms of storage (row-based vs. columnar) and why does it matter for performance? 

# COMMAND ----------

# MAGIC %md
# MAGIC ans:n CSV is a row based format where data is stored line by line. It does not store schema information, so Spark must infer data types every time it reads the file.
# MAGIC
# MAGIC Parquet is a columnar format. It stores data column by column and includes schema metadata. This makes it more efficient for analytics.
# MAGIC
# MAGIC Parquet files are smaller in size due to compression and encoding. They also allow Spark to read only the required columns instead of the entire dataset, which improves performance significantly.

# COMMAND ----------

# MAGIC %md
# MAGIC Q5: Given a DataFrame df, write a query to select the columns product_id and price where the category is 'Electronics'.

# COMMAND ----------

from pyspark.sql.functions import col

df.select("user_id", "price") \
  .filter(col("product_category") == "Electronics") \
  .show()

# COMMAND ----------

# MAGIC %md
# MAGIC Q6: Write the code to "revise" a DataFrame by renaming the column old_name to new_name and casting the price column from a String to a Double

# COMMAND ----------

df_revised = df.withColumnRenamed("price", "item_price")

# COMMAND ----------

# MAGIC %md
# MAGIC Q7: How does Spark use the Lineage Graph (DAG) to provide fault tolerance if a worker node fails? 

# COMMAND ----------

# MAGIC %md
# MAGIC ans: Spark records every transformation as a lineage graph. If a worker holding a partition of week5_dataset_1000.csv fails mid-job, Spark recomputes only that lost partition by replaying the transformations from the original file — no full re-read or data replication needed.

# COMMAND ----------

# MAGIC %md
# MAGIC Q8: Write a query to filter a DataFrame df_orders for rows where the status is 'Completed' AND the amount is greater than 1000. 

# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

import pyspark.sql.functions as F
df.filter((F.col("status") == "active") & (F.col("price") > 1000))

# COMMAND ----------

# MAGIC %md
# MAGIC Q9: Explain the concept of Predicate Pushdown in Parquet and how it affects the amount of data loaded into memory. 

# COMMAND ----------

df.write.mode("overwrite") \
  .parquet("/Volumes/dbacademy/default/raw_data/week5_parquet/")

# COMMAND ----------

from pyspark.sql import functions as F

df_parquet = spark.read.parquet(
    "/Volumes/dbacademy/default/raw_data/week5_parquet/"
)

df_parquet.filter(F.col("price") > 1000).show()

df_parquet.filter(F.col("price") > 1000).explain(True)
df_parquet.filter(F.col("price") > 1000).select("user_id", "price", "product_category")


# COMMAND ----------

# MAGIC %md
# MAGIC Predicate pushdown is an optimization where filtering is applied as early as possible, ideally while reading the data from disk.
# MAGIC
# MAGIC Parquet supports this by storing metadata such as minimum and maximum values for each column in blocks of data.
# MAGIC
# MAGIC When you filter on a column like price, Spark can skip entire blocks that do not meet the condition. This reduces disk input and speeds up queries.

# COMMAND ----------

# MAGIC %md
# MAGIC Q10: Write a code snippet to add a new column final_price which is the base_price multiplied by 1.18 (18% tax). 

# COMMAND ----------

df_with_tax = df.withColumn("final_price", F.round(F.col("price") * 1.18, 2))

# COMMAND ----------

# MAGIC %md
# MAGIC Q11: What is the difference between Transformations and Actions? Provide two examples of each. 

# COMMAND ----------

# MAGIC %md
# MAGIC Transformations are operations that define how data should be processed. They are not executed immediately.
# MAGIC
# MAGIC Examples include selecting columns, filtering rows, and adding new columns.
# MAGIC
# MAGIC Actions trigger the actual execution of the job and return results or write data to storage.
# MAGIC
# MAGIC Examples include displaying data, counting rows, and saving output

# COMMAND ----------

# MAGIC %md
# MAGIC Q12: Write the Spark command to load a Parquet file from "path/to/input", filter out any rows where user_id is null, and save the result as a CSV at "path/to/output". 

# COMMAND ----------

from pyspark.sql.functions import col

f = spark.read.parquet("/Volumes/dbacademy/default/raw_data/week5_parquet/")


df_filtered = f.filter(col("user_id").isNotNull())

df_filtered.write \
    .option("header", "true") \
    .mode("overwrite") \
    .csv("/Volumes/dbacademy/default/raw_data/output/")

# COMMAND ----------

# MAGIC %md
# MAGIC A common workflow in Spark involves reading data from a Parquet file, cleaning it by removing null values, and writing the result to another format such as CSV.
# MAGIC
# MAGIC This demonstrates a typical extract, transform, and load process used in real world data engineering.

# COMMAND ----------

# MAGIC %md
# MAGIC Q13: In Spark Architecture, what is the difference between Client Mode and Cluster Mode? 

# COMMAND ----------

# MAGIC %md
# MAGIC In client mode, the Driver runs on your local machine. This is useful for development and debugging because you can directly see logs and results.
# MAGIC
# MAGIC In cluster mode, the Driver runs inside the cluster. This is better for production workloads because the job continues running even if your local machine disconnects.

# COMMAND ----------

# MAGIC %md
# MAGIC Q14: Write a query to filter a dataset for rows where the region is 'North' OR the priority is 'High'. 

# COMMAND ----------

df.filter((F.col("region") == "West") | (F.col("subscription") == "Premium"))

# COMMAND ----------

# MAGIC %md
# MAGIC Spark also supports combining conditions using logical OR.
# MAGIC
# MAGIC For example, you can retrieve rows where either the region matches a specific value or the subscription type meets a condition. This helps in building flexible queries.

# COMMAND ----------

# MAGIC %md
# MAGIC Q15: When exploring a dataset, why is it safer to use .show(5) instead of .collect() on a multi-terabyte dataset? 

# COMMAND ----------

# MAGIC %md
# MAGIC The show operation displays a limited number of rows and is safe to use even with large datasets.
# MAGIC
# MAGIC The collect operation retrieves all data to the Driver. This can cause memory issues if the dataset is large.
# MAGIC
# MAGIC It is always better to use show when you only need a quick preview of the data.