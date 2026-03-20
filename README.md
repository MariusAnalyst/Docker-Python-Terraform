# Streaming

A streaming data processing project using Apache Flink, Redpanda (Kafka-compatible), and Python.

## Prerequisites

Before running this project, ensure you have the following installed:

### Python 3.12 or higher
- Download from [python.org](https://www.python.org/downloads/)
- Or use your system package manager (e.g., `apt install python3.12` on Ubuntu)

### uv (Python package manager)
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or via pip: `pip install uv`
- Verify: `uv --version`

### Docker and Docker Compose
- **Install Docker:**
  - On Ubuntu/Debian: `sudo apt update && sudo apt install docker.io docker-compose-plugin`
  - On CentOS/RHEL: `sudo yum install docker docker-compose-plugin`
  - On macOS: Download from [docker.com](https://www.docker.com/products/docker-desktop)
  - On Windows: Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
- **Start Docker service:** `sudo systemctl start docker` (Linux)
- **Add user to docker group:** `sudo usermod -aG docker $USER` (log out and back in)
- **Verify Docker:** `docker --version`
- **Verify Docker Compose:** `docker compose version`

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd streaming
   ```

2. Install Python dependencies:
   ```bash
   uv sync
   ```

3. (Optional) Activate the virtual environment:
   ```bash
   source .venv/bin/activate  # On Linux/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

## Usage

1. Start the services (Redpanda, Flink, and Postgres):
   ```bash
   docker compose up -d
   ```

2. Initialize the Postgres database tables:
   ```bash
   # Create table for raw events job
   docker exec streaming-postgres-1 psql -U postgres -c "CREATE TABLE processed_events (PULocationID BIGINT, DOLocationID BIGINT, passenger_count BIGINT, trip_distance DOUBLE PRECISION, tip_amount DOUBLE PRECISION, total_amount DOUBLE PRECISION, pickup_datetime TIMESTAMP, dropoff_datetime TIMESTAMP);"

   # Create table for window aggregation job
   docker exec streaming-postgres-1 psql -U postgres -c "CREATE TABLE windowed_trip_counts (window_start TIMESTAMP, PULocationID BIGINT, num_trips BIGINT);"

   # Create table for session window job
   docker exec streaming-postgres-1 psql -U postgres -c "CREATE TABLE session_results (PULocationID BIGINT, num_trips BIGINT, session_start TIMESTAMP(3), session_end TIMESTAMP(3));"

   # Create table for hourly tip analysis
   docker exec streaming-postgres-1 psql -U postgres -c "CREATE TABLE hourly_tips (window_start TIMESTAMP(3), total_tips DOUBLE PRECISION);"
   ```

3. Verify tables were created successfully:
   ```bash
   docker exec streaming-postgres-1 psql -U postgres -c "\dt"
   ```

4. Run the Flink jobs inside the jobmanager container:
   ```bash
   # Option A: Standard event processing
   docker exec -it streaming-jobmanager-1 flink run -py /opt/src/job/assignment_flink_job.py

   # Option B: Windowed aggregation (5-minute intervals)
   docker exec -it streaming-jobmanager-1 flink run -py /opt/src/job/window_job.py

   # Option C: Session window aggregation (5-minute gap)
   docker exec -it streaming-jobmanager-1 flink run -py /opt/src/job/session_window_job.py

   # Option D: Hourly tip analysis
   docker exec -it streaming-jobmanager-1 flink run -py /opt/src/job/tip_analysis_job.py
   ```

5. Verify the jobs are running:
   ```bash
   docker exec streaming-jobmanager-1 flink list
   ```

## Verification & Monitoring

- **Flink Dashboard**: Access [http://localhost:8081](http://localhost:8081) to see the job graph and metrics.
- **Postgres Sink**: Check if data is being written to the database:
  ```bash
  docker exec streaming-postgres-1 psql -U postgres -c "SELECT count(*) FROM processed_events;"
  docker exec streaming-postgres-1 psql -U postgres -c "SELECT count(*) FROM windowed_trip_counts;"
  docker exec streaming-postgres-1 psql -U postgres -c "SELECT count(*) FROM session_results;"
  docker exec streaming-postgres-1 psql -U postgres -c "SELECT count(*) FROM hourly_tips;"
  ```
- **Top 3 Trips Query**: Identify the locations with the highest number of trips in a window:
  ```bash
  docker exec -it streaming-postgres-1 psql -U postgres -c "SELECT PULocationID, num_trips FROM windowed_trip_counts ORDER BY num_trips DESC LIMIT 3;"
  ```
- **Top Session Query**:
  ```bash
  docker exec -it streaming-postgres-1 psql -U postgres -c "SELECT PULocationID, num_trips, session_start, session_end FROM session_results ORDER BY num_trips DESC LIMIT 1;"
  ```
- **Hourly Tip Query**:
  ```bash
  docker exec -it streaming-postgres-1 psql -U postgres -c "SELECT window_start, total_tips FROM hourly_tips ORDER BY window_start DESC LIMIT 5;"
  ```
- **Highest Hourly Tip Query**:
  ```bash
  docker exec -it streaming-postgres-1 psql -U postgres -c "SELECT window_start, total_tips FROM hourly_tips ORDER BY total_tips DESC LIMIT 1;"
  ```
- **Postgres CLI**:
 Access the database directly to run custom queries:
  ```bash
  docker exec -it streaming-postgres-1 psql -U postgres
  ```
- **Redpanda Source**: Verify messages are available in the Kafka topic:
  ```bash
  docker exec streaming-redpanda-1 rpk topic consume green-trips --num 1 --brokers redpanda:29092
  ```

## Step-by-Step Resolution Log

The following steps were taken to resolve issues and successfully launch the streaming jobs:

1.  **Path Correction**: Identified that the Flink job was located at `src/job/` on the host, which maps to `/opt/src/job/` inside the container via the `docker-compose.yaml` volume mapping (`./src/:/opt/src`).
2.  **Conflict Resolution**: Discovered conflicting containers (`my-postgres` and `redpanda`) running on the default Docker bridge network. These were stopped to allow the project-specific services to bind to the required ports (5432, 9092).
3.  **Database Initialization**: The Postgres sink requires target tables to exist. Manually initialized schemas for `processed_events`, `windowed_trip_counts`, `session_results`, and `hourly_tips`.
4.  **Kafka Topic Verification**: Confirmed the `green-trips` topic was present in Redpanda using `rpk topic list`.
5.  **JSON Serialization Fix**: Encountered `NaN` values in `passenger_count` which caused JSON parsing failures. Resolved by adding `'json.ignore-parse-errors' = 'true'` to all Kafka source table definitions.
6.  **TaskManager Recovery**: Restarted the TaskManager after it crashed due to the initial database connection failures.
7.  **Cluster Refresh**: Restarted the entire Flink cluster to clear cached state and ensure updated job scripts were loaded.

## Project Structure

- `main.py`: Main application entry point (producer/consumer script)
- `src/job/`: Contains Flink streaming job scripts
  - `assignment_flink_job.py`: Standard data transformation job.
  - `window_job.py`: 5-minute tumbling window aggregation job.
  - `session_window_job.py`: 5-minute gap session window job.
  - `tip_analysis_job.py`: 1-hour tumbling window tip sum job.
- `docker-compose.yaml`: Docker services configuration
- `Dockerfile.flink`: Flink jobmanager Docker image
- `pyproject.toml`: Project configuration and dependencies
- `uv.lock`: Locked dependency versions

## Troubleshooting

- **Incorrect Job Path**: The `src/` directory is mapped to `/opt/src/` inside the container.
- **Port Conflicts**: Ensure ports 5432 (Postgres), 9092 (Kafka), and 8081 (Flink Web UI) are not in use.
- **Database Table Missing**: Flink JDBC sink will fail if the table does not exist. Use the `CREATE TABLE` commands in the Usage section.
- **NaN in JSON**: If jobs fail with JSON parse errors, ensure `'json.ignore-parse-errors' = 'true'` is set in the Kafka source `WITH` clause.
- **TaskManager Crash**: Check TaskManager logs (`docker logs streaming-taskmanager-1`) if slots are unavailable (0 available in Dashboard). Restart the TaskManager if it exits.
