# app/services/data_cleaning_service.py
# Service de nettoyage et validation des données
# Nettoie automatiquement les données avant affichage des rapports

import pandas as pd
import re
from datetime import datetime, date
import logging
from typing import Dict, List, Tuple, Optional
import numpy as np

class DataCleaningService:
    """
    Service spécialisé pour le nettoyage et la validation des données
    
    Fonctionnalités :
    - Normalisation des formats de dates (français DD/MM/YYYY)
    - Validation et correction des heures
    - Nettoyage des noms et numéros d'apprenants
    - Détection et signalement des incohérences
    - Cache des données nettoyées pour optimiser les performances
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._cache_timestamps = {}
        self.cache_duration = 300  # 5 minutes de cache
        
        # Patterns pour la validation
        self.date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',      # DD/MM/YYYY ou D/M/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{4})',      # DD-MM-YYYY ou D-M-YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',      # YYYY-MM-DD
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',    # DD.MM.YYYY
        ]
        
        self.time_pattern = r'^(\d{1,2}):(\d{2})$'  # HH:MM
        
        # Messages d'erreur standardisés
        self.error_messages = {
            'no_presence': 'Aucune présence enregistrée pour cet apprenant',
            'invalid_date': 'Date invalide détectée et corrigée',
            'missing_data': 'Données manquantes complétées',
            'format_corrected': 'Format de données corrigé automatiquement'
        }
    
    def clean_inscription_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Nettoie les données d'inscription
        
        Args:
            df: DataFrame des inscriptions
            
        Returns:
            Tuple[DataFrame nettoyé, Liste des messages d'alerte]
        """
        if df.empty:
            return df, ['Aucune donnée d\'inscription trouvée']
        
        df_clean = df.copy()
        alerts = []
        
        # 1. Nettoyage des dates
        date_columns = ['Date de naissance', 'Date inscription', 'Première venue', 'Arrivée en France']
        for col in date_columns:
            if col in df_clean.columns:
                df_clean[col], date_alerts = self._clean_date_column(df_clean[col], col)
                alerts.extend(date_alerts)
        
        # 2. Nettoyage des numéros d'apprenants
        if 'N°' in df_clean.columns:
            df_clean['N°'], num_alerts = self._clean_numero_column(df_clean['N°'])
            alerts.extend(num_alerts)
        
        # 3. Nettoyage des noms
        for col in ['NOM', 'Prénom']:
            if col in df_clean.columns:
                df_clean[col] = self._clean_name_column(df_clean[col])
        
        # 4. Validation des âges
        if 'Age' in df_clean.columns and 'Date de naissance' in df_clean.columns:
            df_clean['Age'], age_alerts = self._validate_age(df_clean['Date de naissance'], df_clean['Age'])
            alerts.extend(age_alerts)
        
        # 5. Nettoyage des coordonnées
        for col in ['Téléphone', 'Email']:
            if col in df_clean.columns:
                df_clean[col] = self._clean_contact_column(df_clean[col], col)
        
        return df_clean, alerts
    
    def clean_presence_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Nettoie les données de présence
        
        Args:
            df: DataFrame des présences
            
        Returns:
            Tuple[DataFrame nettoyé, Liste des messages d'alerte]
        """
        if df.empty:
            return df, ['Aucune donnée de présence trouvée']
        
        df_clean = df.copy()
        alerts = []
        
        # 1. Nettoyage des dates
        if 'Date du Jour' in df_clean.columns:
            df_clean['Date du Jour'], date_alerts = self._clean_date_column(df_clean['Date du Jour'], 'Date du Jour')
            alerts.extend(date_alerts)
        
        # 2. Nettoyage des heures
        time_columns = ['Activités Apprenants Début', 'Activités Apprenants Fin', 
                       'Activité Encadrant Début', 'Activité Encadrant Fin']
        for col in time_columns:
            if col in df_clean.columns:
                df_clean[col], time_alerts = self._clean_time_column(df_clean[col], col)
                alerts.extend(time_alerts)
        
        # 3. Nettoyage des durées
        duration_columns = ['Durée Activité Apprenants', 'Activité Encadrant Durée']
        for col in duration_columns:
            if col in df_clean.columns:
                df_clean[col], duration_alerts = self._clean_duration_column(df_clean[col], col)
                alerts.extend(duration_alerts)
        
        # 4. Validation des numéros d'apprenants
        if 'Numéro Apprenant' in df_clean.columns:
            df_clean['Numéro Apprenant'], num_alerts = self._clean_numero_column(df_clean['Numéro Apprenant'])
            alerts.extend(num_alerts)
        
        # 5. Cohérence début/fin/durée
        coherence_alerts = self._validate_time_coherence(df_clean)
        alerts.extend(coherence_alerts)
        
        return df_clean, alerts
    
    def _clean_date_column(self, series: pd.Series, column_name: str) -> Tuple[pd.Series, List[str]]:
        """Nettoie une colonne de dates en format français"""
        alerts = []
        cleaned_series = series.copy()
        
        def parse_french_date(date_str):
            """Parse une date en format français avec plusieurs patterns"""
            if pd.isna(date_str) or date_str == '':
                return None
                
            date_str = str(date_str).strip()
            
            # Pattern principal : DD/MM/YYYY
            for pattern in self.date_patterns:
                match = re.match(pattern, date_str)
                if match:
                    try:
                        groups = match.groups()
                        if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD
                            year, month, day = map(int, groups)
                        else:  # DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
                            day, month, year = map(int, groups)
                        
                        # Validation des valeurs
                        if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2030:
                            return f"{day:02d}/{month:02d}/{year}"
                    except ValueError:
                        continue
            
            # Si aucun pattern ne fonctionne, essayer pandas
            try:
                parsed_date = pd.to_datetime(date_str, dayfirst=True, errors='coerce')
                if not pd.isna(parsed_date):
                    return parsed_date.strftime('%d/%m/%Y')
            except:
                pass
            
            alerts.append(f"Date invalide dans {column_name}: '{date_str}'")
            return None
        
        # Appliquer le nettoyage
        for idx in series.index:
            if not pd.isna(series[idx]):
                cleaned_date = parse_french_date(series[idx])
                if cleaned_date:
                    cleaned_series[idx] = cleaned_date
                else:
                    cleaned_series[idx] = None
        
        return cleaned_series, alerts
    
    def _clean_time_column(self, series: pd.Series, column_name: str) -> Tuple[pd.Series, List[str]]:
        """Nettoie une colonne d'heures (format HH:MM)"""
        alerts = []
        cleaned_series = series.copy()
        
        def parse_time(time_str):
            """Parse une heure en format HH:MM"""
            if pd.isna(time_str) or time_str == '':
                return None
                
            time_str = str(time_str).strip()
            
            # Pattern HH:MM
            match = re.match(self.time_pattern, time_str)
            if match:
                hours, minutes = map(int, match.groups())
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    return f"{hours:02d}:{minutes:02d}"
            
            # Essayer de parser avec pandas
            try:
                if isinstance(time_str, str) and ':' in time_str:
                    parts = time_str.split(':')
                    if len(parts) >= 2:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        if 0 <= hours <= 23 and 0 <= minutes <= 59:
                            return f"{hours:02d}:{minutes:02d}"
            except ValueError:
                pass
            
            alerts.append(f"Heure invalide dans {column_name}: '{time_str}'")
            return None
        
        # Appliquer le nettoyage
        for idx in series.index:
            if not pd.isna(series[idx]):
                cleaned_time = parse_time(series[idx])
                cleaned_series[idx] = cleaned_time
        
        return cleaned_series, alerts
    
    def _clean_duration_column(self, series: pd.Series, column_name: str) -> Tuple[pd.Series, List[str]]:
        """Nettoie une colonne de durées"""
        alerts = []
        cleaned_series = series.copy()
        
        def format_duration(duration):
            """Formate une durée en HH:MM"""
            if pd.isna(duration):
                return None
            
            # Si c'est déjà un objet time
            if hasattr(duration, 'hour') and hasattr(duration, 'minute'):
                return f"{duration.hour:02d}:{duration.minute:02d}"
            
            # Si c'est une string
            duration_str = str(duration).strip()
            
            # Pattern HH:MM
            if re.match(r'^\d{1,2}:\d{2}$', duration_str):
                return duration_str
            
            # Pattern timedelta ou autres formats
            try:
                # Essayer de convertir en timedelta puis en heures:minutes
                if 'day' in duration_str or 'hour' in duration_str or 'minute' in duration_str:
                    td = pd.to_timedelta(duration_str)
                    total_seconds = int(td.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    return f"{hours:02d}:{minutes:02d}"
            except:
                pass
            
            alerts.append(f"Durée invalide dans {column_name}: '{duration}'")
            return None
        
        # Appliquer le nettoyage
        for idx in series.index:
            cleaned_duration = format_duration(series[idx])
            cleaned_series[idx] = cleaned_duration
        
        return cleaned_series, alerts
    
    def _clean_numero_column(self, series: pd.Series) -> Tuple[pd.Series, List[str]]:
        """Nettoie les numéros d'apprenants (format YY-XXX)"""
        alerts = []
        cleaned_series = series.copy()
        
        def format_numero(numero):
            """Formate un numéro d'apprenant"""
            if pd.isna(numero):
                return None
            
            numero_str = str(numero).strip()
            
            # Pattern YY-XXX
            if re.match(r'^\d{2}-\d{3}$', numero_str):
                return numero_str
            
            # Essayer de corriger des formats proches
            if re.match(r'^\d{2}\d{3}$', numero_str):  # YYXXX -> YY-XXX
                return f"{numero_str[:2]}-{numero_str[2:]}"
            
            if re.match(r'^\d{2}_\d{3}$', numero_str):  # YY_XXX -> YY-XXX
                return numero_str.replace('_', '-')
            
            alerts.append(f"Format de numéro non standard: '{numero}'")
            return numero_str  # Garder tel quel si pas de format reconnu
        
        # Appliquer le nettoyage
        for idx in series.index:
            if not pd.isna(series[idx]):
                cleaned_numero = format_numero(series[idx])
                cleaned_series[idx] = cleaned_numero
        
        return cleaned_series, alerts
    
    def _clean_name_column(self, series: pd.Series) -> pd.Series:
        """Nettoie les noms (majuscules, espaces)"""
        def clean_name(name):
            if pd.isna(name):
                return None
            
            name_str = str(name).strip()
            # Supprimer les espaces multiples et mettre en forme
            name_str = re.sub(r'\s+', ' ', name_str)
            # Mettre en majuscules pour les noms, title case pour les prénoms
            return name_str.upper() if series.name == 'NOM' else name_str.title()
        
        return series.apply(clean_name)
    
    def _clean_contact_column(self, series: pd.Series, column_type: str) -> pd.Series:
        """Nettoie les contacts (téléphone, email)"""
        def clean_contact(contact):
            if pd.isna(contact):
                return None
            
            contact_str = str(contact).strip()
            
            if column_type == 'Téléphone':
                # Nettoyer le téléphone : garder uniquement les chiffres et espaces/points/tirets
                contact_str = re.sub(r'[^\d\s\.\-]', '', contact_str)
                contact_str = re.sub(r'\s+', ' ', contact_str)
                return contact_str
            
            elif column_type == 'Email':
                # Validation basique de l'email
                if '@' in contact_str and '.' in contact_str:
                    return contact_str.lower()
                return None
            
            return contact_str
        
        return series.apply(clean_contact)
    
    def _validate_age(self, date_birth_series: pd.Series, age_series: pd.Series) -> Tuple[pd.Series, List[str]]:
        """Valide et corrige les âges par rapport aux dates de naissance"""
        alerts = []
        cleaned_age = age_series.copy()
        
        current_year = datetime.now().year
        
        for idx in date_birth_series.index:
            birth_date_str = date_birth_series[idx]
            current_age = age_series[idx] if idx in age_series.index else None
            
            if not pd.isna(birth_date_str):
                try:
                    # Parser la date de naissance
                    birth_date = datetime.strptime(str(birth_date_str), '%d/%m/%Y')
                    calculated_age = current_year - birth_date.year
                    
                    # Ajuster si l'anniversaire n'est pas encore passé cette année
                    if datetime.now().month < birth_date.month or \
                       (datetime.now().month == birth_date.month and datetime.now().day < birth_date.day):
                        calculated_age -= 1
                    
                    # Vérifier la cohérence avec l'âge indiqué
                    if not pd.isna(current_age):
                        current_age_num = int(str(current_age).replace(' ans', '').strip())
                        if abs(calculated_age - current_age_num) > 1:
                            alerts.append(f"Âge incohérent corrigé: {current_age} -> {calculated_age} ans")
                    
                    cleaned_age[idx] = f"{calculated_age} ans"
                    
                except ValueError:
                    pass
        
        return cleaned_age, alerts
    
    def _validate_time_coherence(self, df: pd.DataFrame) -> List[str]:
        """Valide la cohérence entre heures de début, fin et durée"""
        alerts = []
        
        if not all(col in df.columns for col in ['Activités Apprenants Début', 'Activités Apprenants Fin', 'Durée Activité Apprenants']):
            return alerts
        
        for idx in df.index:
            debut = df.loc[idx, 'Activités Apprenants Début']
            fin = df.loc[idx, 'Activités Apprenants Fin']
            duree = df.loc[idx, 'Durée Activité Apprenants']
            
            if not pd.isna(debut) and not pd.isna(fin):
                try:
                    debut_time = datetime.strptime(str(debut), '%H:%M').time()
                    fin_time = datetime.strptime(str(fin), '%H:%M').time()
                    
                    if fin_time <= debut_time:
                        alerts.append(f"Ligne {idx}: Heure de fin antérieure au début ({debut} -> {fin})")
                        
                except ValueError:
                    continue
        
        return alerts
    
    def get_cleaning_summary(self, inscription_alerts: List[str], presence_alerts: List[str]) -> Dict:
        """Génère un résumé du nettoyage effectué"""
        return {
            'total_issues': len(inscription_alerts) + len(presence_alerts),
            'inscription_issues': len(inscription_alerts),
            'presence_issues': len(presence_alerts),
            'inscription_details': inscription_alerts[:10],  # Limiter à 10 pour l'affichage
            'presence_details': presence_alerts[:10],
            'timestamp': datetime.now().isoformat(),
            'status': 'success' if len(inscription_alerts) + len(presence_alerts) == 0 else 'cleaned'
        }
    
    def validate_apprenant_exists(self, numero_apprenant: str, inscription_df: pd.DataFrame, presence_df: pd.DataFrame) -> Dict:
        """Valide qu'un apprenant existe et a des données cohérentes"""
        result = {
            'exists_inscription': False,
            'exists_presence': False,
            'has_valid_data': False,
            'message': '',
            'warnings': []
        }
        
        # Vérifier existence dans inscriptions
        if not inscription_df.empty and 'N°' in inscription_df.columns:
            result['exists_inscription'] = numero_apprenant in inscription_df['N°'].values
        
        # Vérifier existence dans présences
        if not presence_df.empty and 'Numéro Apprenant' in presence_df.columns:
            result['exists_presence'] = numero_apprenant in presence_df['Numéro Apprenant'].values
        
        # Déterminer le statut et message
        if result['exists_inscription'] and result['exists_presence']:
            result['has_valid_data'] = True
            result['message'] = 'Apprenant trouvé avec données complètes'
        elif result['exists_inscription'] and not result['exists_presence']:
            result['message'] = self.error_messages['no_presence']
            result['warnings'].append('Apprenant inscrit mais aucune présence enregistrée')
        elif not result['exists_inscription'] and result['exists_presence']:
            result['message'] = 'Présences trouvées mais apprenant non inscrit'
            result['warnings'].append('Données de présence sans inscription correspondante')
        else:
            result['message'] = 'Apprenant non trouvé'
        
        return result
