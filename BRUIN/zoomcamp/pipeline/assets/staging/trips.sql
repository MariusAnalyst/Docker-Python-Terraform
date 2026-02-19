/* @bruin

name: staging.trips
type: duckdb.sql

depends:
  - ingestion.trips
  - ingestion.payment_lookup

materialization:
  type: table
  strategy: time_interval
  incremental_key: TPEP_PICKUP_DATETIME
  time_granularity: timestamp

columns:
  - name: TPEP_PICKUP_DATETIME
    type: timestamp
    description: When the meter was engaged
    primary_key: true
    checks:
      - name: not_null
  - name: TPEP_DROPOFF_DATETIME
    type: timestamp
    description: When the meter was disengaged
    checks:
      - name: not_null
  - name: PU_LOCATION_ID
    type: integer
    description: Pickup location ID
  - name: DO_LOCATION_ID
    type: integer
    description: Dropoff location ID
  - name: PASSENGER_COUNT
    type: integer
    description: Number of passengers
  - name: TRIP_DISTANCE
    type: float
    description: Trip distance in miles
  - name: FARE_AMOUNT
    type: float
    description: Fare amount
  - name: TOTAL_AMOUNT
    type: float
    description: Total amount charged
  - name: PAYMENT_TYPE
    type: integer
    description: Payment type ID
  - name: PAYMENT_TYPE_NAME
    type: string
    description: Payment type name from lookup
  - name: TAXI_TYPE
    type: string
    description: Type of taxi (yellow or green)

@bruin */

WITH deduplicated AS (
    SELECT
        TRY_CAST(TPEP_PICKUP_DATETIME AS TIMESTAMP) AS TPEP_PICKUP_DATETIME,
        TRY_CAST(TPEP_DROPOFF_DATETIME AS TIMESTAMP) AS TPEP_DROPOFF_DATETIME,
        PASSENGER_COUNT,
        TRIP_DISTANCE,
        PU_LOCATION_ID,
        DO_LOCATION_ID,
        PAYMENT_TYPE,
        FARE_AMOUNT,
        TOTAL_AMOUNT,
        TAXI_TYPE,
        EXTRACTED_AT,
        ROW_NUMBER() OVER (
            PARTITION BY TPEP_PICKUP_DATETIME, TPEP_DROPOFF_DATETIME, 
                         PU_LOCATION_ID, DO_LOCATION_ID, FARE_AMOUNT
            ORDER BY EXTRACTED_AT DESC
        ) AS rn
    FROM ingestion.trips
    WHERE TPEP_PICKUP_DATETIME >= '{{ start_datetime }}'
      AND TPEP_PICKUP_DATETIME < '{{ end_datetime }}'
)
SELECT
    d.TPEP_PICKUP_DATETIME,
    d.TPEP_DROPOFF_DATETIME,
    d.PASSENGER_COUNT,
    d.TRIP_DISTANCE,
    d.PU_LOCATION_ID,
    d.DO_LOCATION_ID,
    d.PAYMENT_TYPE,
    d.FARE_AMOUNT,
    d.TOTAL_AMOUNT,
    d.TAXI_TYPE,
    p.PAYMENT_TYPE_NAME
FROM deduplicated d
LEFT JOIN ingestion.payment_lookup p
    ON d.PAYMENT_TYPE = p.PAYMENT_TYPE_ID
WHERE d.rn = 1
