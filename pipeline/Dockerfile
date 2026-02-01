FROM python:3.13.11-slim
RUN apt-get update && apt-get install -y sed

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"

COPY pyproject.toml .python-version uv.lock ./
RUN uv sync --locked

COPY ingestion_data.py .

ENTRYPOINT ["python", "ingestion_data.py"]