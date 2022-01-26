-- This query can be used to extract the transaction outputs data from the Litecoin blockchain.
--
-- Author:  Roman Overko
-- Contact: roman.overko@iota.org
-- Date:    January 26, 2022

#standardSQL 

-- All transaction outputs data will be skipped after this date
DECLARE FINAL_DATE DATE;
SET FINAL_DATE = DATE("2022-01-17"); --exclusively

SELECT FORMAT_DATE("%Y-%m-%d", outputs.block_timestamp) AS date, array_to_string(outputs.addresses, ",") AS address, outputs.value AS value
FROM `bigquery-public-data.crypto_litecoin.outputs` AS outputs WHERE outputs.value > 0 AND DATE(outputs.block_timestamp) < FINAL_DATE
ORDER BY date ASC
