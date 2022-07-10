#!/usr/bin/env python3.9

# This script can be used to split CSV files downloaded from GCS by weekly data saved into pickle files.
# The resulting pickle files can then be processed by script calc_top_balances.py
#
# Author:  Roman Overko
# Contact: roman.overko@iota.org
# Date:    February 08, 2022

import os
import argparse
import datetime
import pandas as pd
from time import time


def main():
    formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50)
    parser = argparse.ArgumentParser(
            description='Converts and splits CSV files (downloaded from GCS) to weekly data saved in '
                'pickle files',
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
            help='Name of blockchain (also the name of the folder with CSV files)',
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
            '--rm',
            action='store_true',
            default=False,
            help='Remove CSV files after converting, defaults to False'
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
    args = parser.parse_args()
    
    DIR = os.path.join(args.dir, args.name)
    if not os.path.isdir(DIR):
        raise FileNotFoundError('Directory \"{}\" does not exist!'.format(DIR))

    SUB_DIRS = [d for d in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, d))]
    if not SUB_DIRS:
        raise FileNotFoundError('Directory \"{}\" contains no subfolders!'.format(DIR))
    
    first_dates = []
    for sd in SUB_DIRS:
        sub_dir = os.path.join(DIR, sd, 'csv')
        # csv_files = [f for f in os.listdir(sub_dir) if f[-3:] == 'csv']
        csv_files = os.listdir(sub_dir)
        if not csv_files:
            raise FileNotFoundError('Directory \"{}\" contains no CSV files!'.format(sub_dir))
        csv_files = list(sorted(csv_files))
        
        df = pd.read_csv(os.path.join(sub_dir, csv_files[0]), nrows=1, parse_dates=['block_date'])
        first_date = df['block_date'].iloc[0]
        first_dates.append(first_date)
        del df

    first_date = min(first_dates)
    END_WEEKDAY = datetime.datetime.strptime(args.end_date, '%Y-%m-%d').weekday()
    DELTA = datetime.timedelta(weeks=1)
    
    days_ahead = END_WEEKDAY - first_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    START_DATE = first_date + datetime.timedelta(days_ahead)
    assert START_DATE.weekday() == END_WEEKDAY
    print('Use \"{}\" as start_date for calc_top_balances.py'.\
            format(datetime.datetime.strftime(START_DATE, '%Y-%m-%d')))
    # exit()
    
    start = time()
    for sd in SUB_DIRS:
        date = START_DATE + DELTA
        csv_rows_counter = 0
        pkl_rows_counter = 0
        week_counter = 0
        to_save_df = pd.DataFrame()
        
        sub_dir = os.path.join(DIR, sd)
        # csv_files = [f for f in os.listdir(sub_dir) if f[-3:] == 'csv']
        csv_files = os.listdir(os.path.join(sub_dir, 'csv'))
        csv_files = list(sorted(csv_files))
        n_files = len(csv_files)

        if not os.path.isdir(os.path.join(sub_dir, 'pkl')):
            os.makedirs(os.path.join(sub_dir, 'pkl'))

        print('Converting data in \"{}\"...'.format(sub_dir))
        for i, file_ in enumerate(csv_files):
            if args.verbose:
                print(' file {} out of {}'.format(i, n_files - 1), end='\r')
        
            fname = os.path.join(sub_dir, 'csv', file_)
            df = pd.read_csv(fname, dtype={'value': float}, parse_dates=['block_date'])
            csv_rows_counter += df.shape[0]
            
            to_save_df = pd.concat([to_save_df, df[df['block_date'] <= date][['address', 'value']]])
            remain_df = df[df['block_date'] > date]
        
            while not remain_df.empty:
                to_save_df.to_pickle(os.path.join(sub_dir, 'pkl', '{:04d}.pkl'.format(week_counter)))
                pkl_rows_counter += to_save_df.shape[0]
                week_counter += 1
                date += DELTA
        
                df = remain_df
                to_save_df = df[df['block_date'] <= date][['address', 'value']]
                remain_df = df[df['block_date'] > date]
        
            if args.rm:
                os.remove(fname)
        
        to_save_df.to_pickle(os.path.join(sub_dir, 'pkl', '{:04d}.pkl'.format(week_counter)))
        pkl_rows_counter += to_save_df.shape[0]
        assert pkl_rows_counter == csv_rows_counter
    
    print(' ' * 50, end='\r')
    print('Converting done!')
    print('Elapsed time: {:.4f} s'.format(time() - start))


if __name__ == '__main__':
    main()
