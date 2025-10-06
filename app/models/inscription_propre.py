# app/models/inscription_propre.py
# Preprocessing complet pour la prédiction d'inscriptions futures

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from pathlib import Path
from datetime import datetime, timedelta
import warnings
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
import os

# Import optionnel de plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("⚠️ Plotly non disponible - utilisation de matplotlib uniquement")

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    Classe complète pour le preprocessing des données d'inscription
    Optimisée pour la prédiction temporelle d'inscriptions futures
    """
    
    def __init__(self, data_folder_path):
        """
        Initialise le preprocessor
        
        Args:
            data_folder_path (str): Chemin vers le dossier contenant inscription.xlsx
        """
        self.data_folder = Path(data_folder_path)
        self.file_path = self.data_folder / "inscription.xlsx"
        self.df_raw = None
        self.df_clean = None
        self.df_temporal = None
        self.encoders = {}
        self.scalers = {}
        self.eda_results = {}
        
        # Créer le dossier pour les visualisations
        self.viz_folder = Path("app/static/img/ml_viz")
        self.viz_folder.mkdir(parents=True, exist_ok=True)
        
    def load_data(self):
        """
        Charge et analyse les données d'inscription
        
        Returns:
            pd.DataFrame: DataFrame brut chargé
        """
        logger.info("=== CHARGEMENT DONNÉES INSCRIPTION ===")
        
        try:
            self.df_raw = pd.read_excel(self.file_path)
            
            logger.info(f"✅ Dataset chargé: {self.df_raw.shape[0]} lignes, {self.df_raw.shape[1]} colonnes")
            logger.info(f"📊 Colonnes: {list(self.df_raw.columns)}")
            
            # Analyse rapide des valeurs manquantes
            missing_analysis = self._analyze_missing_values()
            logger.info(f"📈 Colonnes avec plus de 50% de valeurs manquantes: {missing_analysis['high_missing']}")
            
            return self.df_raw
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement: {e}")
            raise
    
    def _analyze_missing_values(self):
        """Analyse détaillée des valeurs manquantes"""
        missing_info = self.df_raw.isnull().sum()
        missing_pct = (missing_info / len(self.df_raw)) * 100
        
        missing_df = pd.DataFrame({
            'Colonne': missing_info.index,
            'Manquantes': missing_info.values,
            'Pourcentage': missing_pct.values
        }).sort_values('Pourcentage', ascending=False)
        
        high_missing = missing_df[missing_df['Pourcentage'] > 50]['Colonne'].tolist()
        moderate_missing = missing_df[(missing_df['Pourcentage'] > 20) & (missing_df['Pourcentage'] <= 50)]['Colonne'].tolist()
        
        return {
            'missing_df': missing_df,
            'high_missing': high_missing,
            'moderate_missing': moderate_missing
        }
    
    def handle_missing_values(self):
        """
        Gestion intelligente des valeurs manquantes
        Stratégies adaptées selon le type et l'importance des colonnes
        """
        logger.info("=== GESTION VALEURS MANQUANTES ===")
        
        if self.df_raw is None:
            raise ValueError("Les données doivent être chargées avant le nettoyage")
        
        self.df_clean = self.df_raw.copy()
        
        # Stratégies de nettoyage par importance pour la prédiction temporelle
        cleaning_strategies = {
            # Variables temporelles CRITIQUES - imputation intelligente
            'Date inscription': 'interpolate_date',
            'Première venue': 'interpolate_date',
            'Date de naissance': 'median_date',
            'Arrivée en France': 'median_date',
            
            # Variables démographiques importantes
            'Sexe': 'mode',
            'Age': 'median_numeric',
            'Nationalité': 'mode',
            'Continent': 'most_frequent',
            'Pays de naissance': 'most_frequent',
            
            # Variables géographiques
            'Code postal': 'mode',
            'Ville': 'mode',
            'Prioritaire/Veille': 'mode',
            
            # Variables socio-économiques
            'Situation Familiale': 'mode',
            'Type de logement': 'most_frequent',
            'Revenus': 'median_categorical',
            
            # Variables avec trop de valeurs manquantes - suppression ou imputation simple
            'Age': 'drop_column',  # 99% manquant
            'Continent': 'drop_column',  # 99% manquant
            'ISO': 'drop_column',  # 98% manquant
            'Statut actuel': 'drop_column',  # 99% manquant
            'Structure actuelle': 'drop_column',  # 99% manquant
            'Document': 'most_frequent',  # Garder mais imputer
            'Email': 'fill_missing',  # Marquer comme "Non fourni"
            'Téléphone': 'fill_missing',
            'Commentaires': 'fill_missing'
        }
        
        for column, strategy in cleaning_strategies.items():
            if column in self.df_clean.columns:
                self._apply_cleaning_strategy(column, strategy)
        
        # Rapport final
        initial_missing = self.df_raw.isnull().sum().sum()
        final_missing = self.df_clean.isnull().sum().sum()
        logger.info(f"✅ Valeurs manquantes réduites: {initial_missing} → {final_missing}")
        
        return self.df_clean
    
    def _apply_cleaning_strategy(self, column, strategy):
        """Applique une stratégie de nettoyage spécifique"""
        try:
            if strategy == 'drop_column':
                self.df_clean.drop(columns=[column], inplace=True)
                logger.info(f"🗑️ Colonne supprimée: {column}")
                
            elif strategy == 'mode':
                mode_value = self.df_clean[column].mode().iloc[0] if not self.df_clean[column].mode().empty else 'Inconnu'
                self.df_clean[column].fillna(mode_value, inplace=True)
                
            elif strategy == 'most_frequent':
                most_frequent = self.df_clean[column].value_counts().index[0] if len(self.df_clean[column].value_counts()) > 0 else 'Inconnu'
                self.df_clean[column].fillna(most_frequent, inplace=True)
                
            elif strategy == 'median_numeric':
                # Essayer de convertir en numérique et prendre la médiane
                numeric_values = pd.to_numeric(self.df_clean[column], errors='coerce')
                median_val = numeric_values.median()
                self.df_clean[column].fillna(median_val, inplace=True)
                
            elif strategy == 'interpolate_date':
                # Interpolation temporelle pour les dates
                date_col = pd.to_datetime(self.df_clean[column], errors='coerce')
                date_col = date_col.interpolate(method='time')
                self.df_clean[column] = date_col
                
            elif strategy == 'median_date':
                date_col = pd.to_datetime(self.df_clean[column], errors='coerce')
                median_date = date_col.median()
                self.df_clean[column].fillna(median_date, inplace=True)
                
            elif strategy == 'fill_missing':
                self.df_clean[column].fillna('Non fourni', inplace=True)
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur nettoyage {column} avec {strategy}: {e}")
    
    def create_temporal_features(self):
        """
        Création des features temporelles pour la prédiction
        """
        logger.info("=== CRÉATION FEATURES TEMPORELLES ===")
        
        if self.df_clean is None:
            raise ValueError("Les données doivent être nettoyées avant la création des features")
        
        # Convertir les colonnes de date avec gestion d'erreurs
        date_columns = ['Date inscription', 'Première venue', 'Date de naissance']
        
        for col in date_columns:
            if col in self.df_clean.columns:
                try:
                    self.df_clean[col] = pd.to_datetime(self.df_clean[col], errors='coerce')
                    logger.info(f"✅ Date convertie: {col}")
                except Exception as e:
                    logger.warning(f"⚠️ Erreur conversion date {col}: {e}")
        
        # Utiliser 'Date inscription' comme référence principale
        if 'Date inscription' in self.df_clean.columns:
            # Créer les features temporelles seulement pour les dates valides
            valid_dates = self.df_clean['Date inscription'].notna()
            
            self.df_clean.loc[valid_dates, 'annee_inscription'] = self.df_clean.loc[valid_dates, 'Date inscription'].dt.year
            self.df_clean.loc[valid_dates, 'mois_inscription'] = self.df_clean.loc[valid_dates, 'Date inscription'].dt.month
            self.df_clean.loc[valid_dates, 'trimestre_inscription'] = self.df_clean.loc[valid_dates, 'Date inscription'].dt.quarter
            self.df_clean.loc[valid_dates, 'semaine_inscription'] = self.df_clean.loc[valid_dates, 'Date inscription'].dt.isocalendar().week
            self.df_clean.loc[valid_dates, 'jour_semaine'] = self.df_clean.loc[valid_dates, 'Date inscription'].dt.dayofweek
            
            # Features cycliques pour capturer la saisonnalité (seulement pour les valeurs valides)
            valid_months = self.df_clean['mois_inscription'].notna()
            self.df_clean.loc[valid_months, 'mois_sin'] = np.sin(2 * np.pi * self.df_clean.loc[valid_months, 'mois_inscription'] / 12)
            self.df_clean.loc[valid_months, 'mois_cos'] = np.cos(2 * np.pi * self.df_clean.loc[valid_months, 'mois_inscription'] / 12)
            
            logger.info(f"✅ Features temporelles créées pour {valid_dates.sum()} lignes valides")
        
        # Créer des agrégations temporelles pour la prédiction
        self._create_temporal_aggregations()
        
        logger.info("✅ Features temporelles créées")
        return self.df_clean
    
    def _create_temporal_aggregations(self):
        """Crée les agrégations temporelles nécessaires pour la prédiction"""
        
        # Filtrer les lignes avec des années valides
        df_valid = self.df_clean[self.df_clean['annee_inscription'].notna()].copy()
        
        # Agrégations par année
        self.yearly_counts = df_valid.groupby('annee_inscription').size().reset_index(name='nombre_inscriptions')
        
        # Agrégations par mois (avec gestion des valeurs manquantes)
        monthly_valid = df_valid[df_valid['mois_inscription'].notna()].copy()
        if len(monthly_valid) > 0:
            self.monthly_counts = monthly_valid.groupby(['annee_inscription', 'mois_inscription']).size().reset_index(name='nombre_inscriptions')
            # Créer la date avec jour=1 par défaut
            self.monthly_counts['date'] = pd.to_datetime(
                self.monthly_counts[['annee_inscription', 'mois_inscription']].assign(day=1).rename(
                    columns={'annee_inscription': 'year', 'mois_inscription': 'month'}
                )
            )
        else:
            self.monthly_counts = pd.DataFrame(columns=['annee_inscription', 'mois_inscription', 'nombre_inscriptions', 'date'])
        
        # Agrégations par semaine (avec gestion des valeurs manquantes)
        weekly_valid = df_valid[df_valid['semaine_inscription'].notna()].copy()
        if len(weekly_valid) > 0:
            self.weekly_counts = weekly_valid.groupby(['annee_inscription', 'semaine_inscription']).size().reset_index(name='nombre_inscriptions')
        else:
            self.weekly_counts = pd.DataFrame(columns=['annee_inscription', 'semaine_inscription', 'nombre_inscriptions'])
        
        # Sauvegarder pour l'EDA
        self.eda_results['temporal_aggregations'] = {
            'yearly': self.yearly_counts,
            'monthly': self.monthly_counts,
            'weekly': self.weekly_counts
        }
    
    def encode_categorical_features(self):
        """
        Encodage des variables catégorielles
        """
        logger.info("=== ENCODAGE VARIABLES CATÉGORIELLES ===")
        
        if self.df_clean is None:
            raise ValueError("Les données doivent être nettoyées avant l'encodage")
        
        # Variables à encoder avec One-Hot (nominales)
        onehot_columns = ['Sexe', 'Prioritaire/Veille', 'Situation Familiale', 'Type de logement']
        
        # Variables à encoder avec Label Encoding (ordinales ou avec beaucoup de catégories)
        label_columns = ['Nationalité', 'Pays de naissance', 'Code postal', 'Ville', 'Prescripteur']
        
        # One-Hot Encoding
        for col in onehot_columns:
            if col in self.df_clean.columns:
                dummies = pd.get_dummies(self.df_clean[col], prefix=col, dummy_na=True)
                self.df_clean = pd.concat([self.df_clean, dummies], axis=1)
                self.df_clean.drop(columns=[col], inplace=True)
                logger.info(f"✅ One-Hot: {col} → {len(dummies.columns)} colonnes")
        
        # Label Encoding
        for col in label_columns:
            if col in self.df_clean.columns:
                le = LabelEncoder()
                self.df_clean[f'{col}_encoded'] = le.fit_transform(self.df_clean[col].astype(str))
                self.encoders[col] = le
                logger.info(f"✅ Label: {col} → {col}_encoded")
        
        return self.df_clean
    
    def perform_eda(self):
        """
        Analyse exploratoire des données avec visualisations
        """
        logger.info("=== ANALYSE EXPLORATOIRE DES DONNÉES ===")
        
        if self.df_clean is None:
            raise ValueError("Les données doivent être préparées avant l'EDA")
        
        # 1. Analyse temporelle des inscriptions
        self._plot_temporal_trends()
        
        # 2. Analyse démographique
        self._plot_demographic_analysis()
        
        # 3. Analyse géographique
        self._plot_geographic_analysis()
        
        # 4. Matrice de corrélation
        self._plot_correlation_matrix()
        
        # 5. Statistiques descriptives
        self._generate_descriptive_stats()
        
        logger.info(f"✅ EDA terminée - Visualisations sauvées dans {self.viz_folder}")
        return self.eda_results
    
    def _plot_temporal_trends(self):
        """Graphiques des tendances temporelles"""
        
        # Graphique des inscriptions par année
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Inscriptions par année
        yearly_data = self.eda_results['temporal_aggregations']['yearly']
        axes[0,0].bar(yearly_data['annee_inscription'], yearly_data['nombre_inscriptions'], color='skyblue')
        axes[0,0].set_title('Nombre d\'inscriptions par année')
        axes[0,0].set_xlabel('Année')
        axes[0,0].set_ylabel('Nombre d\'inscriptions')
        
        # Inscriptions par mois (moyenne mobile)
        monthly_data = self.eda_results['temporal_aggregations']['monthly']
        axes[0,1].plot(monthly_data['date'], monthly_data['nombre_inscriptions'], marker='o', color='orange')
        axes[0,1].set_title('Évolution mensuelle des inscriptions')
        axes[0,1].set_xlabel('Date')
        axes[0,1].set_ylabel('Nombre d\'inscriptions')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Distribution par mois de l'année
        month_dist = self.df_clean.groupby('mois_inscription').size()
        axes[1,0].bar(month_dist.index, month_dist.values, color='lightgreen')
        axes[1,0].set_title('Distribution saisonnière (par mois)')
        axes[1,0].set_xlabel('Mois')
        axes[1,0].set_ylabel('Total inscriptions')
        
        # Distribution par jour de la semaine
        dow_dist = self.df_clean.groupby('jour_semaine').size()
        jours = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        axes[1,1].bar(range(7), [dow_dist.get(i, 0) for i in range(7)], color='coral')
        axes[1,1].set_title('Distribution par jour de la semaine')
        axes[1,1].set_xlabel('Jour')
        axes[1,1].set_ylabel('Total inscriptions')
        axes[1,1].set_xticks(range(7))
        axes[1,1].set_xticklabels(jours)
        
        plt.tight_layout()
        plt.savefig(self.viz_folder / 'temporal_trends.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Sauvegarde des insights
        self.eda_results['temporal_insights'] = {
            'total_years': len(yearly_data),
            'peak_year': yearly_data.loc[yearly_data['nombre_inscriptions'].idxmax(), 'annee_inscription'],
            'avg_monthly': monthly_data['nombre_inscriptions'].mean(),
            'peak_month': month_dist.idxmax(),
            'total_inscriptions': len(self.df_clean)
        }
    
    def _plot_demographic_analysis(self):
        """Analyse démographique"""
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Distribution par sexe
        if 'Sexe_F' in self.df_clean.columns and 'Sexe_M' in self.df_clean.columns:
            sexe_counts = [self.df_clean['Sexe_F'].sum(), self.df_clean['Sexe_M'].sum()]
            axes[0,0].pie(sexe_counts, labels=['Femmes', 'Hommes'], autopct='%1.1f%%', startangle=90)
            axes[0,0].set_title('Répartition par sexe')
        
        # Top 10 nationalités
        if 'Nationalité_encoded' in self.df_clean.columns:
            nat_counts = self.df_clean['Nationalité_encoded'].value_counts().head(10)
            axes[0,1].barh(range(len(nat_counts)), nat_counts.values)
            axes[0,1].set_title('Top 10 Nationalités (encodées)')
            axes[0,1].set_xlabel('Nombre d\'inscriptions')
        
        # Top 10 villes
        if 'Ville_encoded' in self.df_clean.columns:
            ville_counts = self.df_clean['Ville_encoded'].value_counts().head(10)
            axes[1,0].barh(range(len(ville_counts)), ville_counts.values, color='lightcoral')
            axes[1,0].set_title('Top 10 Villes (encodées)')
            axes[1,0].set_xlabel('Nombre d\'inscriptions')
        
        # Distribution prioritaire/veille
        prioritaire_cols = [col for col in self.df_clean.columns if col.startswith('Prioritaire/Veille_')]
        if prioritaire_cols:
            prioritaire_counts = [self.df_clean[col].sum() for col in prioritaire_cols]
            labels = [col.replace('Prioritaire/Veille_', '') for col in prioritaire_cols]
            axes[1,1].bar(labels, prioritaire_counts, color='lightsteelblue')
            axes[1,1].set_title('Distribution Prioritaire/Veille')
            axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.viz_folder / 'demographic_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_geographic_analysis(self):
        """Analyse géographique"""
        
        # Top 15 codes postaux
        if 'Code postal_encoded' in self.df_clean.columns:
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            
            cp_counts = self.df_clean['Code postal_encoded'].value_counts().head(15)
            ax.bar(range(len(cp_counts)), cp_counts.values, color='darkseagreen')
            ax.set_title('Top 15 Codes Postaux (encodés)')
            ax.set_xlabel('Code Postal (ID encodé)')
            ax.set_ylabel('Nombre d\'inscriptions')
            
            plt.tight_layout()
            plt.savefig(self.viz_folder / 'geographic_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def _plot_correlation_matrix(self):
        """Matrice de corrélation des variables numériques"""
        
        # Sélectionner uniquement les colonnes numériques
        numeric_cols = self.df_clean.select_dtypes(include=[np.number]).columns
        correlation_data = self.df_clean[numeric_cols]
        
        if len(correlation_data.columns) > 1:
            plt.figure(figsize=(12, 10))
            correlation_matrix = correlation_data.corr()
            
            # Simple heatmap with matplotlib
            plt.imshow(correlation_matrix, cmap='coolwarm', vmin=-1, vmax=1)
            plt.colorbar(shrink=0.8)
            plt.title('Matrice de Corrélation des Variables Numériques')
            
            # Ajouter les labels si pas trop nombreux
            if len(correlation_matrix.columns) < 20:
                plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=45)
                plt.yticks(range(len(correlation_matrix.columns)), correlation_matrix.columns)
            
            plt.tight_layout()
            plt.savefig(self.viz_folder / 'correlation_matrix.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # Sauvegarder les corrélations fortes
            strong_corr = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_val = correlation_matrix.iloc[i, j]
                    if abs(corr_val) > 0.5:  # Corrélation forte
                        strong_corr.append({
                            'var1': correlation_matrix.columns[i],
                            'var2': correlation_matrix.columns[j],
                            'correlation': corr_val
                        })
            
            self.eda_results['strong_correlations'] = strong_corr
    
    def _generate_descriptive_stats(self):
        """Génère les statistiques descriptives"""
        
        stats = {
            'dataset_shape': self.df_clean.shape,
            'numeric_vars': len(self.df_clean.select_dtypes(include=[np.number]).columns),
            'categorical_vars': len(self.df_clean.select_dtypes(include=['object']).columns),
            'missing_values': self.df_clean.isnull().sum().sum(),
            'date_range': {
                'min_date': self.df_clean['Date inscription'].min() if 'Date inscription' in self.df_clean.columns else None,
                'max_date': self.df_clean['Date inscription'].max() if 'Date inscription' in self.df_clean.columns else None
            }
        }
        
        self.eda_results['descriptive_stats'] = stats
        
        # Sauvegarder un rapport textuel
        report_path = self.viz_folder / 'eda_report.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=== RAPPORT D'ANALYSE EXPLORATOIRE ===\n\n")
            f.write(f"Forme du dataset: {stats['dataset_shape']}\n")
            f.write(f"Variables numériques: {stats['numeric_vars']}\n")
            f.write(f"Variables catégorielles: {stats['categorical_vars']}\n")
            f.write(f"Valeurs manquantes restantes: {stats['missing_values']}\n\n")
            
            if 'temporal_insights' in self.eda_results:
                insights = self.eda_results['temporal_insights']
                f.write("=== INSIGHTS TEMPORELS ===\n")
                f.write(f"Période couverte: {insights['total_years']} années\n")
                f.write(f"Année avec le plus d'inscriptions: {insights['peak_year']}\n")
                f.write(f"Moyenne mensuelle: {insights['avg_monthly']:.1f} inscriptions\n")
                f.write(f"Mois de pointe: {insights['peak_month']}\n")
                f.write(f"Total inscriptions: {insights['total_inscriptions']}\n\n")
            
            if 'strong_correlations' in self.eda_results and self.eda_results['strong_correlations']:
                f.write("=== CORRÉLATIONS FORTES (>0.5) ===\n")
                for corr in self.eda_results['strong_correlations']:
                    f.write(f"{corr['var1']} ↔ {corr['var2']}: {corr['correlation']:.3f}\n")
    
    def prepare_for_ml(self):
        """
        Prépare le dataset final pour l'entraînement ML
        
        Returns:
            dict: Datasets préparés pour différents types de prédiction
        """
        logger.info("=== PRÉPARATION POUR MACHINE LEARNING ===")
        
        if self.df_clean is None:
            raise ValueError("Les données doivent être préprocessées avant la préparation ML")
        
        # Dataset pour prédiction temporelle (agrégations)
        ml_datasets = {
            'yearly_prediction': self._prepare_yearly_dataset(),
            'monthly_prediction': self._prepare_monthly_dataset(),
            'weekly_prediction': self._prepare_weekly_dataset(),
            'individual_features': self._prepare_individual_dataset()
        }
        
        logger.info("✅ Datasets ML préparés")
        return ml_datasets
    
    def _prepare_yearly_dataset(self):
        """Prépare le dataset pour prédiction annuelle"""
        yearly_data = self.yearly_counts.copy()
        
        # Ajouter des features temporelles
        yearly_data['annee_normalized'] = (yearly_data['annee_inscription'] - yearly_data['annee_inscription'].min()) / (yearly_data['annee_inscription'].max() - yearly_data['annee_inscription'].min())
        yearly_data['trend'] = range(len(yearly_data))
        
        return {
            'features': yearly_data[['annee_inscription', 'annee_normalized', 'trend']],
            'target': yearly_data['nombre_inscriptions'],
            'dates': yearly_data['annee_inscription']
        }
    
    def _prepare_monthly_dataset(self):
        """Prépare le dataset pour prédiction mensuelle"""
        monthly_data = self.monthly_counts.copy()
        
        # Features temporelles avancées
        monthly_data['mois_sin'] = np.sin(2 * np.pi * monthly_data['mois_inscription'] / 12)
        monthly_data['mois_cos'] = np.cos(2 * np.pi * monthly_data['mois_inscription'] / 12)
        monthly_data['trend'] = range(len(monthly_data))
        monthly_data['annee_normalized'] = (monthly_data['annee_inscription'] - monthly_data['annee_inscription'].min()) / (monthly_data['annee_inscription'].max() - monthly_data['annee_inscription'].min())
        
        return {
            'features': monthly_data[['annee_inscription', 'mois_inscription', 'mois_sin', 'mois_cos', 'trend', 'annee_normalized']],
            'target': monthly_data['nombre_inscriptions'],
            'dates': monthly_data['date']
        }
    
    def _prepare_weekly_dataset(self):
        """Prépare le dataset pour prédiction hebdomadaire"""
        weekly_data = self.weekly_counts.copy()
        
        # Features temporelles
        weekly_data['semaine_sin'] = np.sin(2 * np.pi * weekly_data['semaine_inscription'] / 52)
        weekly_data['semaine_cos'] = np.cos(2 * np.pi * weekly_data['semaine_inscription'] / 52)
        weekly_data['trend'] = range(len(weekly_data))
        
        return {
            'features': weekly_data[['annee_inscription', 'semaine_inscription', 'semaine_sin', 'semaine_cos', 'trend']],
            'target': weekly_data['nombre_inscriptions'],
            'dates': weekly_data[['annee_inscription', 'semaine_inscription']]
        }
    
    def _prepare_individual_dataset(self):
        """Prépare le dataset avec features individuelles pour analyse complémentaire"""
        
        # Sélectionner les colonnes numériques et encodées
        feature_cols = []
        
        # Features temporelles
        temporal_features = ['annee_inscription', 'mois_inscription', 'trimestre_inscription', 
                           'semaine_inscription', 'jour_semaine', 'mois_sin', 'mois_cos']
        feature_cols.extend([col for col in temporal_features if col in self.df_clean.columns])
        
        # Features encodées
        encoded_features = [col for col in self.df_clean.columns if col.endswith('_encoded')]
        feature_cols.extend(encoded_features)
        
        # Features one-hot
        onehot_features = [col for col in self.df_clean.columns if any(prefix in col for prefix in ['Sexe_', 'Prioritaire/Veille_', 'Situation Familiale_', 'Type de logement_'])]
        feature_cols.extend(onehot_features)
        
        X = self.df_clean[feature_cols].fillna(0)
        
        return {
            'features': X,
            'feature_names': feature_cols,
            'target_date': self.df_clean['Date inscription'] if 'Date inscription' in self.df_clean.columns else None
        }
    
    def get_processing_summary(self):
        """
        Retourne un résumé complet du preprocessing
        
        Returns:
            dict: Résumé des étapes et résultats
        """
        summary = {
            'original_shape': self.df_raw.shape if self.df_raw is not None else None,
            'cleaned_shape': self.df_clean.shape if self.df_clean is not None else None,
            'encoders_used': list(self.encoders.keys()),
            'visualizations_created': list(self.viz_folder.glob('*.png')),
            'eda_insights': self.eda_results.get('temporal_insights', {}),
            'strong_correlations': len(self.eda_results.get('strong_correlations', [])),
            'missing_values_handled': True if self.df_clean is not None else False
        }
        
        return summary
