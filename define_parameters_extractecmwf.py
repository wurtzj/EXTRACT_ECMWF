#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:19:43 2022

@author: wurtzj
"""


from ecmwfapi import ECMWFService
import os
import numpy as np
import json


def str_num(i,num_chiffre=2):

    if i<10:
        return (num_chiffre-1)*"0"+str(i)
    elif i<100:
        return (num_chiffre-2)*"0"+str(i)

    else :
        return str(i)
    
import pandas
import datetime

def generate_list_date(YEAR_START,MONTH_START,DAY_START, YEAR_END, MONTH_END, DAY_END):
     sdate = datetime.date(YEAR_START,MONTH_START,DAY_START)   # start date
     edate = datetime.date(YEAR_END,MONTH_END,DAY_END)+datetime.timedelta(days=1)   # end date
     liste_of_dates = pandas.date_range(sdate,edate-datetime.timedelta(days=1)).strftime('%Y%m%d').tolist()#,freq='d')
     return liste_of_dates


#Adding automatic dates
def generate_date(date_debut,date_fin):
    
    if date_debut==date_fin:

        return [date_debut]

    LISTE_DATES = pandas.date_range(date_debut,date_fin,freq='d')
    
    return list(LISTE_DATES.strftime("%Y%m%d"))



MAIL = #to be completed 

KEY =  #to be completed


openfile = open('PARAMS_EXTRACT.json', 'r')
 
json_params = json.load(openfile)


openfile.close()


#Directory where files will be available
#It has to end with a /
TARGET_DIRECTORY=json_params["TARGET_DIRECTORY"]


if TARGET_DIRECTORY[-1] != "/":
    TARGET_DIRECTORY = TARGET_DIRECTORY + "/"

#adding automatic path creation
import os
try :
    os.mkdir(TARGET_DIRECTORY)
    print("creation of "+ TARGET_DIRECTORY + " exists : OK")

except:
    print(TARGET_DIRECTORY + " exists : OK")


#List of dates to extract
#Format AAAAMMDD
LISTE_DATES=json_params["LISTE_DATES"]

import pandas
date_debut=json_params["date_debut"]
date_fin=json_params["date_fin"]



#priority to liste of dates
if LISTE_DATES == [] : 
    LISTE_DATES=generate_date(date_debut,date_fin)




#type of data
#analysis
#forecast
#ensemble -> ensemble analysis
TYPE =json_params["TYPE"]

if TYPE=="forecast":
    TYPE="FC"
if TYPE=="analysis":
    TYPE="AN"
if TYPE=="ensemble":
    TYPE="EN"



#start time
START_TIME=json_params["START_TIME"]
#end time
END_TIME=json_params["END_TIME"]
#output frequency
STEP=json_params["STEP"]

FORECAST_START_TIME = json_params["FORECAST_START_TIME"]





if TYPE=="FC" and END_TIME=="00" and START_TIME=="00":
	END_TIME="24"
	print("END_TIME=START_TIME=00 , as type = FC setting END_TIME to 24")

if TYPE=="AN" and END_TIME=="00" and START_TIME=="00":
	END_TIME="18"
	print("END_TIME=START_TIME=00 , as type = AN setting END_TIME to 18")

HOURS_ECMWF=START_TIME+"/to/"+END_TIME+"/by/"+STEP


#Domain 
#keep empty to get EUROPE domain
LAT_MIN=json_params["LAT_MIN"]
LAT_MAX=json_params["LAT_MAX"]
LON_MIN=json_params["LON_MIN"]
LON_MAX=json_params["LON_MAX"]
AREA_ECMWF=json_params["AREA_ECMWF"]

#GRID
#enables to get the correct grid for MNH
GRID=json_params["GRID"]
GRID_ECMWF=GRID+"/"+GRID





#get surface parameters or not
#Default True
GET_SURFACE=True

if AREA_ECMWF=="" and LAT_MAX != "":
    AREA_ECMWF=LAT_MAX+"/"+LON_MIN+"/"+LAT_MIN+"/"+LON_MAX

if AREA_ECMWF=='GLOBAL' and LAT_MAX=="":
    AREA_ECMWF=""


if LAT_MIN=="" or LAT_MAX=="" or LAT_MIN=='' or LAT_MAX=='' :
    print("Warning ! No domain specified, EUROPE set as default")
    AREA_ECMWF="EUROPE"

server = ECMWFService("mars", url="https://api.ecmwf.int/v1",key=KEY,email=MAIL)


if TYPE=="EN":
    number_of_members=26
    MEMBERS="/".join(np.array(range(0,number_of_members)).astype("str"))

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

if TYPE=="FC":
    PRESSURE="/134"
    PARAM_ATM="130/131/132/133" 
    PARAM_SURF="129/172/139/141/170/183/236/39/40/41/42"+ PRESSURE
else:
    PRESSURE="/152"
    PARAM_ATM="130/131/132/133" + PRESSURE
    PARAM_SURF="129/172/139/141/170/183/236/39/40/41/42"




