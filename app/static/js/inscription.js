// app/static/js/inscription.js

// Fonction pour voir les détails d'une inscription
function voirDetails(numeroApprenant, event) {
    // Empêcher la propagation de l'événement si appelé depuis un bouton
    if (event) {
        event.stopPropagation();
    }
    
    if (!numeroApprenant) {
        alert('Numéro d\'apprenant non valide');
        return;
    }
    
    // Rediriger vers la page de détails (à créer si nécessaire)
    // Pour l'instant, on affiche une popup avec les informations
    showInscriptionModal(numeroApprenant);
}

// Fonction pour afficher une modal avec les détails
function showInscriptionModal(numeroApprenant) {
    // Créer la modal
    const modalHtml = `
        <div class="modal fade" id="detailsModal" tabindex="-1" aria-labelledby="detailsModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="detailsModalLabel">
                            <i class="fas fa-user"></i> Détails de l'inscription N° ${numeroApprenant}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" id="modalContent">
                        <div class="text-center">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Chargement...</span>
                            </div>
                            <p>Chargement des détails...</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Supprimer l'ancienne modal si elle existe
    const existingModal = document.getElementById('detailsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Ajouter la nouvelle modal au DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Afficher la modal
    const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
    modal.show();
    
    // Charger les détails via AJAX
    loadInscriptionDetails(numeroApprenant);
}

// Fonction pour charger les détails via AJAX
function loadInscriptionDetails(numeroApprenant) {
    fetch(`/inscriptions/details/${numeroApprenant}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors du chargement des détails');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                displayInscriptionDetails(data.inscription);
            } else {
                throw new Error(data.message || 'Erreur inconnue');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            document.getElementById('modalContent').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Erreur lors du chargement des détails: ${error.message}
                </div>
            `;
        });
}

// Fonction pour afficher les détails dans la modal
function displayInscriptionDetails(inscription) {
    const modalContent = document.getElementById('modalContent');
    
    // Générer la vignette photo avec fallback jpg/jpeg/default
    const numero = inscription['N°'] || '';
    const nom = inscription['NOM'] || '';
    const prenom = inscription['Prénom'] || '';
    const photoUrl = `/photos_profils_apprenants/${numero}.jpg`;
    const photoUrlJpeg = `/photos_profils_apprenants/${numero}.jpeg`;
    const defaultUrl = '/photos_profils_apprenants/defaut_profil.jpg';
    const vignetteHtml = `
        <div class="d-flex align-items-center mb-3">
            <img src="${photoUrl}" alt="Photo ${numero}" class="rounded-circle me-3" style="width:60px;height:60px;object-fit:cover;border:2px solid #dee2e6;"
                onerror="this.onerror=null;this.src='${photoUrlJpeg}';this.onerror=function(){this.src='${defaultUrl}';}">
            <div>
                <div class="fw-bold text-primary" style="font-size:1.2rem;">${numero}</div>
                <div>${nom} ${prenom}</div>
            </div>
        </div>
    `;
    const detailsHtml = `
        ${vignetteHtml}
        <div class="mb-3 text-end">
            <a href="/rapport_activite_apprenant/${numero}" target="_blank" class="btn btn-outline-primary">
                <i class="fas fa-file-alt"></i> Voir le rapport d'activité
            </a>
        </div>
        <div class="row">
            <div class="col-md-6">
                <h6><i class="fas fa-id-card"></i> Informations personnelles</h6>
                <table class="table table-sm">
                    <tr><td><strong>N°:</strong></td><td>${numero || '-'}</td></tr>
                    <tr><td><strong>Nom:</strong></td><td>${nom || '-'}</td></tr>
                    <tr><td><strong>Prénom:</strong></td><td>${prenom || '-'}</td></tr>
                    <tr><td><strong>Sexe:</strong></td><td>${inscription['Sexe'] || '-'}</td></tr>
                    <tr><td><strong>Date de naissance:</strong></td><td>${inscription['Date de naissance'] || '-'}</td></tr>
                    <tr><td><strong>Âge:</strong></td><td>${inscription['Age'] || '-'}</td></tr>
                    <tr><td><strong>Pays de naissance:</strong></td><td>${inscription['Pays de naissance'] || '-'}</td></tr>
                    <tr><td><strong>Nationalité:</strong></td><td>${inscription['Nationalité'] || '-'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6><i class="fas fa-map-marker-alt"></i> Adresse et contact</h6>
                <table class="table table-sm">
                    <tr><td><strong>Adresse:</strong></td><td>${inscription['Adresse'] || '-'}</td></tr>
                    <tr><td><strong>Code postal:</strong></td><td>${inscription['Code postal'] || '-'}</td></tr>
                    <tr><td><strong>Ville:</strong></td><td>${inscription['Ville'] || '-'}</td></tr>
                    <tr><td><strong>Téléphone:</strong></td><td>${inscription['Téléphone'] ? `<a href="tel:${inscription['Téléphone']}">${inscription['Téléphone']}</a>` : '-'}</td></tr>
                    <tr><td><strong>Email:</strong></td><td>${inscription['Email'] ? `<a href="mailto:${inscription['Email']}">${inscription['Email']}</a>` : '-'}</td></tr>
                </table>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-md-6">
                <h6><i class="fas fa-file-alt"></i> Statut et documents</h6>
                <table class="table table-sm">
                    <tr><td><strong>Document:</strong></td><td>${inscription['Document'] || '-'}</td></tr>
                    <tr><td><strong>Statut à l'entrée:</strong></td><td>${inscription["Statut à l'entrée"] || '-'}</td></tr>
                    <tr><td><strong>Statut actuel:</strong></td><td>${inscription['Statut actuel'] || '-'}</td></tr>
                    <tr><td><strong>Prioritaire/Veille:</strong></td><td>${inscription['Prioritaire/Veille'] || '-'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6><i class="fas fa-calendar"></i> Dates importantes</h6>
                <table class="table table-sm">
                    <tr><td><strong>Arrivée en France:</strong></td><td>${inscription['Arrivée en France'] || '-'}</td></tr>
                    <tr><td><strong>Date inscription:</strong></td><td>${inscription['Date inscription'] || '-'}</td></tr>
                    <tr><td><strong>Première venue:</strong></td><td>${inscription['Première venue'] || '-'}</td></tr>
                </table>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12">
                <h6><i class="fas fa-info-circle"></i> Informations complémentaires</h6>
                <table class="table table-sm">
                    <tr><td><strong>Situation familiale:</strong></td><td>${inscription['Situation Familiale'] || '-'}</td></tr>
                    <tr><td><strong>Type de logement:</strong></td><td>${inscription['Type de logement'] || '-'}</td></tr>
                    <tr><td><strong>Revenus:</strong></td><td>${inscription['Revenus'] || '-'}</td></tr>
                    <tr><td><strong>Langues parlées:</strong></td><td>${inscription['Langues Parlées'] || '-'}</td></tr>
                    <tr><td><strong>Prescripteur:</strong></td><td>${inscription['Prescripteur'] || '-'}</td></tr>
                    <tr><td><strong>Structure actuelle:</strong></td><td>${inscription['Structure actuelle'] || '-'}</td></tr>
                </table>
            </div>
        </div>
        
        ${inscription['Commentaires'] ? `
        <div class="row mt-3">
            <div class="col-12">
                <h6><i class="fas fa-comment"></i> Commentaires</h6>
                <div class="alert alert-info">
                    ${inscription['Commentaires']}
                </div>
            </div>
        </div>
        ` : ''}
    `;
    
    modalContent.innerHTML = detailsHtml;
}

// Fonction pour filtrer les inscriptions en temps réel
// Fonction pour filtrer les inscriptions (formulaire unifié)
function filterInscriptions() {
    const form = document.getElementById('filterForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const searchParams = new URLSearchParams();
    
    for (let [key, value] of formData.entries()) {
        if (value.trim()) {
            searchParams.append(key, value);
        }
    }
    
    // Recharger la page avec les nouveaux paramètres
    window.location.search = searchParams.toString();
}

// Fonction pour filtrer par dates (maintenant inutile car tout est dans le même formulaire)
function filterByDates() {
    filterInscriptions();
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Gérer uniquement la soumission du formulaire via le bouton "Filtrer"
    const mainForm = document.getElementById('filterForm');
    if (mainForm) {
        mainForm.addEventListener('submit', function(e) {
            e.preventDefault();
            filterInscriptions();
        });
    }
});
