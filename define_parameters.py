#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:19:43 2022

@author: wurtzj
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
import numpy as np
import json
import pandas
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("                                                           ")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# -------------------------------------------------------
#   Define internal functions
# -------------------------------------------------------
def str_num(i,num_chiffre=2):
    if i<10:
        return (num_chiffre-1)*"0"+str(i)
    elif i<100:
        return (num_chiffre-2)*"0"+str(i)
    else :
        return str(i)
    
def generate_date(start_date,end_date):
    if start_date==end_date:
        return [start_date]
    list_of_dates = pandas.date_range(start_date,end_date,freq='d')
    return list(list_of_dates.strftime("%Y%m%d"))

# -------------------------------------------------------
#   Open, Read and Close json file
# -------------------------------------------------------
json_file    = open('user_parameters.json', 'r')
json_params = json.load(json_file)
json_file.close()

# -------------------------------------------------------
#   Store json params in variables
# -------------------------------------------------------

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Directory where files will be available. It has to end with a /
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
target_directory=json_params["target_directory"]

if target_directory=="":
    print("Please precise the path for the output in target_directory in   ")
    print("user_parameters.json")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("                                                           ")
    quit()

if target_directory[-1] != "/":
    target_directory = target_directory + "/"

# Adding automatic path creation
try :
    os.mkdir(target_directory)
    print("Creation of output directory "+target_directory)
except:
    print("Output directory "+target_directory+" exists")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   List of dates and time to extract
#   date format YYYYMMDD 
#   time format HH
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
list_of_dates = json_params["list_of_dates"]
start_date    = json_params["start_date"]
end_date      = json_params["end_date"]

# Priority to list of dates
if list_of_dates == [] : 
    list_of_dates = generate_date(start_date,end_date)

start_time = json_params["start_time"]
end_time   = json_params["end_time"]
step       = json_params["step"]
hours      = start_time+"/to/"+end_time+"/by/"+step

forecast_start_time = json_params["forecast_start_time"]

print("Following dates will be extracted ", list_of_dates, " for hours", hours)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Type of data
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# analysis
# forecast
# ensemble -> ensemble analysis
type_data =json_params["type_data"]

if type_data=="forecast":
    type_data="FC"
if type_data=="analysis":
    type_data="AN"
if type_data=="ensemble":
    type_data="EN"

if type_data=="EN":
    number_of_members=26
    members="/".join(np.array(range(0,number_of_members)).astype("str"))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Domain extension and grid 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Keep empty to get EUROPE domain
lat_min = json_params["lat_min"]
lat_max = json_params["lat_max"]
lon_min = json_params["lon_min"]
lon_max = json_params["lon_max"]
area    = json_params["area"]

if area == "" and lat_min != "" and lat_max != "" and lon_min != "" and lon_max != "":
    area = lat_max+"/"+lon_min+"/"+lat_min+"/"+lon_max

if lat_min == "" or lat_max == "" or lat_min == "" or lat_max == "" or area == "":
    print("Warning ! No domain specified, EUROPE set as default")
    area="EUROPE"

# Grid resolution
grid = json_params["grid"]
grid = grid+"/"+grid

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Id parameters to be extracted  
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Get surface parameters or not, default is True
get_surface = json_params["get_surface"]

# Get sea state parameters or not, default is False
get_sea_state = json_params["get_sea_state"]

if type=="FC":
    pressure="/134"
    param_atm="130/131/132/133" 
    param_surf="129/172/139/141/170/183/236/39/40/41/42"+ pressure
    param_sea_state="229/234/237"
else:
    pressure="/152"
    param_atm="130/131/132/133" + pressure
    param_surf="129/172/139/141/170/183/236/39/40/41/42"
    param_sea_state="229/234/237"

print("Login to https://apps.ecmwf.int/webmars/joblist/ to follow your requests.")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  Remove tmp files or not
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

remove_tmp_files = json_params["remove_tmp_files"]

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("                                                           ")
