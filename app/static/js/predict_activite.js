(function(){
  // Récupère les données JSON embarquées
  const dataEl = document.getElementById('activiteData');
  if (!dataEl) return;
  let predictions;
  try {
    predictions = JSON.parse(dataEl.textContent || '{}');
  } catch(e) {
    console.error('predict_activite: JSON invalide', e);
    return;
  }

  const canvas = document.getElementById('activiteForecastChart');
  if (!canvas || !predictions || !predictions.predictions_6_mois) return;

  // Construit les séries pour Chart.js
  const entries = Object.entries(predictions.predictions_6_mois);
  // Tri par clé YYYY-MM
  entries.sort((a,b) => a[0].localeCompare(b[0]));

  const labels = entries.map(([ym]) => ym);
  const activites = entries.map(([,v]) => v.activites_predites || 0);
  const duree = entries.map(([,v]) => v.duree_moyenne_predite_minutes || 0);

  // Formatage des labels mois lisibles (optionnel)
  const monthNames = ['Jan','Fév','Mar','Avr','Mai','Juin','Juil','Août','Sep','Oct','Nov','Déc'];
  const prettyLabels = labels.map(ym => {
    const [y,m] = ym.split('-').map(Number);
    return (monthNames[(m-1)%12] || ym) + ' ' + String(y).slice(-2);
  });

  // Instancie Chart.js
  // Chart.js est déjà inclus via base.html
  const ctx = canvas.getContext('2d');
  /* global Chart */
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js non chargé');
    return;
  }

  // Détruit un éventuel graphique déjà rendu sur ce canvas
  try {
    const existing = (typeof Chart.getChart === 'function')
      ? Chart.getChart(canvas)
      : (canvas._chartInstance || null);
    if (existing && typeof existing.destroy === 'function') {
      existing.destroy();
    }
  } catch(err) {
    console.warn('Impossible de détruire le graphique existant:', err);
  }

  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: prettyLabels,
      datasets: [
        {
          type: 'bar',
          label: "Activités prédites",
          data: activites,
          backgroundColor: 'rgba(255, 193, 7, 0.6)',
          borderColor: 'rgba(255, 193, 7, 1)',
          borderWidth: 1,
          yAxisID: 'y'
        },
        {
          type: 'line',
          label: "Durée moyenne (min)",
          data: duree,
          borderColor: 'rgba(13, 110, 253, 1)',
          backgroundColor: 'rgba(13, 110, 253, 0.2)',
          borderWidth: 2,
          tension: 0.25,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top' },
        tooltip: { enabled: true }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Nombre d\'activités' }
        },
        y1: {
          beginAtZero: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          title: { display: true, text: 'Durée moyenne (min)' }
        }
      }
    }
  });

  // Mémorise la nouvelle instance pour de futurs nettoyages
  canvas._chartInstance = chart;
})();
