#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script fusionné pour l'extraction de données ECMWF.
Basé sur les versions "ville" et "define_parameters_extractecmwf.py".
Auteurs : wurtzj, DINUM (adaptation)
Date : 18/09/2026
"""

import os
import numpy as np
import json
import pandas as pd
import datetime
from ecmwfapi import ECMWFService

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fonctions utilitaires
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def str_num(i, num_chiffre=2):
    """Formate un entier avec des zéros devant pour atteindre `num_chiffre` chiffres."""
    if i < 10:
        return (num_chiffre - 1) * "0" + str(i)
    elif i < 100:
        return (num_chiffre - 2) * "0" + str(i)
    else:
        return str(i)

def generate_date(start_date, end_date):
    """Génère une liste de dates au format YYYYMMDD entre `start_date` et `end_date`."""
    if start_date == end_date:
        return [start_date]
    list_of_dates = pd.date_range(start_date, end_date, freq='d')
    return list(list_of_dates.strftime("%Y%m%d"))

def generate_list_date(YEAR_START, MONTH_START, DAY_START, YEAR_END, MONTH_END, DAY_END):
    """Alternative pour générer des dates à partir d'années, mois, jours."""
    sdate = datetime.date(YEAR_START, MONTH_START, DAY_START)
    edate = datetime.date(YEAR_END, MONTH_END, DAY_END) + datetime.timedelta(days=1)
    return pd.date_range(sdate, edate - datetime.timedelta(days=1)).strftime('%Y%m%d').tolist()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Chargement des paramètres depuis le fichier JSON
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

try:
    with open('PARAMS_EXTRACT.json', 'r') as json_file:
        json_params = json.load(json_file)
except FileNotFoundError:
    print("Erreur : Le fichier 'PARAMS_EXTRACT.json' est introuvable.")
    quit()
except json.JSONDecodeError:
    print("Erreur : Le fichier JSON est mal formé.")
    quit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configuration du répertoire de sortie
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

target_directory = json_params.get("target_directory", "") or json_params.get("TARGET_DIRECTORY", "")
target_directory = "/cnrm/ville/DATA/FORCING_ECMWF/"+target_directory
if not target_directory:
    print("Veuillez préciser le chemin de sortie dans 'target_directory' ou 'TARGET_DIRECTORY' du fichier JSON.")
    quit()

if target_directory[-1] != "/":
    target_directory += "/"

# Création automatique du répertoire
try:
    os.makedirs(target_directory, exist_ok=True)
    print(f"Répertoire de sortie : {target_directory} (créé ou existant)")
except OSError as e:
    print(f"Erreur lors de la création du répertoire : {e}")
    quit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Gestion des dates
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

list_of_dates = json_params.get("list_of_dates", []) or json_params.get("LISTE_DATES", [])
start_date = json_params.get("start_date", "") or json_params.get("date_debut", "")
end_date = json_params.get("end_date", "") or json_params.get("date_fin", "")

# Priorité à la liste de dates si elle est fournie
if not list_of_dates or list_of_dates == [""]:
    if start_date and end_date:
        list_of_dates = generate_date(start_date, end_date)
    else:
        print("Aucune date spécifiée. Utilisation des dates par défaut ou arrêt.")
        quit()

print(f"Dates à extraire : {list_of_dates}")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configuration des heures et du type de données
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

start_time = json_params.get("start_time", "") or json_params.get("START_TIME", "")
end_time = json_params.get("end_time", "") or json_params.get("END_TIME", "")
step = json_params.get("step", "") or json_params.get("STEP", "")
forecast_start_time = json_params.get("forecast_start_time", "") or json_params.get("FORECAST_START_TIME", "")

# Ajustement automatique pour les cas particuliers
type_data = json_params.get("type_data", "") or json_params.get("TYPE", "")
if type_data == "forecast":
    type_data = "FC"
elif type_data == "analysis":
    type_data = "AN"
elif type_data == "ensemble":
    type_data = "EN"

# Correction des heures pour FC et AN
if type_data == "FC" and end_time == "00" and start_time == "00":
    end_time = "24"
    print("Type = FC et heures = 00/00 : `end_time` ajusté à 24.")
elif type_data == "AN" and end_time == "00" and start_time == "00":
    end_time = "18"
    print("Type = AN et heures = 00/00 : `end_time` ajusté à 18.")

hours = f"{start_time}/to/{end_time}/by/{step}"
print(f"Heures à extraire : {hours}")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configuration du domaine et de la grille
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

lat_min = json_params.get("lat_min", "") or json_params.get("LAT_MIN", "")
lat_max = json_params.get("lat_max", "") or json_params.get("LAT_MAX", "")
lon_min = json_params.get("lon_min", "") or json_params.get("LON_MIN", "")
lon_max = json_params.get("lon_max", "") or json_params.get("LON_MAX", "")
area = json_params.get("area", "") or json_params.get("AREA_ECMWF", "")

# Gestion du domaine par défaut
if not area and lat_min and lat_max and lon_min and lon_max:
    area = f"{lat_max}/{lon_min}/{lat_min}/{lon_max}"
elif area == "GLOBAL":
    lat_min, lat_max, lon_min, lon_max = "-90", "90", "-180", "180"
    area = f"{lat_max}/{lon_min}/{lat_min}/{lon_max}"
elif not area and (not lat_min or not lat_max or not lon_min or not lon_max):
    print("Avertissement : Aucun domaine spécifié. Utilisation de 'EUROPE' par défaut.")
    area = "EUROPE"

# Configuration de la grille
grid = json_params.get("grid", "") or json_params.get("GRID", "")
if grid:
    grid_ecmwf = f"{grid}/{grid}"
else:
    grid_ecmwf = "N48"  # Valeur par défaut pour GLOBAL

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configuration des paramètres à extraire
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

get_surface = json_params.get("get_surface", True)
get_sea_state = json_params.get("get_sea_state", False)

# Paramètres atmosphériques et de surface
if type_data == "FC":
    pressure = "/134"
    param_atm = "130/131/132/133"
    param_surf = "129/172/139/141/170/183/236/39/40/41/42" + pressure
else:
    pressure = "/152"
    param_atm = "130/131/132/133" + pressure
    param_surf = "129/172/139/141/170/183/236/39/40/41/42"

# Paramètres pour l'état de la mer
param_sea_state = "229/234/237"

# Niveaux verticaux
level_list = json_params.get("level_list", "") or json_params.get("LEVEL_LIST", "")
if not level_list:
    vertical_grid = "1/to/137"
else:
    vertical_grid = level_list

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configuration des membres pour les ensembles
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if type_data == "EN":
    number_of_members = 26
    members = "/".join(np.array(range(number_of_members)).astype("str"))
else:
    number_of_members = 1
    members = "/".join(np.array(range(number_of_members)).astype("str"))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Connexion à l'API ECMWF
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Note : Les identifiants doivent être configurés dans un fichier sécurisé ou via des variables d'environnement.
# Exemple : os.getenv("ECMWF_KEY"), os.getenv("ECMWF_EMAIL")
try:
    server = ECMWFService("mars", 
                          url="https://api.ecmwf.int/v1",
                          key="",
                          email=""
                          )

except Exception as e:
    print(f"Erreur de connexion à l'API ECMWF : {e}")
    quit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Affichage des paramètres finaux
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\n" + "=" * 70)
print("CONFIGURATION FINALE :")
print(f"- Type de données : {type_data}")
print(f"- Dates : {list_of_dates}")
print(f"- Heures : {hours}")
print(f"- Domaine : {area}")
print(f"- Grille : {grid_ecmwf}")
print(f"- Paramètres atmosphériques : {param_atm}")
print(f"- Paramètres de surface : {param_surf}")
if get_sea_state:
    print(f"- Paramètres état de la mer : {param_sea_state}")
print(f"- Niveaux verticaux : {vertical_grid}")
if type_data == "EN":
    print(f"- Membres : {members}")
print("=" * 70)

print("\nPour suivre vos requêtes, connectez-vous à : https://apps.ecmwf.int/webmars/joblist/")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Suppression des fichiers temporaires
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

remove_tmp_files = json_params.get("remove_tmp_files", False)
if remove_tmp_files:
    print("Les fichiers temporaires seront supprimés après extraction.")
