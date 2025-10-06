# app/services/__init__.py
# Ce fichier d'initialisation du module services
# Il peut être utilisé pour importer et exposer les services principaux

"""
Module Services - Couche de logique métier de l'application

Ce module contient tous les services qui implémentent la logique métier
de l'application d'analyse de données. Les services font le lien
entre les contrôleurs (qui gèrent les requêtes HTTP) et les modèles (qui
gèrent les données).

Architecture des services :
- BaseService : Classe de base abstraite pour tous les services
- DataService : Service principal pour les opérations de données générales
- InscriptionService : Service spécialisé pour la gestion des inscriptions
- PresenceService : Service spécialisé pour la gestion des présences

Pattern utilisé : Service Layer Pattern
- Sépare la logique métier des contrôleurs
- Réutilisable par différents contrôleurs
- Facilite les tests unitaires
- Centralise les règles de gestion
"""