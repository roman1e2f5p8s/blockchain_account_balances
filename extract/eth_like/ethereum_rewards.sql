-- This query can be used to extract the data of mining rewards from the Ethereum blockchain.
--
-- Author:  Roman Overko
-- Contact: roman.overko@iota.org
-- Date:    January 26, 2022

#standardSQL  
 
-- All mining rewards data will be skipped after this date
DECLARE FINAL_DATE DATE;
SET FINAL_DATE = DATE("2022-01-17"); --exclusively

SELECT FORMAT_DATE("%Y-%m-%d", transactions.block_timestamp) AS date, miner AS address, SUM(CAST(receipt_gas_used as numeric) * CAST((receipt_effective_gas_price - COALESCE(base_fee_per_gas, 0)) AS numeric)) AS value
FROM `bigquery-public-data.crypto_ethereum.transactions` AS transactions
JOIN `bigquery-public-data.crypto_ethereum.blocks` AS blocks ON blocks.number = transactions.block_number
WHERE DATE(transactions.block_timestamp) < FINAL_DATE
GROUP BY blocks.miner, transactions.block_timestamp
ORDER BY date ASC
