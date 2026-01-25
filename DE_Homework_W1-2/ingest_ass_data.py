
## importing the key libaries
# importing libaryis to 
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm
import pyarrow.parquet as pq
import requests
import click 


@click.command()
@click.option('--pg_user', default='root', show_default=True, help='Postgres user')
@click.option('--pg_pass', default='root', show_default=True, help='Postgres password')
@click.option('--pg_host', default='localhost', show_default=True, help='Postgres host')
@click.option('--pg_port', default=5432, show_default=True, help='Postgres port', type=int)
@click.option('--pg_db', default='ny_taxi', show_default=True, help='Postgres database')
@click.option('--batch_size', default=1000, show_default=True, help='Batch size for inserts', type=int)
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, batch_size):

        # Create the connection string
        engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

        # Load entire parquet file into memory
        url_green = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet"
        df = pd.read_parquet(url_green, engine="pyarrow")



        # Create table schema first
        df.head(0).to_sql(
            name="green_taxi_data",
            con=engine,
            if_exists="replace",
            index=False
        )

        # Write data in 100-row chunks
        for start in tqdm(range(0, len(df), batch_size), desc="Writing rows in batches"):
            end = start + batch_size
            df_chunk = df.iloc[start:end]
            df_chunk.to_sql(
                name="green_taxi_data",
                con=engine,
                if_exists="append",
                index=False
            )

        ## working with LU data
        # Target URL
        url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"
        # Spoof headers to mimic a browser
        df_lu = pd.read_csv(url)

        # Step 1: Create table schema using header only
        df_lu.head(0).to_sql(
            name="taxi_zone_lookup",
            con=engine,
            if_exists="replace",  # overwrite if table exists
            index=False
        )

        # Step 2: Insert all rows (except header)
        df_lu.to_sql(
            name="taxi_zone_lookup",
            con=engine,
            if_exists="append",   # append rows into the schema
            index=False
        )

        print(f'✅ Taxi Zone Lookup table created and {len(df_lu)} rows of data inserted!')


if __name__ == '__main__':
    run()




