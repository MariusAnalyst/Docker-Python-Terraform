/* @bruin

name: reports.trips_report
type: duckdb.sql

depends:
  - staging.trips

materialization:
  type: table
  strategy: time_interval
  incremental_key: TRIP_DATE
  time_granularity: date

columns:
  - name: TRIP_DATE
    type: date
    description: Date of the trip
    primary_key: true
  - name: TAXI_TYPE
    type: string
    description: Type of taxi (yellow or green)
    primary_key: true
  - name: PAYMENT_TYPE_NAME
    type: string
    description: Payment type name
    primary_key: true
  - name: TOTAL_TRIPS
    type: bigint
    description: Total number of trips
    checks:
      - name: non_negative
  - name: TOTAL_REVENUE
    type: float
    description: Total revenue
  - name: AVG_TRIP_DISTANCE
    type: float
    description: Average trip distance
    checks:
      - name: non_negative

@bruin */

SELECT
    DATE(TRY_CAST(TPEP_PICKUP_DATETIME AS TIMESTAMP)) AS TRIP_DATE,
    TAXI_TYPE,
    PAYMENT_TYPE_NAME,
    COUNT(*) AS TOTAL_TRIPS,
    SUM(TOTAL_AMOUNT) AS TOTAL_REVENUE,
    AVG(TRIP_DISTANCE) AS AVG_TRIP_DISTANCE
FROM staging.trips
WHERE TPEP_PICKUP_DATETIME >= '{{ start_datetime }}'
  AND TPEP_PICKUP_DATETIME < '{{ end_datetime }}'
GROUP BY
    DATE(TRY_CAST(TPEP_PICKUP_DATETIME AS TIMESTAMP)),
    TAXI_TYPE,
    PAYMENT_TYPE_NAME
