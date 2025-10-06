# app/models/__init__.py
# Fichier d'initialisation du module models
# 
# Ce module contient les classes qui gèrent les DONNÉES (couche Model dans le pattern MVC)
#
# === ARCHITECTURE MVC ===
# Model (models/) : Gestion des données et logique métier
# View (templates/) : Interface utilisateur (HTML)
# Controller (controllers/) : Logique de routage et coordination
#
# === CONTENU DU MODULE MODELS ===
# 
# 📊 data_loader.py : Classe DataLoader
#     - Chargement centralisé des fichiers Excel
#     - Lazy loading (chargement paresseux)
#     - Cache intelligent avec vérification de modification
#     - Normalisation automatique des colonnes
#     - Sauvegarde sécurisée des données
#
# === RESPONSABILITÉS DU MODULE ===
# 
# ✅ Ce que fait ce module :
# - Lecture/écriture des fichiers Excel
# - Validation et nettoyage des données
# - Cache des données pour les performances
# - Normalisation des formats de colonnes
# - Gestion des erreurs de fichiers
#
# ❌ Ce que ne fait PAS ce module :
# - Logique d'interface utilisateur (c'est le rôle des templates)
# - Routage des URLs (c'est le rôle des controllers)
# - Communication avec l'IA (c'est le rôle des services)
# - Validation des formulaires (c'est le rôle des controllers/services)
#
# === PATTERN UTILISÉ ===
# 
# Le DataLoader utilise plusieurs patterns :
# - Singleton Pattern : Une seule instance partagée dans toute l'app
# - Lazy Loading : Charge les données seulement quand nécessaire
# - Cache Pattern : Garde les données en mémoire pour éviter les rechargements
# - Factory Pattern : Crée les DataFrames selon le type de données
#
# === UTILISATION TYPIQUE ===
# 
# from app import data_loader  # Instance globale créée dans app/__init__.py
# 
# # Accès aux données (chargement automatique si nécessaire)
# inscriptions = data_loader.inscriptions  # pandas.DataFrame
# presences = data_loader.presences        # pandas.DataFrame
# 
# # Informations sur les fichiers
# info = data_loader.get_file_info()
# 
# # Rechargement forcé si fichiers modifiés externes
# data_loader.reload_all()
# 
# # Sauvegarde des modifications
# data_loader.save_inscriptions(nouveau_df)
#
# === AVANTAGES DE CETTE ARCHITECTURE ===
# 
# 🚀 Performance : Cache évite les rechargements inutiles
# 🛡️ Sécurité : Validation et gestion d'erreurs centralisées
# 🔧 Maintenance : Un seul endroit pour la logique de données
# 📈 Évolutivité : Facile d'ajouter de nouveaux types de données
# 🧪 Tests : Logique isolée et testable indépendamment