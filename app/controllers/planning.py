# app/controllers/planning.py
# Contrôleur pour la gestion du planning hebdomadaire des ateliers
# Ce fichier gère l'affichage et la manipulation du planning des activités

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from datetime import datetime, timedelta            # Pour la gestion des dates

# === CRÉATION DU BLUEPRINT ===
# Blueprint avec préfixe URL '/planning' pour toutes les routes de ce module
planning_bp = Blueprint('planning', __name__, url_prefix='/planning')

@planning_bp.route('/')
def index():
    """Page de gestion des classes récurrentes (page principale du planning)"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Charger la liste des apprenants pour les sélections
        apprenants = data_service.get_apprenants_list()
        
        return render_template('gestion/gestion_classes.html', 
                             apprenants=apprenants)
    
    except Exception as e:
        print(f"Erreur lors du chargement de la gestion des classes: {e}")
        return render_template('gestion/gestion_classes.html', 
                             apprenants=[], 
                             error="Erreur lors du chargement des données")

@planning_bp.route('/api/ateliers/<semaine>')
def api_ateliers_semaine(semaine):
    """
    API pour récupérer les ateliers d'une semaine donnée
    
    Cette route API retourne tous les ateliers programmés pour une semaine
    spécifique au format JSON. Utilisée par JavaScript pour l'affichage dynamique.
    
    Args:
        semaine (str): Date de début de semaine au format YYYY-MM-DD
        
    Returns:
        JSON: Liste des ateliers de la semaine ou message d'erreur
    """
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # === INITIALISATION DU SERVICE ===
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # === RÉCUPÉRATION DES ATELIERS ===
        # Charger tous les ateliers de la semaine spécifiée
        ateliers = data_service.get_ateliers_par_semaine(semaine)
        
        # === RÉPONSE JSON DE SUCCÈS ===
        return jsonify({
            'success': True,     # Indicateur de succès
            'ateliers': ateliers # Liste des ateliers
        })
    
    except Exception as e:
        # === RÉPONSE JSON D'ERREUR ===
        return jsonify({
            'success': False,    # Indicateur d'échec
            'error': str(e)      # Message d'erreur
        })

@planning_bp.route('/api/atelier', methods=['POST'])
def api_sauvegarder_atelier():
    """
    API pour sauvegarder un nouvel atelier ou modifier un atelier existant
    
    Cette route reçoit les données d'un atelier au format JSON et les
    sauvegarde dans le système. Elle peut créer un nouvel atelier ou
    modifier un atelier existant selon les données reçues.
    
    Returns:
        JSON: Confirmation de sauvegarde ou message d'erreur
    """
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # === RÉCUPÉRATION DES DONNÉES ===
        # Récupérer les données JSON envoyées par le client
        data = request.get_json()
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Validation des données requises
        champs_requis = ['jour', 'activite', 'heure_debut', 'heure_fin', 'encadrant', 'semaine']
        for champ in champs_requis:
            if not data.get(champ):
                return jsonify({
                    'success': False,
                    'error': f'Le champ {champ} est requis'
                })
        
        # Sauvegarder l'atelier
        if data.get('id'):
            # Modification d'un atelier existant
            result = data_service.modifier_atelier(data)
        else:
            # Création d'un nouvel atelier
            result = data_service.creer_atelier(data)
        
        return jsonify({
            'success': True,
            'atelier_id': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/atelier/<int:atelier_id>', methods=['DELETE'])
def api_supprimer_atelier(atelier_id):
    """API pour supprimer un atelier"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        data_service.supprimer_atelier(atelier_id)
        
        return jsonify({
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/horaires-defaut')
def api_horaires_defaut():
    """API pour récupérer les horaires par défaut"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utilisation de l'instance globale data_service
        horaires = data_service.get_horaires_planning_defaut()
        
        return jsonify({
            'success': True,
            'horaires': horaires
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'horaires': [
                '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
                '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
                '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00'
            ]
        })

@planning_bp.route('/api/horaires-defaut', methods=['POST'])
def api_modifier_horaires_defaut():
    """API pour modifier les horaires par défaut"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        data = request.get_json()
        # Utilisation de l'instance globale data_service
        
        horaires = data.get('horaires', [])
        if not horaires:
            return jsonify({
                'success': False,
                'error': 'Liste des horaires requise'
            })
        
        data_service.modifier_horaires_planning_defaut(horaires)
        
        return jsonify({
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/export/<semaine>')
def export_planning_semaine(semaine):
    """Exporter le planning d'une semaine en Excel"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utilisation de l'instance globale data_service
        
        # Créer le fichier Excel du planning
        fichier_path = data_service.exporter_planning_excel(semaine)
        
        return redirect(url_for('static', filename=f'exports/{fichier_path}'))
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/dupliquer/<semaine_source>/<semaine_cible>')
def dupliquer_planning(semaine_source, semaine_cible):
    """Dupliquer un planning d'une semaine vers une autre"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utilisation de l'instance globale data_service
        
        nombre_ateliers = data_service.dupliquer_planning_semaine(semaine_source, semaine_cible)
        
        return jsonify({
            'success': True,
            'message': f'{nombre_ateliers} ateliers dupliqués avec succès'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/pointage')
def pointage():
    """Page de pointage des présences"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utilisation de l'instance globale data_service
        
        # Charger la liste des apprenants pour les sélections
        apprenants = data_service.get_apprenants_list()
        
        # Charger les données des classes depuis classes.json
        classes = data_service.get_classes()
        
        return render_template('gestion/pointage.html', 
                             apprenants=apprenants,
                             classes=classes)
    
    except Exception as e:
        print(f"Erreur lors du chargement du pointage: {e}")
        return render_template('gestion/pointage.html', 
                             apprenants=[], 
                             classes=[],
                             error="Erreur lors du chargement des données")

@planning_bp.route('/api/sauvegarder-pointage-temporaire', methods=['POST'])
def api_sauvegarder_pointage_temporaire():
    """API pour sauvegarder temporairement les pointages en cours"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        import json
        import os
        from datetime import datetime
        
        data = request.get_json()
        
        date_jour = data.get('date')
        presences_data = data.get('presences', {})
        observations_data = data.get('observations', {})
        apprenants_temporaires_data = data.get('apprenants_temporaires', {})  # NOUVEAU
        
        if not date_jour:
            return jsonify({
                'success': False,
                'error': 'Date requise'
            })
        
        # Créer la structure des données temporaires
        donnees_temporaires = {
            'date': date_jour,
            'timestamp': datetime.now().isoformat(),
            'presences': presences_data,
            'observations': observations_data,
            'apprenants_temporaires': apprenants_temporaires_data  # NOUVEAU
        }
        
        # Chemin du fichier temporaire
        fichier_temporaire = os.path.join('data', 'pointage_pour_engistrer.json')
        
        # Sauvegarder dans le fichier JSON
        with open(fichier_temporaire, 'w', encoding='utf-8') as f:
            json.dump(donnees_temporaires, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Pointage sauvegardé temporairement'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/charger-pointage-temporaire/<date>')
def api_charger_pointage_temporaire(date):
    """API pour charger un pointage temporaire existant"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        import json
        import os
        
        fichier_temporaire = os.path.join('data', 'pointage_pour_engistrer.json')
        
        if not os.path.exists(fichier_temporaire):
            return jsonify({
                'success': True,
                'data': None,
                'message': 'Aucun pointage temporaire trouvé'
            })
        
        with open(fichier_temporaire, 'r', encoding='utf-8') as f:
            donnees_temporaires = json.load(f)
        
        # Vérifier si les données correspondent à la date demandée
        if donnees_temporaires.get('date') == date:
            return jsonify({
                'success': True,
                'data': donnees_temporaires,
                'message': 'Pointage temporaire chargé'
            })
        else:
            return jsonify({
                'success': True,
                'data': None,
                'message': 'Aucun pointage temporaire pour cette date'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/supprimer-pointage-temporaire/<date>', methods=['DELETE'])
def api_supprimer_pointage_temporaire(date):
    """API pour supprimer un pointage temporaire après validation définitive"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        import os
        
        fichier_temporaire = os.path.join('data', 'pointage_pour_engistrer.json')
        
        if os.path.exists(fichier_temporaire):
            os.remove(fichier_temporaire)
            return jsonify({
                'success': True,
                'message': 'Pointage temporaire supprimé'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Aucun pointage temporaire à supprimer'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/valider-presences', methods=['POST'])
def api_valider_presences():
    """API pour valider les présences d'une journée"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        data = request.get_json()
        
        # Utilisation de l'instance globale data_service
        
        date_jour = data.get('date')
        presences_data = data.get('presences', {})
        observations_data = data.get('observations', {})
        
        if not date_jour:
            return jsonify({
                'success': False,
                'error': 'Date requise'
            })
        
        # Sauvegarder les présences dans Excel avec les observations
        resultat = data_service.sauvegarder_presences_journee(date_jour, presences_data, observations_data)
        
        # Supprimer le fichier temporaire après validation réussie
        try:
            import os
            fichier_temporaire = os.path.join('data', 'pointage_pour_engistrer.json')
            if os.path.exists(fichier_temporaire):
                os.remove(fichier_temporaire)
        except:
            pass  # Ignorer les erreurs de suppression
        
        return jsonify({
            'success': True,
            'nombre_presences': resultat['nombre_presences'],
            'message': resultat['message'],
            'apprenants_ignores': resultat.get('apprenants_ignores', [])
        })
    
    except Exception as e:
        # Vérifier si c'est une erreur d'apprenant non trouvé
        error_msg = str(e)
        if "non trouvés dans les inscriptions" in error_msg:
            return jsonify({
                'success': False,
                'error': error_msg,
                'redirect_to_inscription': True
            })
        else:
            return jsonify({
                'success': False,
                'error': error_msg
            })

@planning_bp.route('/api/classes')
def api_classes():
    """API pour récupérer toutes les classes"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utilisation de l'instance globale data_service
        classes = data_service.get_classes()
        
        return jsonify({
            'success': True,
            'classes': classes
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/classe', methods=['POST'])
def api_sauvegarder_classe():
    """API pour sauvegarder une nouvelle classe ou modifier une existante"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        data = request.get_json()
        # Utilisation de l'instance globale data_service
        
        # Validation des données requises
        champs_requis = ['nom', 'activite', 'encadrant', 'jours', 'heure_debut', 'heure_fin']
        for champ in champs_requis:
            if not data.get(champ):
                return jsonify({
                    'success': False,
                    'error': f'Le champ {champ} est requis'
                })
        
        # Sauvegarder la classe
        if data.get('id') and data['id'] != 'undefined' and data['id'] != '':
            # Modification d'une classe existante
            # S'assurer que l'ID est un entier pour la comparaison
            try:
                data['id'] = int(data['id'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'ID de classe invalide'
                })
            result = data_service.modifier_classe(data)
        else:
            # Création d'une nouvelle classe
            result = data_service.creer_classe(data)
        
        return jsonify({
            'success': True,
            'classe_id': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/classe/<int:classe_id>', methods=['DELETE'])
def api_supprimer_classe(classe_id):
    """API pour supprimer une classe"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utilisation de l'instance globale data_service
        data_service.supprimer_classe(classe_id)
        
        return jsonify({
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Endpoint de génération automatique supprimé

@planning_bp.route('/api/rechercher-apprenants')
def api_rechercher_apprenants():
    """API pour rechercher des apprenants par nom, prénom ou numéro"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        query = request.args.get('q', '').strip()
        
        if len(query) < 2:
            return jsonify([])
        
        # Utilisation de l'instance globale data_service
        
        # Récupérer tous les apprenants
        apprenants = data_service.get_all_apprenants()
        
        # Filtrer par nom, prénom ou numéro (insensible à la casse)
        resultats_numero = []  # Résultats trouvés par numéro (priorité)
        resultats_nom = []     # Résultats trouvés par nom/prénom
        
        for apprenant in apprenants:
            nom_complet = apprenant['nom_complet'].lower()
            nom = apprenant['nom'].lower()
            prenom = apprenant['prenom'].lower()
            numero = str(apprenant['numero']).lower()
            
            apprenant_data = {
                'numero': apprenant['numero'],
                'nom': apprenant['nom'],
                'prenom': apprenant['prenom'],
                'nom_complet': apprenant['nom_complet']
            }
            
            # Recherche par numéro (priorité)
            if query.lower() in numero:
                resultats_numero.append(apprenant_data)
            # Recherche par nom/prénom (si pas déjà trouvé par numéro)
            elif (query.lower() in nom_complet or 
                  query.lower() in nom or 
                  query.lower() in prenom):
                resultats_nom.append(apprenant_data)
        
        # Combiner les résultats : numéros en premier, puis noms/prénoms
        resultats_numero = sorted(resultats_numero, key=lambda x: str(x['numero']))
        resultats_nom = sorted(resultats_nom, key=lambda x: x['nom_complet'])
        resultats = resultats_numero + resultats_nom
        
        # Limiter à 10 résultats
        return jsonify(resultats[:10])
        
    except Exception as e:
        return jsonify({'error': f'Erreur: {str(e)}'})

@planning_bp.route('/gestion-encadrants')
def gestion_encadrants():
    """Page de gestion des encadrants et leurs numéros"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utilisation de l'instance globale data_service
        
        return render_template('gestion/gestion_encadrants.html')
    
    except Exception as e:
        print(f"Erreur lors du chargement de la gestion des encadrants: {e}")
        return render_template('gestion/gestion_encadrants.html', 
                             error="Erreur lors du chargement des données")

@planning_bp.route('/api/encadrants')
def api_get_encadrants():
    """API pour récupérer tous les encadrants et leurs numéros"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utilisation de l'instance globale data_service
        encadrants = data_service.get_config_encadrants()
        
        return jsonify({
            'success': True,
            'encadrants': encadrants
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/encadrant', methods=['POST'])
def api_ajouter_encadrant():
    """API pour ajouter ou modifier un encadrant"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        data = request.get_json()
        # Utilisation de l'instance globale data_service
        
        nom_encadrant = data.get('nom_encadrant', '').strip()
        numero_encadrant = data.get('numero_encadrant', '').strip()
        
        if not nom_encadrant or not numero_encadrant:
            return jsonify({
                'success': False,
                'error': 'Nom et numéro d\'encadrant requis'
            })
        
        data_service.add_encadrant_mapping(nom_encadrant, numero_encadrant)
        
        return jsonify({
            'success': True,
            'message': f'Encadrant {nom_encadrant} ajouté/modifié avec succès'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/encadrant/<nom_encadrant>', methods=['DELETE'])
def api_supprimer_encadrant(nom_encadrant):
    """API pour supprimer un encadrant"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Utilisation de l'instance globale data_service
        
        if data_service.remove_encadrant_mapping(nom_encadrant):
            return jsonify({
                'success': True,
                'message': f'Encadrant {nom_encadrant} supprimé avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Encadrant non trouvé'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/ajouter-apprenant-classe', methods=['POST'])
def api_ajouter_apprenant_classe():
    """API pour ajouter un apprenant à une classe"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        data = request.get_json()
        # Utilisation de l'instance globale data_service
        
        classe_id = data.get('classe_id')
        numero_apprenant = data.get('numero_apprenant')
        
        if not classe_id or not numero_apprenant:
            return jsonify({
                'success': False,
                'error': 'ID de classe et numéro d\'apprenant requis'
            })
        
        # Ajouter l'apprenant à la classe
        resultat = data_service.ajouter_apprenant_a_classe(classe_id, numero_apprenant)
        
        if resultat:
            return jsonify({
                'success': True,
                'message': 'Apprenant ajouté avec succès à la classe'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'ajout de l\'apprenant'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/retirer-apprenant-classe', methods=['POST'])
def api_retirer_apprenant_classe():
    """API pour retirer un apprenant d'une classe"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        data = request.get_json()
        # Utilisation de l'instance globale data_service
        
        classe_id = data.get('classe_id')
        numero_apprenant = data.get('numero_apprenant')
        
        if not classe_id or not numero_apprenant:
            return jsonify({
                'success': False,
                'error': 'ID de classe et numéro d\'apprenant requis'
            })
        
        # Retirer l'apprenant de la classe
        resultat = data_service.retirer_apprenant_de_classe(classe_id, numero_apprenant)
        
        if resultat:
            return jsonify({
                'success': True,
                'message': 'Apprenant retiré avec succès de la classe'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erreur lors du retrait de l\'apprenant'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@planning_bp.route('/api/classe/<int:classe_id>/apprenants')
def api_get_apprenants_classe(classe_id):
    """API pour récupérer les apprenants assignés à une classe spécifique"""
    try:
        # Utiliser l'instance unique depuis l'application Flask
        data_service = current_app.data_service
        
        # Récupérer la classe spécifique
        classes = data_service.get_classes()
        classe_trouvee = None
        
        for classe in classes:
            if classe['id'] == classe_id:
                classe_trouvee = classe
                break
        
        if not classe_trouvee:
            return jsonify({
                'success': False,
                'error': 'Classe non trouvée'
            })
        
        # Récupérer les numéros des apprenants assignés
        numeros_apprenants = classe_trouvee.get('apprenants', [])
        
        # Récupérer les détails complets des apprenants assignés
        tous_apprenants = data_service.get_all_apprenants()
        apprenants_assignes = []
        
        for numero in numeros_apprenants:
            apprenant = next((a for a in tous_apprenants if a['numero'] == numero), None)
            if apprenant:
                apprenants_assignes.append({
                    'numero': apprenant['numero'],
                    'nom': apprenant['nom'],
                    'prenom': apprenant['prenom'],
                    'nom_complet': apprenant['nom_complet']
                })
        
        return jsonify({
            'success': True,
            'apprenants': apprenants_assignes,
            'nombre_apprenants': len(apprenants_assignes)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
