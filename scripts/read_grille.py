# Petit script pour afficher le contenu de grille_suivit_apprenant.xlsx
# Usage: python scripts\read_grille.py
import pandas as pd
from pathlib import Path
p = Path(__file__).resolve().parent.parent / 'data' / 'grille_suivit_apprenant.xlsx'
print('Fichier:', p)
if not p.exists():
    print('Erreur: fichier introuvable:', p)
    raise SystemExit(1)
xl = pd.ExcelFile(p)
print('Feuilles trouvées:', xl.sheet_names)
for name in xl.sheet_names:
    print('\n--- FEUILLE:', name, '---')
    df = xl.parse(name)
    print('Shape:', df.shape)
    if df.empty:
        print('(feuille vide)')
        continue
    # afficher jusqu'à 20 lignes
    preview = df.head(20)
    # afficher les colonnes et types
    print('Colonnes:', list(preview.columns))
    print(preview.to_csv(index=False))
