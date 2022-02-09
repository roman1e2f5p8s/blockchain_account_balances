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
[Google BigQuery workspace](https://console.cloud.google.com/bigquery). For example, for Dash, the 
query [extract/btc_like/dash_inputs.sql](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/extract/btc_like/dash_inputs.sql) returns the following results 
(note that only the first five rows are presented here):

| date       | address                            | value        |
| ---------- | -----------------------------------| -------------|
| 2014-01-19 | Xm4x8WXU4Yzh6DJZaMhU6AURze2rnXd3SZ | -12702199    |
| 2014-01-19 | Xo1TKKMRk15sfP46WENHX3Cj3VLgb5CYvP | -27700000000 |  
| 2014-01-19 | XqjJHF1krBxbHrUpfMQAfRgDm7wQq7o4qu | -50000000000 |
| 2014-01-19 | XtqSRHufguDsBmsirgAQZjxYhSS52sZxRf | -50000000000 |
| 2014-01-19 | XyTSKzD7pbVLhJQV1fVsNVR9NFALjpyuBR | -27700000000 |


Query results can also be directly exported to CSV files saved on Google Cloud Storage (GCS). 
For instructions, please refer to 
[extract2csv.sql](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/extract2csv.sql) in 
[our another repository](https://github.com/roman1e2f5p8s/erc20_token_holders) on ERC20 token holders. 

The queried data in the form of CSV files for other blockchains is publicly available in 
[this bucket on GCS](https://console.cloud.google.com/storage/browser/blockchain_historical_data).

## Data processing

Queried data must thereafter be processed in order to calculate weekly top account balances.
Two Python scripts are used for data processing: 
[split_csv.py](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/split_csv.py) and 
[calc_top_balances.py](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/calc_top_balances.py).

### Step 1: split CSV files to weekly data saved in pickle files

Use [split_csv.py](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/split_csv.py) 
to split CSV files downloaded from GCS by weekly data saved into pickle files.
The choice of the pickle format over CSV is made to save storage space and speed up data loading.

Example usage: assuming CSV files for the Dash blockchain (can be downloaded from 
[Google Drive](https://drive.google.com/drive/folders/1oWilo-ss1yRWieO4BZ-RvzhyP3Yk94Vt?usp=sharing) 
or directly extracted using both 
[extract/btc_like/dash_inputs.sql](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/extract/btc_like/dash_inputs.sql) and 
[extract/btc_like/dash_outputs.sql](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/extract/btc_like/dash_outputs.sql) scripts) are stored in ````./data/dash/````:

```bash
python3.9 split_csv.py --dir="data" --name="dash" --verbose
```

The script 
[split_csv.py](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/split_csv.py) 
also outputs the start date to be used later in the 
[calc_top_balances.py](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/calc_top_balances.py) script. The start date is date such that a week ahead will be the 
first date for which top richest accounts 
will be calculated. For example, for Dash, 
[split_csv.py](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/split_csv.py) 
will output:

```
Use "2014-01-26" as start_date for calc_top_balances.py
```

See help files for more details:

```bash
python3.9 split_csv.py --help
```

```
usage: split_csv.py --dir DIR --name NAME [-h] [--rm] [--end_date END_DATE] [--verbose]

Converts and splits CSV files (downloaded from GCS) to weekly data saved in pickle files

required arguments:
  --dir DIR            Path to parent directory with blockchain historical data
  --name NAME          Name of blockchain (also the name of the folder with CSV files)

optional arguments:
  -h, --help           show this help message and exit
  --rm                 Remove CSV files after converting, defaults to False
  --end_date END_DATE  End date to consider, defaults to 2022-01-16
  --verbose            Print detailed output to console, defaults to False
```

### Step 2: calculate weekly top account balances

Use 
[calc_top_balances.py](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/calc_top_balances.py) to calculates top account balances from pickle files split by weeks.

Example usage: assuming pickle files for the Dash blockchain are stored in ````./data/dash/````, and 
the start date (returned by 
[split_csv.py](https://github.com/roman1e2f5p8s/blockchain_account_balances/blob/main/split_csv.py)) 
is ````2014-01-26````:

```bash
python3.9 calc_top_balances.py --dir="data" --name="dash" --start_date="2014-01-26" --verbose
```

This will generate a CSV file (saved in ````./data/dash/````) with weekly top 10000 account balances.
For example, top five account balances for the first three dates are given in the table below:

|2014-02-02      | 2014-02-09      | 2014-02-16      |
|----------------|-----------------|-----------------|
|184214.658      | 193500.99334055 | 193500.99334055 |
|159329.968      | 184214.658      | 184214.658      |
|143733.42810545 | 157599.995      | 157501          |
|94363.99        | 157501          | 157500          |
|88752.40714677  | 142009.03728116 | 141571.506493   |

See help files for more details:

```bash
python3.9 calc_top_balances.py --help
```

```
usage: calc_top_balances.py --dir DIR --name NAME --start_date START_DATE [-h] [--top TOP]
                            [--drop_step DROP_STEP] [--rm] [--end_date END_DATE] [--verbose]

Calculates top account balances from pickle files split by weeks

required arguments:
  --dir DIR                Path to parent directory with blockchain historical data
  --name NAME              Name of blockchain (also the name of the folder with pickle files)
  --start_date START_DATE  Start date to consider (this date is printed by split_csv.py)

optional arguments:
  -h, --help               show this help message and exit
  --top TOP                How many top account balances to consider, defaults to 10000
  --drop_step DROP_STEP    Drop zero balances (after reading each DROP_STEP-th pickle file) from directory before sorting it (reduces memory consumption), defaults to 10
  --rm                     Remove pickle files after calculating, defaults to False
  --end_date END_DATE      End date to consider, defaults to 2022-01-16
  --verbose                Print detailed output to console, defaults to False
```
