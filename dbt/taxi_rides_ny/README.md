Welcome to your new dbt project!

### Using the starter project

Try running the following commands:
- dbt run
- dbt test


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices

---

## Project Setup and Dependencies

This section details the steps required to set up the dbt project environment, including the Python virtual environment, dbt-core with necessary adapters, and the DuckDB Command Line Interface (CLI).

### 0. Initialize dbt Project (If starting from scratch)

If you are setting up a new dbt project from scratch, you would typically use the `dbt init` command.
**Note:** This `taxi_rides_ny` project is already initialized. You would run this command from the parent directory *before* entering the `taxi_rides_ny` directory.

```bash
dbt init taxi_rides_ny
```

### 1. Python Virtual Environment Setup

It is highly recommended to use a Python virtual environment to manage project dependencies.

1.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```
2.  **Activate the virtual environment:**
    *   **On Windows (PowerShell):**
        ```bash
        .venv\Scripts\Activate.ps1
        ```
    *   **On Windows (Command Prompt):**
        ```bash
        .venv\Scripts\activate.bat
        ```
    *   **On macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```
    (Once activated, your terminal prompt should show `(.venv)`).

### 2. Installing dbt-core and Adapters

With the virtual environment activated, install `dbt-core` along with the `dbt-bigquery` and `dbt-duckdb` adapters.

```bash
pip install dbt-core dbt-bigquery dbt-duckdb
```

### 3. DuckDB Command Line Interface (CLI) Installation

To use the `duckdb` CLI directly from your terminal (outside of Python scripts), follow these steps:

1.  **Download the `duckdb` CLI executable:**
    Visit the official [DuckDB Installation page](https://duckdb.org/docs/installation/index.html).
    Navigate to the "Command Line Interface (CLI)" section and download the `duckdb.exe` file for Windows.

2.  **Place `duckdb.exe` in your system's PATH:**
    *   Move the downloaded `duckdb.exe` to a directory already included in your system's `PATH` environment variable (e.g., `C:\Windows`, `C:\Program Files\Git\cmd`).
    *   **Alternatively (recommended for organization):**
        *   Create a new directory (e.g., `C:\duckdb\bin`).
        *   Place `duckdb.exe` inside this new directory.
        *   Add this new directory to your system's `PATH` environment variable:
            1.  Search for "Environment Variables" in the Windows Start menu.
            2.  Select "Edit the system environment variables".
            3.  Click the "Environment Variables..." button.
            4.  Under "System variables", find and select the `Path` variable, then click "Edit...".
            5.  Click "New" and add the full path to your new directory (e.g., `C:\duckdb\bin`).
            6.  Click "OK" on all open windows to save the changes.

    **Important:** After modifying the PATH, you **must restart your terminal or command prompt** for the changes to take effect.

3.  **Verify installation:**
    Open a new terminal and run:
    ```bash
    duckdb --version
    ```
    This command should now display the installed DuckDB CLI version.

---

### 4. Configure `profiles.yml`

The `profiles.yml` file contains the connection details for your data warehouses (BigQuery and DuckDB in this project). This file is typically located in your `~/.dbt/` directory (on Windows, `C:\Users\<your_username>\.dbt\profiles.yml`). You should **never** commit this file to version control as it contains sensitive credentials.

Here's an example structure for `profiles.yml` tailored for this project:

```yaml
taxi_rides_ny: # This should match the `profile` name in your dbt_project.yml
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      keyfile: /path/to/your/bigquery/keyfile.json # Replace with the actual path to your BigQuery service account key file
      project: your-gcp-project-id # Replace with your GCP project ID
      dataset: dbt_dev_dataset # Replace with your desired BigQuery dataset
      threads: 4
      timeout_seconds: 300
      location: US

    local_duckdb: # An alternative output for local development with DuckDB
      type: duckdb
      path: 'taxi_rides_ny.duckdb' # The name of your DuckDB database file
      threads: 4
```

**Summary of Content:**

*   **`taxi_rides_ny`**: The name of the dbt profile, which should match the `profile` setting in `dbt_project.yml`.
*   **`target`**: Specifies the default connection target (e.g., `dev` or `local_duckdb`).
*   **`outputs`**: Contains definitions for different connection targets.
    *   **`dev` (BigQuery)**:
        *   `type`: `bigquery`
        *   `method`: `service-account` (recommended for CI/CD)
        *   `keyfile`: Path to your GCP service account JSON key file.
        *   `project`: Your Google Cloud Project ID.
        *   `dataset`: The BigQuery dataset where dbt will build tables.
        *   `threads`, `timeout_seconds`, `location`: Standard BigQuery connection parameters.
    *   **`local_duckdb` (DuckDB)**:
        *   `type`: `duckdb`
        *   `path`: The file path for your DuckDB database. `dbt` will create this file if it doesn't exist.
        *   `threads`: Number of concurrent threads to use.
---

## Data Transformation Pipeline Overview (Learnings from the past week)

This dbt project implements a robust data transformation pipeline for NYC taxi trip data, demonstrating best practices in data warehousing and ETL/ELT using dbt. Key learnings and architectural patterns observed include:

### 1. Layered Data Architecture (Staging, Intermediate, Marts)
The project clearly separates data transformations into distinct layers:
*   **Staging Layer (`stg_*` models):** Focuses on cleaning, standardizing, and casting raw data from disparate sources (green and yellow taxi data). This layer harmonizes column names and applies initial data quality checks (e.g., `vendorid IS NOT NULL`). This ensures a clean and consistent base for subsequent transformations.
*   **Intermediate Layer (`int_*` models):** Combines and refines data from the staging layer. For instance, `int_trip_union` effectively merges green and yellow taxi datasets into a single, unified stream, preparing it for higher-level business logic.
*   **Marts Layer (`fct_*`, `dim_*` models):** Designed for business consumption, providing analytical-ready fact and dimension tables. `fct_trips` serves as the core fact table, enriched with dimensional attributes from `dim_zones`.

### 2. Data Harmonization and Quality
*   **Consistent Naming:** Standardized column names across different taxi datasets (e.g., `pickup_datetime`, `vendor_id`) ensure uniformity.
*   **Type Casting:** Explicit `CAST` operations and the use of the `safe_cast` macro provide data type integrity and handle potential parsing errors gracefully.
*   **Data Filtering:** Initial data quality checks, like filtering `NULL` `vendor_id` records, are applied early in the pipeline.

### 3. Reusability and Modularity with dbt Macros
*   **`get_trip_duration_minutes` Macro:** A clear example of abstracting common logic into a reusable macro. This macro calculates trip duration using `dbt.datediff`, promoting code consistency and cross-database compatibility.
*   **`safe_cast` Macro (inferred):** The use of such a macro for `ratecodeid` in staging models highlights an understanding of handling schema variations and data robustness.

### 4. Incremental Data Loading
*   The `fct_trips` model is configured for **incremental materialization** (`materialized='incremental'`, `incremental_strategy='merge'`, `unique_key='trip_id'`). This is a critical learning for optimizing performance and cost in large datasets, as it processes only new or changed records rather than rebuilding the entire table on each run.
*   The `on_schema_change='append_new_columns'` strategy demonstrates a forward-thinking approach to schema evolution.

### 5. Development Environment Best Practices
*   **Dev-Specific Data Sampling:** The inclusion of `{% if target.name == 'dev' %}` blocks in staging models to filter data based on `dev_start_date` and `dev_end_date` is a valuable practice for accelerating development and testing cycles without processing full production volumes.
*   **Profile-driven Configuration:** The `dbt_project.yml` and `profiles.yml` demonstrate how to manage different environments (e.g., `dev`, `local_duckdb` for BigQuery and DuckDB respectively), allowing for flexible local development and production deployments.

### 6. Star Schema Design
*   The `fct_trips` model joins with `dim_zones` (used twice for pickup and dropoff locations), clearly illustrating the implementation of a star schema. This design facilitates efficient querying and analytical reporting.

This project serves as an excellent foundation for building scalable and maintainable data analytics solutions using dbt.
