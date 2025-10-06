import pandas as pd
from pathlib import Path
import sys

# Chemin vers le fichier Excel temporaire
excel_file = Path("data/~$inscription.xlsx")

# Vérifier si le fichier existe
if not excel_file.exists():
    print(f"Le fichier {excel_file} n'existe pas.")
    sys.exit(1)

try:
    # Lire le fichier Excel
    df = pd.read_excel(excel_file)
    
    # Afficher les informations de base
    print("=== INFORMATIONS SUR LE FICHIER EXCEL ===")
    print(f"Nombre de lignes : {len(df)}")
    print(f"Nombre de colonnes : {len(df.columns)}")
    print("\n=== COLONNES ===")
    for i, col in enumerate(df.columns):
        print(f"{i+1:2d}. {col}")
    
    print("\n=== PREMIÈRES LIGNES ===")
    print(df.head().to_string())
    
    print("\n=== INFORMATIONS SUR LES COLONNES ===")
    print(df.info())
    
except Exception as e:
    print(f"Erreur lors de la lecture du fichier Excel : {e}")
    sys.exit(1)