
# DE_Homework_W1-2: Data Engineering Pipeline

pulling the docker image for python 3.13
docker pull python:3.13
docker run -it python:3.13 bash 
pip --version 
db:5432

## Overview

This project demonstrates key data engineering concepts using Docker, PostgreSQL, pgAdmin, Python, and Terraform. The main steps include:

- Setting up the Python environment with uv
- Building Docker images and running containers
- Creating and managing PostgreSQL and pgAdmin services
- Writing a data pipeline to ingest and insert data into PostgreSQL
- Using the uv package for dependency management
- Infrastructure management with Terraform

---

## 1. Setting Up the Python Environment

We use the [uv](https://github.com/astral-sh/uv) package for fast Python dependency management and virtual environments.

```sh
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

Or, to sync from a lock file:

```sh
uv sync --locked
```

---

## 2. Building Docker Images

Build the custom image for the data pipeline:

```sh
docker build -t taxi_ingest_green:V001 .
```

---

## 3. Running Docker Containers

Run the data ingestion pipeline with parameters (using click):

```sh
docker run --rm --network=backend taxi_ingest_green:V001 \
  --pg_user=root \
  --pg_pass=root \
  --pg_host=pgdatabase \
  --pg_port=5432 \
  --pg_db=ny_taxi \
  --batch_size=1000
```

---

## 4. Creating PostgreSQL and pgAdmin Services

Services are defined in `pipeline/docker-compose.yaml`:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: pgdatabase
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: ny_taxi
    ports:
      - "5432:5432"
    networks:
      - backend
    volumes:
      - ./postgres_data:/var/lib/postgresql/data

  pgadmin:
    image: dpage/pgadmin4
    container_name: pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: root
    ports:
      - "8085:80"
    networks:
      - backend
    volumes:
      - ./pgadmin_data:/var/lib/pgadmin

networks:
  backend:
    driver: bridge
```

Start the services:

```sh
docker-compose up -d
```

---

## 5. Data Pipeline: Ingesting Data into PostgreSQL

The pipeline script downloads, processes, and inserts data into PostgreSQL in batches:

```python
@click.command()
@click.option('--pg_user', default='root')
@click.option('--pg_pass', default='root')
@click.option('--pg_host', default='pgdatabase')
@click.option('--pg_port', default=5432)
@click.option('--pg_db', default='ny_taxi')
@click.option('--batch_size', default=1000)
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, batch_size):
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')
    # ... data ingestion logic ...
```

---

## 6. Intro to uv Package Usage

- Fast dependency resolution and installation
- Drop-in replacement for pip and venv
- Lockfile support for reproducible builds

Example:

```sh
uv pip install pandas sqlalchemy click
uv pip freeze > uv.lock
uv sync --locked
```

---

## 7. Infrastructure as Code with Terraform

Terraform is used to provision cloud resources. Example usage:

```sh
cd terra_ass
terraform init
terraform plan
terraform apply
terraform destroy
```

Variables and credentials are managed in `variable.tf` and the `keys/` directory.

---
# SQL

## 8. SQL Commands for PostgreSQL (via pgAdmin)

The following SQL queries were used to interact with the PostgreSQL database using pgAdmin:

### Question 1: Counting Short Trips
For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a trip_distance of less than or equal to 1 mile?

```sql
SELECT COUNT(*)
FROM public.green_taxi_data
WHERE lpep_pickup_datetime::date >= '2025-11-01'
  AND lpep_pickup_datetime::date < '2025-12-01'
  AND trip_distance <= 1;
```

### Question 2: Pick Up Day with Longest Trip Distance
Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles (to exclude data errors). Use the pick up time for your calculations.

```sql
SELECT trip_distance,
       CAST(lpep_pickup_datetime AS DATE) AS "Day"
FROM public.green_taxi_data
WHERE trip_distance < 100
ORDER BY trip_distance DESC;
```

### Question 3: Pickup Zone with Largest Total Amount on Nov 18, 2025
Which was the pickup zone with the largest total_amount (sum of all trips) on November 18th, 2025?

```sql
SELECT 
    zl."Zone" AS pickup_zone,
    SUM(gt.total_amount) AS total_revenue
FROM public.green_taxi_data AS gt
JOIN public.taxi_zone_lookup AS zl
  ON gt."PULocationID" = zl."LocationID"
WHERE gt.lpep_pickup_datetime::date = '2025-11-18'
GROUP BY zl."Zone"
ORDER BY total_revenue DESC
LIMIT 1;
```

### Question 4: Drop Off Zone with Largest Tip for 'East Harlem North' Pickups
For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

```sql
SELECT 
    du."Zone" AS "drop_zone",
    max(gt.tip_amount) AS "total_tip"
FROM public.green_taxi_data AS gt
JOIN public.taxi_zone_lookup AS pu
  ON gt."PULocationID" = pu."LocationID"
JOIN public.taxi_zone_lookup AS du
  ON gt."DOLocationID" = du."LocationID"
WHERE gt.lpep_pickup_datetime >= '2025-11-01'::timestamp
  AND gt.lpep_pickup_datetime < '2025-12-01'::timestamp
  AND pu."Zone" = 'East Harlem North'
GROUP BY "drop_zone"
ORDER BY "total_tip" DESC
LIMIT 1;
```

