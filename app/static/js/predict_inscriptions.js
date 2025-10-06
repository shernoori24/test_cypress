(function(){
  // Données JSON embarquées (6 premiers mois)
  const dataEl = document.getElementById('enrollData');
  const canvas = document.getElementById('enrollForecastChart');
  if (!dataEl || !canvas) return;

  let items = [];
  try {
    items = JSON.parse(dataEl.textContent || '[]');
  } catch(e) {
    console.error('predict_inscriptions: JSON invalide', e);
    return;
  }

  // Nettoyage: filtrer les objets valides
  items = (items || []).filter(x => x && typeof x.month === 'string');

  // Tri par ordre chronologique si possible (mois texte anglais -> garder l'ordre d'origine si ambigu)
  // On tente de parser avec Date.parse, sinon on garde l'ordre original
  const parsed = items.map((it, idx) => {
    const t = Date.parse(it.month);
    return { idx, t: isNaN(t) ? idx : t, it };
  });
  parsed.sort((a,b) => a.t - b.t);

  const labels = parsed.map(p => p.it.month);
  const counts = parsed.map(p => Number(p.it.predicted_count) || 0);
  const conf = parsed.map(p => Math.round((Number(p.it.confidence) || 0) * 100));

  /* global Chart */
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js non chargé');
    return;
  }

  const ctx = canvas.getContext('2d');

  // Détruit graphe existant s'il y en a un
  try {
    const existing = (typeof Chart.getChart === 'function') ? Chart.getChart(canvas) : (canvas._chartInstance || null);
    if (existing && typeof existing.destroy === 'function') existing.destroy();
  } catch(err) { console.warn('Destroy chart failed', err); }

  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          type: 'bar',
          label: 'Prévision',
          data: counts,
          backgroundColor: 'rgba(25, 135, 84, 0.6)',
          borderColor: 'rgba(25, 135, 84, 1)',
          borderWidth: 1,
          yAxisID: 'y'
        },
        {
          type: 'line',
          label: 'Confiance (%)',
          data: conf,
          borderColor: 'rgba(13, 202, 240, 1)',
          backgroundColor: 'rgba(13, 202, 240, 0.2)',
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
          title: { display: true, text: "Inscriptions prévues" }
        },
        y1: {
          beginAtZero: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          title: { display: true, text: 'Confiance (%)' },
          suggestedMax: 100
        }
      }
    }
  });

  canvas._chartInstance = chart;
})();
