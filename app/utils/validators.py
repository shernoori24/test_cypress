# app/utils/validators.py
import pandas as pd
from datetime import datetime
import re
from .error_handler import DataValidationError

def validate_inscription_data(data):
    """
    Valide les données d'inscription
    
    Args:
        data (dict): Données d'inscription à valider
        
    Returns:
        tuple: (is_valid, errors_list)
    """
    errors = []
    
    # Champs obligatoires
    required_fields = ['numero_apprenant', 'nom', 'prenom', 'adresse', 'code_postal', 'ville']
    for field in required_fields:
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f"Le champ '{field}' est obligatoire")
    
    # Validation du numéro d'apprenant (format AA-NNN)
    if data.get('numero_apprenant'):
        numero_pattern = r'^\d{2}-\d{3}$'
        if not re.match(numero_pattern, str(data['numero_apprenant']).strip()):
            errors.append("Le numéro d'apprenant doit être au format AA-NNN (ex: 25-001)")
    
    # Validation du code postal (5 chiffres)
    if data.get('code_postal'):
        if not re.match(r'^\d{5}$', str(data['code_postal'])):
            errors.append("Le code postal doit contenir exactement 5 chiffres")
    
    # Validation de l'email
    if data.get('email'):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            errors.append("Format d'email invalide")
    
    # Validation du téléphone
    if data.get('telephone'):
        phone_pattern = r'^(\+33|0)[1-9](\d{8})$'
        if not re.match(phone_pattern, str(data['telephone']).replace(' ', '')):
            errors.append("Format de téléphone invalide")
    
    # Validation des dates
    date_fields = ['date_naissance', 'arrivee_france', 'date_inscription', 'premiere_venue']
    for field in date_fields:
        if data.get(field):
            try:
                datetime.strptime(str(data[field]), '%Y-%m-%d')
            except ValueError:
                errors.append(f"Format de date invalide pour '{field}' (attendu: YYYY-MM-DD)")
    
    return len(errors) == 0, errors

def validate_presence_data(data):
    """
    Valide les données de présence
    
    Args:
        data (dict): Données de présence à valider
        
    Returns:
        tuple: (is_valid, errors_list)
    """
    errors = []
    
    # Champs obligatoires
    required_fields = ['date_jour', 'numero_apprenant', 'apprenant', 'activite_debut', 'activite_fin']
    for field in required_fields:
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f"Le champ '{field}' est obligatoire")
    
    # Validation de la date
    if data.get('date_jour'):
        try:
            datetime.strptime(str(data['date_jour']), '%Y-%m-%d')
        except ValueError:
            errors.append("Format de date invalide (attendu: YYYY-MM-DD)")
    
    # Validation des heures
    time_fields = ['activite_debut', 'activite_fin']
    for field in time_fields:
        if data.get(field):
            try:
                datetime.strptime(str(data[field]), '%H:%M')
            except ValueError:
                errors.append(f"Format d'heure invalide pour '{field}' (attendu: HH:MM)")
    
    # Validation logique : heure de fin après heure de début
    if data.get('activite_debut') and data.get('activite_fin'):
        try:
            debut = datetime.strptime(str(data['activite_debut']), '%H:%M')
            fin = datetime.strptime(str(data['activite_fin']), '%H:%M')
            if fin <= debut:
                errors.append("L'heure de fin doit être postérieure à l'heure de début")
        except ValueError:
            pass  # Erreur déjà capturée plus haut
    
    # Validation du numéro d'apprenant
    if data.get('numero_apprenant'):
        if not re.match(r'^\d{2}-\d{3}$', str(data['numero_apprenant'])):
            errors.append("Format de numéro d'apprenant invalide (attendu: XX-XXX)")
    
    return len(errors) == 0, errors

def validate_planning_data(data):
    """
    Valide les données de planning
    
    Args:
        data (dict): Données de planning à valider
        
    Returns:
        tuple: (is_valid, errors_list)
    """
    errors = []
    
    # Champs obligatoires
    required_fields = ['jour', 'activite', 'heure_debut', 'heure_fin', 'encadrant', 'semaine']
    for field in required_fields:
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f"Le champ '{field}' est obligatoire")
    
    # Validation du jour de la semaine
    jours_valides = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    if data.get('jour') and data['jour'].lower() not in jours_valides:
        errors.append("Le jour doit être un jour de la semaine valide")
    
    # Validation des heures
    time_fields = ['heure_debut', 'heure_fin']
    for field in time_fields:
        if data.get(field):
            try:
                datetime.strptime(str(data[field]), '%H:%M')
            except ValueError:
                errors.append(f"Format d'heure invalide pour '{field}' (attendu: HH:MM)")
    
    # Validation de la semaine (format ISO)
    if data.get('semaine'):
        try:
            datetime.strptime(str(data['semaine']), '%Y-%m-%d')
        except ValueError:
            errors.append("Format de semaine invalide (attendu: YYYY-MM-DD)")
    
    return len(errors) == 0, errors
