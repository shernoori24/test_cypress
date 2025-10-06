# app/services/base_service.py
# Ce fichier contient la classe de base pour tous les services de l'application
# Il implémente le pattern "Template Method" et fournit des fonctionnalités communes

import logging                          # Pour enregistrer les messages de debug/info/erreur
from abc import ABC                        # Pour créer une classe abstraite (Abstract Base Class)
from app.utils.error_handler import DataProcessingError  # Exception personnalisée pour les erreurs de données

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)

class BaseService(ABC):
    """
    Classe de base abstraite pour tous les services de l'application
    
    Cette classe implémente le pattern "Template Method" qui définit
    une structure commune pour tous les services :
    - Accès centralisé au data loader
    - Méthodes communes pour la manipulation des données
    - Logging standardisé des opérations
    - Validation des DataFrames
    
    Pattern utilisé : Template Method + Service Layer
    - Template Method : Structure commune pour tous les services
    - Service Layer : Couche de logique métier entre contrôleurs et modèles
    """
    
    def __init__(self):
        """
        Initialise le service de base
        
        Vérifie que le data loader global est disponible et l'assigne
        au service. Lève une exception si le data loader n'est pas initialisé.
        
        Raises:
            DataProcessingError: Si le data loader n'est pas disponible
        """
        # Importer le data loader global au moment de l'utilisation
        # (évite les problèmes d'importation circulaire et d'initialisation)
        from app import data_loader
        self.data_loader = data_loader
        
        # Vérification de sécurité : s'assurer que le data loader est disponible
        if not self.data_loader:
            raise DataProcessingError("Data loader non initialisé")
    
    @property
    def inscriptions_df(self):
        """
        Propriété qui donne accès au DataFrame des inscriptions
        
        Cette propriété utilise le système de lazy loading du DataLoader :
        - Les données ne sont chargées qu'au premier accès
        - Le cache est automatiquement géré par le DataLoader
        - Les modifications de fichiers sont détectées automatiquement
        
        Returns:
            pandas.DataFrame: DataFrame contenant toutes les inscriptions
        """
        return self.data_loader.inscriptions
    
    @property
    def presences_df(self):
        """
        Propriété qui donne accès au DataFrame des présences
        
        Cette propriété utilise le système de lazy loading du DataLoader :
        - Les données ne sont chargées qu'au premier accès
        - Le cache est automatiquement géré par le DataLoader
        - Les modifications de fichiers sont détectées automatiquement
        
        Returns:
            pandas.DataFrame: DataFrame contenant toutes les présences
        """
        return self.data_loader.presences
    
    def reload_data(self):
        """
        Force le rechargement complet de toutes les données
        
        Cette méthode est utile quand on veut s'assurer d'avoir
        les données les plus récentes, par exemple après des
        modifications externes aux fichiers Excel.
        
        Elle vide tous les caches et force un nouveau chargement
        depuis les fichiers sources.
        """
        self.data_loader.reload_all()
    
    def _log_operation(self, operation, details=""):
        """
        Méthode protégée pour logger les opérations du service
        
        Cette méthode standardise le format des logs pour tous les services :
        - Inclut automatiquement le nom de la classe du service
        - Format : "NomService - Opération: Détails"
        - Niveau INFO pour traçabilité des opérations
        
        Args:
            operation (str): Nom de l'opération effectuée
            details (str): Détails supplémentaires sur l'opération
        """
        # Récupérer le nom de la classe du service (ex: InscriptionService)
        service_name = self.__class__.__name__
        
        # Logger avec un format standardisé pour tous les services
        logger.info(f"{service_name} - {operation}: {details}")
    
    def _validate_dataframe(self, df, required_columns):
        """
        Méthode protégée pour valider qu'un DataFrame contient les colonnes requises
        
        Cette méthode effectue deux validations :
        1. Vérifier que le DataFrame n'est pas vide
        2. Vérifier que toutes les colonnes requises sont présentes
        
        Args:
            df (pandas.DataFrame): DataFrame à valider
            required_columns (list): Liste des colonnes obligatoires
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
                  - is_valid: True si valide, False sinon
                  - error_message: Message d'erreur si invalid, "" si valide
        """
        # Vérifier si le DataFrame est vide
        if df.empty:
            return False, "DataFrame vide"
        
        # Vérifier que toutes les colonnes requises sont présentes
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            # Créer un message d'erreur détaillant les colonnes manquantes
            return False, f"Colonnes manquantes: {', '.join(missing_columns)}"
        
        # Si tout est OK, retourner succès
        return True, ""
