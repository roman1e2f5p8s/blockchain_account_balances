#!/usr/bin/env python3.9

# This script can bee used to calcualted top account balances from weekly pickle files.
#
# Author:  Roman Overko
# Contact: roman.overko@iota.org
# Date:    February 09, 2022

import os
import gc
import signal
import pickle
import argparse
import datetime
import pandas as pd
from time import time, sleep
from collections import defaultdict

# handler stop calculating and save dictionary to file
global stop
stop = False
def handler(signum, frame):
    global stop
    stop = True


def main():
    formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50)
    parser = argparse.ArgumentParser(
            description='Calculates top account balances from pickle files split by weeks',
            add_help=False,
            formatter_class=formatter,
            )
    
    # required arguments
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument(
            '--dir',
            type=str,
            required=True,
            help='Path to parent directory with blockchain historical data',
            )
    required_args.add_argument(
            '--name',
            type=str,
            required=True,
            help='Name of blockchain (also the name of the folder with pickle files)',
            )
    required_args.add_argument(
            '--start_date',
            type=str,
            required=True,
            help='Start date to consider (this date is printed by split_csv.py)'
            )
    
    # optimal arguments
    optional_args = parser.add_argument_group('optional arguments')
    optional_args.add_argument(
            '-h',
            '--help',
            action='help',
            help='show this help message and exit',
            )
    optional_args.add_argument(
            '--top',
            type=int,
            default=10000,
            help='How many top account balances to consider, defaults to 10000',
            )
    optional_args.add_argument(
            '--drop_step',
            type=int,
            default=10,
            help='Drop zero balances (after reading each DROP_STEP-th pickle file) from directory '
                'before sorting it (reduces memory consumption), defaults to 10',
            )
    optional_args.add_argument(
            '--rm',
            action='store_true',
            default=False,
            help='Remove pickle files after calculating, defaults to False'
            )
    optional_args.add_argument(
            '--end_date',
            type=str,
            default='2022-07-01',
            help='End date to consider, defaults to 2022-07-01'
            )
    optional_args.add_argument(
            '--verbose',
            action='store_true',
            default=False,
            help='Print detailed output to console, defaults to False'
            )
    optional_args.add_argument(
            '--keep_address',
            action='store_true',
            default=False,
            help='Keep address along with its values, defaults to False'
            )
    args = parser.parse_args()
    
    DIR = os.path.join(args.dir, args.name)
    if not os.path.isdir(DIR):
        raise FileNotFoundError('Directory \"{}\" does not exist!'.format(DIR))
    
    SUB_DIRS = [d for d in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, d))]
    if not SUB_DIRS:
        raise FileNotFoundError('Directory \"{}\" contains no subfolders!'.format(DIR))
    
    n_files = []
    for sd in SUB_DIRS:
        sub_dir = os.path.join(DIR, sd, 'pkl')
        # pkl_files = [f for f in os.listdir(sub_dir) if f[-3:] == 'pkl']
        pkl_files = os.listdir(sub_dir)
        if not pkl_files:
            raise FileNotFoundError('Directory \"{}\" contains no pickle files!'.format(DIR))
        n_files.append(len(pkl_files))
    assert n_files.count(n_files[0]) == len(n_files)
    
    try:
        BALANCES_PKL_FILE = [f for f in os.listdir(DIR) if f.endswith('pickle')][0]
        NUM_PROCESSED_WEEKS = int(BALANCES_PKL_FILE.split('.')[0].split('_')[-1])
    except IndexError:
        BALANCES_PKL_FILE = None
        NUM_PROCESSED_WEEKS  = 0

    PKL_FILES = list(sorted(pkl_files))[NUM_PROCESSED_WEEKS:]
    N_FILES = len(PKL_FILES)
    print(NUM_PROCESSED_WEEKS, N_FILES, PKL_FILES[0])
    
    START_DATE = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
    DELTA = datetime.timedelta(weeks=1)

    date = START_DATE + DELTA * NUM_PROCESSED_WEEKS
    # date = START_DATE + DELTA
    if BALANCES_PKL_FILE:
        with open(os.path.join(DIR, BALANCES_PKL_FILE), 'rb') as f:
            balances = pickle.load(f)
        os.remove(os.path.join(DIR, BALANCES_PKL_FILE))
        fname = os.path.join(DIR, 'top{}_balances'.format(args.top) + \
            '_addresses' * args.keep_address + '.csv')
        main_df = pd.read_csv(fname, header=0)
    else:
        balances = defaultdict(float)
        main_df = pd.DataFrame()

    signal.signal(signal.SIGINT, handler)

    print('Calculating top account balances...')
    start = time()
    for i, file_ in enumerate(PKL_FILES):
        if args.verbose:
            print(' file {} out of {}'.format(i + NUM_PROCESSED_WEEKS,
                N_FILES + NUM_PROCESSED_WEEKS - 1), end='\r')

        for sd in SUB_DIRS:
            fname = os.path.join(DIR, sd, 'pkl', file_)
            f = open(fname, 'rb')
            gc.disable()
            df = pickle.load(f)
            gc.enable()
            f.close()

            z1 = zip(*df.to_dict('list').values())
            for address, value in z1:
                balances[address] += (value / 10**8) if not args.name.lower().startswith('eth') \
                        else (value / 10**18)
        
        if args.keep_address:
            balances = defaultdict(float, {k: v for k, v in sorted(balances.items(), reverse=True, 
                key=lambda item: item[1]) if v})
            sorted_d_len = len(balances)
        else:
            if i % args.drop_step:
                sorted_d = [v for v in balances.values() if v]
            else:
                balances = defaultdict(float, {k: v for k, v in balances.items() if v})
                sorted_d = list(balances.values())
            sorted_d.sort(reverse=True)
            sorted_d_len = len(sorted_d)

        cut = args.top if sorted_d_len >= args.top else sorted_d_len
    
        if not args.keep_address:
            df = pd.DataFrame({date.strftime('%Y-%m-%d'): sorted_d[:cut]})
        else:
            df = pd.DataFrame({date.strftime('%Y-%m-%d'): list(balances.keys())[:cut]})
            df = pd.concat([df, pd.DataFrame({'': list(balances.values())[:cut]})], axis=1)
        main_df = pd.concat([main_df, df], axis=1)
        date += DELTA

        # sleep(2)

        if stop:
            print('\nSaving balances to pkl file at week {}...'.format(i + NUM_PROCESSED_WEEKS))
            with open(os.path.join(DIR, 'balances_{}.pickle'.format(i + NUM_PROCESSED_WEEKS + 1)), 
                    'wb') as f:
                pickle.dump(balances, f, pickle.HIGHEST_PROTOCOL)
            # assert main_df.shape[1] == N_FILES if not args.keep_address else N_FILES / 2
            fname = os.path.join(DIR, 'top{}_balances'.format(args.top) + \
                '_addresses' * args.keep_address + '.csv')
            main_df.to_csv(fname, index=False)
            print('Exiting...')
            exit()

    print(' ' * 50, end='\r')
    print('Calculating done! Saving data...')
    # assert main_df.shape[1] == N_FILES if not args.keep_address else N_FILES / 2
    fname = os.path.join(DIR, 'top{}_balances'.format(args.top) + \
            '_addresses' * args.keep_address + '.csv')
    # main_df = main_df / 10**8 if not args.name.lower().startswith('eth') else main_df / 10**18
    main_df.to_csv(fname)
    with open(os.path.join(DIR, 'balances_{}.pickle'.format(N_FILES + NUM_PROCESSED_WEEKS - 1)), 
            'wb') as f:
        pickle.dump(balances, f, pickle.HIGHEST_PROTOCOL)
    print('Elapsed time: {:.4f} s'.format(time() - start))
    print('Data saved in {}'.format(fname))


if __name__ == '__main__':
    main()
