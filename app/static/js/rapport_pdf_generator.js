/**
 * Script JavaScript pour générer un rapport d'activité PDF côté client
 * Utilise jsPDF, autoTable, Chart.js et html2canvas
 * 
 * Remplace la génération PDF Python par une solution JavaScript complète
 */

// =====================================
// CONFIGURATION ET CONSTANTES
// =====================================

const PDF_CONFIG = {
    format: 'a4',
    orientation: 'portrait',
    margins: {
        top: 20,
        left: 15,
        right: 15,
        bottom: 20
    },
    pageWidth: 210, // A4 en mm
    pageHeight: 297, // A4 en mm
    colors: {
        primary: '#007bff',
        secondary: '#6c757d',
        success: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#17a2b8',
        dark: '#343a40'
    }
};

// Variables globales pour les données
let currentApprenantData = null;
let currentFilters = {
    dateDebut: null,
    dateFin: null
};

// =====================================
// CLASSE PRINCIPALE POUR LA GÉNÉRATION PDF
// =====================================

class RapportApprenantPDF {
    constructor() {
        this.jsPDF = null;
        this.doc = null;
        this.currentY = 0;
        this.pageNumber = 1;
    }

    /**
     * Initialise le document PDF
     */
    initDocument() {
        // Charger jsPDF avec les plugins nécessaires
        this.jsPDF = window.jspdf.jsPDF;
        this.doc = new this.jsPDF({
            orientation: PDF_CONFIG.orientation,
            unit: 'mm',
            format: PDF_CONFIG.format
        });

        // Position Y initiale
        this.currentY = PDF_CONFIG.margins.top;
        
        // Configurer la police par défaut
        this.doc.setFont('helvetica');
    }

    /**
     * Ajoute un en-tête de page
     */
    addHeader(apprenantInfo) {
        // Logo ou titre principal
        this.doc.setFontSize(20);
        this.doc.setTextColor(PDF_CONFIG.colors.primary);
        this.doc.text('RAPPORT D\'ACTIVITE APPRENANT', PDF_CONFIG.margins.left, this.currentY);
        this.currentY += 10;

        // Ligne de séparation
        this.doc.setDrawColor(PDF_CONFIG.colors.primary);
        this.doc.setLineWidth(0.5);
        this.doc.line(PDF_CONFIG.margins.left, this.currentY, 
                     PDF_CONFIG.pageWidth - PDF_CONFIG.margins.right, this.currentY);
        this.currentY += 8;

        // Date de génération
        this.doc.setFontSize(10);
        this.doc.setTextColor(PDF_CONFIG.colors.secondary);
        const currentDate = new Date().toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        this.doc.text(`Généré le ${currentDate}`, PDF_CONFIG.margins.left, this.currentY);
        this.currentY += 12;
    }

    /**
     * Ajoute un pied de page
     */
    addFooter() {
        const pageHeight = PDF_CONFIG.pageHeight;
        const footerY = pageHeight - 15;
        
        // Ligne de séparation
        this.doc.setDrawColor(PDF_CONFIG.colors.secondary);
        this.doc.setLineWidth(0.3);
        this.doc.line(PDF_CONFIG.margins.left, footerY - 5, 
                     PDF_CONFIG.pageWidth - PDF_CONFIG.margins.right, footerY - 5);

        // Numéro de page
        this.doc.setFontSize(9);
        this.doc.setTextColor(PDF_CONFIG.colors.secondary);
        this.doc.text(`Page ${this.pageNumber}`, 
                     PDF_CONFIG.pageWidth - PDF_CONFIG.margins.right - 20, footerY);
    }

    /**
     * Ajoute une nouvelle page si nécessaire
     */
    checkPageBreak(requiredHeight = 20) {
        if (this.currentY + requiredHeight > PDF_CONFIG.pageHeight - PDF_CONFIG.margins.bottom - 20) {
            this.addFooter();
            this.doc.addPage();
            this.pageNumber++;
            this.currentY = PDF_CONFIG.margins.top;
            return true;
        }
        return false;
    }

    /**
     * Ajoute un titre de section
     */
    addSectionTitle(title, color = PDF_CONFIG.colors.dark) {
        this.checkPageBreak(15);
        
        // Nettoyer le titre des caractères problématiques
        const cleanTitle = this.cleanText(title);
        
        this.doc.setFontSize(14);
        this.doc.setTextColor(color);
        this.doc.setFont('helvetica', 'bold');
        this.doc.text(cleanTitle, PDF_CONFIG.margins.left, this.currentY);
        this.currentY += 8;

        // Ligne sous le titre
        this.doc.setDrawColor(color);
        this.doc.setLineWidth(0.3);
        this.doc.line(PDF_CONFIG.margins.left, this.currentY, 
                     PDF_CONFIG.margins.left + 60, this.currentY);
        this.currentY += 8;
    }

    /**
     * Nettoie le texte des caractères problématiques pour jsPDF
     */
    cleanText(text) {
        if (!text || typeof text !== 'string') {
            return '';
        }
        
        // Remplacer les emojis par des équivalents texte
        const emojiMap = {
            '📋': '[INFO]',
            '📊': '[EVAL]',
            '📈': '[STATS]',
            '📅': '[PRESENCE]',
            '🔍': '[FILTRE]',
            '👤': '[PROFIL]',
            '📄': '[RAPPORT]',
            '⚠️': '[ATTENTION]',
            '✅': '[OK]',
            '❌': '[ERREUR]',
            '🎯': '[OBJECTIF]',
            '🧪': '[TEST]'
        };
        
        let cleanedText = text;
        
        // Remplacer chaque emoji
        Object.keys(emojiMap).forEach(emoji => {
            cleanedText = cleanedText.replace(new RegExp(emoji, 'g'), emojiMap[emoji]);
        });
        
        // Supprimer les autres emojis restants (plage Unicode des emojis)
        cleanedText = cleanedText.replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '');
        
        // Nettoyer les caractères spéciaux problématiques tout en gardant les accents français
        cleanedText = cleanedText
            .replace(/[àáâãäå]/g, 'a')
            .replace(/[èéêë]/g, 'e')
            .replace(/[ìíîï]/g, 'i')
            .replace(/[òóôõö]/g, 'o')
            .replace(/[ùúûü]/g, 'u')
            .replace(/[ýÿ]/g, 'y')
            .replace(/[ç]/g, 'c')
            .replace(/[ÀÁÂÃÄÅ]/g, 'A')
            .replace(/[ÈÉÊË]/g, 'E')
            .replace(/[ÌÍÎÏ]/g, 'I')
            .replace(/[ÒÓÔÕÖ]/g, 'O')
            .replace(/[ÙÚÛÜ]/g, 'U')
            .replace(/[ÝŸ]/g, 'Y')
            .replace(/[Ç]/g, 'C')
            .replace(/\s+/g, ' ')         // Normaliser les espaces
            .trim();
        
        return cleanedText;
    }

    /**
     * Ajoute les informations personnelles de l'apprenant
     */
    addPersonalInfo(apprenantInfo) {
        this.addSectionTitle('INFORMATIONS PERSONNELLES', PDF_CONFIG.colors.info);

        // Préparer les données
        const data = [
            ['Nom complet', `${apprenantInfo['Prénom'] || ''} ${apprenantInfo['NOM'] || ''}`],
            ['Numéro apprenant', apprenantInfo['N°'] || ''],
            ['Sexe', apprenantInfo['Sexe'] || ''],
            ['Âge', apprenantInfo['Age'] || ''],
            ['Nationalité', apprenantInfo['Nationalité'] || ''],
            ['Ville', apprenantInfo['Ville'] || ''],
            ['Téléphone', apprenantInfo['Téléphone'] || ''],
            ['Email', apprenantInfo['Email'] || '']
        ];

        // Créer le tableau avec autoTable
        this.doc.autoTable({
            startY: this.currentY,
            head: [['Information', 'Valeur']],
            body: data,
            margin: { left: PDF_CONFIG.margins.left, right: PDF_CONFIG.margins.right },
            styles: {
                fontSize: 10,
                cellPadding: 3
            },
            headStyles: {
                fillColor: [23, 162, 184],
                textColor: 255,
                fontStyle: 'bold'
            },
            alternateRowStyles: {
                fillColor: [248, 249, 250]
            },
            columnStyles: {
                0: { fontStyle: 'bold', cellWidth: 40 },
                1: { cellWidth: 'auto' }
            }
        });

        this.currentY = this.doc.lastAutoTable.finalY + 10;
    }

    /**
     * Ajoute les évaluations
     */
    addEvaluations(evaluations) {
        if (!evaluations || evaluations.length === 0) {
            this.addSectionTitle('EVALUATIONS DANS LE TEMPS', PDF_CONFIG.colors.warning);
            this.doc.setFontSize(10);
            this.doc.setFont('helvetica', 'normal');
            this.doc.setTextColor(PDF_CONFIG.colors.secondary);
            this.doc.text('Aucune evaluation disponible', PDF_CONFIG.margins.left, this.currentY);
            this.currentY += 15;
            return;
        }

        this.addSectionTitle('EVALUATIONS DANS LE TEMPS', PDF_CONFIG.colors.success);

        // Préparer les données pour le tableau
        const headers = [
            'Date', 'Note /20', 'Compr. orale', 'Compr. écrite', 
            'Prod. orale', 'Prod. écrite', 'Observation', 'Niveau global'
        ];

        const data = evaluations.map(ev => [
            ev.Date || '',
            ev.Note_test_sur_20 || '',
            ev.Comprehension_orale || '',
            ev.Comprehension_ecrit || '',
            ev.Production_orale || '',
            ev.Production_ecrit || '',
            ev.Observation || '',
            ev.Niveau_global || ''
        ]);

        this.checkPageBreak(50);

        this.doc.autoTable({
            startY: this.currentY,
            head: [headers],
            body: data,
            margin: { left: PDF_CONFIG.margins.left, right: PDF_CONFIG.margins.right },
            styles: {
                fontSize: 8,
                cellPadding: 2
            },
            headStyles: {
                fillColor: [40, 167, 69],
                textColor: 255,
                fontStyle: 'bold'
            },
            columnStyles: {
                0: { cellWidth: 20 },
                1: { cellWidth: 15 },
                2: { cellWidth: 15 },
                3: { cellWidth: 15 },
                4: { cellWidth: 15 },
                5: { cellWidth: 15 },
                6: { cellWidth: 40 },
                7: { cellWidth: 20 }
            }
        });

        this.currentY = this.doc.lastAutoTable.finalY + 10;
    }

    /**
     * Ajoute la grille de progression
     */
    addGrilleProgression(grille) {
        if (!grille || Object.keys(grille).length === 0) {
            return; // Pas de grille = pas d'affichage
        }

        this.checkPageBreak(30);

        // Titre de la grille
        const title = grille.title || `Grille progression ${grille.level || ''}`;
        
        this.doc.setFontSize(12);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(PDF_CONFIG.colors.info);
        this.doc.text('GRILLE DE PROGRESSION - ' + this.cleanText(title), PDF_CONFIG.margins.left, this.currentY);
        this.currentY += 8;

        // Cadre pour la grille
        const capabilities = grille.capabilities || [];
        
        if (capabilities.length === 0) {
            this.doc.setFontSize(10);
            this.doc.setFont('helvetica', 'normal');
            this.doc.setTextColor(PDF_CONFIG.colors.secondary);
            this.doc.text('Aucune capacité définie', PDF_CONFIG.margins.left, this.currentY);
            this.currentY += 10;
            return;
        }

        // Préparer les données pour le tableau
        const capabilitiesData = capabilities.map(cap => [cap]);

        this.doc.autoTable({
            startY: this.currentY,
            head: [['Capacités et compétences']],
            body: capabilitiesData,
            margin: { left: PDF_CONFIG.margins.left, right: PDF_CONFIG.margins.right },
            styles: {
                fontSize: 9,
                cellPadding: 3
            },
            headStyles: {
                fillColor: [108, 117, 125], // Couleur secondary
                textColor: 255,
                fontStyle: 'bold'
            },
            bodyStyles: {
                fontSize: 9
            },
            columnStyles: {
                0: { cellWidth: 'auto' }
            },
            alternateRowStyles: {
                fillColor: [248, 249, 250]
            }
        });

        this.currentY = this.doc.lastAutoTable.finalY + 10;
    }

    /**
     * Ajoute les informations de qualité des données
     */
    async addDataQuality() {
        try {
            // Récupérer les informations de qualité des données
            const response = await fetch('/api/data_quality');
            if (!response.ok) {
                console.warn('Impossible de récupérer les données de qualité');
                return;
            }
            
            const qualityData = await response.json();
            
            if (qualityData && qualityData.message) {
                this.addSectionTitle('QUALITE DES DONNEES', PDF_CONFIG.colors.info);
                
                // Déterminer la couleur selon le type de message
                let messageColor = PDF_CONFIG.colors.dark;
                let iconText = '[INFO]';
                
                switch (qualityData.message_type) {
                    case 'success':
                        messageColor = PDF_CONFIG.colors.success;
                        iconText = '[OK]';
                        break;
                    case 'warning':
                        messageColor = PDF_CONFIG.colors.warning;
                        iconText = '[ATTENTION]';
                        break;
                    case 'error':
                        messageColor = PDF_CONFIG.colors.danger;
                        iconText = '[ERREUR]';
                        break;
                    default:
                        messageColor = PDF_CONFIG.colors.info;
                        iconText = '[INFO]';
                }
                
                // Nettoyer le message
                const cleanMessage = this.cleanText(qualityData.message);
                
                // Ajouter l'icône et le message
                this.doc.setFontSize(10);
                this.doc.setFont('helvetica', 'bold');
                this.doc.setTextColor(messageColor);
                this.doc.text(iconText, PDF_CONFIG.margins.left, this.currentY);
                
                // Calculer la position pour le texte (après l'icône)
                const iconWidth = this.doc.getTextWidth(iconText);
                const textX = PDF_CONFIG.margins.left + iconWidth + 5;
                
                this.doc.setFont('helvetica', 'normal');
                
                // Diviser le message en lignes si nécessaire
                const maxWidth = PDF_CONFIG.pageWidth - textX - PDF_CONFIG.margins.right;
                const lines = this.doc.splitTextToSize(cleanMessage, maxWidth);
                
                // Ajouter chaque ligne
                for (let i = 0; i < lines.length; i++) {
                    this.doc.text(lines[i], textX, this.currentY);
                    this.currentY += 5;
                }
                
                this.currentY += 10; // Espacement après la section
            }
            
        } catch (error) {
            console.warn('Erreur lors de la récupération des données de qualité:', error);
            // Ne pas arrêter la génération du PDF pour cette erreur
        }
    }

    /**
     * Ajoute les statistiques globales
     */
    addStatistics(statistics) {
        this.addSectionTitle('STATISTIQUES GLOBALES', PDF_CONFIG.colors.primary);

        // Informations sur la période filtrée
        if (currentFilters.dateDebut || currentFilters.dateFin) {
            this.doc.setFontSize(10);
            this.doc.setFont('helvetica', 'italic');
            this.doc.setTextColor(PDF_CONFIG.colors.warning);
            let periodeText = '[FILTRE] Periode filtree: ';
            if (currentFilters.dateDebut && currentFilters.dateFin) {
                periodeText += `du ${this.formatDate(currentFilters.dateDebut)} au ${this.formatDate(currentFilters.dateFin)}`;
            } else if (currentFilters.dateDebut) {
                periodeText += `a partir du ${this.formatDate(currentFilters.dateDebut)}`;
            } else if (currentFilters.dateFin) {
                periodeText += `jusqu'au ${this.formatDate(currentFilters.dateFin)}`;
            }
            this.doc.text(periodeText, PDF_CONFIG.margins.left, this.currentY);
            this.currentY += 10;
        }

        // Statistiques principales
        const statsData = [
            ['Total des présences', statistics.total_presences || 0],
            ['Jours uniques de formation', statistics.jours_uniques || 0],
            ['Activités différentes', (statistics.activites_uniques ? statistics.activites_uniques.length : 0)],
            ['Total des heures', statistics.total_heures || '0h00']
        ];

        this.doc.autoTable({
            startY: this.currentY,
            head: [['Indicateur', 'Valeur']],
            body: statsData,
            margin: { left: PDF_CONFIG.margins.left, right: PDF_CONFIG.margins.right },
            styles: {
                fontSize: 11,
                cellPadding: 4
            },
            headStyles: {
                fillColor: [0, 123, 255],
                textColor: 255,
                fontStyle: 'bold'
            },
            columnStyles: {
                0: { fontStyle: 'bold', cellWidth: 80 },
                1: { cellWidth: 'auto', halign: 'center', fontStyle: 'bold' }
            }
        });

        this.currentY = this.doc.lastAutoTable.finalY + 10;
    }

    /**
     * Ajoute une image de graphique
     */
    async addChartImage(chartElementId, title, width = 160, height = 80) {
        this.checkPageBreak(height + 20);

        // Ajouter le titre du graphique
        this.doc.setFontSize(12);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(PDF_CONFIG.colors.dark);
        this.doc.text(this.cleanText(title), PDF_CONFIG.margins.left, this.currentY);
        this.currentY += 8;

        try {
            // Récupérer l'élément canvas du graphique
            const chartElement = document.getElementById(chartElementId);
            if (!chartElement) {
                this.doc.setFontSize(10);
                this.doc.setTextColor(PDF_CONFIG.colors.secondary);
                this.doc.text('Graphique non disponible', PDF_CONFIG.margins.left, this.currentY);
                this.currentY += 15;
                return;
            }

            // Convertir le canvas en image avec html2canvas
            const canvas = await html2canvas(chartElement, {
                backgroundColor: '#ffffff',
                scale: 2, // Améliorer la qualité
                logging: false
            });

            // Convertir en base64
            const imgData = canvas.toDataURL('image/png');

            // Calculer la position centrée
            const imgX = (PDF_CONFIG.pageWidth - width) / 2;

            // Ajouter l'image au PDF
            this.doc.addImage(imgData, 'PNG', imgX, this.currentY, width, height);
            this.currentY += height + 10;

        } catch (error) {
            console.error('Erreur lors de l\'ajout du graphique:', error);
            this.doc.setFontSize(10);
            this.doc.setTextColor(PDF_CONFIG.colors.danger);
            this.doc.text('Erreur lors de la génération du graphique', PDF_CONFIG.margins.left, this.currentY);
            this.currentY += 15;
        }
    }

    /**
     * Ajoute le tableau détaillé des présences
     */
    addPresenceTable(presences) {
        this.addSectionTitle('DETAIL DES PRESENCES', PDF_CONFIG.colors.dark);

        if (!presences || presences.length === 0) {
            this.doc.setFontSize(10);
            this.doc.setFont('helvetica', 'normal');
            this.doc.setTextColor(PDF_CONFIG.colors.secondary);
            this.doc.text('Aucune presence enregistree pour cette periode', PDF_CONFIG.margins.left, this.currentY);
            this.currentY += 15;
            return;
        }

        // Préparer les données
        const headers = ['Date', 'Activité', 'Début', 'Fin', 'Durée', 'Encadrant'];
        const data = presences.map(presence => [
            this.formatDateFromPresence(presence['Date du Jour']) || '',
            presence['Activités'] || '',
            presence['Activités Apprenants Début'] || '',
            presence['Activités Apprenants Fin'] || '',
            presence['Durée Activité Apprenants'] || '',
            presence['Encadrant'] || ''
        ]);

        // Calculer le total des heures
        let totalMinutes = 0;
        presences.forEach(presence => {
            totalMinutes += this.convertDurationToMinutes(presence['Durée Activité Apprenants']);
        });
        const totalFormate = this.formatDuration(totalMinutes);

        // Ajouter une ligne de total
        data.push(['', '', '', 'TOTAL:', totalFormate, '']);

        this.checkPageBreak(50);

        this.doc.autoTable({
            startY: this.currentY,
            head: [headers],
            body: data,
            margin: { left: PDF_CONFIG.margins.left, right: PDF_CONFIG.margins.right },
            styles: {
                fontSize: 8,
                cellPadding: 2
            },
            headStyles: {
                fillColor: [52, 58, 64],
                textColor: 255,
                fontStyle: 'bold'
            },
            bodyStyles: {
                fontSize: 8
            },
            columnStyles: {
                0: { cellWidth: 20 },
                1: { cellWidth: 50 },
                2: { cellWidth: 15 },
                3: { cellWidth: 15 },
                4: { cellWidth: 15 },
                5: { cellWidth: 35 }
            },
            didParseCell: function(data) {
                // Mettre en évidence la ligne de total
                if (data.row.index === data.table.body.length - 1) {
                    data.cell.styles.fontStyle = 'bold';
                    data.cell.styles.fillColor = [248, 249, 250];
                }
            }
        });

        this.currentY = this.doc.lastAutoTable.finalY + 10;
    }

    /**
     * Utilitaires de formatage
     */
    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR');
    }

    formatDateFromPresence(dateString) {
        if (!dateString) return '';
        if (dateString.includes('/')) {
            try {
                const parts = dateString.split('/');
                if (parts.length === 3) {
                    const date = new Date(parts[2], parts[1] - 1, parts[0]);
                    return date.toLocaleDateString('fr-FR');
                }
            } catch (e) {
                return dateString;
            }
        }
        return dateString;
    }

    convertDurationToMinutes(duration) {
        if (!duration || typeof duration !== 'string') {
            return 0;
        }

        duration = duration.toString().toLowerCase().trim();
        let totalMinutes = 0;

        try {
            // Format "HH:MM"
            const formatHHMM = duration.match(/^(\d{1,2}):(\d{2})$/);
            if (formatHHMM) {
                const heures = parseInt(formatHHMM[1], 10);
                const minutes = parseInt(formatHHMM[2], 10);
                return (heures * 60) + minutes;
            }

            // Format "Xh" ou "XhYY"
            const formatHeure = duration.match(/(\d+)\s*h(?:\s*(\d+))?/);
            if (formatHeure) {
                const heures = parseInt(formatHeure[1], 10);
                const minutes = formatHeure[2] ? parseInt(formatHeure[2], 10) : 0;
                return (heures * 60) + minutes;
            }

            // Format "XX min"
            const formatMinutes = duration.match(/(\d+)\s*min/);
            if (formatMinutes) {
                return parseInt(formatMinutes[1], 10);
            }

            // Format décimal
            const nombre = parseFloat(duration);
            if (!isNaN(nombre)) {
                return Math.round(nombre * 60);
            }

        } catch (error) {
            console.warn('Erreur lors de la conversion de la durée:', duration, error);
        }

        return 0;
    }

    formatDuration(totalMinutes) {
        if (totalMinutes === 0) {
            return '0h00';
        }

        const heures = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;

        return `${heures}h${minutes.toString().padStart(2, '0')}`;
    }

    /**
     * Génère le PDF complet
     */
    async generatePDF(apprenantData, filters = {}) {
        try {
            // Sauvegarder les données et filtres
            currentApprenantData = apprenantData;
            currentFilters = filters;

            console.log('Début de la génération PDF...', apprenantData);

            // Initialiser le document
            this.initDocument();

            // Ajouter l'en-tête
            this.addHeader(apprenantData.apprenant);

            // Ajouter les informations personnelles
            this.addPersonalInfo(apprenantData.apprenant);

            // Ajouter les informations de qualité des données
            await this.addDataQuality();

            // Ajouter les évaluations
            if (apprenantData.evaluations) {
                this.addEvaluations(apprenantData.evaluations);
            }

            // Ajouter la grille de progression (après les évaluations)
            if (apprenantData.grille_progression) {
                this.addGrilleProgression(apprenantData.grille_progression);
            }

            // Ajouter les statistiques
            this.addStatistics(apprenantData.statistiques);

            // Ajouter les graphiques (si les éléments existent)
            const chartIds = [
                { id: 'chartPresenceDate', title: 'EVOLUTION DES PRESENCES DANS LE TEMPS' },
                { id: 'chartPresenceJour', title: 'REPARTITION PAR JOUR DE LA SEMAINE' },
                { id: 'chartEvolutionPeriode', title: 'EVOLUTION PAR PERIODE', height: 100 }
            ];

            for (const chart of chartIds) {
                await this.addChartImage(chart.id, chart.title, 160, chart.height || 80);
            }

            // Ajouter le tableau des présences
            this.addPresenceTable(apprenantData.presences);

            // Ajouter le pied de page à la dernière page
            this.addFooter();

            // Générer le nom du fichier
            const nomApprenant = `${apprenantData.apprenant['Prénom'] || ''}_${apprenantData.apprenant['NOM'] || ''}`.replace(/\s+/g, '_');
            const numeroApprenant = apprenantData.apprenant['N°'] || 'inconnu';
            const dateGeneration = new Date().toISOString().slice(0, 10);
            const fileName = `rapport_activite_${nomApprenant}_${numeroApprenant}_${dateGeneration}.pdf`;

            // Télécharger le PDF
            this.doc.save(fileName);

            console.log('PDF généré avec succès:', fileName);
            return true;

        } catch (error) {
            console.error('Erreur lors de la génération du PDF:', error);
            alert('Erreur lors de la génération du PDF: ' + error.message);
            return false;
        }
    }
}

// =====================================
// FONCTIONS D'INTERFACE ET D'INTÉGRATION
// =====================================

/**
 * Instance globale du générateur PDF
 */
const pdfGenerator = new RapportApprenantPDF();

/**
 * Fonction principale pour exporter le PDF (remplace la fonction existante)
 */
async function exporterPDFClientSide() {
    const numeroApprenant = document.getElementById('selectedApprenantNumero').value;

    if (!numeroApprenant) {
        alert('Veuillez d\'abord sélectionner un apprenant et charger ses données.');
        return;
    }

    // Vérifier que les données sont chargées
    if (!currentApprenantData) {
        alert('Veuillez d\'abord charger les données de l\'apprenant.');
        return;
    }

    // Afficher un indicateur de chargement
    const btnPDF = document.getElementById('btnExportPDF');
    const originalText = btnPDF.innerHTML;
    btnPDF.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Génération...';
    btnPDF.disabled = true;

    try {
        // Récupérer les filtres actuels
        const filters = {
            dateDebut: document.getElementById('dateDebut').value,
            dateFin: document.getElementById('dateFin').value
        };

        // Générer le PDF
        await pdfGenerator.generatePDF(currentApprenantData, filters);

    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la génération du PDF: ' + error.message);
    } finally {
        // Restaurer le bouton
        btnPDF.innerHTML = originalText;
        btnPDF.disabled = false;
    }
}

/**
 * Fonction pour récupérer les données via l'API (simulation ou vraie API)
 */
async function fetchApprenantDataForPDF(numeroApprenant, filters = {}) {
    try {
        // Construire l'URL avec les filtres
        let url = `/api/apprenant_details/${numeroApprenant}`;
        const params = new URLSearchParams();
        
        if (filters.dateDebut) {
            params.append('date_debut', filters.dateDebut);
        }
        if (filters.dateFin) {
            params.append('date_fin', filters.dateFin);
        }
        
        if (params.toString()) {
            url += '?' + params.toString();
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        return data;

    } catch (error) {
        console.error('Erreur lors de la récupération des données:', error);
        throw error;
    }
}

// =====================================
// INTÉGRATION AVEC L'APPLICATION EXISTANTE
// =====================================

/**
 * Fonction pour sauvegarder les données d'apprenant pour le PDF
 */
function saveApprenantDataForPDF(data) {
    currentApprenantData = data;
    console.log('✅ Données sauvegardées pour PDF:', data);
}

/**
 * Hook pour intercepter les données lors du chargement de l'apprenant
 */
function saveApprenantDataForPDF(data) {
    currentApprenantData = data;
    console.log('✅ Données sauvegardées pour PDF:', data);
}

// =====================================
// INITIALISATION
// =====================================

// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Script PDF client-side initialisé');
    
    // Attendre que la page soit complètement chargée
    setTimeout(() => {
        // Hook pour la fonction chargerApprenant
        if (typeof window.chargerApprenant === 'function') {
            const originalChargerApprenant = window.chargerApprenant;
            window.chargerApprenant = async function() {
                await originalChargerApprenant.apply(this, arguments);
                
                // Sauvegarder les données pour le PDF
                const numeroApprenant = document.getElementById('selectedApprenantNumero').value;
                if (numeroApprenant) {
                    try {
                        const filters = {
                            dateDebut: document.getElementById('dateDebut').value,
                            dateFin: document.getElementById('dateFin').value
                        };
                        const data = await fetchApprenantDataForPDF(numeroApprenant, filters);
                        saveApprenantDataForPDF(data);
                    } catch (error) {
                        console.error('Erreur lors de la sauvegarde des données pour PDF:', error);
                    }
                }
            };
            console.log('✅ Hook chargerApprenant installé');
        }

        // Hook pour la fonction de filtrage
        if (typeof window.chargerApprenantAvecFiltre === 'function') {
            const originalChargerApprenantAvecFiltre = window.chargerApprenantAvecFiltre;
            window.chargerApprenantAvecFiltre = async function() {
                await originalChargerApprenantAvecFiltre.apply(this, arguments);
                
                // Sauvegarder les données filtrées pour le PDF
                const numeroApprenant = document.getElementById('selectedApprenantNumero').value;
                if (numeroApprenant) {
                    try {
                        const filters = {
                            dateDebut: document.getElementById('dateDebut').value,
                            dateFin: document.getElementById('dateFin').value
                        };
                        const data = await fetchApprenantDataForPDF(numeroApprenant, filters);
                        saveApprenantDataForPDF(data);
                    } catch (error) {
                        console.error('Erreur lors de la sauvegarde des données filtrées pour PDF:', error);
                    }
                }
            };
            console.log('✅ Hook chargerApprenantAvecFiltre installé');
        }

        // Remplacer la fonction exporterPDF existante
        if (window.exporterPDF) {
            window.exporterPDFOriginal = window.exporterPDF;
        }
        window.exporterPDF = exporterPDFClientSide;
        console.log('✅ Fonction exporterPDF remplacée');
        
        console.log('🎯 Générateur PDF JavaScript intégré avec succès');
    }, 1000);
});

// Export pour utilisation externe
window.RapportApprenantPDF = RapportApprenantPDF;
window.exporterPDFClientSide = exporterPDFClientSide;

console.log('Module PDF client-side chargé');
