-- This query can be used to extract the data of received funds from the Ethereum blockchain.
--
-- Author:  Roman Overko
-- Contact: roman.overko@iota.org
-- Date:    January 26, 2022

#standardSQL

-- All received funds data will be skipped after this date
DECLARE FINAL_DATE DATE;
SET FINAL_DATE = DATE("2022-01-17"); --exclusively

SELECT FORMAT_DATE("%Y-%m-%d", block_timestamp) AS date, to_address AS address, value AS value
FROM `bigquery-public-data.crypto_ethereum.traces`
WHERE to_address IS NOT NULL AND status = 1 AND value > 0 AND (call_type NOT IN ('delegatecall', 'callcode', 'staticcall') OR call_type IS NULL) AND DATE(block_timestamp) < FINAL_DATE
ORDER BY date ASC
