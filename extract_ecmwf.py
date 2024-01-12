#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:20:28 2022

@author: wurtzj
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
from   define_parameters import *
from   ecmwfapi import ECMWFService
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

date                  = sys.argv[1]
output_file           = "EC."+type_data+"."+date+".grib" 
output_file_sfc       = "EC."+type_data+".SFC."+date+".grib"
output_file_sea_state = "EC."+type_data+".SEA_STATE."+date+".grib"
print(date)

server          = ECMWFService("mars", url="https://api.ecmwf.int/v1")

# -------------------------------------------------------
#   Forecast
# -------------------------------------------------------
if type_data=="FC":
    server.execute(
        {
        "class"    : "od",
        "date"     : date,
        "expver"   : "1",
        "levtype"  : "ml",
        "levelist" : "1/to/137",
        "param"    : param_atm,
        "step"     : hours,
        "stream"   : "oper",
        "type"     : "fc", 
        "area"     : area,
        "grid"     : grid,
        "time"     : forecast_start_time,
        },
        target_directory+output_file)
    
    if get_surface :
        server.execute(
            {
            "class"   : "od",
            "date"    : date,
            "expver"  : "1",
            "levtype" : "sfc",
            "param"   : param_surf,
            "step"    : hours,
            "stream"  : "oper",
            "type"    : "fc", 
            "area"    : area,
            "grid"    : grid,
            "time"    : forecast_start_time,
            },
            target_directory+output_file_sfc)

    if get_sea_state :
        server.execute(
            {
            "class"   : "od",
            "date"    : date,
            "expver"  : "1",
            "levtype" : "sfc",
            "param"   : param_sea_state,
            "step"    : hours,
            "stream"  : "wave",
            "type"    : "fc",
            "area"    : area,
            "grid"    : grid,
            "time"    : forecast_start_time,
            },
            target_directory+output_file_sea_state)


# -------------------------------------------------------
#   Analysis
# -------------------------------------------------------
if type_data=="AN":
    server.execute(
        {
        "class"    : "od",
        "date"     : date,
        "expver"   : "1",
        "levtype"  : "ml",
        "levelist" : "1/to/137",
        "param"    : param_atm,
        "time"     : hours,
        "stream"   : "oper",
        "type"     : "an", 
        "area"     : area,
        "grid"     : grid,
        },
        target_directory+output_file)
    
    if get_surface :
        server.execute(
            {
            "class"   : "od",
            "date"    : date,
            "expver"  : "1",
            "levtype" : "sfc",
            "param"   : param_surf,
            "time"    : hours,
            "stream"  : "oper",
            "type"    : "an", 
            "area"    : area,
            "grid"    : grid,
            },
            target_directory+output_file_sfc)

    if get_sea_state :
        server.execute(
            {
            "class"   : "od",
            "date"    : date,
            "expver"  : "1",
            "levtype" : "sfc",
            "param"   : param_sea_state,
            "time"    : hours,
            "stream"  : "wave",
            "type"    : "an",
            "area"    : area,
            "grid"    : grid,
            },
            target_directory+output_file_sea_state)

# -------------------------------------------------------
#   Ensemble analysis
# -------------------------------------------------------
if type_data=="EN":
        hours=""
        if int(end_time) > 18 :
            print("Warning : please specify an other date for hours > 18 hours")

        for hour in range(int(start_time),int(end_time)+1,int(step)):
            if hour%6==0 and hour<=18 : #one output every 6 hours
                if hours=="":
                    hours=str_num(hour)+":00:00"
                else:
                    hours=hours+"/"+str_num(hour)+":00:00"
        
        server.execute(
            {  
            "class"    : "od",
            "date"     : date,
            "expver"   : "1",
            "levtype"  : "ml",
            "levelist" : "1/to/137",
            "number"   : members,
            "param"    : param_atm,
            "time"     : hours,            
            "type"     : "an",
            "stream"   : "elda",
            "area"     : area,
            },
            target_directory+output_file)
          
        if get_surface :
            server.execute(
            {
            "class"   : "od",
            "date"    : date,
            "expver"  : "1",
            "levtype" : "sfc",
            "number"  : members,
            "param"   : param_surf,
            "time"    : hours,            
            "stream"  : "elda",
            "type"    : "an", 
            "area"    : area,
            },
            target_directory+output_file_sfc)

# -------------------------------------------------------
#   Separate grib files per dates (one per datetime)
#   + concatenate sfc and sea_state grib files
#   with atmospheric one if necesseary
# -------------------------------------------------------
    
if get_surface:
    if get_sea_state:
      os.system("grib_copy " + target_directory+output_file_sfc +" " + target_directory+output_file_sea_state + " " + target_directory+output_file + " " + target_directory+output_file+"_tempo")
      os.system("rename " + "grib_tempo" + " grib" + target_directory+output_file+"_tempo") #etape may be unusefull but to be sure file is not corrupted
    else:
      os.system("grib_copy " + target_directory+output_file_sfc +" " + target_directory+output_file + " " + target_directory+output_file+"_tempo")
      os.system("rename " + "grib_tempo" + " grib" + target_directory+output_file+"_tempo") #etape may be unusefull but to be sure file is not corrupted

if type_data=="EN":
    os.system('grib_copy '+ target_directory+output_file+"_tempo" +" " + target_directory+ "EC."+type_data+".[dataDate].[dataTime]h.member.[perturbationNumber].offset.[offsetToEndOf4DvarWindow].grib")
if type_data=="AN":
    os.system('grib_copy '+ target_directory+output_file+"_tempo" +" " + target_directory+ "EC."+type_data+".[dataDate].[dataTime].grib")
    if get_surface:
        os.system("grib_copy " + target_directory+output_file_sfc +" " + target_directory+ "EC."+type_data+".SFC."+"[dataDate].[dataTime].grib")
    if get_sea_state:
        os.system("grib_copy " + target_directory+output_file_sfc +" " + target_directory+ "EC."+type_data+".SEA_STATE."+"[dataDate].[dataTime].grib")

if type_data=="FC":
    os.system('grib_copy '+ target_directory+output_file+"_tempo" +" " + target_directory+ "EC."+type_data+".[dataDate].[stepRange].grib")
    if get_surface:
        os.system("grib_copy " + target_directory+output_file_sfc +" " + target_directory+ "EC."+type_data+".SFC."+"[dataDate].[stepRange].grib")

# -------------------------------------------------------
#   Remove temporary files if desired
# -------------------------------------------------------

if remove_tmp_files:
    os.system('rm '+target_directory+output_file)
    os.system('rm '+target_directory+'*_tempo')
    if get_surface:
        os.system('rm '+target_directory+'*.SFC.*')
    if get_sea_state:
        os.system('rm '+target_directory+'*.SEA_STATE.*')
