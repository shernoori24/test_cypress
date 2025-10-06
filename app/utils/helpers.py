# app/utils/helpers.py
from datetime import datetime, timedelta
import pandas as pd
import re

def format_date(date_input, input_format='%Y-%m-%d', output_format='%d/%m/%Y'):
    """
    Formate une date selon le format souhaité
    
    Args:
        date_input: Date à formater (string, datetime ou pd.Timestamp)
        input_format: Format d'entrée
        output_format: Format de sortie
        
    Returns:
        str: Date formatée ou chaîne vide si erreur
    """
    try:
        if isinstance(date_input, str):
            date_obj = datetime.strptime(date_input, input_format)
        elif isinstance(date_input, (datetime, pd.Timestamp)):
            date_obj = date_input
        else:
            return ""
        
        return date_obj.strftime(output_format)
    except (ValueError, TypeError):
        return ""

def format_duration(start_time, end_time):
    """
    Calcule et formate la durée entre deux heures
    
    Args:
        start_time: Heure de début (format HH:MM)
        end_time: Heure de fin (format HH:MM)
        
    Returns:
        str: Durée formatée (ex: "2h30") ou chaîne vide si erreur
    """
    try:
        start = datetime.strptime(str(start_time), '%H:%M')
        end = datetime.strptime(str(end_time), '%H:%M')
        
        if end < start:
            # Cas où l'activité se termine le lendemain
            end += timedelta(days=1)
        
        duration = end - start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}h{minutes:02d}"
        elif hours > 0:
            return f"{hours}h"
        elif minutes > 0:
            return f"{minutes}min"
        else:
            return "0min"
    except (ValueError, TypeError):
        return ""

def safe_convert_to_int(value, default=0):
    """
    Convertit une valeur en entier de manière sûre
    
    Args:
        value: Valeur à convertir
        default: Valeur par défaut si conversion impossible
        
    Returns:
        int: Valeur convertie ou valeur par défaut
    """
    try:
        if pd.isna(value) or value == '':
            return default
        return int(float(str(value)))
    except (ValueError, TypeError):
        return default

def safe_convert_to_float(value, default=0.0):
    """
    Convertit une valeur en float de manière sûre
    
    Args:
        value: Valeur à convertir
        default: Valeur par défaut si conversion impossible
        
    Returns:
        float: Valeur convertie ou valeur par défaut
    """
    try:
        if pd.isna(value) or value == '':
            return default
        return float(str(value))
    except (ValueError, TypeError):
        return default

def clean_phone_number(phone):
    """
    Nettoie et formate un numéro de téléphone
    
    Args:
        phone: Numéro de téléphone à nettoyer
        
    Returns:
        str: Numéro nettoyé ou chaîne vide
    """
    if not phone:
        return ""
    
    # Supprimer tous les caractères non numériques sauf le +
    cleaned = re.sub(r'[^\d+]', '', str(phone))
    
    # Cas du numéro français
    if cleaned.startswith('0') and len(cleaned) == 10:
        return cleaned
    elif cleaned.startswith('+33') and len(cleaned) == 12:
        return '0' + cleaned[3:]
    elif cleaned.startswith('33') and len(cleaned) == 11:
        return '0' + cleaned[2:]
    
    return cleaned

def extract_person_name_from_text(text, keywords):
    """
    Extrait le nom d'une personne depuis un texte basé sur des mots-clés
    
    Args:
        text: Texte à analyser
        keywords: Liste de mots-clés indicateurs
        
    Returns:
        str: Nom extrait ou None
    """
    if not text or not keywords:
        return None
    
    words = text.split()
    for i, word in enumerate(words):
        if word.lower() in [kw.lower() for kw in keywords]:
            # Prendre les mots suivants comme nom
            if i + 1 < len(words):
                # Joindre jusqu'à 3 mots suivants (prénom + nom + éventuel nom composé)
                name_parts = []
                for j in range(i + 1, min(i + 4, len(words))):
                    # Arrêter si on rencontre un mot qui ressemble à un verbe/préposition
                    if words[j].lower() in ['est', 'était', 'a', 'le', 'la', 'les', 'de', 'du', 'des']:
                        break
                    name_parts.append(words[j])
                
                if name_parts:
                    return ' '.join(name_parts).strip('?.,!;:')
    
    return None

def generate_unique_filename(original_filename, existing_files):
    """
    Génère un nom de fichier unique en évitant les conflits
    
    Args:
        original_filename: Nom de fichier original
        existing_files: Liste ou set des fichiers existants
        
    Returns:
        str: Nom de fichier unique
    """
    if original_filename not in existing_files:
        return original_filename
    
    name, ext = original_filename.rsplit('.', 1) if '.' in original_filename else (original_filename, '')
    counter = 1
    
    while True:
        new_name = f"{name}_{counter}.{ext}" if ext else f"{name}_{counter}"
        if new_name not in existing_files:
            return new_name
        counter += 1

def paginate_data(data, page=1, per_page=20):
    """
    Pagine une liste de données
    
    Args:
        data: Liste ou DataFrame à paginer
        page: Numéro de page (commence à 1)
        per_page: Nombre d'éléments par page
        
    Returns:
        dict: Données paginées avec métadonnées
    """
    if isinstance(data, pd.DataFrame):
        total = len(data)
        start = (page - 1) * per_page
        end = start + per_page
        items = data.iloc[start:end].to_dict('records')
    else:
        total = len(data)
        start = (page - 1) * per_page
        end = start + per_page
        items = data[start:end]
    
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_num': page - 1 if has_prev else None,
        'next_num': page + 1 if has_next else None
    }
