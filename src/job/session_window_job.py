from pyflink.table import EnvironmentSettings, StreamTableEnvironment

def run_session_window_job():
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(environment_settings=settings)

    # 1. Source: Setup Event Time and 5-second Watermark
    t_env.execute_sql("""
        CREATE TABLE green_trips_session (
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

    # 2. Sink: Table for session results
    t_env.execute_sql("""
        CREATE TABLE session_results (
            PULocationID BIGINT,
            num_trips BIGINT,
            session_start TIMESTAMP(3),
            session_end TIMESTAMP(3)
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'session_results',
            'username' = 'postgres',
            'password' = 'postgres'
        )
    """)

    # 3. Session Window Logic: 5-minute gap
    t_env.execute_sql("""
        INSERT INTO session_results
        SELECT 
            PULocationID,
            COUNT(*) AS num_trips,
            SESSION_START(ts, INTERVAL '5' MINUTE) AS session_start,
            SESSION_END(ts, INTERVAL '5' MINUTE) AS session_end
        FROM green_trips_session
        GROUP BY 
            SESSION(ts, INTERVAL '5' MINUTE), 
            PULocationID
    """).wait()

if __name__ == '__main__':
    run_session_window_job()