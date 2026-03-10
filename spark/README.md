# Spark Environment Setup on Google Cloud VM

This repository documents the steps I followed to provision a development environment on a Google Cloud Platform virtual machine. The goal was to build a Linux-based (Ubuntu) data science workspace leveraging Java, Apache Spark, PySpark, and Jupyter notebooks. This README is written with recruiters and collaborators in mind, showcasing my ability to perform infrastructure setup, remote development, and Python data tooling.

## ✅ Provisioning the VM
1. **Create a VM instance** in Google Cloud Console using an Ubuntu distribution.
2. **Enable SSH access** and connect via Visual Studio Code's Remote - SSH extension, allowing me to work as if the code were local.

## 🛠️ Installing Dependencies
Once connected to the Linux machine, I executed the following steps to prepare the environment:

### Java (OpenJDK)
```bash
# Download and extract OpenJDK 11
wget https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
tar xzfv openjdk-11.0.2_linux-x64_bin.tar.gz
rm openjdk-11.0.2_linux-x64_bin.tar.gz

# Configure environment variables
export JAVA_HOME="${HOME}/spark/jdk-11.0.2"
export PATH="${JAVA_HOME}/bin:${PATH}"
```
These variables were added to `~/.bashrc` so they are set automatically whenever a new terminal session opens.

### Apache Spark & PySpark
```bash
# Download and unpack Spark
wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar xzfv spark-3.5.0-bin-hadoop3.tgz
rm spark-3.5.0-bin-hadoop3.tgz

# Update environment
export SPARK_HOME="${HOME}/spark/spark-3.5.0-bin-hadoop3"
export PATH="${SPARK_HOME}/bin:${PATH}"
```
Adding these exports to `~/.bashrc` enables the `pyspark` command anywhere in the terminal.

### Python, Jupyter, and Pandas
```bash
sudo apt update
sudo apt install -y python3-pip python3-pandas
pip3 install jupyter
```
I launched PySpark with Jupyter support using:
```bash
PYSPARK_DRIVER_PYTHON=jupyter \\
PYSPARK_DRIVER_PYTHON_OPTS="notebook" \\
$SPARK_HOME/bin/pyspark
```
This opened a notebook server directly tied to the Spark context.

## 🔄 Shell Configuration
The `.bashrc` file was updated to include:
```bash
# Java and Spark environment variables
export JAVA_HOME="${HOME}/spark/jdk-11.0.2"
export SPARK_HOME="${HOME}/spark/spark-3.5.0-bin-hadoop3"
export PATH="${JAVA_HOME}/bin:${SPARK_HOME}/bin:${PATH}"
```
With these lines, every new shell session is ready for Spark development without manual configuration.

## 🎯 Outcome
This setup demonstrates proficiency in:
- Cloud infrastructure provisioning (GCP VM)
- Remote development using VS Code SSH
- Installing and configuring Java and Apache Spark on Ubuntu
- Integrating Spark with Python via PySpark and Jupyter
- Managing environment variables for reproducible workflows

---

## 📚 Spark Concepts & Tutorials

This directory contains several Jupyter notebooks that demonstrate key PySpark concepts:

### 1️⃣ **Reading and Writing Files**

#### Reading CSV Files
```python
# Basic CSV read
df = spark.read \
    .option("header", "true") \
    .csv('path/to/file.csv')

# CSV read with specified schema
df = spark.read \
    .option("header", "true") \
    .schema(my_schema) \
    .csv('path/to/file.csv')
```

#### Reading Parquet Files
```python
# Read parquet file or directory
df = spark.read.parquet('path/to/parquet/file')

# Read multi-level parquet directories
df = spark.read.parquet('data/pq/green/*/*')
```

#### Writing Files in Different Formats
```python
# Write as Parquet (columnar format, highly compressed)
df.write.parquet('output/path/')

# Write with repartitioning
df.repartition(24).write.parquet('output/path/')

# Write with coalesce (reduce partitions) and overwrite mode
df.coalesce(1).write.parquet('output/path/', mode='overwrite')
```

**When to use each format:**
- **CSV**: Human-readable, easier to inspect, but larger file size
- **Parquet**: Compressed, faster for analytics, preserves schema, recommended for data lakes

---

### 2️⃣ **Working with Schema**

#### Understanding DataFrame Schema
```python
# Display schema in tree format
df.printSchema()

# Get schema object
schema = df.schema
```

#### Defining Custom Schema
```python
from pyspark.sql import types

my_schema = types.StructType([
    types.StructField("VendorID", types.IntegerType(), True),
    types.StructField("pickup_datetime", types.TimestampType(), True),
    types.StructField("trip_distance", types.DoubleType(), True),
    types.StructField("payment_type", types.IntegerType(), True),
    types.StructField("service_type", types.StringType(), True)
])
```

#### Inferring Schema from Pandas
```python
import pandas as pd

df_pandas = pd.read_csv('sample.csv', nrows=1000)
spark_schema = spark.createDataFrame(df_pandas).schema
```

#### Schema Field Types
- `StringType()` - Text data
- `IntegerType()` - Integer numbers
- `DoubleType()` - Floating-point numbers
- `TimestampType()` - Date and time
- `BooleanType()` - True/False values
- `ArrayType()` - Lists/arrays
- `MapType()` - Key-value pairs
- `StructType()` - Nested structures

**Benefits of defining schema:**
- Ensures correct data types
- Improves performance (no type inference needed)
- Provides validation of incoming data
- Enables reproducible data pipelines

---

### 3️⃣ **Spark SQL Queries**

#### Registering Temporary Tables
```python
# Register DataFrame as a temporary table
df.registerTempTable('trips_data')

# Now you can write SQL queries
spark.sql("""
    SELECT * FROM trips_data LIMIT 10
""").show()
```

#### Common Spark SQL Operations
```python
# Aggregations with GROUP BY
spark.sql("""
    SELECT 
        service_type,
        COUNT(1) as trip_count,
        AVG(trip_distance) as avg_distance,
        SUM(total_amount) as total_revenue
    FROM
        trips_data
    GROUP BY 
        service_type
""").show()

# Date truncation
spark.sql("""
    SELECT 
        date_trunc('month', pickup_datetime) as month,
        SUM(fare_amount) as monthly_fare
    FROM
        trips_data
    GROUP BY
        date_trunc('month', pickup_datetime)
""").show()

# Complex aggregations with multiple calculations
spark.sql("""
    SELECT 
        PULocationID AS revenue_zone,
        DATE_TRUNC('month', pickup_datetime) AS revenue_month, 
        service_type,
        SUM(fare_amount) AS total_fare,
        SUM(tip_amount) AS total_tips,
        AVG(passenger_count) AS avg_passengers,
        COUNT(1) AS trip_count
    FROM
        trips_data
    GROUP BY
        1, 2, 3
    ORDER BY
        revenue_month DESC
""").show()
```

#### Combining with DataFrame API
```python
# Register table, run SQL, and continue with DataFrame operations
result_df = spark.sql("""
    SELECT service_type, COUNT(*) as count
    FROM trips_data
    GROUP BY service_type
""")

# Further transformations on SQL results
result_df.write.parquet('output/results/')
```

---

### 4️⃣ **Parquet Format & Data Organization**

#### Why Parquet?
- **Columnar storage**: Only read the columns you need
- **Compression**: Reduce storage by 10-100x
- **Schema preservation**: Maintains data types
- **Efficient for analytics**: Much faster than CSV for queries
- **Partitioning support**: Organize data by date, region, etc.

#### Writing Partitioned Parquet Data
```python
# Write with 4 partitions
df.repartition(4).write.parquet('data/output/')

# Process and convert multiple files
for month in range(1, 13):
    input_path = f'data/raw/green/2020/{month:02d}/'
    output_path = f'data/pq/green/2020/{month:02d}/'
    
    df = spark.read \
        .option("header", "true") \
        .schema(green_schema) \
        .csv(input_path)
    
    df.repartition(4).write.parquet(output_path)
```

---

### 5️⃣ **Transformations & Actions**

#### Lazy Transformations (Not executed immediately)
```python
# These operations create a recipe but don't execute
df_transformed = df \
    .select('pickup_datetime', 'dropoff_datetime', 'PULocationID') \
    .filter(df.hvfhs_license_num == 'HV0003') \
    .withColumn('pickup_date', F.to_date(F.col('pickup_datetime')))
```

#### Eager Actions (Execute immediately)
```python
# These operations trigger computation
df.show()           # Display rows
df.head(5)          # Get first 5 rows
df.count()          # Count rows
df.write.parquet('path/')  # Write to file
df.collect()        # Get all data (careful with large datasets!)
```

#### Column Transformations
```python
from pyspark.sql import functions as F

df_transformed = df \
    .withColumn('pickup_date', F.to_date(F.col('pickup_datetime'))) \
    .withColumnRenamed('tpep_pickup_datetime', 'pickup_datetime') \
    .withColumn('service_type', F.lit('green'))  # Add constant column
```

---

### 6️⃣ **DataFrames Operations**

#### Selecting & Filtering
```python
# Select specific columns
df.select('pickup_datetime', 'PULocationID', 'DOLocationID').show()

# Filter rows
df.filter(df.fare_amount > 10).show()

# Using set operations for column intersection
common_cols = set(df_green.columns) & set(df_yellow.columns)
df.select(list(common_cols)).show()
```

#### Union Operations
```python
# Combine two DataFrames with same schema
combined_df = df_green_sel.unionAll(df_yellow_sel)

# Calculate union statistics
combined_df.groupBy('service_type').count().show()
```

#### Column Statistics
```python
# Get all columns
df.columns

# Print schema
df.printSchema()

# Count rows
df.count()
```

---

### 7️⃣ **User Defined Functions (UDF)**

#### Creating Custom UDFs
```python
from pyspark.sql import types

def custom_logic(base_num):
    num = int(base_num[1:])
    if num % 7 == 0:
        return f's/{num:03x}'
    elif num % 3 == 0:
        return f'a/{num:03x}'
    else:
        return f'e/{num:03x}'

# Register as UDF
custom_udf = F.udf(custom_logic, returnType=types.StringType())

# Apply UDF to DataFrame
df_with_custom = df.withColumn('custom_col', custom_udf(F.col('dispatching_base_num')))
```

---

### 📂 File Structure & Notebooks

- **01_pyspark.ipynb** - Basics: Reading CSV/Parquet, Schema definition, Data writing
- **05_taxi_schema.ipynb** - Schema management, Multi-file processing, Data conversion
- **06_spark_sql.ipynb** - SQL queries, Data fusion, Aggregations, Report generation
- **07_groupby_join.ipynb** - Grouping operations, Join patterns

### 🚀 Quick Start

```python
# 1. Initialize Spark
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").appName('myapp').getOrCreate()

# 2. Read data
df = spark.read.option("header", "true").csv('data.csv')

# 3. Explore
df.printSchema()
df.show()

# 4. Transform
from pyspark.sql import functions as F
df = df.filter(F.col('amount') > 0)

# 5. Write
df.write.parquet('output.parquet')
```

Feel free to explore the notebooks or reach out if you'd like me to walk through the implementation in a live demo!

