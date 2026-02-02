# Kestra Workflow Orchestration Example

This directory contains an example of workflow orchestration using Kestra, an open-source orchestrator that enables defining, scheduling, and monitoring complex workflows. This setup leverages Docker for easy deployment and includes integrations with PostgreSQL, pgAdmin, and even Gemini AI.

## Table of Contents
*   [Overview](#kestra-workflow-orchestration-example)
*   [`docker-compose.yaml`](#docker-composeyaml)
*   [`Size_yellow_taxi_2020_12.yaml`](#size_yellow_taxi_2020_12yaml)
*   [`elt_taxi_file_postgress.yaml`](#elt_taxi_file_postgressyaml)

## `docker-compose.yaml`

This file defines the multi-service Docker environment for running Kestra and its dependencies:

*   **`postgres`**: A PostgreSQL database instance used for general data storage (e.g., `ny_taxi` database, which could be used for data processed by Kestra flows).
*   **`pgadmin`**: A web-based administration tool for managing PostgreSQL databases, accessible at `http://localhost:8085`.
*   **`kestra_postgres`**: A dedicated PostgreSQL instance specifically for Kestra's internal data storage (e.g., flow definitions, execution history).
*   **`kestra`**: The Kestra platform itself, configured to:
    *   Connect to `kestra_postgres` for its repository, storage, and queue.
    *   Expose its UI on `http://localhost:8086` (mapped from container port 8080).
    *   Include an AI integration with **Gemini AI** (`gemini-2.5-flash` model), demonstrating Kestra's extensibility for AI-powered tasks. The `GEMINI_API_KEY` is expected to be provided via an `.env` file.
    *   Mount volumes for persistent data (`kestra_data`, `kestra_postgres_data`, `pgadmin_data`, `postgres_data`) and Docker socket access.

This `docker-compose.yaml` provides a complete, self-contained environment to run Kestra, manage its database, and even experiment with AI integrations within workflows.

## `Size_yellow_taxi_2020_12.yaml`

This YAML file defines a Kestra flow (`id: kestra_HW1`) that demonstrates a common data engineering pattern: downloading external data, processing it, and logging key metrics.

The flow features:

*   **Inputs**: It's parameterized to allow users to select the `taxi` type (yellow, green), `year`, and `month` for the NYC taxi trip data. This makes the flow highly reusable.
*   **Variables**: Dynamically constructs filenames and table names based on user inputs.
*   **`set_label`**: Adds labels to the execution for better organization and filtering within the Kestra UI.
*   **`extract`**: This is a `shell.Commands` task that:
    *   Uses `wget` to download a gzipped CSV file from the `DataTalksClub/nyc-tlc-data` GitHub releases.
    *   `gunzip`s the downloaded file.
    *   Saves the extracted CSV into Kestra's internal storage (`outputFiles: ["*.csv"]`).
*   **`get_file_size`**: A `core.storage.Size` task that calculates the size of the downloaded and extracted CSV file.
*   **`log_file_size`**: A `core.log.Log` task that outputs the filename and its size (in MB) to the Kestra execution logs.

This workflow showcases how Kestra can orchestrate external data fetching, command-line operations, and integrate with its internal storage and logging capabilities to create observable and manageable data pipelines. The combination of `docker-compose.yaml` and this flow provides a robust foundation for building and executing various data-centric workflows.

## `elt_taxi_file_postgress.yaml`

This YAML file defines an advanced Kestra workflow (`id: kestra_HW3-4`) for an ELT (Extract, Load, Transform) process that ingests NYC taxi data into a PostgreSQL database. It handles both yellow and green taxi datasets with robust data handling, including deduplication.

### What it Does:

*   **Parameterized Inputs**: Accepts `taxi` type (`yellow` or `green`) as input, allowing for a single flow definition to handle different datasets.
*   **Dynamic Variables**: Constructs filenames and database table names dynamically based on the selected taxi type and the flow's trigger date (e.g., `YYYY-MM`).
*   **Data Extraction (`extract`)**:
    *   Downloads gzipped CSV files containing NYC taxi trip data directly from the `DataTalksClub/nyc-tlc-data` GitHub releases.
    *   Unzips the downloaded content and saves the CSV file to Kestra's internal storage.
*   **Conditional ELT Logic (`if_yellow_taxi`, `if_green_taxi`)**:
    *   Executes a different set of tasks based on whether 'yellow' or 'green' taxi data is being processed, accounting for schema differences between the two.
    *   **Schema Definition**: Creates the main and staging tables in PostgreSQL with appropriate column types if they don't already exist.
    *   **Staging Data**: Truncates the staging table and then uses `CopyIn` to efficiently load the CSV data into it.
    *   **Data Transformation**: Adds a `unique_row_id` (an MD5 hash of key columns for deduplication) and the original `filename` to each record in the staging table.
    *   **Merge/UPSERT**: Performs a `MERGE INTO` operation from the staging table to the main table. This effectively handles new data (inserts records that don't exist) and avoids duplicating existing records based on the `unique_row_id`.
*   **Cleanup (`purge_files`)**: Removes the downloaded files from Kestra's internal storage after successful processing to prevent clutter.
*   **Scheduled Triggers**: The flow is configured to run automatically on a monthly schedule (`cron: "0 9 1 * *"` for green, `cron: "0 10 1 * *"` for yellow) to ingest new monthly data.

### How to Use for Forked Directories:

1.  **Ensure Docker Environment is Running**: Make sure your `docker-compose.yaml` services (PostgreSQL, Kestra) are up and running as described in the `docker-compose.yaml` section. You can start them using `docker-compose up -d`.
2.  **Access Kestra UI**: Navigate to the Kestra UI, typically at `http://localhost:8086`.
3.  **Upload the Flow**: If you fork this repository, you'll need to upload the `elt_taxi_file_postgress.yaml` file to your Kestra instance. You can usually do this via the UI by going to "Flows" and then an "Upload" or "Create" option, pasting the YAML content.
4.  **Run Manually or Let Schedule**: Once uploaded, you can either:
    *   **Trigger Manually**: From the Kestra UI, find the `kestra_HW3-4` flow and manually trigger an execution. You will be prompted to select the `taxi` type.
    *   **Wait for Schedule**: The flow is configured with monthly cron triggers, so it will automatically run at the specified times for both yellow and green taxis.
5.  **Monitor Execution**: Observe the flow's execution in the Kestra UI to see the status, logs, and any output.
6.  **Verify Data in PostgreSQL**: Use `pgAdmin` (accessible at `http://localhost:8085`) to connect to the `ny_taxi` database and verify that the `yellow_tripdata` or `green_tripdata` tables have been populated with the ingested data.

This flow is a comprehensive example of building reliable and automated data ingestion pipelines using Kestra, providing a clear demonstration of ELT principles.