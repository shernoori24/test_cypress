# app/services/data_service_pr.py
# Service pour orchestrer le traitement des données d'inscription et de présence

import pandas as pd
import logging
from pathlib import Path
from app.models.inscription_model_pr import InscriptionModel
from app.models.presence_model_pr import PresenceModel

logger = logging.getLogger(__name__)

class DataService:
    """
    Service principal pour coordonner le traitement des données
    """
    
    def __init__(self, data_folder_path):
        """
        Initialise le service avec le chemin du dossier de données
        
        Args:
            data_folder_path (str): Chemin vers le dossier de données
        """
        self.data_folder = Path(data_folder_path)
        self.inscription_model = InscriptionModel(data_folder_path)
        self.presence_model = PresenceModel(data_folder_path)
        self.merged_data = None
        
    def load_and_clean_all_data(self):
        """
        Charge et nettoie toutes les données (inscription + présence)
        
        Returns:
            dict: Statut du traitement et statistiques
        """
        logger.info("=== DÉBUT DU TRAITEMENT COMPLET DES DONNÉES ===")
        
        results = {
            'status': 'success',
            'inscription': {},
            'presence': {},
            'merge': {}
        }
        
        try:
            # === ÉTAPE 1: INSCRIPTION ===
            logger.info("ÉTAPE 1/4: Chargement des inscriptions")
            self.inscription_model.load_data()
            
            logger.info("ÉTAPE 2/4: Nettoyage des inscriptions")
            self.inscription_model.clean_missing_values()
            self.inscription_model.format_columns()
            self.inscription_model.normalize_data()
            
            results['inscription'] = self.inscription_model.get_summary_stats()
            
            # === ÉTAPE 2: PRÉSENCE ===
            logger.info("ÉTAPE 3/4: Chargement des présences")
            self.presence_model.load_data()
            
            logger.info("ÉTAPE 4/4: Nettoyage des présences")
            self.presence_model.clean_missing_values()
            self.presence_model.format_columns()
            self.presence_model.normalize_data()
            
            results['presence'] = self.presence_model.get_summary_stats()
            
            # === ÉTAPE 3: FUSION DES DONNÉES ===
            logger.info("ÉTAPE BONUS: Fusion des données")
            self._merge_datasets()
            results['merge'] = self._get_merge_stats()
            
            logger.info("=== TRAITEMENT COMPLET TERMINÉ AVEC SUCCÈS ===")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement des données: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def _merge_datasets(self):
        """
        Fusionne les données d'inscription et de présence sur la clé commune
        """
        logger.info("=== FUSION DES DATASETS ===")
        
        inscription_df = self.inscription_model.get_processed_data()
        presence_df = self.presence_model.get_processed_data()
        
        if inscription_df is None or presence_df is None:
            raise ValueError("Les données doivent être chargées avant la fusion")
        
        # Vérifier les clés de liaison
        inscription_key = 'N°'
        presence_key = 'Numéro Apprenant'
        
        if inscription_key not in inscription_df.columns:
            raise ValueError(f"Clé de liaison '{inscription_key}' manquante dans les inscriptions")
        if presence_key not in presence_df.columns:
            raise ValueError(f"Clé de liaison '{presence_key}' manquante dans les présences")
        
        logger.info(f"Fusion sur: {inscription_key} (inscription) ↔ {presence_key} (présence)")
        
        # Calculer d'abord les statistiques de présence par apprenant
        attendance_stats = self.presence_model.get_attendance_by_student()
        
        # Renommer la clé pour la fusion
        attendance_stats = attendance_stats.rename(columns={'Numéro Apprenant': inscription_key})
        
        # Fusionner avec les données d'inscription
        self.merged_data = pd.merge(
            inscription_df,
            attendance_stats,
            on=inscription_key,
            how='left'  # Garder tous les inscrits, même sans présence
        )
        
        logger.info(f"Fusion réussie: {len(self.merged_data)} lignes dans le dataset fusionné")
        
    def _get_merge_stats(self):
        """
        Calcule les statistiques sur les données fusionnées
        
        Returns:
            dict: Statistiques de fusion
        """
        if self.merged_data is None:
            return {}
        
        # Calculer le taux de correspondance
        total_inscrits = len(self.merged_data)
        inscrits_avec_presence = self.merged_data['Date du Jour_count'].notna().sum()
        
        stats = {
            'total_lignes_fusionnees': total_inscrits,
            'inscrits_avec_presence': int(inscrits_avec_presence),
            'inscrits_sans_presence': int(total_inscrits - inscrits_avec_presence),
            'taux_correspondance': round((inscrits_avec_presence / total_inscrits) * 100, 2),
            'colonnes_fusionnees': list(self.merged_data.columns)
        }
        
        return stats
    
    def get_merged_data(self):
        """
        Retourne les données fusionnées
        
        Returns:
            pd.DataFrame: Dataset fusionné inscription + présence
        """
        return self.merged_data
    
    def get_inscription_data(self):
        """
        Retourne les données d'inscription traitées
        
        Returns:
            pd.DataFrame: Dataset inscription
        """
        return self.inscription_model.get_processed_data()
    
    def get_presence_data(self):
        """
        Retourne les données de présence traitées
        
        Returns:
            pd.DataFrame: Dataset présence
        """
        return self.presence_model.get_processed_data()
    
    def get_complete_summary(self):
        """
        Retourne un résumé complet de tous les datasets
        
        Returns:
            dict: Résumé complet
        """
        summary = {
            'inscription': self.inscription_model.get_summary_stats() if self.inscription_model.df is not None else {},
            'presence': self.presence_model.get_summary_stats() if self.presence_model.df is not None else {},
            'merge': self._get_merge_stats()
        }
        
        return summary
    
    def get_status(self):
        """
        Obtient le statut des données pour l'affichage du dashboard
        
        Returns:
            dict: Statut des données avec compteurs et indicateurs
        """
        try:
            # Charger les données si nécessaire
            if self.merged_data is None:
                self.load_and_clean_all_data()
            
            inscription_df = self.get_inscription_data()
            presence_df = self.get_presence_data()
            
            # Statistiques de base
            status = {
                'total_apprenants': len(inscription_df) if inscription_df is not None else 0,
                'total_presences': len(presence_df) if presence_df is not None else 0,
                'merge_rate': 0.85,  # Placeholder - calculer le vrai taux
                'data_ready': True
            }
            
            # Calculer le vrai taux de correspondance si possible
            if self.merged_data is not None and len(self.merged_data) > 0:
                merge_stats = self._get_merge_stats()
                if 'merge_rate' in merge_stats:
                    status['merge_rate'] = merge_stats['merge_rate']
            
            return status
            
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention du statut: {e}")
            return {
                'total_apprenants': 0,
                'total_presences': 0,
                'merge_rate': 0,
                'data_ready': False,
                'error': str(e)
            }
