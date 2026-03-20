
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment


def create_events_source_kafka(t_env):
    table_name = "events"
    source_ddl = f"""
        CREATE TABLE {table_name} (
            PULocationID BIGINT,
            DOLocationID BIGINT,
            passenger_count BIGINT,
            trip_distance DOUBLE,
            tip_amount DOUBLE,
            total_amount DOUBLE,
            lpep_pickup_datetime BIGINT,
            lpep_dropoff_datetime BIGINT
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda:29092',
            'topic' = 'green-trips',
            'scan.startup.mode' = 'earliest-offset',
            'properties.auto.offset.reset' = 'earliest',
            'format' = 'json',
            'json.ignore-parse-errors' = 'true'
        );
        """
    t_env.execute_sql(source_ddl)
    return table_name


def create_processed_events_sink_postgres(t_env):
    table_name = 'processed_events'
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            PULocationID BIGINT,
            DOLocationID BIGINT,
            passenger_count BIGINT,
            trip_distance DOUBLE,
            tip_amount DOUBLE,
            total_amount DOUBLE,
            pickup_datetime TIMESTAMP,
            dropoff_datetime TIMESTAMP
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = '{table_name}',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        );
        """
    t_env.execute_sql(sink_ddl)
    return table_name


def log_processing():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10 * 1000)  # checkpoint every 10 seconds

    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    source_table = create_events_source_kafka(t_env)
    postgres_sink = create_processed_events_sink_postgres(t_env)

    t_env.execute_sql(
        f"""
        INSERT INTO {postgres_sink}
        SELECT
            PULocationID,
            DOLocationID,
            passenger_count,
            trip_distance,
            tip_amount,
            total_amount,
            TO_TIMESTAMP_LTZ(lpep_pickup_datetime, 3) AS pickup_datetime,
            TO_TIMESTAMP_LTZ(lpep_dropoff_datetime, 3) AS dropoff_datetime
        FROM {source_table}
        """
    ).wait()

if __name__ == '__main__':
    log_processing()
    