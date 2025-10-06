# app/__init__.py
# Initialise l'application Flask et configure tous ses composants (sans SocketIO)

from flask import Flask
from config import get_config
from app.utils.error_handler import setup_logging
from app.models.data_loader import DataLoader

# === VARIABLES GLOBALES ===
# Instance globale du data loader pour qu'elle soit accessible partout dans l'application
# Elle sera initialisée dans la fonction create_app()
data_loader = None

def create_app(config_name=None):
    """
    Factory function qui crée et configure l'application Flask
    
    Cette fonction utilise le pattern "Application Factory" qui permet :
    - De créer plusieurs instances de l'app avec des configurations différentes
    - De faciliter les tests avec des configurations spécifiques
    - D'éviter les imports circulaires
    
    Args:
        config_name (str, optional): Nom de la configuration à utiliser
        
    Returns:
        Flask: Instance configurée de l'application Flask
    """
    
    # === CRÉATION DE L'APPLICATION FLASK ===
    app = Flask(__name__)

    # === CONFIGURATION ===
    # Récupérer la classe de configuration appropriée (dev/prod/test)
    config_class = get_config()
    # Appliquer la configuration à l'application Flask
    app.config.from_object(config_class)

    # (Plus de SocketIO: application Flask uniquement)
    
    # === CONFIGURATION DES LOGS ===
    # Configurer le système de logging (fichiers de log, niveaux, formats)
    setup_logging(config_class)
    
    # === INITIALISATION DU DATA LOADER ===
    # Créer l'instance globale du data loader qui va gérer tous les fichiers Excel
    global data_loader
    data_loader = DataLoader(config_class)
    
    # === INITIALISATION DU DATA SERVICE ===
    # Créer une instance unique du service de données
    from app.services.data_service import DataService
    data_service = DataService()
    
    # Rendre le data loader et data service accessibles depuis l'objet app Flask
    # Cela permet d'y accéder avec current_app.data_loader dans les vues
    app.data_loader = data_loader
    app.data_service = data_service
    # === FILTRES PERSONNALISÉS JINJA2 ===
    # Ajout du filtre strftime pour formater les dates dans les templates
    from datetime import datetime
    def strftime_filter(value, format='%d/%m/%Y'):
        """Filtre personnalisé pour formater les dates dans les templates Jinja2"""
        if isinstance(value, str):
            # Si la valeur est une chaîne, on tente de la convertir en datetime
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value
        if isinstance(value, datetime):
            return value.strftime(format)
        return value
    
    # Enregistrer le filtre personnalisé dans l'application Flask
    app.jinja_env.filters['strftime'] = strftime_filter

    # === ENREGISTREMENT DES BLUEPRINTS (MODULES) ===
    # Les blueprints permettent d'organiser l'application en modules
    # Chaque blueprint gère une partie spécifique de l'application
    
    from .controllers.home import home_bp           # Module page d'accueil
    from .controllers.inscription import inscription_bp  # Module gestion des inscriptions
    from .controllers.planning import planning_bp   # Module planning
    from .controllers.rapport_apprenant import report_bp       # Module génération de rapports
    from .controllers.prediction_controller import prediction_bp   # NOUVEAU: Module prédictions IA

    # Enregistrer tous les blueprints dans l'application Flask
    app.register_blueprint(home_bp)          # Routes pour la page d'accueil
    app.register_blueprint(inscription_bp)   # Routes pour la gestion des inscriptions
    app.register_blueprint(planning_bp)      # Routes pour le planning
    app.register_blueprint(report_bp)        # Routes pour les rapports
    app.register_blueprint(prediction_bp)    # NOUVEAU: Routes pour prédictions et analyses


    # Blueprint pour servir les photos profils apprenants depuis data/photos_profils_apprenants
    from app.controllers.photos_profils_apprenants import photos_bp
    app.register_blueprint(photos_bp)

    # Retourner l'application Flask configurée et prête à l'emploi
    return app