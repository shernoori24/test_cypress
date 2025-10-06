# app/controllers/inscription.py
# Contrôleur pour la gestion des inscriptions d'apprenants
# Ce fichier gère toutes les routes liées à la manipulation des données d'inscription

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services.inscription_service import InscriptionService    # Service pour gérer les inscriptions
# from app.services.presence_service import PresenceService          # Service pour gérer les présences
from app.utils.error_handler import handle_errors                  # Décorateur pour gérer les erreurs
from datetime import datetime                                       # Pour gérer les dates

# === CRÉATION DU BLUEPRINT ===
# Blueprint pour organiser toutes les routes liées aux inscriptions
inscription_bp = Blueprint('inscription', __name__)

@inscription_bp.route('/inscriptions/inserer', methods=['GET', 'POST'])
@handle_errors(error_type="form", redirect_to="inscription.inserer_inscription")
def inserer_inscription():
    """
    Route pour insérer une nouvelle inscription d'apprenant
    
    Cette route gère un formulaire permettant d'ajouter un nouvel apprenant
    dans le système avec toutes ses informations personnelles et administratives.
    
    Methods:
        GET: Affiche le formulaire d'inscription
        POST: Traite les données soumises et ajoute l'inscription
        
    Returns:
        str: Template HTML ou redirection selon le cas
    """
    # Créer une instance du service d'inscription
    inscription_service = InscriptionService()
    
    # Si c'est une requête POST (formulaire soumis)
    if request.method == 'POST':
        # === RÉCUPÉRATION DES DONNÉES DU FORMULAIRE ===
        # Créer un dictionnaire avec toutes les données de l'apprenant
        new_inscription = {
            # Numéro d'apprenant (manuel)
            'numero_apprenant': request.form.get('numero_apprenant'),        # Numéro saisi manuellement
            
            # Informations personnelles de base
            'nom': request.form.get('nom'),                                 # Nom de famille
            'prenom': request.form.get('prenom'),                           # Prénom
            # 'nom_complete' sera généré automatiquement dans le service
            'sexe': request.form.get('sexe'),                               # Sexe (M/F)
            'date_naissance': request.form.get('date_naissance'),           # Date de naissance
            
            # Informations de nationalité et origine
            'pays_naissance': request.form.get('pays_naissance'),           # Pays de naissance
            'nationalite': request.form.get('nationalite'),                 # Nationalité
            'continent': request.form.get('continent'),                     # Continent d'origine
            'iso': request.form.get('iso'),                                 # Code ISO pays (3 lettres)
            'arrivee_france': request.form.get('arrivee_france'),           # Date d'arrivée en France
            
            # Informations administratives
            'document': request.form.get('document'),                       # Type de document d'identité
            'statut_entree': request.form.get('statut_entree'),             # Statut à l'entrée en France
            'statut_actuel': request.form.get('statut_actuel'),             # Statut actuel
            
            # Informations de contact et logement
            'adresse': request.form.get('adresse'),                         # Adresse postale
            'code_postal': request.form.get('code_postal'),                 # Code postal
            'ville': request.form.get('ville'),                             # Ville
            'prioritaire_veille': request.form.get('prioritaire_veille'),   # Prioritaire pour la veille
            'type_logement': request.form.get('type_logement'),             # Type de logement
            'telephone': request.form.get('telephone'),                     # Numéro de téléphone
            'email': request.form.get('email'),                             # Adresse email
            
            # Informations sociales et familiales
            'situation_familiale': request.form.get('situation_familiale'), # Situation familiale
            'revenus': request.form.get('revenus'),                         # Situation financière
            'langues_parlees': request.form.get('langues_parlees'),         # Langues parlées
            
            # Informations de suivi
            'prescripteur': request.form.get('prescripteur'),               # Qui a orienté la personne
            'structure_actuelle': request.form.get('structure_actuelle'),   # Structure actuelle de suivi
            'date_inscription': request.form.get('date_inscription'),       # Date d'inscription
            'premiere_venue': request.form.get('premiere_venue'),           # Date de première venue
            'commentaires': request.form.get('commentaires')                # Commentaires libres
        }

        # === TRAITEMENT DE LA NOUVELLE INSCRIPTION ===
        # Appeler le service pour ajouter l'inscription dans le fichier Excel (mode simple)
        success, message = inscription_service.add_inscription_simple(new_inscription)
        
        if success:
            # Succès : afficher un message de confirmation et rediriger
            flash(message, 'success')  # Message vert de succès
            
            # Récupérer les paramètres de retour et de l'apprenant temporaire
            # CORRECTION : Lire depuis form (POST) au lieu de args (GET)
            retour = request.form.get('retour', '')
            classe_id = request.form.get('classe_id', '')
            temp_id = request.form.get('temp_id', '')
            
            # NOUVEAU : Gérer la redirection selon le paramètre retour
            if retour == 'pointage':
                return redirect('/planning/pointage')
            else:
                return redirect(url_for('inscription.inserer_inscription'))
        else:
            # Échec : afficher un message d'erreur MAIS conserver les données saisies
            flash(message, 'danger')   # Message rouge d'erreur
            # Renvoyer le formulaire avec les données pré-remplies
            return render_template('inscription/inserer_une_inscription.html', 
                                 today=datetime.now().strftime('%Y-%m-%d'),
                                 form_data=new_inscription)  # Données à conserver
    
    # === AFFICHAGE DU FORMULAIRE ===
    # Si GET ou si erreur lors du POST, afficher le formulaire avec la date du jour
    # NOUVEAU : Récupérer les paramètres GET pour pré-remplir le formulaire
    prenom_prefill = request.args.get('prenom', '')
    nom_prefill = request.args.get('nom', '')
    
    # Créer un objet de données pré-remplies si des paramètres sont fournis
    prefill_data = None
    if prenom_prefill or nom_prefill:
        prefill_data = {
            'prenom': prenom_prefill,
            'nom': nom_prefill
        }
    
    return render_template('inscription/inserer_une_inscription.html', 
                         today=datetime.now().strftime('%Y-%m-%d'),
                         form_data=prefill_data)

@inscription_bp.route('/inscriptions')
@handle_errors(error_type="form", redirect_to="home.home")
def voir_inscriptions():
    """
    Page de visualisation et filtrage des inscriptions d'apprenants
    
    Cette route affiche une liste de toutes les inscriptions avec possibilité
    de filtrer par différents critères (nom, sexe, ville, prioritaire).
    Elle affiche également des statistiques générales.
    
    URL Parameters:
        search (str): Terme de recherche pour nom/prénom
        sexe (str): Filtre par sexe (M/F)
        ville (str): Filtre par ville
        prioritaire (str): Filtre par statut prioritaire
        reload (str): Forcer le rechargement des données ('true' pour forcer)
        
    Returns:
        str: Template HTML avec la liste des inscriptions et les statistiques
    """
    # Créer une instance du service d'inscription
    inscription_service = InscriptionService()
    
    # === VÉRIFIER SI LE RECHARGEMENT DES DONNÉES EST FORCÉ ===
    # Permet de forcer le rechargement des données à chaque chargement de page
    force_reload = request.args.get('reload', '').lower() == 'true'
    if force_reload:
        # Forcer le rechargement des données depuis les fichiers Excel
        inscription_service.reload_data()
    
    # === RÉCUPÉRATION DES PARAMÈTRES DE FILTRE ===
    # Récupérer les paramètres de filtrage depuis l'URL (GET parameters)
    search = request.args.get('search', '')          # Terme de recherche (nom/prénom)
    sexe = request.args.get('sexe', '')              # Filtre par sexe
    ville = request.args.get('ville', '')            # Filtre par ville
    prioritaire = request.args.get('prioritaire', '') # Filtre par statut prioritaire
    pays_naissance = request.args.get('pays_naissance', '') # Filtre par pays de naissance
    prescripteur = request.args.get('prescripteur', '') # Filtre par prescripteur
    structure_actuelle = request.args.get('structure_actuelle', '') # Filtre par structure actuelle
    mois_anniversaire = request.args.get('mois_anniversaire', '') # Filtre par mois d'anniversaire
    annee_min = request.args.get('annee_min', '')    # Année de naissance minimum
    annee_max = request.args.get('annee_max', '')    # Année de naissance maximum
    date_debut = request.args.get('date_debut', '')  # Date de début d'inscription
    date_fin = request.args.get('date_fin', '')      # Date de fin d'inscription
    
    # === CHARGEMENT DES DONNÉES FILTRÉES ===
    # Appeler le service pour récupérer les inscriptions selon les filtres
    inscriptions = inscription_service.get_filtered_inscriptions(search, sexe, ville, prioritaire, pays_naissance, date_debut, date_fin, prescripteur, structure_actuelle, mois_anniversaire, annee_min, annee_max)
    
    # === CALCUL DES STATISTIQUES ===
    # Récupérer les statistiques générales des inscriptions
    stats = inscription_service.get_inscription_statistics()
    
    # === DONNÉES POUR LES FILTRES ===
    # Récupérer la liste unique des villes pour le menu déroulant de filtre
    villes = inscription_service.get_unique_cities()
    # Récupérer la liste unique des pays de naissance pour le menu déroulant de filtre
    pays = inscription_service.get_unique_countries()
    # Récupérer la liste unique des prescripteurs pour le menu déroulant de filtre
    prescripteurs = inscription_service.get_unique_prescripteurs()
    # Récupérer la liste unique des structures actuelles pour le menu déroulant de filtre
    structures = inscription_service.get_unique_structures()
    # Récupérer la plage d'années de naissance pour les champs min/max
    birth_years_range = inscription_service.get_birth_years_range()
    
    # === RENDU DU TEMPLATE ===
    # Passer toutes les données nécessaires au template HTML
    return render_template('inscription/inscriptions.html',
                         inscriptions=inscriptions,              # Liste des inscriptions filtrées
                         total_inscriptions=stats['total'],      # Nombre total d'inscriptions
                         inscriptions_mois=stats['mois'],        # Inscriptions ce mois
                         inscriptions_jour=stats.get('jour', 0), # Inscriptions aujourd'hui
                         inscriptions_semaine=stats['semaine'],  # Inscriptions cette semaine
                         prioritaires=stats['prioritaires'],     # Nombre de cas prioritaires
                         villes=villes,                          # Liste des villes pour le filtre
                         pays=pays,                              # Liste des pays pour le filtre
                         prescripteurs=prescripteurs,            # Liste des prescripteurs pour le filtre
                         structures=structures,                  # Liste des structures pour le filtre
                         birth_years_range=birth_years_range,   # Plage d'années de naissance
                         force_reload=force_reload)              # Indicateur de rechargement forcé

@inscription_bp.route('/inscriptions/details/<numero>')
@handle_errors(error_type="api")
def inscription_details(numero):
    """
    Route API pour retourner les détails d'une inscription spécifique
    
    Cette route est utilisée pour récupérer les informations complètes
    d'un apprenant en utilisant son numéro d'inscription. Elle retourne
    les données au format JSON pour être utilisées par JavaScript.
    
    Args:
        numero (str): Numéro d'identification de l'apprenant
        
    Returns:
        JSON: Données complètes de l'inscription ou message d'erreur
    """
    # Créer une instance du service d'inscription
    inscription_service = InscriptionService()
    
    # Récupérer les détails de l'inscription
    details = inscription_service.get_inscription_details(numero)
    
    if details:
        # Inscription trouvée : retourner les données en JSON avec succès
        return jsonify({
            'success': True,
            'inscription': details
        })
    else:
        # Inscription non trouvée : retourner une erreur
        return jsonify({
            'success': False,
            'message': 'Inscription non trouvée'
        }), 404



@inscription_bp.route('/inscriptions/api/statistics')
@handle_errors(error_type="api")
def api_statistics():
    """API pour récupérer les statistiques en JSON"""
    inscription_service = InscriptionService()
    stats = inscription_service.get_inscription_statistics()
    return jsonify(stats)

@inscription_bp.route('/inscriptions/api/next-numero')
@handle_errors(error_type="api")
def api_next_numero():
    """
    API pour récupérer le prochain numéro d'inscription disponible
    
    Cette route génère automatiquement le prochain numéro d'inscription
    basé sur la dernière entrée dans le fichier Excel.
    
    Returns:
        JSON: Le prochain numéro d'inscription au format {"numero": "25-186"}
    """
    inscription_service = InscriptionService()
    next_numero = inscription_service.generate_next_numero()
    return jsonify({
        'success': True,
        'numero': next_numero
    })
