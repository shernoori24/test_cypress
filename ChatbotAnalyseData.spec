# -*- mode: python ; coding: utf-8 -*-

# Fichier de spécification PyInstaller pour ChatbotAnalyseData
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
    # Prophet et ses dépendances
    'prophet',
    'prophet.forecaster',
    'prophet.plot',
    'prophet.diagnostics',
    'prophet.serialize',
    'cmdstanpy',
    'pystan',
    # Statsmodels
    'statsmodels',
    'statsmodels.tsa',
    'statsmodels.tsa.arima',
    'statsmodels.tsa.seasonal',
    'statsmodels.stats.diagnostic',
]

# Collecter automatiquement tous les sous-modules de votre app
hiddenimports += collect_submodules('app')

a = Analysis(
    ['main.py'],
    pathex=[r'C:\Users\stagiaire\Documents\jspr\app_plania'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
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
    name='Plania',
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
    icon='app/static/img/logo.ico',  # Icône de l'application
)
