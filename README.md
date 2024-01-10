# EXTRACT_ECMWF

This tool enables to get ecmwf grib files for MESO-NH using python and ECMWF API.
Number of requests are limited. You may have to wait some time if number of requests are high.

Parameters have to be defined in json PARAMS_EXTRACT.json

To run script, best use nohup python3 main_extract_ecmwf_python.py

PARAMS_EXTRACT.json file with contains following informations :

{

"TARGET_DIRECTORY":"/cnrm/ville/DATA/FORCING_ECMWF/NO_SAVE/JEAN/",

"START_DATE" : "20170708",
"date_fin" : "20170710",
"LISTE_DATES": ["20220617"],

"START_TIME":"00",
"END_TIME":"18",
"STEP":"06",
"FORECAST_START_TIME":"00",

"LAT_MIN":"",
"LAT_MAX":"",
"LON_MIN":"",
"LON_MAX":"",

"GRID":".1",

"TYPE":"AN" 

}

TARGET_DIRECTORY : is where your data will be written. Please unsure everybody has the write to write in it (so user wurtzj can write in it) or choose /cnrm/ville/DATA/FORCING_ECMWF/ + USER

start_date : start date
end_date   : end date 

Automatically take all dates between these two dates if LISTE_DATES is empty ([])

LISTE_DATES : lists of dates

START_TIME : 1st time extraction
END_TIME : last time extraction
STEP : time step extraction within the day
FORECAST_START_TIME : in case of forecast : time of launch (00 or 12 for instance)

LAT_MIN
LAT_MAX
LON_MIN
LON_MAX

Domain. If empty get Europe domain.

GRID
.1 by default. Could be coarser

TYPE: AN / FC
possibility to get ensemble in the future - not fully finished

---------------------------------------------------------------------------------------------

HOW TO GET YOUR FILES
---------------------------------------------------------------------------------------------

Fill .json file as desired.
Name it as you want : for instance   REQUEST_WURTZJ.json

Put filed file here :

/cnrm/ville/USERS/wurtzj/EXTRACT_ECMWF/REQUESTS/

An output is available in this folder with an "out" suffix showing it works: /cnrm/ville/USERS/wurtzj/EXTRACT_ECMWF/JOB_STATUS/REQUEST_WURTZJ.json_out
