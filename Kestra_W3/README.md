# Kestra Workflow Orchestration Example

This directory contains an example of workflow orchestration using Kestra, an open-source orchestrator that enables defining, scheduling, and monitoring complex workflows. This setup leverages Docker for easy deployment and includes integrations with PostgreSQL, pgAdmin, and even Gemini AI.

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
