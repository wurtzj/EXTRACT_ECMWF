#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement parallèle pour l'extraction des données ECMWF.
Corrigé pour éviter les erreurs de type "exit status 125".
Auteurs : wurtzj, DINUM (adaptation)
Date : 18/09/2026
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configuration des paramètres
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Nombre maximal de processus parallèles
NB_MAX_PARALLEL = 10

# Temps d'attente entre les lots de processus (en secondes)
TIME_TO_WAIT = 10800  # 3 heures

# Temps d'attente entre le lancement de chaque processus (en secondes)
TIME_BETWEEN_LAUNCHES = 10

# Nom du script d'extraction à exécuter
EXTRACTION_SCRIPT = "extractecmwf_run.py"

# Fichier JSON à supprimer après exécution (optionnel)
JSON_FILE_TO_REMOVE = "" #PARAMS_EXTRACT.json"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Vérification de l'existence du module de paramètres
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

try:
    from define_parameters_extractecmwf import list_of_dates
except ImportError:
    try:
        from define_parameters import list_of_dates
    except ImportError as e:
        print(f"Erreur : Impossible de trouver le module 'define_parameters_extractecmwf' ou 'define_parameters' : {e}")
        sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Vérification de l'existence du script d'extraction
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if not Path(EXTRACTION_SCRIPT).exists():
    print(f"Erreur : Le script '{EXTRACTION_SCRIPT}' est introuvable dans le répertoire courant : {os.getcwd()}")
    sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fonction pour lancer un processus en arrière-plan
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def launch_extraction(date):
    """Lance le script d'extraction pour une date donnée en arrière-plan."""
    command = ["python3", EXTRACTION_SCRIPT, date]

    try:
        # Utilisation de nohup pour éviter que le processus ne soit tué
        # Redirection des sorties vers un fichier log pour éviter les problèmes de terminal
        log_file = f"log_{date}.txt"
        with open(log_file, "w") as log:
            subprocess.Popen(
                command,
                stdout=log,
                stderr=log,
                preexec_fn=os.setsid  # Crée un nouveau groupe de processus
            )
        print(f"Processus lancé pour la date : {date} (log : {log_file})")
    except subprocess.SubprocessError as e:
        print(f"Erreur lors du lancement du processus pour {date} : {e}")
    except Exception as e:
        print(f"Erreur inattendue pour {date} : {e}")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Boucle principale de lancement parallèle
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("Lancement du script de parallélisation...")
count_proc = 0

for date in list_of_dates:
    if count_proc < NB_MAX_PARALLEL:
        launch_extraction(date)
        count_proc += 1
        time.sleep(TIME_BETWEEN_LAUNCHES)  # Attente entre chaque lancement
    else:
        print(f"Avertissement : Nombre maximal de processus ({NB_MAX_PARALLEL}) atteint.")
        print(f"Attente de {TIME_TO_WAIT} secondes avant de relancer de nouveaux processus...")
        time.sleep(TIME_TO_WAIT)
        count_proc = 0
        launch_extraction(date)
        count_proc += 1
        time.sleep(TIME_BETWEEN_LAUNCHES)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Nettoyage (optionnel)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if JSON_FILE_TO_REMOVE and Path(JSON_FILE_TO_REMOVE).exists():
    try:
        os.remove(JSON_FILE_TO_REMOVE)
        print(f"Fichier {JSON_FILE_TO_REMOVE} supprimé.")
    except OSError as e:
        print(f"Erreur lors de la suppression de {JSON_FILE_TO_REMOVE} : {e}")

print("Tous les processus ont été lancés.")
