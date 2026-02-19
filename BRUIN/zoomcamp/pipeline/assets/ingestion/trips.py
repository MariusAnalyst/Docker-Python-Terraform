"""@bruin

name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: VendorID
    type: integer
    description: A code indicating the TPEP provider that provided the record
  - name: tpep_pickup_datetime
    type: string
    description: The date and time when the meter was engaged
  - name: tpep_dropoff_datetime
    type: string
    description: The date and time when the meter was disengaged
  - name: passenger_count
    type: integer
    description: The number of passengers in the vehicle
  - name: trip_distance
    type: float
    description: The elapsed trip distance in miles
  - name: RatecodeID
    type: integer
    description: The final rate code in effect at the end of the trip
  - name: store_and_fwd_flag
    type: string
    description: Whether the trip record was held in vehicle memory before sending
  - name: PULocationID
    type: integer
    description: TLC Taxi Zone in which the meter was engaged
  - name: DOLocationID
    type: integer
    description: TLC Taxi Zone in which the meter was disengaged
  - name: payment_type
    type: integer
    description: A numeric code signifying how the passenger paid
  - name: fare_amount
    type: float
    description: The time-and-distance fare calculated by the meter
  - name: extra
    type: float
    description: Miscellaneous extras and surcharges
  - name: mta_tax
    type: float
    description: MTA tax that is automatically triggered based on the metered rate in use
  - name: tip_amount
    type: float
    description: Tip amount paid via credit card
  - name: tolls_amount
    type: float
    description: Total amount of all tolls paid in trip
  - name: improvement_surcharge
    type: float
    description: Improvement surcharge assessed trips at the flag drop
  - name: total_amount
    type: float
    description: The total amount charged to passengers
  - name: congestion_surcharge
    type: float
    description: Total congestion surcharge
  - name: taxi_type
    type: string
    description: Type of taxi (yellow or green)
  - name: extracted_at
    type: string
    description: Timestamp when the data was extracted

@bruin"""

import io
import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
import requests


def materialize():
    start_date = os.getenv("BRUIN_START_DATE")
    end_date = os.getenv("BRUIN_END_DATE")

    if not start_date or not end_date:
        raise ValueError("BRUIN_START_DATE and BRUIN_END_DATE must be provided")

    taxi_types_var = os.getenv("BRUIN_VARS", "{}")
    taxi_types_data = json.loads(taxi_types_var)
    taxi_types = taxi_types_data.get("taxi_types", ["yellow"])

    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/"

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    all_dataframes = []
    current = start

    while current < end:
        year = current.year
        month = current.month
        month_str = f"{year:04d}-{month:02d}"

        for taxi_type in taxi_types:
            filename = f"{taxi_type}_tripdata_{month_str}.parquet"
            url = f"{base_url}{filename}"

            try:
                response = requests.get(url, timeout=60)
                if response.status_code == 200:
                    df = pd.read_parquet(io.BytesIO(response.content))
                    for col in df.select_dtypes(include=['datetime64[ns]']).columns:
                        df[col] = df[col].astype(str)
                    df["taxi_type"] = taxi_type
                    df["extracted_at"] = datetime.now().isoformat()
                    all_dataframes.append(df)
                    print(f"Fetched {len(df)} rows from {filename}")
                else:
                    print(f"File not found: {filename} (HTTP {response.status_code})")
            except Exception as e:
                print(f"Error fetching {filename}: {e}")

        current += relativedelta(months=1)

    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        return final_df
    else:
        return pd.DataFrame()
