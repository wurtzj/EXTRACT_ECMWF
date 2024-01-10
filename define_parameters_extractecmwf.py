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
json_file    = open('PARAMS_EXTRACT.json', 'r')
json_params = json.load(json_file)
json_file.close()

# -------------------------------------------------------
#   Store json params in variables
# -------------------------------------------------------

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Directory where files will be available. It has to end with a /
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
target_directory=json_params["target_directory"]

if target_directory[-1] != "/":
    target_directory = target_directory + "/"

# Adding automatic path creation
try :
    os.mkdir(target_directory)
    print("creation of "+ target_directory + " exists : OK")

except:
    print(target_directory + " exists : OK")

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

forecast_start_time = json_params["forecast_start_time"]

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

if type_data=="FC" and end_time=="00" and start_time=="00":
    end_time="24"
    print("end_time=start_time=00 , as type_data = FC setting end_time to 24")

if type_data=="AN" and end_time=="00" and start_time=="00":
    end_time="18"
    print("end_time=start_time=00 , as type_data = AN setting end_time to 18")

hours=start_time+"/to/"+end_time+"/by/"+step

if type_data=="EN":
    number_of_members=26
    members="/".join(np.array(range(0,number_of_members)).astype("str"))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Domain extension and grid 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Keep empty to get EUROPE domain
lat_min=json_params["lat_min"]
lat_max=json_params["lat_max"]
lon_min=json_params["lon_min"]
lon_max=json_params["lon_max"]
area=json_params["area"]

if area=="" and lat_max != "":
    area=lat_max+"/"+lon_min+"/"+lat_min+"/"+lon_max

if area=='GLOBAL' and lat_max=="":
    area=""

if lat_min=="" or lat_max=="" or lat_min=='' or lat_max=='' :
    print("Warning ! No domain specified, EUROPE set as default")
    area="EUROPE"

# grid, enables to get the correct grid for MNH
grid = json_params["grid"]
grid = grid+"/"+grid

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Id parameters to be extracted  
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Get surface parameters or not, default is True
get_surface = json_params["get_surface"]

# Get sea state parameters or not, default is False
get_sea_state = json_params["get_sea_state"]

# parameters number necessary to MESO-NH

#Surface fields 
  #129 geopotential
  #172 land_binary_mask
  #43 soil type
  #139 soil temperature level 1
  #141 lwe_thickness_of_surface_snow_amount
  #170 Soil temperature level 2
  #183 Soil temperature level 3
  #236 Soil temperature level 4
  #39 Volumetric soil water layer 1
  #40 Volumetric soil water layer 2
  #41 Volumetric soil water layer 3
  #42 Volumetric soil water layer 4
  
#3D fields
 #133 q specific humidity
 #130 temperature
 #131 u wind
 #132 v wind
 
#Pressure (one of these two is necessary for init)
  #152 lnsp : logarithm of surface pressure (analysis only (?))
  #134 surface pressure (forecast -> which cases ?)

if type=="FC":
    pressure="/134"
    param_atm="130/131/132/133" 
    param_surf="129/172/139/141/170/183/236/39/40/41/42"+ pressure
    param_sea_stae="229/234/237"
else:
    pressure="/152"
    param_atm="130/131/132/133" + pressure
    param_surf="129/172/139/141/170/183/236/39/40/41/42"
    param_sea_state="229/234/237"
