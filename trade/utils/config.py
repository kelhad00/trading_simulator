import os
import shutil
from datetime import datetime
from trade.defaults import defaults as dlt

def save_current_config():
    """
    Sauvegarde la configuration actuelle dans le dossier configs avec un numéro séquentiel
    """
    # Chemin vers le dossier configs
    configs_path = os.path.join(dlt.data_path, "configs")
    
    # Créer le dossier configs s'il n'existe pas
    if not os.path.exists(configs_path):
        os.makedirs(configs_path)
    
    # Trouver le prochain numéro de configuration
    existing_configs = [d for d in os.listdir(configs_path) if os.path.isdir(os.path.join(configs_path, d))]
    next_num = 1
    if existing_configs:
        next_num = max([int(d) for d in existing_configs if d.isdigit()]) + 1
    
    # Créer le nouveau dossier de configuration
    new_config_path = os.path.join(configs_path, str(next_num))
    os.makedirs(new_config_path)
    
    # Fichiers à sauvegarder
    files_to_save = [
        "generated_data.csv",
        "news_en.csv",
        "news_fr.csv",
        "revenue.csv"
    ]
    
    # Copier les fichiers
    for file in files_to_save:
        src = os.path.join(dlt.data_path, file)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(new_config_path, file))
    
    print(f"Configuration sauvegardée dans {new_config_path}") 