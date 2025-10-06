# Utilitaires pour les scripts
"""
Fonctions utilitaires communes pour les scripts du projet.
"""

import os
import json
from datetime import datetime

def get_project_root():
    """Retourne le chemin racine du projet."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json_file(file_path):
    """Charge un fichier JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Fichier non trouvé : {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Erreur de format JSON : {file_path}")
        return None

def save_json_file(data, file_path):
    """Sauvegarde des données dans un fichier JSON."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")
        return False

def log_action(message):
    """Log une action avec timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
