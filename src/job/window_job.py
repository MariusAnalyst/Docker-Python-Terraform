from pyflink.table import EnvironmentSettings, StreamTableEnvironment

def run_window_aggregation():
    # Initialize the environment
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(environment_settings=settings)

    # 1. Define the Source with a Watermark
    # We use 'ts' as a computed column to turn the BIGINT into a TIMESTAMP
    t_env.execute_sql("""
        CREATE TABLE green_trips_source (
            PULocationID BIGINT,
            lpep_pickup_datetime BIGINT,
            ts AS TO_TIMESTAMP_LTZ(lpep_pickup_datetime, 3),
            WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda:29092',
            'topic' = 'green-trips',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json',
            'json.ignore-parse-errors' = 'true'
        )
    """)

    # 2. Define the Postgres Sink for the Window Results
    t_env.execute_sql("""
        CREATE TABLE windowed_trip_counts (
            window_start TIMESTAMP(3),
            PULocationID BIGINT,
            num_trips BIGINT
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'windowed_trip_counts',
            'username' = 'postgres',
            'password' = 'postgres'
        )
    """)

    # 3. The Tumbling Window Logic
    # Grouping by both the 5-minute window and the Location ID
    t_env.execute_sql("""
        INSERT INTO windowed_trip_counts
        SELECT 
            TUMBLE_START(ts, INTERVAL '5' MINUTE) AS window_start,
            PULocationID,
            COUNT(*) AS num_trips
        FROM green_trips_source
        GROUP BY 
            TUMBLE(ts, INTERVAL '5' MINUTE), 
            PULocationID
    """).wait()

if __name__ == '__main__':
    run_window_aggregation()