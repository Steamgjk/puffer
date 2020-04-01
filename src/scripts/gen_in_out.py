#!/usr/bin/env python3
# python ttp_local.py --use-csv --file-path ~/Documents/puffer-201903 --start-date 20190301 --end-date 20190301 --save-model ./save_model/
import json
import argparse
import yaml
import torch
import datetime
import sys
from os import path
from datetime import datetime, timedelta
import numpy as np
from multiprocessing import Process, Array, Pool
import pandas as pd
import matplotlib
import gc
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from helpers import (
    connect_to_influxdb, connect_to_postgres,
    make_sure_path_exists, retrieve_expt_config, create_time_clause,
    get_expt_id, get_user)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--use-debug', dest='use_debug', action='store_true', 
                        help='in debug mode')                        
    parser.add_argument('--file-path', dest='file_path',
                        help='path of training data')  
    parser.add_argument('--start-date', dest='start_date',
                        help='start date of the training data')  
    parser.add_argument('--end-date', dest='end_date',
                        help='end date of the training data')    

    args = parser.parse_args()
    print('file_path {0}'.format(args.file_path))
    print('start date {0}'.format(args.start_date)) 
    print('end date {0}'.format(args.end_date)) 

    start_dt = datetime.strptime(args.start_date,"%Y%m%d")
    end_dt = datetime.strptime(args.end_date,"%Y%m%d")

    # process csv files
    proc_list = []
    for i in range(Model.FUTURE_CHUNKS):
        proc = Process(target=train_or_eval_model,
                       args=(i, args,
                             raw_in_out[i]['in'], raw_in_out[i]['out'],))
        proc.start()
        proc_list.append(proc)

    # wait for all processes to finish
    for proc in proc_list:
        proc.join()


if __name__ == '__main__':
    main()
