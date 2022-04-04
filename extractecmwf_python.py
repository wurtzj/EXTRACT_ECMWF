#!/usr/bin/env python
from ecmwfapi import ECMWFService
import os

server = ECMWFService("mars", url="https://api.ecmwf.int/v1",key="38b0ba68e57fd8d5c7858006bc3dafde",email="jean.wurtz@meteo.fr")
#Surface fields 
  #152 lnsp : logarithm of surface pressure (analysis only)
  #134 surface pressure
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
  
  #"134/129/172/139/141/170/183/236/39/40/41/42",
  
 #Than 3D fields
 #133 q specific humidity
 #130 temperature
 #131 u wind
 #132 v wind
 
server.execute(
    {
    "class": "od",
    "date": "20140320",
    "expver": "1",
    "levtype": "sfc",
    "param": "134/129/172/139/141/170/183/236/39/40/41/42",
    "step": "6/to/12/by/1",
    "stream": "oper",
    "time": "00",
    "type": "fc", 
    "area": "10/-80/-20/-40",
    "grid":".141/.141",
    },
    "target_sfc.grib")
    
    
server.execute(
    {
    "class": "od",
    "date": "20140320",
    "expver": "1",
    "levtype": "ml",
    "levelist" : "1/to/137",
    "param": "130/131/132/133",
    "step": "6/to/12/by/1",
    "stream": "oper",
    "time": "00",
    "type": "fc", 
    "area": "10/-80/-20/-40",
    "grid":".141/.141",
    },
    "target_3d.grib")


#os.system("grib_copy target_sfc.grib target_3d.grib target_total.grib")
#os.system('grib_copy total_grib.grib "ecmwf.FC-FC.OD.20140320.[stepRange].grib"')
