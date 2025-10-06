// JavaScript avancé pour l'amélioration UX du formulaire d'inscription
// Auto-remplissage intelligent des champs pays, nationalité, ISO et continent

// Base de données des pays avec leurs informations complètes
const PAYS_DATABASE = {
    // Europe
    'France': { nationalite: 'Française', iso: 'FRA', continent: 'Europe' },
    'Allemagne': { nationalite: 'Allemande', iso: 'DEU', continent: 'Europe' },
    'Espagne': { nationalite: 'Espagnole', iso: 'ESP', continent: 'Europe' },
    'Italie': { nationalite: 'Italienne', iso: 'ITA', continent: 'Europe' },
    'Portugal': { nationalite: 'Portugaise', iso: 'PRT', continent: 'Europe' },
    'Belgique': { nationalite: 'Belge', iso: 'BEL', continent: 'Europe' },
    'Pays-Bas': { nationalite: 'Néerlandaise', iso: 'NLD', continent: 'Europe' },
    'Royaume-Uni': { nationalite: 'Britannique', iso: 'GBR', continent: 'Europe' },
    'Suisse': { nationalite: 'Suisse', iso: 'CHE', continent: 'Europe' },
    'Autriche': { nationalite: 'Autrichienne', iso: 'AUT', continent: 'Europe' },
    'Pologne': { nationalite: 'Polonaise', iso: 'POL', continent: 'Europe' },
    'Roumanie': { nationalite: 'Roumaine', iso: 'ROU', continent: 'Europe' },
    'Grèce': { nationalite: 'Grecque', iso: 'GRC', continent: 'Europe' },
    'Suède': { nationalite: 'Suédoise', iso: 'SWE', continent: 'Europe' },
    'Norvège': { nationalite: 'Norvégienne', iso: 'NOR', continent: 'Europe' },
    'Danemark': { nationalite: 'Danoise', iso: 'DNK', continent: 'Europe' },
    'Finlande': { nationalite: 'Finlandaise', iso: 'FIN', continent: 'Europe' },
    'Irlande': { nationalite: 'Irlandaise', iso: 'IRL', continent: 'Europe' },
    'République tchèque': { nationalite: 'Tchèque', iso: 'CZE', continent: 'Europe' },
    'Hongrie': { nationalite: 'Hongroise', iso: 'HUN', continent: 'Europe' },
    'Bulgarie': { nationalite: 'Bulgare', iso: 'BGR', continent: 'Europe' },
    'Croatie': { nationalite: 'Croate', iso: 'HRV', continent: 'Europe' },
    'Slovénie': { nationalite: 'Slovène', iso: 'SVN', continent: 'Europe' },
    'Slovaquie': { nationalite: 'Slovaque', iso: 'SVK', continent: 'Europe' },
    'Lituanie': { nationalite: 'Lituanienne', iso: 'LTU', continent: 'Europe' },
    'Lettonie': { nationalite: 'Lettone', iso: 'LVA', continent: 'Europe' },
    'Estonie': { nationalite: 'Estonienne', iso: 'EST', continent: 'Europe' },
    'Ukraine': { nationalite: 'Ukrainienne', iso: 'UKR', continent: 'Europe' },
    'Russie': { nationalite: 'Russe', iso: 'RUS', continent: 'Europe' },
    'Biélorussie': { nationalite: 'Biélorusse', iso: 'BLR', continent: 'Europe' },
    'Moldavie': { nationalite: 'Moldave', iso: 'MDA', continent: 'Europe' },
    'Albanie': { nationalite: 'Albanaise', iso: 'ALB', continent: 'Europe' },
    'Bosnie-Herzégovine': { nationalite: 'Bosnienne', iso: 'BIH', continent: 'Europe' },
    'Serbie': { nationalite: 'Serbe', iso: 'SRB', continent: 'Europe' },
    'Monténégro': { nationalite: 'Monténégrine', iso: 'MNE', continent: 'Europe' },
    'Macédoine du Nord': { nationalite: 'Macédonienne', iso: 'MKD', continent: 'Europe' },
    'Kosovo': { nationalite: 'Kosovare', iso: 'XKX', continent: 'Europe' },

    // Afrique
    'Algérie': { nationalite: 'Algérienne', iso: 'DZA', continent: 'Afrique' },
    'Maroc': { nationalite: 'Marocaine', iso: 'MAR', continent: 'Afrique' },
    'Tunisie': { nationalite: 'Tunisienne', iso: 'TUN', continent: 'Afrique' },
    'Égypte': { nationalite: 'Égyptienne', iso: 'EGY', continent: 'Afrique' },
    'Libye': { nationalite: 'Libyenne', iso: 'LBY', continent: 'Afrique' },
    'Soudan': { nationalite: 'Soudanaise', iso: 'SDN', continent: 'Afrique' },
    'Éthiopie': { nationalite: 'Éthiopienne', iso: 'ETH', continent: 'Afrique' },
    'Kenya': { nationalite: 'Kényane', iso: 'KEN', continent: 'Afrique' },
    'Ouganda': { nationalite: 'Ougandaise', iso: 'UGA', continent: 'Afrique' },
    'Tanzanie': { nationalite: 'Tanzanienne', iso: 'TZA', continent: 'Afrique' },
    'Nigeria': { nationalite: 'Nigériane', iso: 'NGA', continent: 'Afrique' },
    'Ghana': { nationalite: 'Ghanéenne', iso: 'GHA', continent: 'Afrique' },
    'Côte d\'Ivoire': { nationalite: 'Ivoirienne', iso: 'CIV', continent: 'Afrique' },
    'Sénégal': { nationalite: 'Sénégalaise', iso: 'SEN', continent: 'Afrique' },
    'Mali': { nationalite: 'Malienne', iso: 'MLI', continent: 'Afrique' },
    'Burkina Faso': { nationalite: 'Burkinabé', iso: 'BFA', continent: 'Afrique' },
    'Niger': { nationalite: 'Nigérienne', iso: 'NER', continent: 'Afrique' },
    'Guinée': { nationalite: 'Guinéenne', iso: 'GIN', continent: 'Afrique' },
    'Sierra Leone': { nationalite: 'Sierra-léonaise', iso: 'SLE', continent: 'Afrique' },
    'Liberia': { nationalite: 'Libérienne', iso: 'LBR', continent: 'Afrique' },
    'Cameroun': { nationalite: 'Camerounaise', iso: 'CMR', continent: 'Afrique' },
    'République centrafricaine': { nationalite: 'Centrafricaine', iso: 'CAF', continent: 'Afrique' },
    'Tchad': { nationalite: 'Tchadienne', iso: 'TCD', continent: 'Afrique' },
    'République démocratique du Congo': { nationalite: 'Congolaise (RDC)', iso: 'COD', continent: 'Afrique' },
    'République du Congo': { nationalite: 'Congolaise', iso: 'COG', continent: 'Afrique' },
    'Gabon': { nationalite: 'Gabonaise', iso: 'GAB', continent: 'Afrique' },
    'Guinée équatoriale': { nationalite: 'Équato-guinéenne', iso: 'GNQ', continent: 'Afrique' },
    'Angola': { nationalite: 'Angolaise', iso: 'AGO', continent: 'Afrique' },
    'Zambie': { nationalite: 'Zambienne', iso: 'ZMB', continent: 'Afrique' },
    'Zimbabwe': { nationalite: 'Zimbabwéenne', iso: 'ZWE', continent: 'Afrique' },
    'Afrique du Sud': { nationalite: 'Sud-africaine', iso: 'ZAF', continent: 'Afrique' },
    'Namibie': { nationalite: 'Namibienne', iso: 'NAM', continent: 'Afrique' },
    'Botswana': { nationalite: 'Botswanaise', iso: 'BWA', continent: 'Afrique' },
    'Lesotho': { nationalite: 'Lesothane', iso: 'LSO', continent: 'Afrique' },
    'Eswatini': { nationalite: 'Swazi', iso: 'SWZ', continent: 'Afrique' },
    'Mozambique': { nationalite: 'Mozambicaine', iso: 'MOZ', continent: 'Afrique' },
    'Madagascar': { nationalite: 'Malgache', iso: 'MDG', continent: 'Afrique' },
    'Maurice': { nationalite: 'Mauricienne', iso: 'MUS', continent: 'Afrique' },
    'Comores': { nationalite: 'Comorienne', iso: 'COM', continent: 'Afrique' },
    'Seychelles': { nationalite: 'Seychelloise', iso: 'SYC', continent: 'Afrique' },
    'Djibouti': { nationalite: 'Djiboutienne', iso: 'DJI', continent: 'Afrique' },
    'Somalie': { nationalite: 'Somalienne', iso: 'SOM', continent: 'Afrique' },
    'Érythrée': { nationalite: 'Érythréenne', iso: 'ERI', continent: 'Afrique' },
    'Rwanda': { nationalite: 'Rwandaise', iso: 'RWA', continent: 'Afrique' },
    'Burundi': { nationalite: 'Burundaise', iso: 'BDI', continent: 'Afrique' },
    'Malawi': { nationalite: 'Malawienne', iso: 'MWI', continent: 'Afrique' },

    // Asie
    'Afghanistan': { nationalite: 'Afghane', iso: 'AFG', continent: 'Asie' },
    'Pakistan': { nationalite: 'Pakistanaise', iso: 'PAK', continent: 'Asie' },
    'Inde': { nationalite: 'Indienne', iso: 'IND', continent: 'Asie' },
    'Bangladesh': { nationalite: 'Bangladaise', iso: 'BGD', continent: 'Asie' },
    'Sri Lanka': { nationalite: 'Sri-lankaise', iso: 'LKA', continent: 'Asie' },
    'Maldives': { nationalite: 'Maldivienne', iso: 'MDV', continent: 'Asie' },
    'Népal': { nationalite: 'Népalaise', iso: 'NPL', continent: 'Asie' },
    'Bhoutan': { nationalite: 'Bhoutanaise', iso: 'BTN', continent: 'Asie' },
    'Chine': { nationalite: 'Chinoise', iso: 'CHN', continent: 'Asie' },
    'Japon': { nationalite: 'Japonaise', iso: 'JPN', continent: 'Asie' },
    'Corée du Sud': { nationalite: 'Sud-coréenne', iso: 'KOR', continent: 'Asie' },
    'Corée du Nord': { nationalite: 'Nord-coréenne', iso: 'PRK', continent: 'Asie' },
    'Mongolie': { nationalite: 'Mongole', iso: 'MNG', continent: 'Asie' },
    'Taïwan': { nationalite: 'Taïwanaise', iso: 'TWN', continent: 'Asie' },
    'Hong Kong': { nationalite: 'Hongkongaise', iso: 'HKG', continent: 'Asie' },
    'Macao': { nationalite: 'Macanaise', iso: 'MAC', continent: 'Asie' },
    'Thaïlande': { nationalite: 'Thaïlandaise', iso: 'THA', continent: 'Asie' },
    'Vietnam': { nationalite: 'Vietnamienne', iso: 'VNM', continent: 'Asie' },
    'Laos': { nationalite: 'Laotienne', iso: 'LAO', continent: 'Asie' },
    'Cambodge': { nationalite: 'Cambodgienne', iso: 'KHM', continent: 'Asie' },
    'Myanmar': { nationalite: 'Birmane', iso: 'MMR', continent: 'Asie' },
    'Malaisie': { nationalite: 'Malaisienne', iso: 'MYS', continent: 'Asie' },
    'Singapour': { nationalite: 'Singapourienne', iso: 'SGP', continent: 'Asie' },
    'Indonésie': { nationalite: 'Indonésienne', iso: 'IDN', continent: 'Asie' },
    'Philippines': { nationalite: 'Philippine', iso: 'PHL', continent: 'Asie' },
    'Brunei': { nationalite: 'Brunéienne', iso: 'BRN', continent: 'Asie' },
    'Timor oriental': { nationalite: 'Timoraise', iso: 'TLS', continent: 'Asie' },
    'Iran': { nationalite: 'Iranienne', iso: 'IRN', continent: 'Asie' },
    'Irak': { nationalite: 'Irakienne', iso: 'IRQ', continent: 'Asie' },
    'Syrie': { nationalite: 'Syrienne', iso: 'SYR', continent: 'Asie' },
    'Liban': { nationalite: 'Libanaise', iso: 'LBN', continent: 'Asie' },
    'Jordanie': { nationalite: 'Jordanienne', iso: 'JOR', continent: 'Asie' },
    'Israël': { nationalite: 'Israélienne', iso: 'ISR', continent: 'Asie' },
    'Palestine': { nationalite: 'Palestinienne', iso: 'PSE', continent: 'Asie' },
    'Arabie saoudite': { nationalite: 'Saoudienne', iso: 'SAU', continent: 'Asie' },
    'Émirats arabes unis': { nationalite: 'Émirienne', iso: 'ARE', continent: 'Asie' },
    'Qatar': { nationalite: 'Qatarienne', iso: 'QAT', continent: 'Asie' },
    'Bahreïn': { nationalite: 'Bahreïnienne', iso: 'BHR', continent: 'Asie' },
    'Koweït': { nationalite: 'Koweïtienne', iso: 'KWT', continent: 'Asie' },
    'Oman': { nationalite: 'Omanaise', iso: 'OMN', continent: 'Asie' },
    'Yémen': { nationalite: 'Yéménite', iso: 'YEM', continent: 'Asie' },
    'Turquie': { nationalite: 'Turque', iso: 'TUR', continent: 'Asie' },
    'Chypre': { nationalite: 'Chypriote', iso: 'CYP', continent: 'Asie' },
    'Arménie': { nationalite: 'Arménienne', iso: 'ARM', continent: 'Asie' },
    'Géorgie': { nationalite: 'Géorgienne', iso: 'GEO', continent: 'Asie' },
    'Azerbaïdjan': { nationalite: 'Azerbaïdjanaise', iso: 'AZE', continent: 'Asie' },
    'Kazakhstan': { nationalite: 'Kazakhe', iso: 'KAZ', continent: 'Asie' },
    'Kirghizistan': { nationalite: 'Kirghize', iso: 'KGZ', continent: 'Asie' },
    'Tadjikistan': { nationalite: 'Tadjike', iso: 'TJK', continent: 'Asie' },
    'Turkménistan': { nationalite: 'Turkmène', iso: 'TKM', continent: 'Asie' },
    'Ouzbékistan': { nationalite: 'Ouzbèke', iso: 'UZB', continent: 'Asie' },

    // Amérique du Nord
    'États-Unis': { nationalite: 'Américaine', iso: 'USA', continent: 'Amérique du Nord' },
    'Canada': { nationalite: 'Canadienne', iso: 'CAN', continent: 'Amérique du Nord' },
    'Mexique': { nationalite: 'Mexicaine', iso: 'MEX', continent: 'Amérique du Nord' },
    'Guatemala': { nationalite: 'Guatémaltèque', iso: 'GTM', continent: 'Amérique du Nord' },
    'Belize': { nationalite: 'Bélizienne', iso: 'BLZ', continent: 'Amérique du Nord' },
    'Salvador': { nationalite: 'Salvadorienne', iso: 'SLV', continent: 'Amérique du Nord' },
    'Honduras': { nationalite: 'Hondurienne', iso: 'HND', continent: 'Amérique du Nord' },
    'Nicaragua': { nationalite: 'Nicaraguayenne', iso: 'NIC', continent: 'Amérique du Nord' },
    'Costa Rica': { nationalite: 'Costaricienne', iso: 'CRI', continent: 'Amérique du Nord' },
    'Panama': { nationalite: 'Panaméenne', iso: 'PAN', continent: 'Amérique du Nord' },
    'Cuba': { nationalite: 'Cubaine', iso: 'CUB', continent: 'Amérique du Nord' },
    'Jamaïque': { nationalite: 'Jamaïcaine', iso: 'JAM', continent: 'Amérique du Nord' },
    'Haïti': { nationalite: 'Haïtienne', iso: 'HTI', continent: 'Amérique du Nord' },
    'République dominicaine': { nationalite: 'Dominicaine', iso: 'DOM', continent: 'Amérique du Nord' },

    // Amérique du Sud
    'Brésil': { nationalite: 'Brésilienne', iso: 'BRA', continent: 'Amérique du Sud' },
    'Argentine': { nationalite: 'Argentine', iso: 'ARG', continent: 'Amérique du Sud' },
    'Chili': { nationalite: 'Chilienne', iso: 'CHL', continent: 'Amérique du Sud' },
    'Pérou': { nationalite: 'Péruvienne', iso: 'PER', continent: 'Amérique du Sud' },
    'Bolivie': { nationalite: 'Bolivienne', iso: 'BOL', continent: 'Amérique du Sud' },
    'Équateur': { nationalite: 'Équatorienne', iso: 'ECU', continent: 'Amérique du Sud' },
    'Colombie': { nationalite: 'Colombienne', iso: 'COL', continent: 'Amérique du Sud' },
    'Venezuela': { nationalite: 'Vénézuélienne', iso: 'VEN', continent: 'Amérique du Sud' },
    'Guyana': { nationalite: 'Guyanienne', iso: 'GUY', continent: 'Amérique du Sud' },
    'Suriname': { nationalite: 'Surinamaise', iso: 'SUR', continent: 'Amérique du Sud' },
    'Guyane française': { nationalite: 'Française', iso: 'GUF', continent: 'Amérique du Sud' },
    'Paraguay': { nationalite: 'Paraguayenne', iso: 'PRY', continent: 'Amérique du Sud' },
    'Uruguay': { nationalite: 'Uruguayenne', iso: 'URY', continent: 'Amérique du Sud' },

    // Océanie
    'Australie': { nationalite: 'Australienne', iso: 'AUS', continent: 'Océanie' },
    'Nouvelle-Zélande': { nationalite: 'Néo-zélandaise', iso: 'NZL', continent: 'Océanie' },
    'Papouasie-Nouvelle-Guinée': { nationalite: 'Papouane', iso: 'PNG', continent: 'Océanie' },
    'Fidji': { nationalite: 'Fidjienne', iso: 'FJI', continent: 'Océanie' },
    'Vanuatu': { nationalite: 'Vanuatuane', iso: 'VUT', continent: 'Océanie' },
    'Samoa': { nationalite: 'Samoane', iso: 'WSM', continent: 'Océanie' },
    'Tonga': { nationalite: 'Tongienne', iso: 'TON', continent: 'Océanie' },
    'Kiribati': { nationalite: 'Kiribatienne', iso: 'KIR', continent: 'Océanie' },
    'Tuvalu': { nationalite: 'Tuvaluane', iso: 'TUV', continent: 'Océanie' },
    'Nauru': { nationalite: 'Nauruane', iso: 'NRU', continent: 'Océanie' },
    'Palaos': { nationalite: 'Palaosienne', iso: 'PLW', continent: 'Océanie' },
    'États fédérés de Micronésie': { nationalite: 'Micronésienne', iso: 'FSM', continent: 'Océanie' },
    'Îles Marshall': { nationalite: 'Marshallaise', iso: 'MHL', continent: 'Océanie' }
};

// Fonction de recherche floue pour trouver les pays correspondants
function rechercherPays(terme) {
    const termeLower = terme.toLowerCase().trim();
    if (termeLower.length < 2) return [];
    
    const resultats = [];
    
    // Recherche exacte au début
    for (const pays in PAYS_DATABASE) {
        if (pays.toLowerCase().startsWith(termeLower)) {
            resultats.push(pays);
        }
    }
    
    // Recherche contenant le terme (si pas assez de résultats)
    if (resultats.length < 5) {
        for (const pays in PAYS_DATABASE) {
            if (pays.toLowerCase().includes(termeLower) && !resultats.includes(pays)) {
                resultats.push(pays);
            }
        }
    }
    
    return resultats.slice(0, 8); // Maximum 8 suggestions
}

// Auto-remplissage intelligent des champs
function remplirChampsPays(pays) {
    const infos = PAYS_DATABASE[pays];
    if (!infos) return;

    const nationaliteField = document.getElementById('nationalite');
    const isoField = document.getElementById('iso');
    const continentField = document.getElementById('continent');

    console.log('🔄 Remplissage automatique pour:', pays, infos);

    // Animation de remplissage plus visible
    const fields = [nationaliteField, isoField, continentField].filter(f => f);
    
    fields.forEach(field => {
        field.style.background = '#e8f5e8';
        field.style.borderLeft = '4px solid #28a745';
        field.classList.add('is-auto-filled');
    });

    setTimeout(() => {
        // Nationalité : F pour France, E pour les autres
        if (nationaliteField) {
            nationaliteField.value = (pays === 'France' || pays.toLowerCase() === 'france') ? 'F' : 'E';
        }
        if (isoField) isoField.value = infos.iso;
        if (continentField) continentField.value = infos.continent;
        
        console.log('✅ Champs remplis:', {
            nationalite: (pays === 'France' || pays.toLowerCase() === 'france') ? 'F' : 'E',
            iso: infos.iso, 
            continent: infos.continent
        });
        
        // Retirer l'animation après 2 secondes mais garder la classe
        setTimeout(() => {
            fields.forEach(field => {
                field.style.background = '';
                field.style.borderLeft = '';
            });
        }, 2000);
    }, 200);
}
// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    const paysInput = document.getElementById('pays_naissance');
    const paysList = document.getElementById('pays-list');
    
    // CSS pour les champs auto-remplis
    const style = document.createElement('style');
    style.textContent = `
        .auto-filled.is-auto-filled {
            background-color: #e8f5e8 !important;
            border-left: 4px solid #28a745;
        }
        .auto-filled.is-auto-filled:focus {
            background-color: #fff !important;
            border-left: 4px solid #007bff;
        }
    `;
    document.head.appendChild(style);
    
    // Remplir la datalist avec tous les pays
    function remplirDatalist() {
        if (!paysList) return;
        paysList.innerHTML = '';
        Object.keys(PAYS_DATABASE).forEach(pays => {
            const option = document.createElement('option');
            option.value = pays;
            paysList.appendChild(option);
        });
    }
    
    // Fonction pour gérer la sélection de pays
    function gererSelectionPays() {
        const valeur = paysInput.value.trim();
        console.log('🔍 Pays sélectionné:', valeur);
        
        if (PAYS_DATABASE[valeur]) {
            console.log('✅ Pays trouvé dans la base, remplissage automatique...');
            remplirChampsPays(valeur);
        } else {
            console.log('❌ Pays non trouvé dans la base:', valeur);
            // Recherche approximative
            const paysProche = Object.keys(PAYS_DATABASE).find(pays => 
                pays.toLowerCase() === valeur.toLowerCase()
            );
            if (paysProche) {
                console.log('✅ Pays trouvé par recherche approximative:', paysProche);
                paysInput.value = paysProche;
                remplirChampsPays(paysProche);
            }
        }
    }
    
    // Écouter les changements dans le champ pays
    if (paysInput) {
        // Event 'input' pour la saisie en temps réel
        paysInput.addEventListener('input', function() {
            const valeur = this.value.trim();
            
            // Mettre à jour les suggestions en temps réel
            if (valeur.length >= 2) {
                const suggestions = rechercherPays(valeur);
                if (paysList) {
                    paysList.innerHTML = '';
                    suggestions.forEach(pays => {
                        const option = document.createElement('option');
                        option.value = pays;
                        paysList.appendChild(option);
                    });
                }
            }
            
            // Si correspondance exacte, remplir immédiatement
            if (PAYS_DATABASE[valeur]) {
                remplirChampsPays(valeur);
            }
        });
        
        // Event 'change' pour la sélection finale
        paysInput.addEventListener('change', gererSelectionPays);
        
        // Event 'blur' pour la perte de focus
        paysInput.addEventListener('blur', function() {
            setTimeout(gererSelectionPays, 100); // Petit délai pour laisser la datalist se fermer
        });
        
        // Event spécial pour détecter la sélection depuis datalist
        paysInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === 'Tab') {
                setTimeout(gererSelectionPays, 50);
            }
        });
    }
    
    // Initialiser la datalist
    remplirDatalist();
    
    console.log('🚀 Système de pays amélioré initialisé!');
    
    // Validation en temps réel du numéro d'apprenant
    const numeroInput = document.getElementById('numero_apprenant');
    if (numeroInput) {
        numeroInput.addEventListener('input', function() {
            const valeur = this.value;
            const regex = /^\d{2}-\d{3}$/;
            
            if (valeur && !regex.test(valeur)) {
                this.setCustomValidity('Format requis: XX-XXX (ex: 25-001)');
                this.style.borderColor = '#dc3545';
            } else {
                this.setCustomValidity('');
                this.style.borderColor = '';
            }
        });
    }
    
    // Barre de progression du formulaire
    const progressBar = document.getElementById('progress-bar');
    const form = document.querySelector('form');
    
    if (form && progressBar) {
        const requiredFields = form.querySelectorAll('input[required], select[required]');
        
        function updateProgress() {
            let filledFields = 0;
            requiredFields.forEach(field => {
                if (field.value.trim() !== '') {
                    filledFields++;
                }
            });
            
            const progress = (filledFields / requiredFields.length) * 100;
            progressBar.style.width = progress + '%';
            
            // Changer la couleur selon le progrès
            if (progress < 30) {
                progressBar.className = 'progress-bar bg-danger';
            } else if (progress < 70) {
                progressBar.className = 'progress-bar bg-warning';
            } else {
                progressBar.className = 'progress-bar bg-success';
            }
        }
        
        // Écouter les changements dans tous les champs requis
        requiredFields.forEach(field => {
            field.addEventListener('input', updateProgress);
            field.addEventListener('change', updateProgress);
        });
        
        // Initialiser le progrès
        updateProgress();
        
        // Validation avant soumission
        form.addEventListener('submit', function(e) {
            const progress = (document.querySelectorAll('input[required]:not(:placeholder-shown), select[required]:not([value=""])').length / requiredFields.length) * 100;
            
            if (progress < 100) {
                e.preventDefault();
                alert('⚠️ Veuillez remplir tous les champs obligatoires avant de soumettre le formulaire.');
                
                // Faire défiler vers le premier champ vide
                const firstEmpty = form.querySelector('input[required]:placeholder-shown, select[required][value=""]');
                if (firstEmpty) {
                    firstEmpty.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstEmpty.focus();
                }
            }
        });
    }
    
    // Auto-génération du nom complet côté serveur
    const nomInput = document.getElementById('nom');
    const prenomInput = document.getElementById('prenom');
    
    function updateNomComplet() {
        const nom = nomInput.value.trim();
        const prenom = prenomInput.value.trim();
        
        // Le nom complet sera généré automatiquement côté serveur
        if (nom && prenom) {
            console.log(`✨ Nom complet qui sera généré: ${prenom} ${nom}`);
        }
    }
    
    if (nomInput && prenomInput) {
        nomInput.addEventListener('input', updateNomComplet);
        prenomInput.addEventListener('input', updateNomComplet);
    }
    
    // Amélioration UX: Focus automatique sur le prochain champ
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach((input, index) => {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                const nextInput = inputs[index + 1];
                if (nextInput) {
                    nextInput.focus();
                }
            }
        });
    });
    
    // Amélioration des champs téléphone et code postal
    const phoneInput = document.getElementById('telephone');
    const postalInput = document.getElementById('code_postal');
    
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length <= 10) {
                this.value = value.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
            }
        });
    }
    
    if (postalInput) {
        postalInput.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '').substring(0, 5);
        });
    }
    
    console.log('🚀 Script d\'amélioration UX chargé - Auto-remplissage intelligent activé !');
    
    // === ANCIEN CODE DE PRÉ-REMPLISSAGE (conservé pour compatibilité) ===
    function preremplirChampsDepuisURL() {
        try {
            console.log('🔍 Vérification des paramètres URL pour pré-remplissage...');
            
            // Lire les paramètres de l'URL
            const urlParams = new URLSearchParams(window.location.search);
            const nom = urlParams.get('nom');
            const prenom = urlParams.get('prenom');
            const retour = urlParams.get('retour');
            
            console.log('📋 Paramètres détectés:', { nom, prenom, retour });
            
            // Pré-remplir le nom si fourni
            if (nom) {
                const champNom = document.getElementById('nom');
                if (champNom) {
                    champNom.value = nom;
                    console.log(`✅ Champ nom pré-rempli: "${nom}"`);
                    
                    // Ajouter un effet visuel pour montrer que c'est pré-rempli
                    champNom.style.backgroundColor = '#e7f3ff';
                    setTimeout(() => {
                        champNom.style.backgroundColor = '';
                    }, 2000);
                }
            }
            
            // Pré-remplir le prénom si fourni
            if (prenom) {
                const champPrenom = document.getElementById('prenom');
                if (champPrenom) {
                    champPrenom.value = prenom;
                    console.log(`✅ Champ prénom pré-rempli: "${prenom}"`);
                    
                    // Effet visuel
                    champPrenom.style.backgroundColor = '#e7f3ff';
                    setTimeout(() => {
                        champPrenom.style.backgroundColor = '';
                    }, 2000);
                }
            }
            
            // Afficher une notification si des champs ont été pré-remplis
            if (nom || prenom) {
                afficherNotificationPreremplissage(nom, prenom, retour);
            }
            
        } catch (error) {
            console.error('❌ Erreur lors du pré-remplissage:', error);
        }
    }

    // Afficher une notification pour informer l'utilisateur
    function afficherNotificationPreremplissage(nom, prenom, retour) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show';
        notification.style.marginTop = '10px';
        notification.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <strong>Pré-remplissage automatique :</strong> 
            Les champs nom "${nom}" et prénom "${prenom}" ont été remplis automatiquement.
            ${retour === 'pointage' ? '<br><small>Vous venez de la page de pointage.</small>' : ''}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insérer après le titre
        const titre = document.querySelector('h2');
        if (titre) {
            titre.insertAdjacentElement('afterend', notification);
            
            // Auto-masquer après 5 secondes
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 5000);
        }
    }
    
    // MAINTENANT appeler la fonction (après l'avoir définie)
    preremplirChampsDepuisURL();
    
    // Validation en temps réel
    const validators = {
        // Validation du numéro d'apprenant
        numero_apprenant: function(value) {
            const regex = /^[0-9]{2}-[0-9]{3}$/;
            return regex.test(value) || value === '';
        },
        
        // Validation du code postal français
        code_postal: function(value) {
            const regex = /^[0-9]{5}$/;
            return regex.test(value) || value === '';
        },
        
        // Validation de l'email
        email: function(value) {
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return regex.test(value) || value === '';
        },
        
        // Validation du téléphone français
        telephone: function(value) {
            const regex = /^(?:(?:\+33|0)[1-9](?:[0-9]{8}))$/;
            const formatted = value.replace(/[\s\.-]/g, '');
            return regex.test(formatted) || value === '';
        },
        
        // Validation de la date de naissance (pas dans le futur, âge raisonnable)
        date_naissance: function(value) {
            if (!value) return true;
            const birthDate = new Date(value);
            const today = new Date();
            const age = today.getFullYear() - birthDate.getFullYear();
            return birthDate < today && age >= 0 && age <= 120;
        }
    };
    
    // Fonction pour afficher les erreurs
    function showError(input, message) {
        clearError(input);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        input.parentNode.appendChild(errorDiv);
        input.classList.add('is-invalid');
    }
    
    // Fonction pour effacer les erreurs
    function clearError(input) {
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) errorDiv.remove();
        input.classList.remove('is-invalid');
        input.classList.remove('is-valid');
    }
    
    // Fonction pour marquer comme valide
    function showValid(input) {
        clearError(input);
        input.classList.add('is-valid');
    }
    
    // Validation en temps réel pour chaque champ
    Object.keys(validators).forEach(fieldName => {
        const field = document.getElementById(fieldName);
        if (field) {
            field.addEventListener('blur', function() {
                const value = this.value.trim();
                
                if (validators[fieldName](value)) {
                    if (value !== '') showValid(this);
                    else clearError(this);
                } else {
                    let message = '';
                    switch(fieldName) {
                        case 'numero_apprenant':
                            message = 'Le numéro doit être au format AA-NNN (ex: 25-001)';
                            break;
                        case 'code_postal':
                            message = 'Le code postal doit contenir 5 chiffres';
                            break;
                        case 'email':
                            message = 'Adresse email invalide';
                            break;
                        case 'telephone':
                            message = 'Numéro de téléphone invalide (format français)';
                            break;
                        case 'date_naissance':
                            message = 'Date de naissance invalide';
                            break;
                    }
                    showError(this, message);
                }
            });
        }
    });
    
    // Formatage automatique pour le numéro d'apprenant
    const numeroApprenantField = document.getElementById('numero_apprenant');
    if (numeroApprenantField) {
        numeroApprenantField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^0-9]/g, '');
            if (value.length > 2) {
                value = value.substring(0, 2) + '-' + value.substring(2, 5);
            }
            e.target.value = value;
        });
    }
    
    // Conversion automatique du nom en majuscules
    const nomField = document.getElementById('nom');
    if (nomField) {
        nomField.addEventListener('input', function() {
            // Convertir en majuscules en temps réel
            this.value = this.value.toUpperCase();
        });
        
        // Également au moment de la perte de focus pour s'assurer de la conversion
        nomField.addEventListener('blur', function() {
            this.value = this.value.toUpperCase();
        });
    }
    
    // Conversion automatique de la première lettre du prénom en majuscule
    const prenomField = document.getElementById('prenom');
    if (prenomField) {
        prenomField.addEventListener('blur', function() {
            // Capitaliser la première lettre et mettre le reste en minuscules
            if (this.value.trim() !== '') {
                // Gestion des prénoms composés (Jean-Pierre, Marie Claire, etc.)
                this.value = this.value.trim()
                    .toLowerCase()
                    .replace(/\b[a-z]/g, function(match) {
                        return match.toUpperCase();
                    });
            }
        });
    }
    
    // Validation des champs obligatoires
    const requiredFields = ['nom', 'prenom', 'adresse', 'code_postal', 'ville'];
    
    function validateRequiredFields() {
        let isValid = true;
        
        requiredFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field && !field.value.trim()) {
                showError(field, 'Ce champ est obligatoire');
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    // Auto-complétion ville basée sur code postal
    const codePostalField = document.getElementById('code_postal');
    const villeField = document.getElementById('ville');
    
    if (codePostalField && villeField) {
        codePostalField.addEventListener('blur', function() {
            const cp = this.value.trim();
            if (cp.length === 5 && /^[0-9]{5}$/.test(cp)) {
                // Suggestions de villes basées sur les codes postaux courants
                const suggestions = {
                    '75001': 'PARIS',
                    '69001': 'LYON',
                    '13001': 'MARSEILLE',
                    '59000': 'LILLE',
                    '31000': 'TOULOUSE',
                    '44000': 'NANTES',
                    '67000': 'STRASBOURG',
                    '33000': 'BORDEAUX',
                    '35000': 'RENNES',
                    '34000': 'MONTPELLIER',
                    '08000': 'CHARLEVILLE-MEZIERES'
                };
                
                if (suggestions[cp] && !villeField.value.trim()) {
                    villeField.value = suggestions[cp];
                    showValid(villeField);
                }
            }
        });
    }

    // Auto-complétion pays de naissance avec menu déroulant
    const paysField = document.getElementById('pays_naissance');
    if (paysField) {
        // Liste des pays les plus courants
        const paysList = [
            'France', 'Algérie', 'Maroc', 'Tunisie', 'Sénégal', 'Mali', 'Burkina Faso',
            'Côte d\'Ivoire', 'Niger', 'Guinée', 'Madagascar', 'Cameroun', 'République démocratique du Congo',
            'Syrie', 'Afghanistan', 'Irak', 'Iran', 'Pakistan', 'Bangladesh', 'Sri Lanka',
            'Turquie', 'Liban', 'Égypte', 'Libye', 'Soudan', 'Érythrée', 'Somalie',
            'Chine', 'Inde', 'Vietnam', 'Cambodge', 'Laos', 'Thaïlande', 'Philippines',
            'Russie', 'Ukraine', 'Pologne', 'Roumanie', 'Bulgarie', 'Serbie', 'Bosnie-Herzégovine',
            'Espagne', 'Portugal', 'Italie', 'Allemagne', 'Belgique', 'Pays-Bas', 'Royaume-Uni',
            'Brésil', 'Argentine', 'Chili', 'Colombie', 'Pérou', 'Venezuela', 'Équateur',
            'États-Unis', 'Canada', 'Mexique', 'Haïti', 'République dominicaine', 'Cuba'
        ].sort();
        
        let suggestionBox = null;
        let selectedIndex = -1;
        
        // Créer la boîte de suggestions
        function createSuggestionBox() {
            suggestionBox = document.createElement('div');
            suggestionBox.className = 'suggestion-box';
            suggestionBox.style.cssText = `
                position: absolute;
                background: white;
                border: 1px solid #ccc;
                border-top: none;
                max-height: 200px;
                overflow-y: auto;
                z-index: 1000;
                width: 100%;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            `;
            paysField.parentNode.style.position = 'relative';
            paysField.parentNode.appendChild(suggestionBox);
        }
        
        // Afficher les suggestions
        function showSuggestions(value) {
            if (!suggestionBox) createSuggestionBox();
            
            const filtered = paysList.filter(pays => 
                pays.toLowerCase().includes(value.toLowerCase())
            ).slice(0, 10); // Limiter à 10 suggestions
            
            if (filtered.length === 0 || (filtered.length === 1 && filtered[0].toLowerCase() === value.toLowerCase())) {
                hideSuggestions();
                return;
            }
            
            suggestionBox.innerHTML = '';
            selectedIndex = -1;
            
            filtered.forEach((pays, index) => {
                const item = document.createElement('div');
                item.textContent = pays;
                item.style.cssText = `
                    padding: 8px 12px;
                    cursor: pointer;
                    border-bottom: 1px solid #eee;
                `;
                
                item.addEventListener('mouseenter', function() {
                    clearSelection();
                    this.style.backgroundColor = '#007bff';
                    this.style.color = 'white';
                    selectedIndex = index;
                });
                
                item.addEventListener('mouseleave', function() {
                    this.style.backgroundColor = '';
                    this.style.color = '';
                });
                
                item.addEventListener('click', function() {
                    paysField.value = pays;
                    hideSuggestions();
                    paysField.focus();
                });
                
                suggestionBox.appendChild(item);
            });
            
            suggestionBox.style.display = 'block';
        }
        
        // Masquer les suggestions
        function hideSuggestions() {
            if (suggestionBox) {
                suggestionBox.style.display = 'none';
            }
            selectedIndex = -1;
        }
        
        // Effacer la sélection
        function clearSelection() {
            if (suggestionBox) {
                const items = suggestionBox.querySelectorAll('div');
                items.forEach(item => {
                    item.style.backgroundColor = '';
                    item.style.color = '';
                });
            }
        }
        
        // Sélectionner un élément
        function selectItem(index) {
            if (suggestionBox) {
                const items = suggestionBox.querySelectorAll('div');
                clearSelection();
                if (items[index]) {
                    items[index].style.backgroundColor = '#007bff';
                    items[index].style.color = 'white';
                }
            }
        }
        
        // Événements du champ pays
        paysField.addEventListener('input', function() {
            const value = this.value.trim();
            if (value.length >= 2) {
                showSuggestions(value);
            } else {
                hideSuggestions();
            }
        });
        
        paysField.addEventListener('keydown', function(e) {
            if (!suggestionBox || suggestionBox.style.display === 'none') return;
            
            const items = suggestionBox.querySelectorAll('div');
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    selectedIndex = (selectedIndex + 1) % items.length;
                    selectItem(selectedIndex);
                    break;
                    
                case 'ArrowUp':
                    e.preventDefault();
                    selectedIndex = selectedIndex <= 0 ? items.length - 1 : selectedIndex - 1;
                    selectItem(selectedIndex);
                    break;
                    
                case 'Enter':
                    e.preventDefault();
                    if (selectedIndex >= 0 && items[selectedIndex]) {
                        this.value = items[selectedIndex].textContent;
                        hideSuggestions();
                    }
                    break;
                    
                case 'Escape':
                    hideSuggestions();
                    break;
            }
        });
        
        paysField.addEventListener('blur', function() {
            // Délai pour permettre le clic sur les suggestions
            setTimeout(() => hideSuggestions(), 200);
        });
        
        // Masquer lors du clic ailleurs
        document.addEventListener('click', function(e) {
            if (!paysField.contains(e.target) && (!suggestionBox || !suggestionBox.contains(e.target))) {
                hideSuggestions();
            }
        });
    }

    // Auto-complétion nationalité avec menu déroulant
    const nationaliteField = document.getElementById('nationalite');
    if (nationaliteField) {
        // Liste des nationalités les plus courantes
        const nationalitesList = [
            'Française', 'Algérienne', 'Marocaine', 'Tunisienne', 'Sénégalaise', 'Malienne', 'Burkinabè',
            'Ivoirienne', 'Nigérienne', 'Guinéenne', 'Malgache', 'Camerounaise', 'Congolaise',
            'Syrienne', 'Afghane', 'Irakienne', 'Iranienne', 'Pakistanaise', 'Bangladaise', 'Sri-lankaise',
            'Turque', 'Libanaise', 'Égyptienne', 'Libyenne', 'Soudanaise', 'Érythréenne', 'Somalienne',
            'Chinoise', 'Indienne', 'Vietnamienne', 'Cambodgienne', 'Laotienne', 'Thaïlandaise', 'Philippine',
            'Russe', 'Ukrainienne', 'Polonaise', 'Roumaine', 'Bulgare', 'Serbe', 'Bosniaque',
            'Espagnole', 'Portugaise', 'Italienne', 'Allemande', 'Belge', 'Néerlandaise', 'Britannique',
            'Brésilienne', 'Argentine', 'Chilienne', 'Colombienne', 'Péruvienne', 'Vénézuélienne', 'Équatorienne',
            'Américaine', 'Canadienne', 'Mexicaine', 'Haïtienne', 'Dominicaine', 'Cubaine'
        ].sort();
        
        let nationaliteSuggestionBox = null;
        let nationaliteSelectedIndex = -1;
        
        // Créer la boîte de suggestions pour nationalité
        function createNationaliteSuggestionBox() {
            nationaliteSuggestionBox = document.createElement('div');
            nationaliteSuggestionBox.className = 'suggestion-box-nationalite';
            nationaliteSuggestionBox.style.cssText = `
                position: absolute;
                background: white;
                border: 1px solid #ccc;
                border-top: none;
                max-height: 200px;
                overflow-y: auto;
                z-index: 1000;
                width: 100%;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            `;
            nationaliteField.parentNode.style.position = 'relative';
            nationaliteField.parentNode.appendChild(nationaliteSuggestionBox);
        }
        
        // Afficher les suggestions pour nationalité
        function showNationaliteSuggestions(value) {
            if (!nationaliteSuggestionBox) createNationaliteSuggestionBox();
            
            const filtered = nationalitesList.filter(nationalite => 
                nationalite.toLowerCase().includes(value.toLowerCase())
            ).slice(0, 10); // Limiter à 10 suggestions
            
            if (filtered.length === 0 || (filtered.length === 1 && filtered[0].toLowerCase() === value.toLowerCase())) {
                hideNationaliteSuggestions();
                return;
            }
            
            nationaliteSuggestionBox.innerHTML = '';
            nationaliteSelectedIndex = -1;
            
            filtered.forEach((nationalite, index) => {
                const item = document.createElement('div');
                item.textContent = nationalite;
                item.style.cssText = `
                    padding: 8px 12px;
                    cursor: pointer;
                    border-bottom: 1px solid #eee;
                `;
                
                item.addEventListener('mouseenter', function() {
                    clearNationaliteSelection();
                    this.style.backgroundColor = '#007bff';
                    this.style.color = 'white';
                    nationaliteSelectedIndex = index;
                });
                
                item.addEventListener('mouseleave', function() {
                    this.style.backgroundColor = '';
                    this.style.color = '';
                });
                
                item.addEventListener('click', function() {
                    nationaliteField.value = nationalite;
                    hideNationaliteSuggestions();
                    nationaliteField.focus();
                });
                
                nationaliteSuggestionBox.appendChild(item);
            });
            
            nationaliteSuggestionBox.style.display = 'block';
        }
        
        // Masquer les suggestions pour nationalité
        function hideNationaliteSuggestions() {
            if (nationaliteSuggestionBox) {
                nationaliteSuggestionBox.style.display = 'none';
            }
            nationaliteSelectedIndex = -1;
        }
        
        // Effacer la sélection pour nationalité
        function clearNationaliteSelection() {
            if (nationaliteSuggestionBox) {
                const items = nationaliteSuggestionBox.querySelectorAll('div');
                items.forEach(item => {
                    item.style.backgroundColor = '';
                    item.style.color = '';
                });
            }
        }
        
        // Sélectionner un élément pour nationalité
        function selectNationaliteItem(index) {
            if (nationaliteSuggestionBox) {
                const items = nationaliteSuggestionBox.querySelectorAll('div');
                clearNationaliteSelection();
                if (items[index]) {
                    items[index].style.backgroundColor = '#007bff';
                    items[index].style.color = 'white';
                }
            }
        }
        
        // Événements du champ nationalité
        nationaliteField.addEventListener('input', function() {
            const value = this.value.trim();
            if (value.length >= 2) {
                showNationaliteSuggestions(value);
            } else {
                hideNationaliteSuggestions();
            }
        });
        
        nationaliteField.addEventListener('keydown', function(e) {
            if (!nationaliteSuggestionBox || nationaliteSuggestionBox.style.display === 'none') return;
            
            const items = nationaliteSuggestionBox.querySelectorAll('div');
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    nationaliteSelectedIndex = (nationaliteSelectedIndex + 1) % items.length;
                    selectNationaliteItem(nationaliteSelectedIndex);
                    break;
                    
                case 'ArrowUp':
                    e.preventDefault();
                    nationaliteSelectedIndex = nationaliteSelectedIndex <= 0 ? items.length - 1 : nationaliteSelectedIndex - 1;
                    selectNationaliteItem(nationaliteSelectedIndex);
                    break;
                    
                case 'Enter':
                    e.preventDefault();
                    if (nationaliteSelectedIndex >= 0 && items[nationaliteSelectedIndex]) {
                        this.value = items[nationaliteSelectedIndex].textContent;
                        hideNationaliteSuggestions();
                    }
                    break;
                    
                case 'Escape':
                    hideNationaliteSuggestions();
                    break;
            }
        });
        
        nationaliteField.addEventListener('blur', function() {
            // Délai pour permettre le clic sur les suggestions
            setTimeout(() => hideNationaliteSuggestions(), 200);
        });
        
        // Masquer lors du clic ailleurs
        document.addEventListener('click', function(e) {
            if (!nationaliteField.contains(e.target) && (!nationaliteSuggestionBox || !nationaliteSuggestionBox.contains(e.target))) {
                hideNationaliteSuggestions();
            }
        });
    }
    
    // Auto-complétion pour les langues parlées avec gestion multiple
    const languesField = document.getElementById('langues_parlees');
    if (languesField) {
        // Liste des langues les plus courantes
        const languesList = [
            'Français', 'Anglais', 'Espagnol', 'Portugais', 'Italien', 'Allemand', 'Néerlandais', 'Russe',
            'Arabe', 'Berbère', 'Kabyle', 'Tamashek', 'Wolof', 'Peul', 'Bambara', 'Soninké', 'Malinké',
            'Chinois (Mandarin)', 'Chinois (Cantonais)', 'Hindi', 'Ourdou', 'Bengali', 'Punjabi', 'Tamil',
            'Japonais', 'Coréen', 'Vietnamien', 'Thaï', 'Tagalog', 'Indonésien', 'Malais',
            'Turc', 'Persan', 'Kurde', 'Hébreu', 'Arménien', 'Géorgien', 'Azéri', 'Pashto', 'Dari',
            'Swahili', 'Amharique', 'Tigrinya', 'Somali', 'Haoussa', 'Yoruba', 'Igbo',
            'Albanais', 'Bosniaque', 'Croate', 'Serbe', 'Bulgare', 'Roumain', 'Hongrois', 'Tchèque', 'Polonais',
            'Grec', 'Macédonien', 'Slovène', 'Slovaque', 'Lituanien', 'Letton', 'Estonien',
            'Ukrainien', 'Biélorusse', 'Moldave', 'Finnois', 'Suédois', 'Norvégien', 'Danois', 'Islandais'
        ].sort();
        
        let languesSuggestionBox = null;
        let languesSelectedIndex = -1;
        let currentLangues = [];
        
        // Créer la boîte de suggestions pour les langues
        function createLanguesSuggestionBox() {
            languesSuggestionBox = document.createElement('div');
            languesSuggestionBox.className = 'suggestion-box-langues';
            languesSuggestionBox.style.cssText = `
                position: absolute;
                background: white;
                border: 1px solid #007bff;
                border-radius: 4px;
                max-height: 200px;
                overflow-y: auto;
                z-index: 1000;
                width: 100%;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                display: none;
            `;
            languesField.parentNode.style.position = 'relative';
            languesField.parentNode.appendChild(languesSuggestionBox);
        }
        
        // Analyser les langues déjà saisies
        function parseCurrentLangues() {
            const value = languesField.value;
            if (!value.trim()) return [];
            return value.split(',').map(lang => lang.trim()).filter(lang => lang);
        }
        
        // Obtenir le terme de recherche actuel
        function getCurrentSearchTerm() {
            const value = languesField.value;
            const lastCommaIndex = value.lastIndexOf(',');
            return lastCommaIndex >= 0 ? value.substring(lastCommaIndex + 1).trim() : value.trim();
        }
        
        // Afficher les suggestions de langues
        function showLanguesSuggestions(searchTerm) {
            if (!languesSuggestionBox) createLanguesSuggestionBox();
            
            if (searchTerm.length < 2) {
                hideLanguesSuggestions();
                return;
            }
            
            currentLangues = parseCurrentLangues();
            const filteredLangues = languesList.filter(langue => 
                langue.toLowerCase().includes(searchTerm.toLowerCase()) &&
                !currentLangues.some(currentLang => currentLang.toLowerCase() === langue.toLowerCase())
            );
            
            if (filteredLangues.length === 0) {
                hideLanguesSuggestions();
                return;
            }
            
            languesSuggestionBox.innerHTML = '';
            languesSelectedIndex = -1;
            
            filteredLangues.slice(0, 10).forEach((langue, index) => {
                const div = document.createElement('div');
                div.textContent = langue;
                div.style.cssText = `
                    padding: 8px 12px;
                    cursor: pointer;
                    border-bottom: 1px solid #eee;
                    transition: background-color 0.2s;
                `;
                
                div.addEventListener('mouseenter', () => {
                    div.style.backgroundColor = '#007bff';
                    div.style.color = 'white';
                });
                
                div.addEventListener('mouseleave', () => {
                    div.style.backgroundColor = 'white';
                    div.style.color = 'black';
                });
                
                div.addEventListener('click', () => selectLangue(langue));
                languesSuggestionBox.appendChild(div);
            });
            
            languesSuggestionBox.style.display = 'block';
        }
        
        // Masquer les suggestions
        function hideLanguesSuggestions() {
            if (languesSuggestionBox) {
                languesSuggestionBox.style.display = 'none';
                languesSelectedIndex = -1;
            }
        }
        
        // Sélectionner une langue
        function selectLangue(langue) {
            const value = languesField.value;
            const lastCommaIndex = value.lastIndexOf(',');
            
            if (lastCommaIndex >= 0) {
                // Remplacer le terme de recherche actuel
                languesField.value = value.substring(0, lastCommaIndex + 1) + ' ' + langue + ', ';
            } else {
                // Première langue
                languesField.value = langue + ', ';
            }
            
            hideLanguesSuggestions();
            updateLanguesDisplay();
            languesField.focus();
        }
        
        // Naviguer avec les touches
        function navigateLanguesSuggestions(direction) {
            const suggestions = languesSuggestionBox.querySelectorAll('div');
            if (suggestions.length === 0) return;
            
            // Réinitialiser le style de l'élément précédemment sélectionné
            if (languesSelectedIndex >= 0 && languesSelectedIndex < suggestions.length) {
                suggestions[languesSelectedIndex].style.backgroundColor = 'white';
                suggestions[languesSelectedIndex].style.color = 'black';
            }
            
            // Calculer le nouvel index
            if (direction === 'down') {
                languesSelectedIndex = languesSelectedIndex < suggestions.length - 1 ? languesSelectedIndex + 1 : 0;
            } else {
                languesSelectedIndex = languesSelectedIndex > 0 ? languesSelectedIndex - 1 : suggestions.length - 1;
            }
            
            // Appliquer le style à l'élément sélectionné
            suggestions[languesSelectedIndex].style.backgroundColor = '#007bff';
            suggestions[languesSelectedIndex].style.color = 'white';
        }
        
        // Créer la zone d'affichage des langues sélectionnées
        function createLanguesDisplay() {
            const display = document.createElement('div');
            display.id = 'langues-display';
            display.style.cssText = `
                margin-top: 8px;
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
            `;
            languesField.parentNode.appendChild(display);
            return display;
        }
        
        // Mettre à jour l'affichage des langues sous forme de badges
        function updateLanguesDisplay() {
            let display = document.getElementById('langues-display');
            if (!display) display = createLanguesDisplay();
            
            display.innerHTML = '';
            const langues = parseCurrentLangues();
            
            langues.forEach(langue => {
                if (langue.trim()) {
                    const badge = document.createElement('span');
                    badge.className = 'badge badge-primary';
                    badge.style.cssText = `
                        background-color: #007bff;
                        color: white;
                        padding: 4px 8px;
                        border-radius: 12px;
                        font-size: 12px;
                        display: inline-flex;
                        align-items: center;
                        gap: 4px;
                    `;
                    
                    const removeBtn = document.createElement('button');
                    removeBtn.type = 'button';
                    removeBtn.innerHTML = '&times;';
                    removeBtn.style.cssText = `
                        background: none;
                        border: none;
                        color: white;
                        cursor: pointer;
                        padding: 0;
                        margin-left: 4px;
                        font-size: 14px;
                    `;
                    
                    removeBtn.addEventListener('click', () => removeLangue(langue));
                    
                    badge.textContent = langue;
                    badge.appendChild(removeBtn);
                    display.appendChild(badge);
                }
            });
        }
        
        // Fonction pour supprimer une langue
        function removeLangue(langueToRemove) {
            const langues = parseCurrentLangues().filter(langue => langue !== langueToRemove);
            languesField.value = langues.length > 0 ? langues.join(', ') + ', ' : '';
            updateLanguesDisplay();
        }
        
        // Événements pour le champ langues
        languesField.addEventListener('input', function() {
            const searchTerm = getCurrentSearchTerm();
            showLanguesSuggestions(searchTerm);
            updateLanguesDisplay();
        });
        
        languesField.addEventListener('blur', function() {
            // Nettoyer le champ
            let value = this.value.trim();
            if (value.endsWith(',')) {
                value = value.slice(0, -1).trim();
            }
            this.value = value;
            updateLanguesDisplay();
            
            // Masquer les suggestions après un délai pour permettre les clics
            setTimeout(() => hideLanguesSuggestions(), 150);
        });
        
        languesField.addEventListener('focus', function() {
            const searchTerm = getCurrentSearchTerm();
            if (searchTerm.length >= 2) {
                showLanguesSuggestions(searchTerm);
            }
            updateLanguesDisplay();
        });
        
        languesField.addEventListener('keydown', function(e) {
            if (!languesSuggestionBox || languesSuggestionBox.style.display === 'none') return;
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    navigateLanguesSuggestions('down');
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    navigateLanguesSuggestions('up');
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (languesSelectedIndex >= 0) {
                        const suggestions = languesSuggestionBox.querySelectorAll('div');
                        if (suggestions[languesSelectedIndex]) {
                            selectLangue(suggestions[languesSelectedIndex].textContent);
                        }
                    }
                    break;
                case 'Escape':
                    hideLanguesSuggestions();
                    break;
            }
        });
        
        // Masquer les suggestions quand on clique ailleurs
        document.addEventListener('click', function(e) {
            if (!languesField.contains(e.target) && (!languesSuggestionBox || !languesSuggestionBox.contains(e.target))) {
                hideLanguesSuggestions();
            }
        });
        
        // Initialiser l'affichage au chargement
        updateLanguesDisplay();
    }
    
    // Auto-complétion pour le prescripteur
    const prescripteurField = document.getElementById('prescripteur');
    if (prescripteurField) {
        const prescripteursList = [
            'CAF', 'Mission locale', 'CCAS', 'Pôle emploi', 'CPAM', 'Conseil départemental',
            'OFII', 'CADA', 'CHU', 'CMP', 'PASS', 'Croix-Rouge', 'Secours Catholique',
            'Emmaüs', 'Médecins du Monde', 'France Terre d\'Asile', 'Forum Réfugiés',
            'OFPRA', 'CNDA', 'Préfecture', 'Sous-préfecture'
        ].sort();
        
        let prescripteurSuggestionBox = null;
        
        function createPrescripteurSuggestionBox() {
            prescripteurSuggestionBox = document.createElement('div');
            prescripteurSuggestionBox.className = 'suggestion-box-prescripteur';
            prescripteurSuggestionBox.style.cssText = `
                position: absolute;
                background: white;
                border: 1px solid #007bff;
                border-radius: 4px;
                max-height: 150px;
                overflow-y: auto;
                z-index: 1000;
                width: 100%;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                display: none;
            `;
            prescripteurField.parentNode.style.position = 'relative';
            prescripteurField.parentNode.appendChild(prescripteurSuggestionBox);
        }
        
        function showPrescripteurSuggestions(value) {
            if (!prescripteurSuggestionBox) createPrescripteurSuggestionBox();
            
            if (value.length < 2) {
                prescripteurSuggestionBox.style.display = 'none';
                return;
            }
            
            const filtered = prescripteursList.filter(prescripteur =>
                prescripteur.toLowerCase().includes(value.toLowerCase())
            ).slice(0, 8);
            
            if (filtered.length === 0) {
                prescripteurSuggestionBox.style.display = 'none';
                return;
            }
            
            prescripteurSuggestionBox.innerHTML = '';
            filtered.forEach(prescripteur => {
                const div = document.createElement('div');
                div.textContent = prescripteur;
                div.style.cssText = `
                    padding: 6px 10px;
                    cursor: pointer;
                    border-bottom: 1px solid #eee;
                    transition: background-color 0.2s;
                `;
                
                div.addEventListener('mouseenter', () => {
                    div.style.backgroundColor = '#007bff';
                    div.style.color = 'white';
                });
                
                div.addEventListener('mouseleave', () => {
                    div.style.backgroundColor = 'white';
                    div.style.color = 'black';
                });
                
                div.addEventListener('click', () => {
                    prescripteurField.value = prescripteur;
                    prescripteurSuggestionBox.style.display = 'none';
                });
                
                prescripteurSuggestionBox.appendChild(div);
            });
            
            prescripteurSuggestionBox.style.display = 'block';
        }
        
        prescripteurField.addEventListener('input', function() {
            showPrescripteurSuggestions(this.value);
        });
        
        prescripteurField.addEventListener('blur', function() {
            setTimeout(() => {
                if (prescripteurSuggestionBox) {
                    prescripteurSuggestionBox.style.display = 'none';
                }
            }, 200);
        });
    }
    
    // Auto-complétion pour les statuts
    const statutEntreeField = document.getElementById('statut_entree');
    const statutActuelField = document.getElementById('statut_actuel');
    
    const statutsList = [
        'Demandeur d\'asile', 'Réfugié', 'Protection subsidiaire', 'Apatride',
        'Étudiant', 'Touriste', 'Visiteur', 'Travailleur temporaire', 'Regroupement familial',
        'Vie privée et familiale', 'Conjoint de français', 'Parent d\'enfant français',
        'Talent - Passeport', 'Entrepreneur', 'Salarié détaché', 'Stagiaire',
        'Carte de résident', 'Carte de séjour pluriannuelle', 'Autorisation provisoire de séjour'
    ].sort();
    
    function createStatutAutoComplete(field, className) {
        let suggestionBox = null;
        
        function createSuggestionBox() {
            suggestionBox = document.createElement('div');
            suggestionBox.className = className;
            suggestionBox.style.cssText = `
                position: absolute;
                background: white;
                border: 1px solid #007bff;
                border-radius: 4px;
                max-height: 200px;
                overflow-y: auto;
                z-index: 1000;
                width: 100%;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                display: none;
            `;
            field.parentNode.style.position = 'relative';
            field.parentNode.appendChild(suggestionBox);
        }
        
        function showSuggestions(value) {
            if (!suggestionBox) createSuggestionBox();
            
            if (value.length < 2) {
                suggestionBox.style.display = 'none';
                return;
            }
            
            const filtered = statutsList.filter(statut =>
                statut.toLowerCase().includes(value.toLowerCase())
            ).slice(0, 8);
            
            if (filtered.length === 0) {
                suggestionBox.style.display = 'none';
                return;
            }
            
            suggestionBox.innerHTML = '';
            filtered.forEach(statut => {
                const div = document.createElement('div');
                div.textContent = statut;
                div.style.cssText = `
                    padding: 6px 10px;
                    cursor: pointer;
                    border-bottom: 1px solid #eee;
                    transition: background-color 0.2s;
                `;
                
                div.addEventListener('mouseenter', () => {
                    div.style.backgroundColor = '#007bff';
                    div.style.color = 'white';
                });
                
                div.addEventListener('mouseleave', () => {
                    div.style.backgroundColor = 'white';
                    div.style.color = 'black';
                });
                
                div.addEventListener('click', () => {
                    field.value = statut;
                    suggestionBox.style.display = 'none';
                });
                
                suggestionBox.appendChild(div);
            });
            
            suggestionBox.style.display = 'block';
        }
        
        field.addEventListener('input', function() {
            showSuggestions(this.value);
        });
        
        field.addEventListener('blur', function() {
            setTimeout(() => {
                if (suggestionBox) {
                    suggestionBox.style.display = 'none';
                }
            }, 200);
        });
    }
    
    if (statutEntreeField) {
        createStatutAutoComplete(statutEntreeField, 'suggestion-box-statut-entree');
    }
    
    if (statutActuelField) {
        createStatutAutoComplete(statutActuelField, 'suggestion-box-statut-actuel');
    }
    
    // Validation des dates cohérentes
    function validateDateCoherence() {
        const birthDate = document.getElementById('date_naissance');
        const arrivalDate = document.getElementById('arrivee_france');
        const inscriptionDate = document.getElementById('date_inscription');
        const firstVisitDate = document.getElementById('premiere_venue');
        
        if (birthDate && arrivalDate && birthDate.value && arrivalDate.value) {
            const birth = new Date(birthDate.value);
            const arrival = new Date(arrivalDate.value);
            
            if (arrival <= birth) {
                showError(arrivalDate, 'L\'arrivée en France doit être postérieure à la date de naissance');
                return false;
            } else {
                clearError(arrivalDate);
            }
        }
        
        if (arrivalDate && inscriptionDate && arrivalDate.value && inscriptionDate.value) {
            const arrival = new Date(arrivalDate.value);
            const inscription = new Date(inscriptionDate.value);
            
            if (inscription < arrival) {
                showError(inscriptionDate, 'La date d\'inscription ne peut pas être antérieure à l\'arrivée en France');
                return false;
            } else {
                clearError(inscriptionDate);
            }
        }
        
        if (inscriptionDate && firstVisitDate && inscriptionDate.value && firstVisitDate.value) {
            const inscription = new Date(inscriptionDate.value);
            const firstVisit = new Date(firstVisitDate.value);
            
            if (firstVisit < inscription) {
                showError(firstVisitDate, 'La première venue ne peut pas être antérieure à l\'inscription');
                return false;
            } else {
                clearError(firstVisitDate);
            }
        }
        
        return true;
    }
    
    // Ajout des validations de dates
    ['date_naissance', 'arrivee_france', 'date_inscription', 'premiere_venue'].forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('change', validateDateCoherence);
        }
    });
    
    // Amélioration de la validation téléphone (international)
    const phoneFieldImproved = document.getElementById('telephone');
    if (phoneFieldImproved) {
        phoneFieldImproved.addEventListener('input', function() {
            let value = this.value.replace(/[^\d+]/g, '');
            
            // Formats acceptés: +33, 0033, 06, 07, etc.
            if (value.startsWith('+33')) {
                value = value.replace('+33', '0');
            } else if (value.startsWith('0033')) {
                value = value.replace('0033', '0');
            }
            
            // Formatage français
            if (value.startsWith('0') && value.length >= 2) {
                value = value.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
            }
            
            this.value = value;
        });
    }
    
    // Barre de progression du formulaire
    function updateProgressBar() {
        const requiredFields = document.querySelectorAll('input[required], select[required]');
        const allFields = document.querySelectorAll('input:not([type="submit"]), select, textarea');
        
        let filledRequired = 0;
        let filledTotal = 0;
        
        requiredFields.forEach(field => {
            if (field.value.trim() !== '') filledRequired++;
        });
        
        allFields.forEach(field => {
            if (field.value.trim() !== '') filledTotal++;
        });
        
        // Calcul basé sur les champs obligatoires (70%) + optionnels (30%)
        const requiredProgress = (filledRequired / requiredFields.length) * 70;
        const optionalProgress = (filledTotal / allFields.length) * 30;
        const totalProgress = requiredProgress + optionalProgress;
        
        const progressBar = document.getElementById('progress-bar');
        if (progressBar) {
            progressBar.style.width = totalProgress + '%';
            progressBar.setAttribute('aria-valuenow', totalProgress);
            
            // Changement de couleur selon le progrès
            if (totalProgress < 30) {
                progressBar.className = 'progress-bar bg-danger';
            } else if (totalProgress < 70) {
                progressBar.className = 'progress-bar bg-warning';
            } else {
                progressBar.className = 'progress-bar bg-success';
            }
        }
    }
    
    // Mise à jour de la barre de progression
    document.querySelectorAll('input, select, textarea').forEach(field => {
        field.addEventListener('input', updateProgressBar);
        field.addEventListener('change', updateProgressBar);
    });
    
    // Sauvegarde automatique locale
    function autoSave() {
        const formData = {};
        document.querySelectorAll('input, select, textarea').forEach(field => {
            if (field.name && field.name !== 'csrf_token') {
                formData[field.name] = field.value;
            }
        });
        
        localStorage.setItem('inscription_draft', JSON.stringify(formData));
        
        // Afficher un indicateur de sauvegarde
        const saveIndicator = document.getElementById('save-indicator');
        if (!saveIndicator) {
            const indicator = document.createElement('small');
            indicator.id = 'save-indicator';
            indicator.className = 'text-success';
            indicator.textContent = '✓ Sauvegardé automatiquement';
            indicator.style.position = 'fixed';
            indicator.style.bottom = '20px';
            indicator.style.right = '20px';
            indicator.style.background = 'white';
            indicator.style.padding = '5px 10px';
            indicator.style.borderRadius = '4px';
            indicator.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            document.body.appendChild(indicator);
            
            setTimeout(() => indicator.remove(), 2000);
        }
    }
    
    // Sauvegarde automatique toutes les 30 secondes
    setInterval(autoSave, 30000);
    
    // Restaurer les données au chargement
    function restoreData() {
        const savedData = localStorage.getItem('inscription_draft');
        if (savedData) {
            try {
                const formData = JSON.parse(savedData);
                Object.keys(formData).forEach(fieldName => {
                    const field = document.querySelector(`[name="${fieldName}"]`);
                    if (field && !field.value) {
                        field.value = formData[fieldName];
                    }
                });
                
                // Mettre à jour les affichages spéciaux
                updateLanguesDisplay();
                updateProgressBar();
                
                // Notification de restauration
                const restoreNotification = document.createElement('div');
                restoreNotification.className = 'alert alert-info alert-dismissible fade show';
                restoreNotification.innerHTML = `
                    <strong>📋 Données restaurées !</strong> Vos données précédentes ont été récupérées.
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                form.insertBefore(restoreNotification, form.firstChild);
            } catch (e) {
                console.log('Erreur lors de la restauration des données:', e);
            }
        }
    }
    
    // Restaurer au chargement
    restoreData();
    
    // Nettoyer la sauvegarde après soumission réussie
    form.addEventListener('submit', function() {
        if (validateRequiredFields() && validateDateCoherence()) {
            localStorage.removeItem('inscription_draft');
        }
    });
    
    // Initialisation finale
    updateProgressBar();
    
    // Formatage automatique du téléphone
    const phoneField = document.getElementById('telephone');
    if (phoneField) {
        phoneField.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            
            if (value.startsWith('33')) {
                value = '0' + value.substring(2);
            }
            
            if (value.length >= 2) {
                value = value.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
            }
            
            this.value = value;
        });
    }
    
    // Calcul automatique de l'âge
    const birthDateField = document.getElementById('date_naissance');
    if (birthDateField) {
        birthDateField.addEventListener('change', function() {
            const birthDate = new Date(this.value);
            const today = new Date();
            
            if (birthDate < today) {
                const age = today.getFullYear() - birthDate.getFullYear();
                const monthDiff = today.getMonth() - birthDate.getMonth();
                
                if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                    age--;
                }
                
                // Afficher l'âge calculé (information visuelle)
                const ageInfo = document.getElementById('age-info');
                if (!ageInfo) {
                    const infoSpan = document.createElement('small');
                    infoSpan.id = 'age-info';
                    infoSpan.className = 'text-muted';
                    infoSpan.textContent = ` (${age} ans)`;
                    this.parentNode.appendChild(infoSpan);
                } else {
                    ageInfo.textContent = ` (${age} ans)`;
                }
            }
        });
    }
    
    // Validation avant soumission
    form.addEventListener('submit', function(e) {
        const isValid = validateRequiredFields();
        const datesValid = validateDateCoherence();
        
        // Vérifier aussi les validations spécifiques
        let hasErrors = false;
        Object.keys(validators).forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field && field.value.trim() !== '' && !validators[fieldName](field.value.trim())) {
                hasErrors = true;
            }
        });
        
        if (!isValid || !datesValid || hasErrors) {
            e.preventDefault();
            
            // Scroll vers la première erreur
            const firstError = document.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
            
            // Afficher un message général
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger mt-3';
            alertDiv.textContent = 'Veuillez corriger les erreurs dans le formulaire avant de continuer.';
            
            const existingAlert = form.querySelector('.alert-danger');
            if (existingAlert) existingAlert.remove();
            
            form.appendChild(alertDiv);
            
            // Supprimer l'alerte après 5 secondes
            setTimeout(() => alertDiv.remove(), 5000);
        } else {
            // Désactiver le bouton pour éviter les doubles soumissions
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Ajout en cours...';
        }
    });
    
    // Animation d'apparition des cartes
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Compteur de caractères pour les commentaires
    const commentField = document.getElementById('commentaires');
    if (commentField) {
        const maxLength = 500;
        commentField.setAttribute('maxlength', maxLength);
        
        const counter = document.createElement('small');
        counter.className = 'text-muted';
        counter.textContent = `0/${maxLength} caractères`;
        commentField.parentNode.appendChild(counter);
        
        commentField.addEventListener('input', function() {
            const length = this.value.length;
            counter.textContent = `${length}/${maxLength} caractères`;
            
            if (length > maxLength * 0.9) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
        });
    }
});
