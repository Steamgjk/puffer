#!/usr/bin/env python3

import sys
import json
import argparse
import yaml
import torch
from os import path
from datetime import datetime, timedelta
import numpy as np
from multiprocessing import Process
import subprocess
import shlex
import matplotlib
import matplotlib.pyplot as plt
import gc
from ttp_local import(
    read_csv_to_rows,
    process_raw_csv_data
)


VIDEO_SENT_FILE_PREFIX = 'video_sent_'
VIDEO_ACKED_FILE_PREFIX = 'video_acked_'
CLIENT_BUFFER_FILE_PREFIX = 'client_buffer_'
FILE_SUFFIX = 'T11.csv'
PKT_BYTES = 1500
OUTPUT_STATS="output_stats"
def calc_throughput(folder_name, start_date):
    print("Geting ", folder_name, " start_date=",start_date)
    url_str = "https://storage.googleapis.com/puffer-stanford-data/"+folder_name+".tar.gz"
    cmd = "wget "+ url_str+" --no-check-certificate"
    cmd = shlex.split(cmd)
    subprocess.call(cmd, shell=False)
    print("FIN wget")
    cmd = "tar -zxvf " + folder_name+".tar.gz"
    cmd = shlex.split(cmd)
    subprocess.call(cmd, shell=False)
    print("FIN tar")
    throughput_hist = {}
    min_throuput = sys.maxsize
    max_throughput = 0
    for i in range(0, 32):
        date_item = start_date + timedelta(days=i)
        video_sent_file_name = folder_name+"/"+ VIDEO_SENT_FILE_PREFIX + date_item.strftime('%Y-%m-%d') + FILE_SUFFIX
        video_acked_file_name = folder_name+"/"+ VIDEO_ACKED_FILE_PREFIX + date_item.strftime('%Y-%m-%d') + FILE_SUFFIX
        
        if path.exists(video_sent_file_name) and path.exists(video_acked_file_name):
            video_sent_rows = read_csv_to_rows(video_sent_file_name)
            video_acked_rows = read_csv_to_rows(video_acked_file_name)
            print("len ", len(video_sent_rows), " ", len(video_acked_rows))
            raw_data = process_raw_csv_data(video_sent_rows, video_acked_rows, None)
            del video_sent_rows, video_acked_rows
            gc.collect()
            #print(raw_data)
            
            for session in raw_data:
                for chunk in raw_data[session]:
                    if 'trans_time' in raw_data[session][chunk]:
                        transmission_time  = raw_data[session][chunk]['trans_time']
                        chunk_size = raw_data[session][chunk]['size']
                        throughput = chunk_size*1.0/transmission_time  # bytes/seconds
                        throughput = int(round(throughput))
                        if throughput not in throughput_hist:
                            throughput_hist[throughput] = 0
                            if min_throuput > throughput:
                                min_throuput = throughput
                            if max_throughput < throughput:
                                max_throughput = throughput
                        throughput_hist[throughput] += 1
        else:
            continue 
    sorted_hist = {}
    for i in range(min_throuput, max_throughput+1):
        if  i in throughput_hist:
            sorted_hist[i] = throughput_hist[i]
    print(sorted_hist)
    print("FIN Calc")
    cmd = "rm -rf " + folder_name+".tar.gz"
    cmd = shlex.split(cmd)
    subprocess.call(cmd, shell=False)
    print("FIN rm tar.gz " + folder_name)
    cmd = "rm -rf " + folder_name
    cmd = shlex.split(cmd)
    subprocess.call(cmd, shell=False)
    print("FIN rm folder " + folder_name)
    #with open("")
    return sorted_hist
    
       


def main():
    cmd = "mkdir "+OUTPUT_STATS
    if path.exists(OUTPUT_STATS) is not True:
        cmd = shlex.split(cmd)
        subprocess.call(cmd, shell=False)
    '''
    for i in range(1,13):
        start_dt = datetime(year = 2019, month=i, day = 1)
        folder_name = "puffer-"+"2019"+ str(i).zfill(2)
        print(folder_name)
        print(start_dt)
        calc_throughput(folder, start_dt)
    '''
    start_dt = datetime(year = 2020, month=1, day = 1)
    folder_name = "puffer-"+"2020"+ str(1).zfill(2)
    calc_throughput(folder_name, start_dt)
    return

if __name__ == '__main__':
    main()