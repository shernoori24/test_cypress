// app/static/js/predictions/predict_nombre_inscription.js
// JavaScript pour les prédictions d'inscriptions avec Chart.js

let yearlyChart, monthlyChart, weeklyChart;

// Configuration globale des graphiques
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;

/**
 * Initialise le dashboard des prédictions
 */
function initializePredictionDashboard() {
    console.log('🚀 Initialisation du dashboard des prédictions...');
    
    // Afficher le modal de chargement
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    loadingModal.show();
    
    // Charger tous les graphiques
    Promise.all([
        loadYearlyPredictions(),
        loadMonthlyPredictions(),
        loadWeeklyPredictions(),
        loadInsights()
    ]).then(() => {
        console.log('✅ Dashboard initialisé avec succès');
        loadingModal.hide();
        showAlert('success', 'Dashboard chargé avec succès!');
    }).catch(error => {
        console.error('❌ Erreur initialisation dashboard:', error);
        loadingModal.hide();
        showAlert('danger', 'Erreur lors du chargement du dashboard: ' + error.message);
    });
    
    // Événements des onglets
    setupTabEvents();
}

/**
 * Configure les événements des onglets
 */
function setupTabEvents() {
    const tabs = document.querySelectorAll('#predictionTabs button[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const targetId = event.target.getAttribute('data-bs-target').substring(1);
            console.log(`📊 Onglet activé: ${targetId}`);
            
            // Redimensionner les graphiques si nécessaire
            setTimeout(() => {
                if (targetId === 'yearly' && yearlyChart) yearlyChart.resize();
                if (targetId === 'monthly' && monthlyChart) monthlyChart.resize();
                if (targetId === 'weekly' && weeklyChart) weeklyChart.resize();
                if (targetId === 'performance') {
                    // Graphiques de performance supprimés
                }
            }, 100);
        });
    });
}

/**
 * Charge et affiche les prédictions annuelles
 */
async function loadYearlyPredictions() {
    try {
        const response = await fetch('/prediction/api/predictions/yearly');
        if (!response.ok) throw new Error('Erreur API yearly');
        
        const data = await response.json();
        console.log('📊 Données annuelles reçues:', data);
        
        // Mettre à jour les informations du modèle
        document.getElementById('yearly-model-info').innerHTML = 
            `<small class="text-muted">Modèle: <strong>${data.model.name}</strong> | Confiance: <strong>${data.model.confidence}</strong></small>`;
        
        // Créer le graphique
        createYearlyChart(data);
        
    } catch (error) {
        console.error('❌ Erreur chargement yearly:', error);
        showAlert('warning', 'Erreur lors du chargement des prédictions annuelles');
    }
}

/**
 * Crée le graphique des prédictions annuelles
 */
function createYearlyChart(data) {
    const ctx = document.getElementById('yearlyChart').getContext('2d');
    
    if (yearlyChart) {
        yearlyChart.destroy();
    }
    
    // Combiner les données historiques et les prédictions
    const allYears = [...data.historical.years, ...data.predictions.years];
    const allCounts = [...data.historical.counts, ...data.predictions.counts];
    
    // Point de séparation entre historique et prédictions
    const separationIndex = data.historical.years.length;
    
    yearlyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allYears,
            datasets: [
                {
                    label: 'Données Historiques',
                    data: data.historical.counts.concat(Array(data.predictions.years.length).fill(null)),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#007bff',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    fill: false,
                    tension: 0.2
                },
                {
                    label: 'Prédictions IA',
                    data: Array(data.historical.years.length).fill(null).concat(data.predictions.counts),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    borderDash: [10, 5],
                    pointBackgroundColor: '#28a745',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    fill: false,
                    tension: 0.2
                },
                {
                    label: 'Transition',
                    data: Array(separationIndex - 1).fill(null).concat([
                        data.historical.counts[separationIndex - 1],
                        data.predictions.counts[0]
                    ]).concat(Array(data.predictions.years.length - 1).fill(null)),
                    borderColor: '#ffc107',
                    borderWidth: 2,
                    pointRadius: 0,
                    showLine: true,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Évolution et Prédictions Annuelles des Inscriptions',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        title: function(context) {
                            return `Année ${context[0].label}`;
                        },
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y} inscriptions`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Année'
                    },
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Nombre d\'inscriptions'
                    },
                    beginAtZero: true,
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

/**
 * Charge et affiche les prédictions mensuelles
 */
async function loadMonthlyPredictions() {
    try {
        const response = await fetch('/prediction/api/predictions/monthly');
        if (!response.ok) throw new Error('Erreur API monthly');
        
        const data = await response.json();
        console.log('📊 Données mensuelles reçues:', data);
        
        // Mettre à jour les informations du modèle
        document.getElementById('monthly-model-info').innerHTML = 
            `<small class="text-muted">Modèle: <strong>${data.model.name}</strong> | Confiance: <strong>${data.model.confidence}</strong></small>`;
        
        // Créer le graphique
        createMonthlyChart(data);
        
    } catch (error) {
        console.error('❌ Erreur chargement monthly:', error);
        showAlert('warning', 'Erreur lors du chargement des prédictions mensuelles');
    }
}

/**
 * Crée le graphique des prédictions mensuelles
 */
function createMonthlyChart(data) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    if (monthlyChart) {
        monthlyChart.destroy();
    }
    
    // Combiner les données
    const allDates = [...data.historical.dates, ...data.predictions.dates];
    const allCounts = [...data.historical.counts, ...data.predictions.counts];
    const separationIndex = data.historical.dates.length;
    
    monthlyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allDates,
            datasets: [
                {
                    label: 'Données Historiques',
                    data: data.historical.counts.concat(Array(data.predictions.dates.length).fill(null)),
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
                    borderWidth: 2,
                    pointRadius: 3,
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Prédictions IA',
                    data: Array(data.historical.dates.length).fill(null).concat(data.predictions.counts),
                    borderColor: '#fd7e14',
                    backgroundColor: 'rgba(253, 126, 20, 0.1)',
                    borderWidth: 2,
                    borderDash: [8, 4],
                    pointRadius: 3,
                    fill: true,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Évolution et Prédictions Mensuelles des Inscriptions',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Mois'
                    },
                    ticks: {
                        maxTicksLimit: 12
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Nombre d\'inscriptions'
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Charge et affiche les prédictions hebdomadaires
 */
async function loadWeeklyPredictions() {
    try {
        const response = await fetch('/prediction/api/predictions/weekly');
        if (!response.ok) throw new Error('Erreur API weekly');
        
        const data = await response.json();
        console.log('📊 Données hebdomadaires reçues:', data);
        
        // Mettre à jour les informations du modèle
        document.getElementById('weekly-model-info').innerHTML = 
            `<small class="text-muted">Modèle: <strong>${data.model.name}</strong> | Confiance: <strong>${data.model.confidence}</strong></small>`;
        
        // Créer le graphique
        createWeeklyChart(data);
        
    } catch (error) {
        console.error('❌ Erreur chargement weekly:', error);
        showAlert('warning', 'Erreur lors du chargement des prédictions hebdomadaires');
    }
}

/**
 * Crée le graphique des prédictions hebdomadaires
 */
function createWeeklyChart(data) {
    const ctx = document.getElementById('weeklyChart').getContext('2d');
    
    if (weeklyChart) {
        weeklyChart.destroy();
    }
    
    weeklyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [...data.historical.weeks, ...data.predictions.weeks],
            datasets: [
                {
                    label: 'Historique',
                    data: data.historical.counts.concat(Array(data.predictions.weeks.length).fill(null)),
                    backgroundColor: 'rgba(108, 117, 125, 0.7)',
                    borderColor: '#6c757d',
                    borderWidth: 1
                },
                {
                    label: 'Prédictions',
                    data: Array(data.historical.weeks.length).fill(null).concat(data.predictions.counts),
                    backgroundColor: 'rgba(220, 53, 69, 0.7)',
                    borderColor: '#dc3545',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Prédictions Hebdomadaires des Inscriptions',
                    font: { size: 16, weight: 'bold' }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Semaine'
                    },
                    ticks: {
                        maxTicksLimit: 20
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Nombre d\'inscriptions'
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

// Logique de performance des modèles supprimée

/**
 * Charge et affiche les insights
 */
async function loadInsights() {
    try {
        const response = await fetch('/prediction/api/predictions/insights');
        if (!response.ok) throw new Error('Erreur API insights');
        
        const data = await response.json();
        console.log('💡 Insights reçus:', data);
        
        // Afficher les insights
        displayInsights(data);
        
    } catch (error) {
        console.error('❌ Erreur chargement insights:', error);
        document.getElementById('insights-container').innerHTML = 
            '<div class="alert alert-warning">Erreur lors du chargement des insights</div>';
    }
}

/**
 * Affiche les insights et recommandations
 */
function displayInsights(data) {
    const container = document.getElementById('insights-container');
    
    let html = '<div class="row">';
    
    // Performance des modèles
    if (data.model_performance) {
        html += '<div class="col-lg-6 mb-3">';
        html += '<h6><i class="fas fa-tachometer-alt text-primary"></i> Performance des Modèles</h6>';
        html += '<div class="list-group list-group-flush">';
        
        for (const [period, perf] of Object.entries(data.model_performance)) {
            const badgeClass = perf.reliability === 'Élevée' ? 'success' : 
                             perf.reliability === 'Modérée' ? 'warning' : 'danger';
            
            html += `
                <div class="list-group-item border-0 px-0">
                    <div class="d-flex justify-content-between">
                        <span><strong>${period.charAt(0).toUpperCase() + period.slice(1)}:</strong> ${perf.best_model.replace('_', ' ')}</span>
                        <span class="badge bg-${badgeClass}">${perf.reliability}</span>
                    </div>
                    <small class="text-muted">R² Score: ${perf.r2_score}</small>
                </div>
            `;
        }
        
        html += '</div></div>';
    }
    
    // Recommandations
    if (data.recommendations && data.recommendations.length > 0) {
        html += '<div class="col-lg-6 mb-3">';
        html += '<h6><i class="fas fa-lightbulb text-warning"></i> Recommandations</h6>';
        html += '<div class="list-group list-group-flush">';
        
        data.recommendations.forEach(rec => {
            html += `
                <div class="list-group-item border-0 px-0">
                    <span>${rec}</span>
                </div>
            `;
        });
        
        html += '</div></div>';
    }
    
    // Résumé des prédictions
    if (data.predictions_summary) {
        html += '<div class="col-12 mt-3">';
        html += '<h6><i class="fas fa-chart-line text-success"></i> Résumé des Prédictions</h6>';
        html += '<div class="row">';
        
        if (data.predictions_summary.yearly) {
            const yearly = data.predictions_summary.yearly;
            html += `
                <div class="col-md-6">
                    <div class="card border-0 bg-light">
                        <div class="card-body p-3">
                            <h6 class="card-title">Prédictions Annuelles</h6>
                            <p class="mb-1">Total 5 ans: <strong>${yearly.total_5_years}</strong> inscriptions</p>
                            <p class="mb-1">Moyenne/an: <strong>${yearly.average_per_year}</strong> inscriptions</p>
                            <p class="mb-0">Tendance: <strong>${yearly.trend}</strong></p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        if (data.predictions_summary.monthly) {
            const monthly = data.predictions_summary.monthly;
            html += `
                <div class="col-md-6">
                    <div class="card border-0 bg-light">
                        <div class="card-body p-3">
                            <h6 class="card-title">Prédictions Mensuelles</h6>
                            <p class="mb-1">Prochaine année: <strong>${monthly.total_next_year}</strong> inscriptions</p>
                            <p class="mb-1">Moyenne/mois: <strong>${monthly.average_per_month}</strong> inscriptions</p>
                            <p class="mb-0">Pic prévu: <strong>${monthly.peak_month}</strong></p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += '</div></div>';
    }
    
    html += '</div>';
    
    container.innerHTML = html;
}

/**
 * Actualise tous les modèles
 */
async function refreshModels() {
    console.log('🔄 Actualisation des modèles...');
    
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    loadingModal.show();
    
    try {
        // Déclencher le re-entraînement
        const response = await fetch('/prediction/api/predictions/retrain', {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Erreur re-entraînement');
        
        // Recharger le dashboard
        await initializePredictionDashboard();
        
        showAlert('success', 'Modèles actualisés avec succès!');
        
    } catch (error) {
        console.error('❌ Erreur actualisation:', error);
        showAlert('danger', 'Erreur lors de l\'actualisation: ' + error.message);
    } finally {
        loadingModal.hide();
    }
}

// Fonctions d'export supprimées (API d'export retirée)

/**
 * Affiche une alerte
 */
function showAlert(type, message) {
    const alertsContainer = document.getElementById('alerts-container');
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Supprimer automatiquement après 5 secondes
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}
