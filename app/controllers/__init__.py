# app/controllers/__init__.py
# Fichier d'initialisation du module controllers
# 
# Ce fichier marque le dossier comme un package Python et peut contenir
# des imports communs ou des configurations partagées entre tous les contrôleurs
#
# Pour l'instant, ce fichier est vide car chaque contrôleur est indépendant
# et est importé directement dans app/__init__.py lors de l'enregistrement
# des blueprints.
#
# Structure des contrôleurs :
# - home.py : Page d'accueil et interactions IA
# - inscription.py : Gestion des données Excel (CRUD) et inscriptions
# - rapport_apprenant.py : Génération de rapports et analyses
# - planning.py : Gestion du planning hebdomadaire
#
# Chaque contrôleur utilise le pattern Blueprint de Flask pour organiser
# les routes de manière modulaire.