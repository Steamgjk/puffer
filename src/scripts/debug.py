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

def main():
    expected = []
    loss2=[]
    with open("exception-131/expected-4", "r") as f1:
        for line in f1:
            lis = eval(line)
            print("line1 ", len(lis), " ", lis[0])
            expected.extend(lis)
    with open("exception-131/debug_l2-4", "r") as f2:
        for line in f2:
            lis = eval(line)
            print("line2 ", len(lis), " ", lis[0])
            loss2.extend(lis)    
    print("len = ", len(expected), " ", len(loss2)," ", expected[0], " ", loss2[0] )
    for i in range(len(expected)):
        if int(expected[i]) > 10 or int(loss2[i])>100:
            print( expected[i], " ", loss2[i], "\n")

def get_transmission_time(video_send_file, video_acked_file):
    merge_dt = pd.read_csv( video_send_file,  
                            header=None, encoding="utf_8", engine='python' , 
                            iterator = True, chunksize=100000 ) 
    sent_info = {}
    row_cnt = 0
    for chunk in merge_dt:
        for index, row in chunk.iterrows():
            sent_time = row[0]  
            session_id = row[1]
            presentation_time = row[4]
            if session_id not in sent_info:
                sent_info[session_id]={}
            sent_info[session_id][presentation_time] = sent_time 
        row_cnt += chunk.shape[0]
        if row_cnt%100000 == 0:
            print("sent file ", row_cnt)

    #print("sent info \n")
    #print(sent_info)
    merge_dt = pd.read_csv( video_acked_file,  
                            header=None, encoding="utf_8", engine='python' , 
                            iterator = True, chunksize=100000 ) 
    acked_info = {}
    row_cnt = 0
    for chunk in merge_dt:
        for index, row in chunk.iterrows():
            acked_time = row[0]  
            session_id = row[1]
            presentation_time = row[4]
            #print("acked ", presentation_time)
            if session_id not in acked_info:
                acked_info[session_id]={}
            acked_info[session_id][presentation_time] = acked_time 
        row_cnt += chunk.shape[0] 
        if row_cnt%100000 == 0:
            print("acked file ", row_cnt)
    
    #print("acked info \n", acked_info)

    ans = {}
    for session in acked_info:
        if session in sent_info:
            for presentation_time in acked_info[session]:
                if presentation_time not in sent_info[session]:
                    #print("Presentation Time ", session, " ", presentation_time, " not in sent")
                    '''
                    print("session info keys")
                    for key in sent_info[session]:
                        print("keys ", key, "\n")
                    exit(0)
                    '''
                    continue
                if session not in ans:
                    ans[session]={}
                ans[session][presentation_time]=(sent_info[session][presentation_time], 
                acked_info[session][presentation_time],
                acked_info[session][presentation_time]-sent_info[session][presentation_time],)

        else:
            print(session, " not in sent info")
    return ans
if __name__ == '__main__':
    #main()
    parser = argparse.ArgumentParser()
    parser.add_argument('--sent-file', dest='sent_file',
                        help='sent file')
    parser.add_argument('--acked-file', dest='acked_file',
                        help='acked file')
    args = parser.parse_args()
    ans = get_transmission_time(args.sent_file, args.acked_file)
    print("FINNNNNN\n\n\n")
    print(len(ans))
    with open("131-ts", "w") as f:
        for itm in ans:
            #print("type ", type(ans[itm]))
            for presentation in ans[itm]:
                line = str(itm)+" "+ str(presentation) + " " +str(ans[itm][presentation])+"\n"
                f.write(line)
                if ans[itm][presentation][2]/1000 > 15:
                    print(itm, ans[itm])