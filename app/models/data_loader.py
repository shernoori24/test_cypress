# app/models/data_loader.py
# Ce fichier contient la classe DataLoader qui gère le chargement et la manipulation
# des données Excel (inscriptions et présences) de manière centralisée

import pandas as pd          # Bibliothèque pour manipuler les données (DataFrames)
from pathlib import Path     # Pour gérer les chemins de fichiers de manière moderne
import logging              # Pour enregistrer les messages de débogage et d'erreur
from datetime import datetime  # Pour gérer les dates et heures
from app.utils.error_handler import DataProcessingError  # Exception personnalisée pour les erreurs de données

# Configuration du logger pour ce module (affichage des messages de debug/info/erreur)
logger = logging.getLogger(__name__)

class DataLoader:
    """
    Classe responsable du chargement et de la gestion centralisée des données Excel
    
    Cette classe utilise le pattern "Lazy Loading" (chargement paresseux) :
    - Les données ne sont chargées qu'au moment où on en a besoin
    - Les données sont mises en cache pour éviter de recharger inutilement
    - Vérifie automatiquement si les fichiers ont été modifiés
    """
    
    def __init__(self, config):
        """
        Initialise le DataLoader avec la configuration de l'application
        
        Args:
            config: Objet de configuration contenant les chemins des fichiers
        """
        self.config = config                    # Configuration de l'application
        self.data_folder = config.DATA_FOLDER   # Dossier contenant les fichiers de données
        self._inscription_df = None             # Cache pour les données d'inscription (DataFrame pandas)
        self._presence_df = None                # Cache pour les données de présence (DataFrame pandas)
        self._last_load_time = {}              # Dictionnaire stockant l'heure du dernier chargement pour chaque type de données
        
    @property
    def inscriptions(self):
        """
        Propriété qui retourne le DataFrame des inscriptions (avec chargement automatique)
        
        Cette propriété utilise le "lazy loading" : elle ne charge les données 
        que si nécessaire et les garde en cache pour les prochains accès
        
        Returns:
            pandas.DataFrame: DataFrame contenant toutes les données d'inscription
        """
        # Vérifier s'il faut recharger les données (première fois ou fichier modifié)
        if self._should_reload('inscriptions'):
            self._load_inscriptions()  # Charger les données depuis le fichier Excel
        return self._inscription_df
    
    @property
    def presences(self):
        """
        Propriété qui retourne le DataFrame des présences (avec chargement automatique)
        
        Cette propriété utilise le "lazy loading" : elle ne charge les données 
        que si nécessaire et les garde en cache pour les prochains accès
        
        Returns:
            pandas.DataFrame: DataFrame contenant toutes les données de présence
        """
        # Vérifier s'il faut recharger les données (première fois ou fichier modifié)
        if self._should_reload('presences'):
            self._load_presences()  # Charger les données depuis le fichier Excel
        return self._presence_df
    
    def _should_reload(self, data_type):
        """
        Méthode privée qui détermine s'il faut recharger les données
        
        Cette méthode vérifie deux conditions :
        1. Si les données n'ont jamais été chargées (cache vide)
        2. Si le fichier source a été modifié depuis le dernier chargement
        
        Args:
            data_type (str): Type de données ('inscriptions' ou 'presences')
            
        Returns:
            bool: True s'il faut recharger, False sinon
        """
        if data_type == 'inscriptions':
            # Vérifier si le cache est vide OU si le fichier a changé
            return self._inscription_df is None or self._file_has_changed('inscriptions')
        elif data_type == 'presences':
            # Vérifier si le cache est vide OU si le fichier a changé
            return self._presence_df is None or self._file_has_changed('presences')
        return True  # Par défaut, recharger si type inconnu
    
    def _file_has_changed(self, data_type):
        """
        Méthode privée qui vérifie si un fichier a été modifié depuis le dernier chargement
        
        Cette méthode compare l'heure de modification du fichier avec l'heure 
        du dernier chargement stockée en cache
        
        Args:
            data_type (str): Type de données ('inscriptions' ou 'presences')
            
        Returns:
            bool: True si le fichier a été modifié, False sinon
        """
        try:
            # Obtenir le chemin du fichier selon le type de données
            file_path = self._get_file_path(data_type)
            
            # Si le fichier n'existe pas, pas besoin de recharger
            if not file_path.exists():
                return False
                
            # Obtenir l'heure de dernière modification du fichier (timestamp Unix)
            last_modified = file_path.stat().st_mtime
            
            # Obtenir l'heure du dernier chargement (0 si jamais chargé)
            last_load = self._last_load_time.get(data_type, 0)
            
            # Retourner True si le fichier est plus récent que le dernier chargement
            return last_modified > last_load
        except Exception as e:
            # En cas d'erreur, logger un avertissement et forcer le rechargement par sécurité
            logger.warning(f"Impossible de vérifier la modification du fichier {data_type}: {e}")
            return True
    
    def _get_file_path(self, data_type):
        """
        Méthode privée qui retourne le chemin complet du fichier selon le type de données
        
        Args:
            data_type (str): Type de données ('inscriptions' ou 'presences')
            
        Returns:
            Path: Objet Path représentant le chemin du fichier
            
        Raises:
            ValueError: Si le type de données n'est pas reconnu
        """
        if data_type == 'inscriptions':
            # Retourner directement le chemin configuré (qui contient déjà le dossier data)
            return self.config.INSCRIPTION_FILE
        elif data_type == 'presences':
            # Retourner directement le chemin configuré (qui contient déjà le dossier data)
            return self.config.PRESENCE_FILE
        else:
            # Lever une exception si le type n'est pas reconnu
            raise ValueError(f"Type de données inconnu: {data_type}")
    
    def _load_inscriptions(self):
        """
        Méthode privée qui charge les données d'inscription depuis le fichier Excel
        
        Cette méthode :
        1. Vérifie que le fichier existe
        2. Lit le fichier Excel avec pandas
        3. Normalise les colonnes (noms standardisés)
        4. Met à jour le cache et l'heure de chargement
        5. Gère les erreurs et logs les informations
        """
        # Obtenir le chemin du fichier d'inscription
        file_path = self._get_file_path('inscriptions')
        
        try:
            if file_path.exists():
                
                # Lire le fichier Excel et créer un DataFrame pandas
                self._inscription_df = pd.read_excel(file_path)
                
                # Enregistrer l'heure de chargement pour la vérification de modification
                self._last_load_time['inscriptions'] = datetime.now().timestamp()
            else:
                # Le fichier n'existe pas, créer un DataFrame vide
                logger.warning(f"Fichier d'inscription non trouvé: {file_path}")
                self._inscription_df = pd.DataFrame()
        except Exception as e:
            # En cas d'erreur, logger l'erreur et lever une exception personnalisée
            logger.error(f"Erreur lors du chargement des inscriptions: {e}")
            raise DataProcessingError(f"Impossible de charger les inscriptions: {e}")
    
    def _load_presences(self):
        """
        Méthode privée qui charge les données de présence depuis le fichier Excel
        
        Cette méthode suit le même pattern que _load_inscriptions :
        1. Vérifie l'existence du fichier
        2. Lit le fichier Excel
        3. Normalise les colonnes
        4. Met à jour le cache
        5. Gère les erreurs
        """
        # Obtenir le chemin du fichier de présence
        file_path = self._get_file_path('presences')
        
        try:
            if file_path.exists():
                
                # Lire le fichier Excel et créer un DataFrame pandas
                self._presence_df = pd.read_excel(file_path)
                
                # Enregistrer l'heure de chargement
                self._last_load_time['presences'] = datetime.now().timestamp()
            else:
                # Le fichier n'existe pas, créer un DataFrame vide
                logger.warning(f"Fichier de présence non trouvé: {file_path}")
                self._presence_df = pd.DataFrame()
        except Exception as e:
            # En cas d'erreur, logger l'erreur et lever une exception personnalisée
            logger.error(f"Erreur lors du chargement des présences: {e}")
            raise DataProcessingError(f"Impossible de charger les présences: {e}")
    
    def reload_all(self):
        """
        Méthode publique qui force le rechargement complet de toutes les données
        
        Cette méthode :
        1. Vide tous les caches (DataFrames remis à None)
        2. Efface les heures de chargement
        3. Force le rechargement en accédant aux propriétés inscriptions et presences
        
        Utile quand on sait que les fichiers ont été modifiés externally
        """
        logger.info("Rechargement forcé de toutes les données")
        
        # Vider tous les caches
        self._inscription_df = None
        self._presence_df = None
        self._last_load_time.clear()  # Vider le dictionnaire des heures de chargement
        
        # Déclencher le rechargement en accédant aux propriétés
        # L'accès aux propriétés va automatiquement charger les données
        _ = self.inscriptions  # Le _ indique qu'on n'utilise pas la valeur retournée
        _ = self.presences
    
    def get_file_info(self):
        """
        Méthode publique qui retourne des informations détaillées sur les fichiers de données
        
        Cette méthode est utile pour :
        - Diagnostiquer les problèmes de fichiers
        - Afficher l'état des données dans l'interface
        - Déboguer les problèmes de chargement
        
        Returns:
            dict: Dictionnaire contenant les informations pour chaque type de fichier
                  Format: {
                      'inscriptions': {
                          'exists': bool,
                          'size': int (en octets),
                          'last_modified': datetime,
                          'path': str
                      },
                      'presences': { ... }
                  }
        """
        info = {}
        
        # Itérer sur chaque type de données
        for data_type in ['inscriptions', 'presences']:
            # Obtenir le chemin du fichier
            file_path = self._get_file_path(data_type)
            
            if file_path.exists():
                # Le fichier existe, récupérer ses métadonnées
                stat = file_path.stat()  # Obtenir les statistiques du fichier
                info[data_type] = {
                    'exists': True,
                    'size': stat.st_size,  # Taille en octets
                    'last_modified': datetime.fromtimestamp(stat.st_mtime),  # Date de modification
                    'path': str(file_path)  # Chemin complet du fichier
                }
            else:
                # Le fichier n'existe pas
                info[data_type] = {
                    'exists': False, 
                    'path': str(file_path)
                }
        
        return info
    
    def reload_inscriptions(self):
        """
        Méthode publique pour forcer le rechargement des inscriptions
        
        Cette méthode est utile après avoir modifié le fichier Excel directement
        pour s'assurer que le cache est mis à jour.
        """
        self._inscription_df = None  # Vider le cache
        self._load_inscriptions()    # Recharger depuis le fichier
        logger.info("Rechargement forcé des inscriptions effectué")
    
    def reload_presences(self):
        """
        Méthode publique pour forcer le rechargement des présences
        """
        self._presence_df = None     # Vider le cache
        self._load_presences()       # Recharger depuis le fichier
        logger.info("Rechargement forcé des présences effectué")