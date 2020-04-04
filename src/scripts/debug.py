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

if __name__ == '__main__':
    main()