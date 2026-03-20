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

1. Start the services (Redpanda and Flink jobmanager):
   ```bash
   docker compose up -d
   ```

2. Check that services are running:
   ```bash
   docker ps
   ```

3. View logs:
   ```bash
   docker compose logs -f
   ```

4. Run your streaming application:
   ```bash
   python main.py
   ```

5. Stop services:
   ```bash
   docker compose down
   ```

## Project Structure

- `main.py`: Main application entry point
- `docker-compose.yaml`: Docker services configuration
- `Dockerfile.flink`: Flink jobmanager Docker image
- `pyproject.toml`: Project configuration and dependencies
- `uv.lock`: Locked dependency versions

## Dependencies

- `kafka-python`: Kafka client for Python
- `pandas`: Data manipulation
- `pyarrow`: Columnar data processing

## Troubleshooting

- If Docker build fails due to disk space: `docker system prune -a -f`
- If permission denied with Docker: Ensure user is in docker group
- If Python version issues: Check `python --version` and `uv python list`