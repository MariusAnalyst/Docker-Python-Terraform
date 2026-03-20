from pyflink.table import EnvironmentSettings, StreamTableEnvironment

def run_tip_analysis():
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(environment_settings=settings)

    # 1. Source: Extracting tip_amount and lpep_pickup_datetime
    t_env.execute_sql("""
        CREATE TABLE green_trips_tips (
            tip_amount DOUBLE,
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

    # 2. Sink: Table for hourly tip totals
    t_env.execute_sql("""
        CREATE TABLE hourly_tips (
            window_start TIMESTAMP(3),
            total_tips DOUBLE
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'hourly_tips',
            'username' = 'postgres',
            'password' = 'postgres'
        )
    """)

    # 3. Aggregation: Sum tip_amount per 1-hour window
    t_env.execute_sql("""
        INSERT INTO hourly_tips
        SELECT 
            TUMBLE_START(ts, INTERVAL '1' HOUR) AS window_start,
            SUM(tip_amount) AS total_tips
        FROM green_trips_tips
        GROUP BY 
            TUMBLE(ts, INTERVAL '1' HOUR)
    """).wait()

if __name__ == '__main__':
    run_tip_analysis()