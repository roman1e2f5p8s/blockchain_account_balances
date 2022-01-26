-- This query can be used to extract the data of gas fees from the Ethereum blockchain.
--
-- Author:  Roman Overko
-- Contact: roman.overko@iota.org
-- Date:    January 26, 2022

#standardSQL  

-- All gas fees data will be skipped after this date
DECLARE FINAL_DATE DATE;
SET FINAL_DATE = DATE("2022-01-17"); --exclusively

SELECT FORMAT_DATE("%Y-%m-%d", transactions.block_timestamp) AS date, from_address AS address, -(CAST(receipt_gas_used AS numeric) * CAST(gas_price AS numeric)) AS value
FROM `bigquery-public-data.crypto_ethereum.transactions` AS transactions
WHERE DATE(transactions.block_timestamp) < FINAL_DATE
ORDER BY date ASC
