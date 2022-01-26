-- This query can be used to extract the transaction inputs data from the Dash blockchain.
--
-- Author:  Roman Overko
-- Contact: roman.overko@iota.org
-- Date:    January 26, 2022

#standardSQL 

-- All transaction inputs data will be skipped after this date
DECLARE FINAL_DATE DATE;
SET FINAL_DATE = DATE("2022-01-17"); --exclusively

SELECT FORMAT_DATE("%Y-%m-%d", inputs.block_timestamp) AS date, array_to_string(inputs.addresses, ",") AS address, -inputs.value AS value
FROM `bigquery-public-data.crypto_dash.inputs` AS inputs WHERE inputs.value > 0 AND DATE(inputs.block_timestamp) < FINAL_DATE
ORDER BY date ASC
