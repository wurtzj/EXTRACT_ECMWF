#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'extraction ECMWF pour une date donnée.
Adapté pour être cohérent avec la version fusionnée de define_parameters_extractecmwf.py.
Auteurs : wurtzj, DINUM (adaptation)
Date : 18/09/2026
"""

import os
import sys
import subprocess
from ecmwfapi import ECMWFService

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import des paramètres depuis define_parameters_extractecmwf
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

try:
    from define_parameters_extractecmwf import (
        type_data as TYPE,  # Renommé pour correspondre à la version fusionnée
        list_of_dates as LISTE_DATES,
        target_directory as TARGET_DIRECTORY,
        vertical_grid as VERTICAL_GRID,
        param_atm as PARAM_ATM,
        param_surf as PARAM_SURF,
        param_sea_state as PARAM_SEA_STATE,
        hours as HOURS_ECMWF,
        area as AREA_ECMWF,
        grid_ecmwf as GRID_ECMWF,
        get_surface as GET_SURFACE,
        get_sea_state as GET_SEA_STATE,
        forecast_start_time as FORECAST_START_TIME,
        start_time as START_TIME,
        end_time as END_TIME,
        step as STEP,
        members as MEMBERS,
        remove_tmp_files,
        str_num,
        server
    )
except ImportError as e:
    print(f"Erreur : Impossible d'importer les paramètres depuis 'define_parameters_extractecmwf' : {e}")
    print("Assurez-vous que le script define_parameters_extractecmwf.py a été exécuté correctement.")
    sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Vérification des arguments
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if len(sys.argv) < 2:
    print("Usage: python3 extractecmwf_run.py <DATE>")
    sys.exit(1)

date = sys.argv[1]
print(f"Extraction des données pour la date : {date}")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configuration des fichiers de sortie
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

output_file = f"EC.{TYPE}.{date}.grib"
output_file_sfc = f"EC.{TYPE}.SFC.{date}.grib"
output_file_sea_state = f"EC.{TYPE}.SEA_STATE.{date}.grib"
output_file_tempo = f"{output_file}_tempo"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fonction pour exécuter une requête ECMWF
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def execute_ecmwf_request(request_dict, output_path):
    """Exécute une requête ECMWF et gère les erreurs."""
    try:
        server.execute(request_dict, output_path)
        print(f"Requête ECMWF exécutée avec succès : {output_path}")
    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête pour {output_path} : {e}")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Gestion des heures pour les ensembles (EN)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if TYPE == "EN":
    HOURS_ECMWF = ""
    if int(END_TIME) > 18:
        print("Avertissement : Les heures > 18 ne sont pas supportées pour les ensembles. Utilisez une autre date.")

    for hour in range(int(START_TIME), int(END_TIME) + 1, int(STEP)):
        if hour % 6 == 0 and hour <= 18:  # Une sortie toutes les 6 heures
            if HOURS_ECMWF == "":
                HOURS_ECMWF = f"{str_num(hour)}:00:00"
            else:
                HOURS_ECMWF = f"{HOURS_ECMWF}/{str_num(hour)}:00:00"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Exécution des requêtes selon le type de données
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# -------------------------------------------------------
#   Forecast (FC)
# -------------------------------------------------------
if TYPE == "FC":
    request_atm = {
        "class": "od",
        "date": date,
        "expver": "1",
        "levtype": "ml",
        "levelist": VERTICAL_GRID,
        "param": PARAM_ATM,
        "step": HOURS_ECMWF,
        "stream": "oper",
        "type": "fc",
        "area": AREA_ECMWF,
        "grid": GRID_ECMWF,
        "time": FORECAST_START_TIME,
    }
    execute_ecmwf_request(request_atm, TARGET_DIRECTORY + output_file)

    if GET_SURFACE:
        request_surf = {
            "class": "od",
            "date": date,
            "expver": "1",
            "levtype": "sfc",
            "param": PARAM_SURF,
            "step": HOURS_ECMWF,
            "stream": "oper",
            "type": "fc",
            "area": AREA_ECMWF,
            "grid": GRID_ECMWF,
            "time": FORECAST_START_TIME,
        }
        execute_ecmwf_request(request_surf, TARGET_DIRECTORY + output_file_sfc)

# -------------------------------------------------------
#   Analysis (AN)
# -------------------------------------------------------
elif TYPE == "AN":
    request_atm = {
        "class": "od",
        "date": date,
        "expver": "1",
        "levtype": "ml",
        "levelist": VERTICAL_GRID,
        "param": PARAM_ATM,
        "time": HOURS_ECMWF,
        "stream": "oper",
        "type": "an",
        "area": AREA_ECMWF,
        "grid": GRID_ECMWF,
    }
    execute_ecmwf_request(request_atm, TARGET_DIRECTORY + output_file)

    if GET_SURFACE:
        request_surf = {
            "class": "od",
            "date": date,
            "expver": "1",
            "levtype": "sfc",
            "param": PARAM_SURF,
            "time": HOURS_ECMWF,
            "stream": "oper",
            "type": "an",
            "area": AREA_ECMWF,
            "grid": GRID_ECMWF,
        }
        execute_ecmwf_request(request_surf, TARGET_DIRECTORY + output_file_sfc)

# -------------------------------------------------------
#   Ensemble Analysis (EN)
# -------------------------------------------------------
elif TYPE == "EN":
    request_atm = {
        "class": "od",
        "date": date,
        "expver": "1",
        "levtype": "ml",
        "levelist": VERTICAL_GRID,
        "number": MEMBERS,
        "param": PARAM_ATM,
        "time": HOURS_ECMWF,
        "type": "an",
        "stream": "elda",
        "area": AREA_ECMWF,
    }
    execute_ecmwf_request(request_atm, TARGET_DIRECTORY + output_file)

    if GET_SURFACE:
        request_surf = {
            "class": "od",
            "date": date,
            "expver": "1",
            "levtype": "sfc",
            "number": MEMBERS,
            "param": PARAM_SURF,
            "time": HOURS_ECMWF,
            "stream": "elda",
            "type": "an",
            "area": AREA_ECMWF,
        }
        execute_ecmwf_request(request_surf, TARGET_DIRECTORY + output_file_sfc)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fusion des fichiers GRIB
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def run_grib_copy(*input_files, output_file):
    """Exécute la commande grib_copy pour fusionner des fichiers."""
    input_files_str = " ".join(input_files)
    command = f"grib_copy {input_files_str} {TARGET_DIRECTORY}{output_file}"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Fusion des fichiers GRIB : {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la fusion des fichiers GRIB : {e}")

# Fusion des fichiers selon les paramètres
if GET_SURFACE:
    run_grib_copy(
        f"{TARGET_DIRECTORY}{output_file_sfc}",
        f"{TARGET_DIRECTORY}{output_file}",
        output_file=output_file_tempo
    )
    # Renommage du fichier temporaire (optionnel)
    subprocess.run(f"rename grib_tempo grib {TARGET_DIRECTORY}{output_file_tempo}", shell=True)

# Renommage final selon le type de données
if TYPE == "EN":
    subprocess.run(
        f"grib_copy {TARGET_DIRECTORY}{output_file_tempo} {TARGET_DIRECTORY}EC.{TYPE}.[dataDate].[dataTime]h.member.[perturbationNumber].offset.[offsetToEndOf4DvarWindow].grib",
        shell=True
    )
elif TYPE == "AN":
    subprocess.run(
        f"grib_copy {TARGET_DIRECTORY}{output_file_tempo} {TARGET_DIRECTORY}EC.{TYPE}.[dataDate].[dataTime].grib",
        shell=True
    )
    if GET_SURFACE:
        subprocess.run(
            f"grib_copy {TARGET_DIRECTORY}{output_file_sfc} {TARGET_DIRECTORY}EC.{TYPE}.SFC.[dataDate].[dataTime].grib",
            shell=True
        )
elif TYPE == "FC":
    subprocess.run(
        f"grib_copy {TARGET_DIRECTORY}{output_file_tempo} {TARGET_DIRECTORY}EC.{TYPE}.[dataDate].[stepRange].grib",
        shell=True
    )
    if GET_SURFACE:
        subprocess.run(
            f"grib_copy {TARGET_DIRECTORY}{output_file_sfc} {TARGET_DIRECTORY}EC.{TYPE}.SFC.[dataDate].[stepRange].grib",
            shell=True
        )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Nettoyage des fichiers temporaires
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if remove_tmp_files:
    try:
        os.remove(f"{TARGET_DIRECTORY}{output_file}")
        os.remove(f"{TARGET_DIRECTORY}{output_file_tempo}")
        if GET_SURFACE:
            os.remove(f"{TARGET_DIRECTORY}{output_file_sfc}")
        print("Fichiers temporaires supprimés.")
    except OSError as e:
        print(f"Erreur lors de la suppression des fichiers temporaires : {e}")

print(f"Extraction terminée pour la date : {date}")
