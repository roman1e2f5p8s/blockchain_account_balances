#!/usr/bin/env python3.9

import pandas as pd
from time import time
import gcsfs

start = time()
df = pd.read_csv('data/credits_000000000043.csv')
print('Elapsed time: {}'.format(time() - start))
print(df)

start = time()
fs = gcsfs.GCSFileSystem(project='dev-iota', token='anon')
print('Elapsed time: {}'.format(time() - start))

start = time()
with fs.open('gs://blockchain_historical_data/bitcoin/credits/credits_000000000043.csv') as f:
    df = pd.read_csv(f)
print('Elapsed time: {}'.format(time() - start))
print(df)
