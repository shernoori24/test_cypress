# app/utils/error_handler.py
# Ce fichier contient les outils pour gérer les erreurs de manière centralisée
# Il fournit un décorateur pour capturer les erreurs et un système de logging

from functools import wraps        # Pour créer des décorateurs qui préservent les métadonnées des fonctions
import logging                     # Pour enregistrer les erreurs dans des fichiers de log
import pandas as pd               # Pour gérer les erreurs spécifiques à pandas
from flask import jsonify, flash, redirect, url_for  # Outils Flask pour les réponses HTTP
from pathlib import Path          # Pour gérer les chemins de fichiers

def setup_logging(config):
    """
    Configure le système de logging (journalisation) de l'application
    
    Cette fonction initialise le système de logs qui permet d'enregistrer
    toutes les informations importantes de l'application (erreurs, debug, info)
    dans un fichier et sur la console.
    
    Args:
        config: Objet de configuration contenant les paramètres de logging
        
    Returns:
        logging.Logger: Instance du logger configuré
    """
    # === CRÉATION DU DOSSIER DE LOGS ===
    # Créer le dossier 'logs' s'il n'existe pas
    log_dir = config.BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)  # exist_ok=True évite l'erreur si le dossier existe déjà
    
    # === CONFIGURATION DU SYSTÈME DE LOGGING ===
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),  # Niveau de log (DEBUG, INFO, WARNING, ERROR)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format des messages
        handlers=[
            # Handler pour écrire dans un fichier (avec encodage UTF-8 pour les caractères français)
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            # Handler pour afficher dans la console/terminal
            logging.StreamHandler()
        ]
    )

    # Réduire le bruit des logs HTTP de werkzeug (GET/200/404 récurrents)
    try:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    except Exception:
        pass
    
    # Retourner une instance de logger pour ce module
    return logging.getLogger(__name__)

def handle_errors(error_type="general", redirect_to="home.home"):
    """
    Décorateur pour gérer les erreurs de manière uniforme dans toute l'application
    
    Ce décorateur s'applique aux fonctions/méthodes pour capturer automatiquement
    les erreurs et les traiter de façon cohérente selon le type d'interface.
    
    Args:
        error_type (str): Type d'erreur à gérer :
            - "api" : Erreurs pour les APIs (retourne JSON)
            - "form" : Erreurs pour les formulaires web (affiche flash message)
            - "general" : Erreurs générales (redirection avec message)
        redirect_to (str): Route Flask vers laquelle rediriger en cas d'erreur
        
    Returns:
        function: Décorateur à appliquer aux fonctions
        
    Usage:
        @handle_errors(error_type="form", redirect_to="home.index")
        def ma_fonction():
            # Code qui peut lever des erreurs
            pass
    """
    def decorator(f):
        """
        Décorateur interne qui wrapp la fonction originale
        """
        @wraps(f)  # Préserve les métadonnées de la fonction originale (nom, docstring, etc.)
        def decorated_function(*args, **kwargs):
            # Créer un logger spécifique au module de la fonction
            logger = logging.getLogger(f.__module__)
            
            try:
                # === EXÉCUTION DE LA FONCTION ORIGINALE ===
                return f(*args, **kwargs)
                
            # === GESTION DES ERREURS SPÉCIFIQUES ===
            except FileNotFoundError as e:
                # Erreur : fichier non trouvé (souvent fichiers Excel manquants)
                error_msg = f"Fichier non trouvé: {str(e)}"
                logger.error(f"FileNotFoundError dans {f.__name__}: {e}")
                return _handle_error_response(error_msg, error_type, redirect_to)
                
            except pd.errors.EmptyDataError as e:
                # Erreur pandas : fichier de données vide ou corrompu
                error_msg = "Le fichier de données est vide ou corrompu"
                logger.error(f"EmptyDataError dans {f.__name__}: {e}")
                return _handle_error_response(error_msg, error_type, redirect_to)
                
            except Exception as e:
                # Toute autre erreur inattendue
                error_msg = f"Une erreur inattendue s'est produite: {str(e)}"
                # exc_info=True inclut la stack trace complète dans les logs
                logger.error(f"Erreur dans {f.__name__}: {e}", exc_info=True)
                return _handle_error_response(error_msg, error_type, redirect_to)
                
        # Retourner la fonction décorée
        return decorated_function
    # Retourner le décorateur
    return decorator

def _handle_error_response(error_msg, error_type, redirect_to):
    """
    Fonction privée qui gère la réponse d'erreur selon le type d'interface
    
    Cette fonction centralise la logique de réponse aux erreurs selon le contexte :
    - API : Retourne une réponse JSON avec le statut HTTP 500
    - Form/General : Affiche un message flash et redirige vers une page
    
    Args:
        error_msg (str): Message d'erreur à afficher/retourner
        error_type (str): Type d'erreur ("api", "form", "general")
        redirect_to (str): Route Flask pour la redirection
        
    Returns:
        Response: Réponse Flask appropriée selon le type
    """
    if error_type == "api":
        # Pour les APIs : retourner une réponse JSON avec status 500
        return jsonify({'success': False, 'error': error_msg}), 500
    elif error_type == "form":
        # Pour les formulaires : afficher un message flash et rediriger
        flash(error_msg, 'danger')  # 'danger' = message d'erreur rouge en Bootstrap
        return redirect(url_for(redirect_to))
    else:
        # Pour les cas généraux : même traitement que les formulaires
        flash(error_msg, 'danger')
        return redirect(url_for(redirect_to))

# === CLASSES D'EXCEPTIONS PERSONNALISÉES ===
# Ces classes permettent de créer des erreurs spécifiques à l'application

class AppError(Exception):
    """
    Exception personnalisée de base pour l'application
    
    Cette classe sert de base pour toutes les exceptions spécifiques
    à l'application. Elle permet d'ajouter des informations comme
    un code d'erreur.
    """
    def __init__(self, message, error_code=None):
        """
        Initialise l'exception personnalisée
        
        Args:
            message (str): Message d'erreur descriptif
            error_code (str, optional): Code d'erreur pour le debugging
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)  # Appeler le constructeur de la classe parent Exception

class DataValidationError(AppError):
    """
    Exception pour les erreurs de validation de données
    
    Utilisée quand les données ne respectent pas le format attendu
    (ex: colonnes manquantes, types incorrects, valeurs invalides)
    """
    pass

class DataProcessingError(AppError):
    """
    Exception pour les erreurs de traitement de données
    
    Utilisée quand une erreur survient pendant le traitement des données
    (ex: calculs, transformations, sauvegarde)
    """
    pass
