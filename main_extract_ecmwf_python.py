#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:05:01 2022

@author: wurtzj
"""

import os
import define_parameters_extractecmwf
#Adding parallelisation

nb_max_parallel = 10
count_proc=0
time_to_wait=21600  #in seconds

import time
for DATE in define_parameters_extractecmwf.LISTE_DATES:
    print(DATE)
    if count_proc < nb_max_parallel:
        os.system("nohup python3 extractecmwf_run.py " + DATE +" &")
        count_proc=count_proc+1
        time.sleep(10)
    else:   #if too much dates are requested you will have to wait before resending
        #thresholds have to be tuned (nb and time max)
        time.sleep(time_to_wait)
        count_proc=0
