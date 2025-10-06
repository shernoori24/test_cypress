from flask import Blueprint, send_from_directory, abort
import os
import unicodedata
from pathlib import Path
from config import get_config

photos_bp = Blueprint('photos_profils_apprenants', __name__)

# Dossier des photos basé sur la config, commun à dev et déploiement
_config_class = get_config()
DATA_DIR: Path = _config_class.DATA_FOLDER  # <BASE_DIR>/data
PHOTOS_DIR: Path = DATA_DIR / 'photos_profils_apprenants'

def normalize_filename(name: str) -> str:
    # Supprime les accents, met en minuscule, retire espaces/apostrophes
    nfkd = unicodedata.normalize('NFKD', name)
    only_ascii = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return only_ascii.lower().replace(' ', '').replace("'", "")

@photos_bp.route('/photos_profils_apprenants/<path:filename>')
def photos(filename: str):
    # Sécurité : empêcher la remontée de dossier
    if '..' in filename or filename.startswith('/'):
        abort(404)

    photos_dir_str = str(PHOTOS_DIR)

    # 1) Recherche exacte
    file_path = os.path.join(photos_dir_str, filename)
    if os.path.isfile(file_path):
        return send_from_directory(photos_dir_str, filename)

    # 2) Extension alternative .jpg/.jpeg
    base, ext = os.path.splitext(filename)
    alt_file = None
    if ext.lower() == '.jpg':
        alt_file = base + '.jpeg'
    elif ext.lower() == '.jpeg':
        alt_file = base + '.jpg'
    if alt_file:
        alt_path = os.path.join(photos_dir_str, alt_file)
        if os.path.isfile(alt_path):
            return send_from_directory(photos_dir_str, alt_file)

    # 3) Recherche fuzzy (ignorer accents/casse/espaces/apostrophes)
    norm_requested = normalize_filename(filename)
    if os.path.isdir(photos_dir_str):
        for f in os.listdir(photos_dir_str):
            if normalize_filename(f) == norm_requested:
                return send_from_directory(photos_dir_str, f)

    # 4) Fallback: defaut_profil.jpg dans le dossier des photos
    default_photo = 'defaut_profil.jpg'
    default_path = os.path.join(photos_dir_str, default_photo)
    if os.path.isfile(default_path):
        return send_from_directory(photos_dir_str, default_photo)

    # 5) Fallback: defaut_profil.jpg directement dans data/
    data_dir_str = str(DATA_DIR)
    default_path_data = os.path.join(data_dir_str, default_photo)
    if os.path.isfile(default_path_data):
        return send_from_directory(data_dir_str, default_photo)

    # 6) Rien trouvé
    abort(404)
