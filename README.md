# Tool to extract ECMWF data for Meso-NH

This tool enables to get ECMWF files for Meso-NH using python and ECMWF API.

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

More informations about this tool are available in [Meso-NH's documentation](https://mesonh-beta-test-guide.readthedocs.io/en/latest/getting_started/extract_ecmwf_data/extract_ecmwf_data.html).
