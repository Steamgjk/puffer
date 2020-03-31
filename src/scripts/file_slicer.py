#!/usr/bin/env python3
import os
import sys
import json
import argparse
import yaml
import torch
import datetime
from os import path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from multiprocessing import Process


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video-send-csv-file', dest='video_send_csv_file',
                        help='file path of video_send.csv')
    parser.add_argument('--video-acked-csv-file', dest='video_acked_csv_file',
                        help='file path of video_acked.csv')  
    parser.add_argument('--client-buffer-csv-file', dest='client_buffer_csv_file',
                        help='file path of client_buffer.csv')    
    parser.add_argument('--start-date', dest='start_date',
                        help='start date of the training data')  
    parser.add_argument('--end-date', dest='end_date',
                        help='end date of the training data')    

    args = parser.parse_args()

    print('video_send_csv_file {0}'.format(args.video_send_csv_file))
    print('video_acked_csv_file {0}'.format(args.video_acked_csv_file))
    print('client_buffer_csv_file {0}'.format(args.client_buffer_csv_file))
    print('start time {0}'.format(args.start_date)) 
    print('end time {0}'.format(args.end_date)) 
    start_timestamp=datetime.strptime(args.start_date,"%Y%m%d").timestamp()
    end_timestamp=datetime.strptime(args.end_date,"%Y%m%d").timestamp()
    print('start_timestamp={0}'.format(start_timestamp))
    print('end_timestamp={0}'.format(end_timestamp))

    chunk_size = 100
    df = pd.DataFrame()
    df_dict={}
    merge_dt = pd.read_csv( args.video_send_csv_file,  header=None, encoding="utf_8", engine='python' , iterator = True, chunksize=chunk_size ) 
    for chunk in merge_dt:
        for index, row in chunk.iterrows():
            #print(row[0])
            # time is measured in milliseconds
            dt = datetime.fromtimestamp(row[0]/1000)
            df_key = dt.strftime('%Y%m%d')  
            if not df_dict.__contains__(df_key):
                df_dict[df_key] = pd.DataFrame()                
            df_dict[df_key] = df_dict[df_key].append(row,ignore_index=True)   
        for key, val in df_dict.items():
            print(key)
            print(type(val))
            print(val.shape)
            csv_file_name = key+".csv"
            if not os.path.isfile(csv_file_name):
                val.to_csv(csv_file_name, header=False, index=False, sep=",")
            val.to_csv(csv_file_name, mode='a', header=False, index=False, sep=",")
        '''    
            df = df.append(row,ignore_index=True)   
        if not os.path.isfile('my_csv.csv'):
            df.to_csv('my_csv.csv', header=False, index=False, sep=",")
        else:
            df.to_csv('my_csv.csv', mode='a', header=False, index=False, sep=",")
        '''    
        exit(0)


if __name__ == '__main__':
    main()