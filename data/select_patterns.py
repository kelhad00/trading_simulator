import os
import random
import shutil

# Chemins de base
PATTERN_DIR = 'pattern'
DATASET_DIR = 'dataset'

# Crée le dossier dataset s'il n'existe pas
os.makedirs(DATASET_DIR, exist_ok=True)

# Parcourt les sous-dossiers de pattern
for pattern_name in os.listdir(PATTERN_DIR):
    pattern_path = os.path.join(PATTERN_DIR, pattern_name)
    # On ne prend que les dossiers (pas les fichiers .json à la racine)
    if os.path.isdir(pattern_path):
        # Liste tous les fichiers .json du sous-dossier
        files = [f for f in os.listdir(pattern_path) if f.endswith('.json')]
        if not files:
            continue
        # Tire au hasard 100 fichiers (ou moins si pas assez)
        selected = random.sample(files, min(100, len(files)))
        # Crée le dossier de destination
        dest_dir = os.path.join(DATASET_DIR, pattern_name)
        os.makedirs(dest_dir, exist_ok=True)
        # Copie les fichiers sélectionnés
        for fname in selected:
            src = os.path.join(pattern_path, fname)
            dst = os.path.join(dest_dir, fname)
            shutil.copy2(src, dst)
        print(f"{pattern_name}: {len(selected)} fichiers copiés dans {dest_dir}") 