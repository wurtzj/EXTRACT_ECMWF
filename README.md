# Tool to extract ECMWF data for Meso-NH

This tool enables to get ECMWF files for Meso-NH using python and ECMWF API.
Number of requests are limited. You may have to wait some time if number of requests are high.

User's parameters have to be defined in the configuration file called `user_parameters.json`.

To launched your extraction for number of dates lower than 10, use 
```bash
python main_extract_ecmwf.py
```

If number of dates is higher than 10, use
```bash
nohup python main_extract_ecmwf.py
```

To follow your extraction's submission, login to [ECMWF's website](https://apps.ecmwf.int/webmars/joblist/).

More informations about this tool are available in [Meso-NH's website](http://mesonh2.aero.obs-mip.fr/piaj/extract_ecmwf_data/extract_ecmwf_data.html#operational-data-analysis-forecast-or-ensemble).
