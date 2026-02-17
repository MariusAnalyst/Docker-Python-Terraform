--importing our staging tables and unioning them together
with green_trips as (
    select * from {{ ref('stg_green_tripdata') }}
),
yellow_trips as (
    select * from {{ ref('stg_yellow_tripdata') }}
),
trips_union as (
    select * from green_trips
    union all
    select * from yellow_trips
)
select * from trips_union