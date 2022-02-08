# Account balances for different blockchains: data extraction and processing

The code in this repository is used to extract the data from different blockchains. The data sets are 
publicly available on 
[Google BigQuery](https://bigquery.cloud.google.com/dataset/bigquery-public-data).
The extracted data is then processed in order to obtain top account balances for a given date.

## Implementation

The coding language of this project is ````Python 3.9````. Queries are written in the ````SQL```` 
programming language.

## Getting Started
Please follow these instructions to install all the requirements and use the scripts correctly.

### Requirements and Installation
**Make sure you have installed:**
1. [Python 3.9](https://www.python.org/downloads/release/python-390/)

**Download the code:**
```bash
git clone https://github.com/roman1e2f5p8s/blockchain_account_balances
```

**Create a virtual environment ```venv```:**
```bash
python3.9 -m venv venv
```

**Activate the virtual environment:**
- On Unix or MacOS:
```bash
source venv/bin/activate
```
- On Windows:
```bash
venv\Scripts\activate.bat
```

**Install the dependencies:**
```bash
pip3.9 install -r requirements.txt
```

## Data extraction

To extract the data, please use SQL queries in folder 
[extract/btc_like](https://github.com/roman1e2f5p8s/blockchain_account_balances/tree/main/extract/btc_like)
 for Bitcoin, Bitcoin Cash, Dash, Dogecoin, and Litecoin, and in folder
[extract/eth_like](https://github.com/roman1e2f5p8s/blockchain_account_balances/tree/main/extract/eth_like)
 for Ethereum and Ethereum Classic. The queries can be ran on the 
[Google BigQuery workspace](https://console.cloud.google.com/bigquery). For example, for Dogecoin, the 
query [extract/btc_like/dogecoin_inputs.sql](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/extract/btc_like/dogecoin_inputs.sql) returns the following results 
(note that only the first five rows are presented here):

| date       | address                            | value           |
| ---------- | -----------------------------------| ----------------|
| 2013-12-08 | D9Skh9j59FL7vEoLJCtf4XgKJS1kWir7DP | -2276328996000  |
| 2013-12-08 | DFX4rgQRhx7kkGDKpxk2QtKKyE9yizxr1F | -22762870502680 |
| 2013-12-08 | DUTQtroaiftqibbHFJvKLfKDP1tDR1MP54 | -23767817654776 |
| 2013-12-08 | D7XDX6keURQH6XiumtNoQBPreEwVwRLakR | -20275168324588 |
| 2013-12-08 | DNG3G7pKc1DgciyWs36GFUnVyvJieDhKdb | -59175300000000 |

Query results can also be directly exported to CSV files saved on Google Cloud Storage (GCS). 
For instructions, please refer to 
[extract2csv.sql](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/extract2csv.sql) in 
[our another repository](https://github.com/roman1e2f5p8s/erc20_token_holders).

## Data processing

...
