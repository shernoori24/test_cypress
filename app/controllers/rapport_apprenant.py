# app/controllers/rapport_apprenant.py
# Contrôleur pour la génération du rapport d'activité des apprenants
# Ce fichier gère les routes liées au rapport d'activité individuel des apprenants

from flask import Blueprint, render_template, jsonify, request, current_app
import pandas as pd                                   # Pour la manipulation des données
from datetime import datetime

# === CRÉATION DU BLUEPRINT ===
# Blueprint pour organiser toutes les routes liées aux rapports d'activité
report_bp = Blueprint('report', __name__)

def clean_for_json(obj):
    """
    Fonction utilitaire pour nettoyer les objets pandas en vue de la sérialisation JSON
    
    Les objets pandas (Timestamp, NaN, etc.) ne sont pas directement sérialisables
    en JSON. Cette fonction les convertit en types Python standards.
    
    Args:
        obj: Objet à nettoyer (peut être dict, list, pandas object, etc.)
        
    Returns:
        obj: Objet nettoyé et sérialisable en JSON
    """
    if isinstance(obj, dict):
        # Si c'est un dictionnaire, nettoyer récursivement toutes les valeurs
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Si c'est une liste, nettoyer récursivement tous les éléments
        return [clean_for_json(item) for item in obj]
    elif pd.isna(obj):
        # Les valeurs NaN de pandas deviennent None (null en JSON)
        return None
    elif isinstance(obj, (pd.Timestamp, pd.DatetimeTZDtype)):
        # Les dates pandas deviennent des chaînes de caractères
        return str(obj)
    elif isinstance(obj, (int, float)) and pd.isna(obj):
        # Les nombres NaN deviennent 0
        return 0
    else:
        # Autres types : retourner tel quel
        return obj

@report_bp.route('/rapport_activite_apprenant')
@report_bp.route('/rapport_activite_apprenant/<string:numero_apprenant>')
def rapport_activite_apprenant(numero_apprenant: str | None = None):
    """Route pour le rapport d'activité d'un apprenant.

    - Sans paramètre: affiche la page vide avec la recherche.
    - Avec `<numero_apprenant>`: la page se préremplit et auto-charge cet apprenant.
    """
    data_service = current_app.data_service
    # Forcer le rechargement des données à chaque accès à la page
    data_service.force_data_reload()
    apprenants = data_service.get_all_apprenants()
    return render_template(
        'rapport_activite_apprenant.html',
        apprenants=apprenants,
        numero_apprenant_initial=numero_apprenant or ''
    )

@report_bp.route('/api/apprenant_details/<string:numero_apprenant>')
def api_apprenant_details(numero_apprenant):
    """API pour récupérer les détails d'un apprenant avec validation des données et filtrage par dates"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Récupérer les paramètres de filtrage par dates
        date_debut = request.args.get('date_debut')  # Format: YYYY-MM-DD
        date_fin = request.args.get('date_fin')      # Format: YYYY-MM-DD
        
        # Valider les dates si elles sont fournies
        dates_filter = None
        if date_debut or date_fin:
            try:
                dates_filter = {}
                if date_debut:
                    dates_filter['debut'] = pd.to_datetime(date_debut).date()
                if date_fin:
                    dates_filter['fin'] = pd.to_datetime(date_fin).date()
            except ValueError as e:
                return jsonify({
                    'error': f'Format de date invalide: {str(e)}',
                    'message': 'Les dates doivent être au format YYYY-MM-DD',
                    'message_type': 'error'
                }), 400
        
        # Récupérer les détails avec filtrage
        details = data_service.get_apprenant_complete_info(numero_apprenant, dates_filter)
        if details is None:
            return jsonify({'error': 'Apprenant non trouvé'}), 404
        
        # Si l'apprenant existe mais a une erreur de validation
        if 'error' in details:
            return jsonify(details), 404
        
        # Nettoyer les données pour JSON
        details_clean = clean_for_json(details)
        return jsonify(details_clean)
    except Exception as e:
        print(f"Erreur dans api_apprenant_details: {e}")
        return jsonify({
            'error': f'Erreur serveur: {str(e)}',
            'message': 'Une erreur est survenue lors du chargement des données',
            'message_type': 'error'
        }), 500

@report_bp.route('/api/apprenant_presence_chart/<string:numero_apprenant>')
def api_apprenant_presence_chart(numero_apprenant):
    """API pour récupérer les données de présence pour Chart.js avec gestion des cas sans données et filtrage par dates"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Récupérer les paramètres de filtrage par dates
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        # Préparer le filtre de dates
        dates_filter = None
        if date_debut or date_fin:
            try:
                dates_filter = {}
                if date_debut:
                    dates_filter['debut'] = pd.to_datetime(date_debut).date()
                if date_fin:
                    dates_filter['fin'] = pd.to_datetime(date_fin).date()
            except ValueError:
                pass  # Ignorer les erreurs de format de date
        
        chart_data = data_service.get_apprenant_presence_chart_data(numero_apprenant, dates_filter)
        return jsonify(chart_data)
    except Exception as e:
        print(f"Erreur dans api_apprenant_presence_chart: {e}")
        return jsonify({
            'error': f'Erreur serveur: {str(e)}', 
            'labels': [], 
            'data': [], 
            'total': 0, 
            'jours_uniques': 0,
            'message': 'Erreur lors du chargement des données de présence',
            'status': 'error'
        }), 500

@report_bp.route('/api/apprenant_presence_jours/<string:numero_apprenant>')
def api_apprenant_presence_jours(numero_apprenant):
    """API pour récupérer les données de présence par jour de la semaine avec gestion des messages et filtrage par dates"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Récupérer les paramètres de filtrage par dates
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        # Préparer le filtre de dates
        dates_filter = None
        if date_debut or date_fin:
            try:
                dates_filter = {}
                if date_debut:
                    dates_filter['debut'] = pd.to_datetime(date_debut).date()
                if date_fin:
                    dates_filter['fin'] = pd.to_datetime(date_fin).date()
            except ValueError:
                pass  # Ignorer les erreurs de format de date
        
        presence_data = data_service.get_presence_par_jour_semaine(numero_apprenant, dates_filter)
        
        # Vérifier le statut de la réponse
        if 'status' in presence_data and presence_data['status'] != 'success':
            # Retourner des données vides avec le message d'erreur
            return jsonify({
                'labels': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'],
                'data': [0, 0, 0, 0, 0, 0, 0],
                'total': 0,
                'message': presence_data.get('message', 'Aucune donnée disponible'),
                'status': presence_data.get('status', 'error')
            })
        
        # Préparer les données pour Chart.js avec ordre des jours
        jours_ordre = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        data_ordered = []
        
        for jour in jours_ordre:
            data_ordered.append(presence_data.get(jour, 0))
        
        return jsonify({
            'labels': jours_ordre,
            'data': data_ordered,
            'total': sum(data_ordered),
            'message': presence_data.get('message', f'Répartition sur {sum(data_ordered)} présences'),
            'status': 'success'
        })
    except Exception as e:
        print(f"Erreur dans api_apprenant_presence_jours: {e}")
        return jsonify({
            'error': f'Erreur serveur: {str(e)}', 
            'labels': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], 
            'data': [0, 0, 0, 0, 0, 0, 0],
            'total': 0,
            'message': 'Erreur lors du chargement des données',
            'status': 'error'
        }), 500

@report_bp.route('/api/apprenant_evolution_periode/<string:numero_apprenant>')
def api_apprenant_evolution_periode(numero_apprenant):
    """API pour récupérer l'évolution de la présence sur toute la période avec filtrage par dates"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Récupérer les paramètres de filtrage par dates
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        # Préparer le filtre de dates
        dates_filter = None
        if date_debut or date_fin:
            try:
                dates_filter = {}
                if date_debut:
                    dates_filter['debut'] = pd.to_datetime(date_debut).date()
                if date_fin:
                    dates_filter['fin'] = pd.to_datetime(date_fin).date()
            except ValueError:
                pass  # Ignorer les erreurs de format de date
        
        evolution_data = data_service.get_evolution_presence_periode(numero_apprenant, dates_filter)
        return jsonify(evolution_data)
    except Exception as e:
        print(f"Erreur dans api_apprenant_evolution_periode: {e}")
        return jsonify({'error': f'Erreur serveur: {str(e)}', 'labels': [], 'data': [], 'moyenne_mobile': []}), 500

@report_bp.route('/api/data_quality')
def api_data_quality():
    """API pour récupérer les informations sur la qualité des données"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        quality_info = data_service.get_data_quality_info()
        return jsonify(quality_info)
    except Exception as e:
        print(f"Erreur dans api_data_quality: {e}")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@report_bp.route('/api/reload_data', methods=['POST'])
def api_reload_data():
    """API pour forcer le rechargement des données"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        quality_info = data_service.force_data_reload()
        return jsonify({
            'message': 'Données rechargées avec succès',
            'quality': quality_info
        })
    except Exception as e:
        print(f"Erreur dans api_reload_data: {e}")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
