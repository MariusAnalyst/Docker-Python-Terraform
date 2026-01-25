
# Docker-Python-Pipeline

A complete data engineering project demonstrating containerized Python pipelines, PostgreSQL, pgAdmin, and infrastructure automation with Terraform.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Environment Setup with uv](#environment-setup-with-uv)
- [Building and Running Docker Images](#building-and-running-docker-images)
- [Data Pipeline Scripts](#data-pipeline-scripts)
- [PostgreSQL and pgAdmin with Docker Compose](#postgresql-and-pgadmin-with-docker-compose)
- [SQL Queries for Data Analysis](#sql-queries-for-data-analysis)
- [Infrastructure as Code with Terraform](#infrastructure-as-code-with-terraform)
- [References](#references)

---

## Project Structure

- [`DE_Homework_W1-2/`](DE_Homework_W1-2/): Main Python pipeline, Dockerfile, and Terraform example.
- [`pipeline/`](pipeline/): Alternative pipeline with its own Dockerfile, Compose, and scripts.
- [`Terademo/`](Terademo/): Example Terraform configuration for GCP.
- [`images/`](images/): (If used) for storing project images.
- [README.md](README.md): This file.

---

## Environment Setup with uv

We use [uv](https://github.com/astral-sh/uv) for fast dependency management and reproducible Python environments.

```sh
pip install uv
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
uv sync --locked
```

See: [`DE_Homework_W1-2/pyproject.toml`](DE_Homework_W1-2/pyproject.toml)

---

## Building and Running Docker Images

### Build the pipeline image

```sh
docker build -t taxi_ingest_green:V001 DE_Homework_W1-2/
```

### Run the pipeline container

```sh
docker run --rm --network=backend taxi_ingest_green:V001 \
	--pg_user=root \
	--pg_pass=root \
	--pg_host=pgdatabase \
	--pg_port=5432 \
	--pg_db=ny_taxi \
	--batch_size=1000
```

See: [`DE_Homework_W1-2/Dockerfile`](DE_Homework_W1-2/Dockerfile)

---

## Data Pipeline Scripts

- [`DE_Homework_W1-2/ingest_ass_data.py`](DE_Homework_W1-2/ingest_ass_data.py): Ingests green taxi data into PostgreSQL using batch inserts and Click for CLI.
- [`pipeline/ingestion_data.py`](pipeline/ingestion_data.py): Ingests yellow taxi data with chunked CSV reading and CLI options.

Example (Click-based CLI):

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

## PostgreSQL and pgAdmin with Docker Compose

Services are defined in [`pipeline/docker-compose.yaml`](pipeline/docker-compose.yaml):

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

Start services:

```sh
cd pipeline
docker-compose up -d
```

---

## SQL Queries for Data Analysis

Interact with your data using pgAdmin or psql. Example queries:

**Counting short trips:**
```sql
SELECT COUNT(*)
FROM public.green_taxi_data
WHERE lpep_pickup_datetime::date >= '2025-11-01'
	AND lpep_pickup_datetime::date < '2025-12-01'
	AND trip_distance <= 1;
```

**Longest trip day:**
```sql
SELECT trip_distance,
			 CAST(lpep_pickup_datetime AS DATE) AS "Day"
FROM public.green_taxi_data
WHERE trip_distance < 100
ORDER BY trip_distance DESC;
```

**Pickup zone with largest total amount:**
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

**Drop off zone with largest tip for 'East Harlem North' pickups:**
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

---

## Infrastructure as Code with Terraform

Provision GCP resources using Terraform in [`Terademo/`](Terademo/):

- [`Terademo/main.tf`](Terademo/main.tf): Main configuration for GCP storage and BigQuery.
- [`Terademo/variable.tf`](Terademo/variable.tf): Variable definitions.
- [`Terademo/keys/`](Terademo/keys/): Store your GCP credentials here (not tracked by git).

Example usage:

```sh
cd Terademo
terraform init
terraform plan
terraform apply
terraform destroy
```

---

## References

- [uv Documentation](https://docs.astral.sh/uv/)
- [Docker Documentation](https://docs.docker.com/)
- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pandas](https://pandas.pydata.org/)

---

