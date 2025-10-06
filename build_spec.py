# build_spec.py
# Script pour générer le fichier .spec personnalisé pour PyInstaller

import os
from pathlib import Path

def create_spec_file():
    """Crée un fichier .spec personnalisé pour PyInstaller"""
    
    project_dir = Path(__file__).parent
    app_name = "GestionScolaire"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

# Fichier de spécification PyInstaller pour {app_name}
# Généré automatiquement - Ne pas modifier manuellement

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
from pathlib import Path

block_cipher = None

# Collecter tous les fichiers de données nécessaires
datas = []

# Ajouter les templates Flask
datas += [('app/templates', 'app/templates')]

# Ajouter les fichiers statiques
datas += [('app/static', 'app/static')]

# Ajouter les fichiers de données
datas += [('data', 'data')]

# Ajouter le dossier de configuration si il existe
if os.path.exists('config'):
    datas += [('config', 'config')]

# Modules cachés (hidden imports) nécessaires
hiddenimports = [
    'flask',
    'jinja2',
    'werkzeug',
    'pandas',
    'openpyxl',
    'numpy',
    'requests',
    'pydantic',
    'email_validator',
    'app',
    'app.controllers',
    'app.models',
    'app.services',
    'app.utils',
]

# Collecter automatiquement tous les sous-modules de votre app
hiddenimports += collect_submodules('app')

a = Analysis(
    ['main.py'],
    pathex=[r'{str(project_dir)}'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # ✅ CHANGÉ: True pour éviter stdin errors, on cache programmatiquement
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Vous pouvez ajouter un fichier .ico ici
)
'''
    
    # Écrire le fichier .spec
    spec_file_path = project_dir / f"{app_name}.spec"
    with open(spec_file_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ Fichier .spec créé : {spec_file_path}")
    return spec_file_path

if __name__ == "__main__":
    create_spec_file()
