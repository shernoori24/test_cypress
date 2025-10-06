# config.py
# Ce fichier contient toute la configuration de l'application
# Il définit les paramètres pour différents environnements (développement, production, tests)

import os           # Pour accéder aux variables d'environnement du système
import sys          # Pour détecter si l'application est "gelée" par PyInstaller
from pathlib import Path  # Pour gérer les chemins de fichiers de manière moderne

class Config:
    """
    Classe de configuration de base pour l'application
    
    Cette classe contient tous les paramètres par défaut de l'application.
    Les autres classes héritent de celle-ci et peuvent surcharger certains paramètres.
    """
    
    # === SÉCURITÉ ===
    # Clé secrète pour Flask (utilisée pour les sessions, cookies, etc.)
    # Essaie d'abord de la récupérer des variables d'environnement, sinon utilise une valeur par défaut
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chatbot-ia-secret-key-2025'
    
    # === CHEMINS DE L'APPLICATION ===
    # Gestion des chemins pour PyInstaller (exécutable)
    if getattr(sys, 'frozen', False):
        # Si l'application est "gelée" par PyInstaller
        BASE_DIR = Path(sys.executable).parent
    else:
        # Si l'application est lancée normalement
        BASE_DIR = Path(__file__).parent
    
    DATA_FOLDER = BASE_DIR / 'data'           # Dossier contenant les fichiers Excel (données)
    UPLOAD_FOLDER = BASE_DIR / 'uploads'      # Dossier pour les fichiers uploadés par les utilisateurs
    STATIC_FOLDER = BASE_DIR / 'app' / 'static'  # Dossier contenant les fichiers statiques (CSS, JS, images)
    
    # === CONFIGURATION DES FICHIERS DE DONNÉES ===
    INSCRIPTION_FILE = DATA_FOLDER / 'inscription.xlsx'    # Chemin complet du fichier Excel contenant les inscriptions
    PRESENCE_FILE = DATA_FOLDER / 'presence.xlsx'          # Chemin complet du fichier Excel contenant les présences
    NETWORK_CONFIG_FILE = DATA_FOLDER / 'network_config.json'  # Fichier de configuration réseau
    
    # === CONFIGURATION DES LOGS ===
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')  # Niveau de log (DEBUG, INFO, WARNING, ERROR)
    LOG_FILE = BASE_DIR / 'logs' / 'app.log'         # Fichier où écrire les logs
    
    # === CONFIGURATION DE L'INTERFACE ===
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', '20'))  # Nombre d'éléments par page dans les listes

class DevelopmentConfig(Config):
    """
    Configuration spécifique à l'environnement de développement
    
    Cette configuration est utilisée quand vous développez l'application
    sur votre machine locale. Elle active le mode debug qui permet :
    - Le rechargement automatique du code
    - L'affichage détaillé des erreurs
    - Des fonctionnalités de débogage
    """
    DEBUG = True    # Active le mode debug de Flask
    TESTING = False # Désactive le mode test

class ProductionConfig(Config):
    """
    Configuration spécifique à l'environnement de production
    
    Cette configuration est utilisée quand l'application est déployée
    pour les utilisateurs finaux. Elle désactive le debug pour la sécurité.
    """
    DEBUG = False   # Désactive le mode debug pour la sécurité
    TESTING = False # Désactive le mode test
    
    def __init__(self):
        """
        Initialisation spéciale pour la production
        
        En production, on s'assure que la clé secrète provient obligatoirement
        des variables d'environnement pour des raisons de sécurité
        """
        super().__init__()  # Appeler le constructeur de la classe parent
        
        # En production, on s'assure que la clé secrète est définie dans l'environnement
        secret_key = os.environ.get('SECRET_KEY')
        if secret_key:
            self.SECRET_KEY = secret_key

class TestingConfig(Config):
    """
    Configuration spécifique aux tests automatisés
    
    Cette configuration est utilisée pendant les tests unitaires.
    Elle utilise des données de test séparées pour ne pas affecter
    les vraies données de l'application.
    """
    DEBUG = True     # Active le debug pour voir les erreurs pendant les tests
    TESTING = True   # Active le mode test de Flask
    DATA_FOLDER = Config.BASE_DIR / 'test_data'  # Utilise un dossier de données séparé pour les tests
# === DICTIONNAIRE DE CONFIGURATION ===
# Dictionnaire pour faciliter l'accès aux différentes configurations selon l'environnement
config = {
    'development': DevelopmentConfig,  # Configuration de développement
    'production': ProductionConfig,    # Configuration de production  
    'testing': TestingConfig,          # Configuration de test
    'default': DevelopmentConfig       # Configuration par défaut si aucune n'est spécifiée
}

def get_config():
    """
    Fonction qui retourne la classe de configuration appropriée selon l'environnement
    
    Cette fonction lit la variable d'environnement FLASK_ENV pour déterminer
    quel environnement utiliser (development, production, testing).
    
    Returns:
        Class: La classe de configuration correspondant à l'environnement
        
    Example:
        config_class = get_config()  # Récupère la classe
        config_instance = config_class()  # Crée une instance de la configuration
    """
    # Si l'application est packagée (PyInstaller), privilégier la configuration production
    if getattr(sys, 'frozen', False):
        return ProductionConfig

    # Lire la variable d'environnement FLASK_ENV (par défaut: 'default')
    env = os.environ.get('FLASK_ENV', 'default')

    # Retourner la classe de configuration correspondante
    # Si l'environnement n'est pas trouvé, utiliser la configuration par défaut
    return config.get(env, config['default'])
