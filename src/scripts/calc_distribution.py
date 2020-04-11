#!/usr/bin/env python3

import sys
import json
import argparse
import yaml
import torch
from os import path
from datetime import datetime, timedelta
import numpy as np
from multiprocessing import Process, Array, Pool
import subprocess
import shlex
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import gc
import json
import tkinter
import scipy.stats

from ttp_local import(
    read_csv_to_rows,
    process_raw_csv_data
)

VIDEO_SENT_FILE_PREFIX = 'video_sent_'
VIDEO_ACKED_FILE_PREFIX = 'video_acked_'
CLIENT_BUFFER_FILE_PREFIX = 'client_buffer_'
FILE_SUFFIX = 'T11.csv'
OUTPUT_STATS="output_stats"
def calc_throughput_sub(video_sent_file_name, video_acked_file_name):
    throughput_hist = {}
    if path.exists(video_sent_file_name) and path.exists(video_acked_file_name):
        print("reading..", video_sent_file_name)
        video_sent_rows = read_csv_to_rows(video_sent_file_name)
        print("reading..", video_acked_file_name)
        video_acked_rows = read_csv_to_rows(video_acked_file_name)
        print(video_sent_file_name," ", video_acked_file_name, "len ", len(video_sent_rows), " ", len(video_acked_rows))
        raw_data = process_raw_csv_data(video_sent_rows, video_acked_rows, None)
        print("RAW DATA OK ", video_sent_file_name," ", video_acked_file_name)
        del video_sent_rows, video_acked_rows
        gc.collect()
        #print(raw_data)
        for session in raw_data:
            for chunk in raw_data[session]:
                if 'trans_time' in raw_data[session][chunk]:
                    transmission_time  = raw_data[session][chunk]['trans_time']
                    chunk_size = raw_data[session][chunk]['size']
                    if transmission_time == 0:
                        print("transmission_time=",transmission_time, " chunk_size=", chunk_size)
                        continue
                    throughput = chunk_size*1.0/transmission_time  # packets/seconds                    
                    throughput = int(round(throughput))
                    if throughput not in throughput_hist:
                        throughput_hist[throughput] = 0
                    throughput_hist[throughput] += 1
    return  throughput_hist

def func(video_sent_file_name, video_acked_file_name):
    return video_sent_file_name, video_acked_file_name

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
    
    cmd = "rm -rf " + folder_name+".tar.gz"
    cmd = shlex.split(cmd)
    subprocess.call(cmd, shell=False)
    print("FIN rm tar.gz " + folder_name)

    throughput_hist = {}
    min_throuput = sys.maxsize
    max_throughput = 0
    sorted_hist = {}
    for j in range(4):   
        pool = Pool(processes= 8)
        result = [] 
        for i in range(8*j, 8*j+8):
            date_item = start_date + timedelta(days=i)
            if date_item.strftime('%Y-%m-%d') == '2019-06-02':
                #null file, skip
                continue
            video_sent_file_name = folder_name+"/"+ VIDEO_SENT_FILE_PREFIX + date_item.strftime('%Y-%m-%d') + FILE_SUFFIX
            video_acked_file_name = folder_name+"/"+ VIDEO_ACKED_FILE_PREFIX + date_item.strftime('%Y-%m-%d') + FILE_SUFFIX
            
            result.append(pool.apply_async(calc_throughput_sub, args=(video_sent_file_name, video_acked_file_name)))
        
        for res in result:
            hist = res.get() 
            for throughput in hist:
                if min_throuput > throughput:
                    min_throuput = throughput
                if max_throughput < throughput:
                    max_throughput = throughput
                if throughput not in sorted_hist:
                    throughput_hist[throughput] = 0
                throughput_hist[throughput] += hist[throughput]
        pool.close()
        pool.join()
    
    for i in range(min_throuput, max_throughput+1):
        if  i in throughput_hist:
            sorted_hist[i] = throughput_hist[i]
    print(sorted_hist)
    print("FIN Calc")

    
    cmd = "rm -rf " + folder_name
    cmd = shlex.split(cmd)
    subprocess.call(cmd, shell=False)
    print("FIN rm folder " + folder_name)
    jsObj = json.dumps(sorted_hist)  
    with open( OUTPUT_STATS +"/"+ folder_name+".stat", "w") as f:
        f.write(jsObj)
    return sorted_hist
    
       



if __name__ == '__main__':
        
    parser = argparse.ArgumentParser()
    parser.add_argument('--sta', dest='sta', type=int)  
    parser.add_argument('--end', dest='end', type=int)  
    args = parser.parse_args()
    '''
    cmd = "mkdir "+OUTPUT_STATS
    if path.exists(OUTPUT_STATS) is not True:
        cmd = shlex.split(cmd)
        subprocess.call(cmd, shell=False)
    for i in range(args.sta,args.end):
        start_dt = datetime(year = 2019, month=i, day = 1)
        folder_name = "puffer-"+"2019"+ str(i).zfill(2)
        print(folder_name)
        print(start_dt)
        calc_throughput(folder_name, start_dt)    
    '''
    #start_date = datetime(year = 2020, month=1, day = 1)
    #folder_name = "puffer-"+"2020"+ str(1).zfill(2)
    #start_date = datetime(year = 2020, month=2, day = 1)
    #folder_name = "puffer-fake-sample"
    #calc_throughput(folder_name, start_date)
    max_val = 0
    min_val = sys.maxsize
    json_arr = []
    bin_cap = 5000
    bin_size = 15
    max_val = -1
    row_size = 5
    col_size = 3
    
    f, ax = plt.subplots(row_size, col_size, figsize=(10,15), sharex=False, sharey=False)
    plt.subplots_adjust(wspace=0.2, hspace=0.2)
    distris = []
    lbs =[]
    fig_cnt = 0
    for y in range(2019, 2021):
        for i in range(args.sta,args.end):
            file_name = OUTPUT_STATS+"/"+"puffer-"+str(y)+ str(i).zfill(2)+".stat"
            if path.exists(file_name) == False:
                continue
            f = open(file_name, "r")
            jsonObj = json.load(f)
            f.close()
            invalid_keys = []
            for key in jsonObj:
                if int(key) < 0:
                    invalid_keys.append(key)
            for invalid_key in invalid_keys:
                del jsonObj[invalid_key]

            distri = [0 for k in range(bin_size)]
            ele_num = len(jsonObj)
            for key in jsonObj:
                key = int(key)
                #print("  ", int(key/bin_cap), " ", (key/bin_cap), " ", key," ",bin_cap )
                if int(key/bin_cap) < bin_size:
                    distri[ int(key/bin_cap) ] += 1
                else:
                    distri[-1] += 1
            for k in range(bin_size):
                distri[k] = distri[k] * 100.0/ele_num
            
            distris.append(distri)
            lbs.append(str(y)+ str(i).zfill(2))
            sum_val = 0
            for k in range(bin_size):
                sum_val += distri[k]
            print("sum_val=", sum_val)
            print(distri)
            xx =  [(k) for k in range(bin_size)]
            xxx = [int(bin_cap*k/1000) for k in range(bin_size)]
            row_idx = int(fig_cnt/col_size)
            col_idx = int(fig_cnt%col_size)
            
            ax[row_idx][col_idx].set_ylim(0,12)
            ax[row_idx][col_idx].set_xticks(xx, xxx)
            ax[row_idx][col_idx].bar(xx, distri)
            ax[row_idx][col_idx].set_xlabel("Throughput (1000 Packets/Second)")
            ax[row_idx][col_idx].set_ylabel("Percentage (%)")
            title = "Throughput Distribution "+ str(y)+ str(i).zfill(2)
            ax[row_idx][col_idx].set_title(title)
            '''
            plt.ylim(0,12)
            plt.xticks(xx, xxx)
            plt.bar(xx, distri)
            plt.xlabel("Throughput (1000 Packets/Second)")
            plt.ylabel("Percentage (%)")
            title = "Throughput Distribution "+ str(y)+ str(i).zfill(2)
            plt.title(title)
            plt.savefig(title+".png")
            plt.close()
            '''
            fig_cnt += 1

    plt.subplots_adjust(wspace=0.5, hspace=0.5)
    plt.savefig("Distribution.png")

    print("KL Divergence \n\n\n ")
    distri_num = len(distris)
    for i in range(distri_num):
        for k in range(len(distris[i])):
            if(distris[i][k] == 0):
                distris[i][k] = 0.00001
    kl_divergences = [ [0.0 for i in range(distri_num)] for j in range(distri_num)]
    line = "\t"
    for i in range(distri_num):
        line += lbs[i]+"\t"
    print(line)
    for i in range(distri_num):
        line = lbs[i] + "\t"
        for j in range(distri_num):    
            kl_divergences[i][j] = round(scipy.stats.entropy(distris[i], distris[j]),3) 
            line += str(kl_divergences[i][j])+ "\t"
        print(line)
    
            
    






