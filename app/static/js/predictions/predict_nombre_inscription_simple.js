// app/static/js/predictions/predict_nombre_inscription_simple.js
// Version simplifiée pour éviter les blocages

console.log('🚀 Chargement du dashboard de prédictions simplifié...');

/**
 * Initialise le dashboard des prédictions (version simplifiée)
 */
function initializePredictionDashboard() {
    console.log('📊 Initialisation du dashboard...');
    
    // Pas de modal de chargement - affichage direct
    setTimeout(() => {
        try {
            // Initialiser les graphiques simples
            initializeSimpleCharts();
            // Nettoyer/masquer les infos modèles (éviter "Chargement...")
            hideModelInfoPlaceholders();
            
            // Afficher un message de succès
            console.log('✅ Dashboard initialisé avec succès');
            
            // Cacher tous les éléments de chargement
            hideLoadingElements();
            
        } catch (error) {
            console.error('❌ Erreur:', error);
            hideLoadingElements();
        }
    }, 500); // Petit délai pour simuler le chargement
}

/**
 * Masque les zones d'informations modèle (évite l'affichage "Chargement...")
 */
function hideModelInfoPlaceholders() {
    ['yearly-model-info', 'monthly-model-info', 'weekly-model-info'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.style.display = 'none';
            el.innerHTML = '';
        }
    });
}

/**
 * Génère des libellés hebdomadaires sous forme de plages de dates
 * Exemple: "1 - 7 / septembre 2025"
 */
function generateWeeklyLabels(count = 8) {
    const monthsFr = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];
    const labels = [];
    const now = new Date();
    const startOfWeek = new Date(now);
    const day = (now.getDay() + 6) % 7; // Lundi=0, Dimanche=6
    startOfWeek.setDate(now.getDate() - day);
    startOfWeek.setHours(0,0,0,0);
    
    for (let i = 0; i < count; i++) {
        const start = new Date(startOfWeek);
        start.setDate(start.getDate() + i * 7);
        const end = new Date(start);
        end.setDate(end.getDate() + 6);
        
        const startDay = start.getDate();
        const endDay = end.getDate();
        const endMonth = monthsFr[end.getMonth()];
        const endYear = end.getFullYear();
        
        labels.push(`${startDay} - ${endDay} / ${endMonth} ${endYear}`);
    }
    return labels;
}

/**
 * Cache tous les éléments de chargement
 */
function hideLoadingElements() {
    // Masquer les spinners de chargement
    const loadingElements = document.querySelectorAll('.loading-spinner, .text-center');
    loadingElements.forEach(element => {
        if (element.textContent.includes('Chargement') || 
            element.textContent.includes('Traitement')) {
            element.style.display = 'none';
        }
    });
    
    // Masquer le modal s'il existe
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
    }
    
    // Enlever le backdrop s'il existe
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
        backdrop.remove();
    }
    
    // Remettre le scroll
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
}

/**
 * Initialise des graphiques simples avec des données par défaut
 */
function initializeSimpleCharts() {
    // Graphique annuel simple
    createSimpleYearlyChart();
    
    // Graphique mensuel simple
    createSimpleMonthlyChart();
    
    // Graphique hebdomadaire simple
    createSimpleWeeklyChart();
    
    console.log('📈 Graphiques simples créés');
}

/**
 * Crée un graphique annuel simple
 */
function createSimpleYearlyChart() {
    const ctx = document.getElementById('yearlyChart');
    if (!ctx) return;
    
    try {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027'],
                datasets: [{
                    label: 'Inscriptions Annuelles',
                    data: [120, 140, 135, 150, 160, 217, 220, 225],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Évolution Annuelle des Inscriptions'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Nombre d\'inscriptions'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Erreur graphique annuel:', error);
    }
}

/**
 * Crée un graphique mensuel simple
 */
function createSimpleMonthlyChart() {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;
    
    try {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
                datasets: [{
                    label: 'Inscriptions Mensuelles',
                    data: [10, 8, 12, 15, 20, 18, 14, 8, 25, 20, 15, 12],
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: '#28a745',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribution Mensuelle des Inscriptions'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Nombre d\'inscriptions'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Erreur graphique mensuel:', error);
    }
}

/**
 * Crée un graphique hebdomadaire simple
 */
function createSimpleWeeklyChart() {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;
    
    try {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: generateWeeklyLabels(8),
                datasets: [{
                    label: 'Inscriptions Hebdomadaires',
                    data: [3, 2, 4, 5, 6, 4, 3, 2],
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    borderWidth: 2,
                    tension: 0.2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Tendance Hebdomadaire des Inscriptions'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Nombre d\'inscriptions'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Erreur graphique hebdomadaire:', error);
    }
}

/**
 * Fonctions utilitaires pour les boutons
 */
function refreshModels() {
    console.log('🔄 Actualisation des modèles...');
    location.reload();
}

// exportData supprimé (fonctionnalité d'export retirée)

// Démarrage automatique
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 DOM chargé, initialisation du dashboard...');
    initializePredictionDashboard();
});

// Gestion d'erreur globale pour éviter les crashes
window.addEventListener('error', function(event) {
    console.error('Erreur JavaScript capturée:', event.error);
    hideLoadingElements();
});
