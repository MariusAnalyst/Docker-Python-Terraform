-- Query public available table
-- Creating external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE `teraform-mar.datawarehouse.yellow_taxi_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://marius_dezoomcamp_hw3_2026/yellow_tripdata_2024-*.parquet']
);


-- quering the external table and the materialized table
SELECT DISTINCT(PULocationID)
FROM `datawarehouse.yellow_taxi_data`


-- Querying the external table
SELECT DISTINCT(PULocationID)
FROM `datawarehouse.yellow_taxi_external`


-- Creating a partition and cluster table
CREATE OR REPLACE TABLE `teraform-mar.datawarehouse.yellow_taxi_external-partitioned-clustered`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT * FROM `teraform-mar.datawarehouse.yellow_taxi_external`;


/*Question 6 write a query to check the partitions of the partitioned table
Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01
 and 2024-03-15 (inclusive). Use the materialized table you created earlier in
  your from clause and note the estimated bytes. Now change the table in the from clause 
  to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values?
*/

SELECT DISTINCT(VendorID)
FROM `datawarehouse.yellow_taxi_data`
WHERE DATE(tpep_dropoff_datetime) BETWEEN '2024-03-01' AND '2024-03-15'

-- querying the partitioned and clustered table
SELECT DISTINCT(VendorID)
FROM `teraform-mar.datawarehouse.yellow_taxi_external-partitioned-clustered`
WHERE DATE(tpep_dropoff_datetime) BETWEEN '2024-03-01' AND '2024-03-15'

/* Write a `SELECT count(*)` query FROM the 
materialized table you created. How many bytes does it estimate will
 be read? Why?
 */

SELECT count(*) 
FROM `datawarehouse.yellow_taxi_data`

