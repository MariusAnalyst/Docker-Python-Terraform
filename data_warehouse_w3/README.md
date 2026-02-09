# Data Warehouse Week 3 Learnings

This document summarizes the key learnings and troubleshooting steps taken during the setup and execution of the data loading process for week 3.

## Key Learnings:

### 1. Google Cloud Storage Library Installation
To interact with Google Cloud Storage, the following Python libraries were installed using pip:

```bash
pip install google-cloud-storage google-api-core
```

### 2. Service Account Credential Configuration
The application uses a service account JSON key file for authentication with Google Cloud Storage. Initially, there were issues loading the credentials due to incorrect file paths.

### 3. Troubleshooting FileNotFoundError in Jupyter Notebooks
A common challenge when working with Jupyter Notebooks is handling file paths correctly, as the notebook's execution path might differ from the project's root directory. We encountered a `FileNotFoundError` when trying to load the credentials file using a relative path.

**Solution:**
The issue was resolved by using an absolute path to the credentials file. This ensures that the file can be located regardless of the notebook's working directory. The `os.path.abspath()` function in Python can be used to generate an absolute path from a relative one.

### 4. Notebook Cleanup and Refactoring
The Jupyter Notebook was refactored to:
- Remove unnecessary and erroneous cells.
- Consolidate the credential loading logic into a single, corrected cell.

This process improved the notebook's clarity and reliability.

### 5. BigQuery SQL Statements
The `big_query.sql` file contains a series of SQL statements for interacting with BigQuery. These statements demonstrate the following concepts:

- **Creating an External Table:** An external table is created to reference the Parquet files stored in a Google Cloud Storage bucket. This allows querying the data in place without loading it into BigQuery.

- **Querying External and Materialized Tables:** The SQL file shows how to query both the external table and a materialized (native) BigQuery table.

- **Creating a Partitioned and Clustered Table:** A new table is created that is partitioned by the `tpep_dropoff_datetime` and clustered by `VendorID`. This is a common optimization technique in BigQuery to improve query performance and reduce costs.

- **Querying Partitioned Tables:** The file includes queries that leverage the partitioning to scan only a subset of the data, which can significantly improve query performance and reduce the amount of data scanned.

- **Analyzing Query Performance:** The comments in the SQL file prompt the user to compare the estimated bytes processed when querying the materialized table versus the partitioned table. This is a key aspect of understanding the benefits of partitioning in BigQuery.