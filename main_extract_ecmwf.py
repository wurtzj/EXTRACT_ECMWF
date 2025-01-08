#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:05:01 2022

@author: wurtzj
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
import time
import define_parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

nb_max_parallel         = 10
count_proc              = 0
time_to_wait_in_seconds = 10800

for date in define_parameters.list_of_dates:
    if count_proc < nb_max_parallel:
        os.system("nohup python extract_ecmwf.py " + date +" &")
        count_proc=count_proc+1
    else:
        # if too much dates are requested you will have to wait before resending
        # thresholds have to be tuned (nb and time max)
        print("Warning ! Number of requested dates is higher than ", nb_max_parallel)
        print("-> Launched the script with nohup command if it is not yet the case")
        time.sleep(time_to_wait_in_seconds)
        count_proc=0


