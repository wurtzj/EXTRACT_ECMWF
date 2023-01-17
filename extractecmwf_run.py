#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:20:28 2022

@author: wurtzj
"""

#Extraction on a single date

import sys
from define_parameters_extractecmwf import *


DATE = sys.argv[1]

OUTPUT_FILE="ecmwf."+TYPE+"."+DATE+".grib" 
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
    if GET_SURFACE:
        os.system("grib_copy " + TARGET_DIRECTORY+OUTPUT_FILE_SFC +" " + TARGET_DIRECTORY+ "ecmwf."+TYPE+".SFC."+"[dataDate].[dataTime].grib")
if TYPE=="forecast":
    os.system('grib_copy '+ TARGET_DIRECTORY+OUTPUT_FILE+"_tempo" +" " + TARGET_DIRECTORY+ "ecmwf."+TYPE+".[dataDate].[stepRange].grib")




