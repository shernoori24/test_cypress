
# app/controllers/home.py
# Contrôleur principal pour la page d'accueil
# Ce fichier définit les routes (URLs) pour la page d'accueil de l'application

import logging                                        # Pour les logs
from flask import Blueprint, render_template         # Composants Flask pour les routes et templates

# === CRÉATION DU BLUEPRINT ===
# Un Blueprint permet d'organiser l'application en modules
# Toutes les routes définies dans ce fichier seront préfixées par 'home'
home_bp = Blueprint('home', __name__)

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)

@home_bp.route('/')
def home():
    
    
    return render_template('home.html')

