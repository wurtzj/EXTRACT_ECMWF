#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 09:55:09 2022

@author: wurtzj
"""

from ecmwfapi import ECMWFService
import os
import numpy as np


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

#Directory where files will be available
#It has to end with a /
TARGET_DIRECTORY="/home/wurtzj/" ##"/cnrm/ville/NO_SAVE/wurtzj/ECMWF/POUR_DIDIER/"

#List of dates to extract
#Format AAAAMMDD


#LISTE_DATES=generate_list_date(2022,7,27,2022,8,15)
#LISTE_DATES=["20190724","20190725","20190726","20190727","20190728","20190729","20190801"]
#LISTE_DATES=["20190729","20190801"] #didier
#LISTE_DATES=["20200105","20200106","20200208","20200209", "20200307", "20200308" ] #Marie
LISTE_DATES=["20191230"] #Marie


#Using ECMWF_DATES enables to collect all dates
#It may not be efficient to extract MESO-NH data
#ECMWF_DATES="/".join(LISTE_DATES) 


#start time
START_TIME="00"
#end time
END_TIME="18"
#output frequency
STEP="6"

FORECAST_START_TIME = "00"

#possibility to remove last step in case of multiple date ?
#END_TIME=str(int(END_TIME)-int(STEP)) 

HOURS_ECMWF=START_TIME+"/to/"+END_TIME+"/by/"+STEP


#Domain #didier
# =============================================================================
# LAT_MIN="40"
# LAT_MAX="52"
# LON_MIN="3"
# LON_MAX="20"
# 
# =============================================================================
#Domain #marie
LAT_MIN="43"
LAT_MAX="46"
LON_MIN="-2"
LON_MAX="1"


# =============================================================================
# LAT_MIN=""
# LAT_MAX=""
# LON_MIN=""
# LON_MAX=""
# 
# =============================================================================

#GRID -> may be not usefull as grid is automatically set to archived one
# may be usefull is simulation have gross resolution
GRID=".1"
GRID_ECMWF=GRID+"/"+GRID


#type of data
#analysis
#forecast
#ensemble -> ensemble analysis
TYPE = "analysis" 

#get surface parameters or not
#Default True
GET_SURFACE=True #True


AREA_ECMWF=LAT_MAX+"/"+LON_MIN+"/"+LAT_MIN+"/"+LON_MAX

if LAT_MIN=="" or LAT_MAX=="" or LAT_MIN=='' or LAT_MAX=='' :
    print("Warning ! No domain specified, EUROPE set as default")
    AREA_ECMWF="EUROPE"

server = ECMWFService("mars", url="https://api.ecmwf.int/v1",key="38b0ba68e57fd8d5c7858006bc3dafde",email="jean.wurtz@meteo.fr")


if TYPE=="elda":
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

if TYPE=="forecast":
    PRESSURE="/134"
    PARAM_ATM="130/131/132/133" 
    PARAM_SURF="129/172/139/141/170/183/236/39/40/41/42"+ PRESSURE
else:
    PRESSURE="/152"
    PARAM_ATM="130/131/132/133" + PRESSURE
    PARAM_SURF="129/172/139/141/170/183/236/39/40/41/42"



for DATE in LISTE_DATES :
    OUTPUT_FILE="ecmwf."+TYPE+"."+DATE+".grib" #"target_3d_ricard_"+DATE+".grib"
    OUTPUT_FILE_SFC="ecmwf."+TYPE+".SFC."+DATE+".grib"
    print(DATE)

    if TYPE=="forecast":
        server.execute(
            {
            "class": "od",
            "date": DATE,
            "expver": "1",
            "levtype": "ml",
            "levelist" : "1/to/137",
            "param": PARAM_ATM,
            "step": HOURS_ECMWF,
            "stream": "oper",
            "type": "fc", 
            "area": AREA_ECMWF,
            "grid":GRID_ECMWF,
            "time":FORECAST_START_TIME,

            },
            TARGET_DIRECTORY+OUTPUT_FILE)
        
        if GET_SURFACE :
  
            server.execute(
                {
                "class": "od",
                "date": DATE,
                "expver": "1",
                "levtype": "sfc",
                "param": PARAM_SURF,
                "step": HOURS_ECMWF,
                "stream": "oper",
                "type": "fc", 
                "area": AREA_ECMWF,
                "grid":GRID_ECMWF,
                "time":FORECAST_START_TIME,


                },
                TARGET_DIRECTORY+OUTPUT_FILE_SFC)
        
        #option                 "grid":GRID_ECMWF, necessaire pour avoir une grille reguliere

    if TYPE=="analysis":
        server.execute(
            {
            "class": "od",
            "date": DATE,
            "expver": "1",
            "levtype": "ml",
            "levelist" : "1/to/137",
            "param": PARAM_ATM,
            "time": HOURS_ECMWF,
            "stream": "oper",
            "type": "an", 
            "area": AREA_ECMWF,
            "grid":GRID_ECMWF,

            },
            TARGET_DIRECTORY+OUTPUT_FILE)
        
        if GET_SURFACE :
            server.execute(
            {
            "class": "od",
            "date": DATE,
            "expver": "1",
            "levtype": "sfc",
            "param": PARAM_SURF,
            "time" : HOURS_ECMWF,
            "stream": "oper",
            "type": "an", 
            "area": AREA_ECMWF,
            "grid":GRID_ECMWF,

            },
                TARGET_DIRECTORY+OUTPUT_FILE_SFC)
            
        
    if TYPE=="ensemble": #ensemble analysis
            HOURS_ECMWF=""
            if int(END_TIME) > 18 :
                print("Warning : please specify an other date for hours > 18 hours")

            for HOUR in range(int(START_TIME),int(END_TIME)+1,int(STEP)):
                if HOUR%6==0 and HOUR<=18 : #one output every 6 hours
                    if HOURS_ECMWF=="":
                        HOURS_ECMWF=str_num(HOUR)+":00:00"
                    else:
                        HOURS_ECMWF=HOURS_ECMWF+"/"+str_num(HOUR)+":00:00"
            
            
            server.execute(
            {  
            "class":"od",
            "date":DATE,
            "expver": "1",
            "levtype":"ml",
            "levelist" : "1/to/137",
            "number":MEMBERS, #numero du membre
            "param": PARAM_ATM,
            "time":HOURS_ECMWF,            
            "type":"an",
            "stream":"elda",
            "area": AREA_ECMWF,

                    },
            TARGET_DIRECTORY+OUTPUT_FILE)
              
            if GET_SURFACE :
                server.execute(
                {
                "class": "od",
                "date": DATE,
                "expver": "1",
                "levtype": "sfc",
                "number":MEMBERS, #numero du membre
                "param": PARAM_SURF,
                "time":HOURS_ECMWF,            
                "stream": "elda",
                "type": "an", 
                "area": AREA_ECMWF,
                },
            TARGET_DIRECTORY+OUTPUT_FILE_SFC)

        
    if GET_SURFACE:
       os.system("grib_copy " + TARGET_DIRECTORY+OUTPUT_FILE_SFC +" " + TARGET_DIRECTORY+OUTPUT_FILE + " " + TARGET_DIRECTORY+OUTPUT_FILE+"_tempo")
       os.system("rename.ul " + "grib_tempo" + " grib" + TARGET_DIRECTORY+OUTPUT_FILE+"_tempo") #etape may be unusefull but to be sure file is not corrupted


    if TYPE=="ensemble":
        os.system('grib_copy '+ TARGET_DIRECTORY+OUTPUT_FILE+"_tempo" +" " + TARGET_DIRECTORY+ "ecmwf."+TYPE+".[dataDate].[dataTime]h.member.[perturbationNumber].offset.[offsetToEndOf4DvarWindow].grib")
    if TYPE=="analysis":
        os.system('grib_copy '+ TARGET_DIRECTORY+OUTPUT_FILE+"_tempo" +" " + TARGET_DIRECTORY+ "ecmwf."+TYPE+".[dataDate].[dataTime].grib")
        os.system("grib_copy " + TARGET_DIRECTORY+OUTPUT_FILE_SFC +" " + TARGET_DIRECTORY+ "ecmwf."+TYPE+".SFC."+"[dataDate].[dataTime].grib")
    if TYPE=="forecast":
        os.system('grib_copy '+ TARGET_DIRECTORY+OUTPUT_FILE+"_tempo" +" " + TARGET_DIRECTORY+ "ecmwf."+TYPE+".[dataDate].[stepRange].grib")





