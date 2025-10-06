# update_app.py
# Script pour automatiser la création de nouvelles versions

import shutil
import os
from pathlib import Path
from datetime import datetime
import zipfile

def clean_build_artifacts(project_dir):
    """Nettoie les artefacts de build après création de version"""
    build_dir = project_dir / "build"
    dist_dir = project_dir / "dist"

    print("🧹 Nettoyage des artefacts de build...")

    # Supprimer build/
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
        print("🗑️  Dossier build/ supprimé")

    # Supprimer dist/
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("🗑️  Dossier dist/ supprimé")

    # Supprimer les dossiers __pycache__ dans le projet (mais pas dans venv)
    def remove_pycache(dir_path):
        for root, dirs, files in os.walk(dir_path):
            if '__pycache__' in dirs:
                pycache_path = Path(root) / '__pycache__'
                # Ne pas supprimer dans venv
                if 'venv' not in str(pycache_path):
                    shutil.rmtree(pycache_path)
                    print(f"🗑️  __pycache__/ supprimé dans {Path(root).relative_to(project_dir)}")

    remove_pycache(project_dir)

    # Supprimer les fichiers .pyc individuels
    for root, dirs, files in os.walk(project_dir):
        # Ne pas toucher au venv
        if 'venv' in root:
            continue
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = Path(root) / file
                pyc_file.unlink()
                print(f"🗑️  {file} supprimé dans {Path(root).relative_to(project_dir)}")

    print("✅ Nettoyage terminé")

def check_dependencies():
    """Vérifie et installe les dépendances critiques pour le build"""
    print("🔍 Vérification des dépendances critiques...")
    
    import subprocess
    import sys
    
    # Vérifier PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller disponible")
    except ImportError:
        print("⚠️ PyInstaller non trouvé, installation...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installé")
    
    # Vérifier Pillow
    try:
        import PIL
        print("✅ Pillow disponible")
    except ImportError:
        print("⚠️ Pillow non trouvé, installation...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
        print("✅ Pillow installé")
    
    print("✅ Vérification des dépendances terminée")
    return True

def create_new_version():
    """Crée une nouvelle version de l'application portable"""

    print("🔄 Création d'une nouvelle version...")

    # Chemins
    project_dir = Path(__file__).parent
    build_dir = project_dir / "build"
    dist_dir = project_dir / "dist"
    venv_path = project_dir / "venv"
    
    # Vérifier l'environnement virtuel
    if not venv_path.exists():
        print("❌ Erreur : environnement virtuel non trouvé")
        print(f"   Attendu : {venv_path}")
        return False
    
    # Vérifier les dépendances critiques
    if not check_dependencies():
        print("❌ Erreur : impossible de vérifier/installer les dépendances")
        return False
    
    # Date pour la version
    version_date = datetime.now().strftime("%Y%m%d_%H%M")
    version_folder = project_dir / f"versions" / f"v{version_date}"
    
    # Créer le dossier des versions
    version_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Dossier de version : {version_folder}")
    
    # 1. Nettoyer les anciens builds
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("🧹 Ancien build supprimé")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("🧹 Ancienne distribution supprimée")
    
    # 2. Reconstruire l'exécutable
    print("🔨 Reconstruction de l'exécutable...")
    import subprocess
    import sys
    
    # S'assurer que l'icône .ico existe (convertir depuis PNG si nécessaire)
    app_dir = project_dir / "app" / "static" / "img"
    ico_path = app_dir / "logo.ico"
    png_path = app_dir / "logo.png"
    try:
        # Importer Pillow (et installer si nécessaire)
        try:
            from PIL import Image  # type: ignore
        except ImportError:
            print("⚠️ Pillow (PIL) non trouvé, installation...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            try:
                from PIL import Image  # type: ignore
            except Exception as e:
                print(f"⚠️ Impossible de charger Pillow après installation: {e}")
                Image = None

        if not ico_path.exists() and png_path.exists():
            if 'Image' in globals() and Image is not None:
                img = Image.open(png_path)
                img.save(ico_path, format='ICO', sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
                print("✅ Icône .ico générée depuis logo.png")
            else:
                print("⚠️ Conversion PNG→ICO ignorée (Pillow indisponible). Assurez-vous que app/static/img/logo.ico existe.")
    except Exception as e:
        print(f"⚠️ Impossible de générer l'icône .ico: {e}")

    print(f"➡️ Lancement du build PyInstaller...")
    print(f"🔧 Commande : pyinstaller --clean ChatbotAnalyseData.spec")
    
    try:
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "ChatbotAnalyseData.spec"], 
                               capture_output=False, check=False)
        result = result.returncode
    except Exception as e:
        print(f"❌ Erreur lors du lancement de PyInstaller: {e}")
        result = 1
    
    if result != 0:
        print("❌ Erreur lors de la construction de l'exécutable (code de retour non-zéro)")
        return False
    
    print("✅ Build terminé, vérification de l'exécutable...")
    
    # Vérification stricte que l'exécutable a bien été créé
    expected_exe = dist_dir / "Plania.exe"
    if not expected_exe.exists():
        print(f"❌ Erreur : exécutable non trouvé à l'emplacement attendu ({expected_exe})")
        print("🔍 Contenu du dossier dist/ :")
        if dist_dir.exists():
            for item in dist_dir.iterdir():
                print(f"   - {item.name}")
        else:
            print("   ❌ Le dossier dist/ n'existe pas !")
        return False
    
    # Vérifier que l'exécutable n'est pas vide ou trop petit
    exe_size = expected_exe.stat().st_size
    if exe_size < 1024:  # Moins de 1KB = problème
        print(f"❌ Erreur : l'exécutable est trop petit ({exe_size} bytes)")
        return False
    
    print(f"✅ Exécutable trouvé et valide ({exe_size / (1024*1024):.1f} MB)")
    print("✅ Préparation de la copie vers versions/...")
    
    # 3. Copier vers le dossier de version avec vérifications strictes
    print("📋 Vérification du contenu de dist/ avant copie...")
    
    if not dist_dir.exists():
        print("❌ Erreur : le dossier dist/ n'existe pas")
        return False
    
    dist_contents = list(dist_dir.iterdir())
    if not dist_contents:
        print("❌ Erreur : le dossier dist/ est vide")
        return False
    
    print(f"📁 Contenu de dist/ ({len(dist_contents)} éléments) :")
    for item in dist_contents:
        print(f"   - {item.name} ({'dossier' if item.is_dir() else 'fichier'})")
    
    exe_files = list(dist_dir.glob("*.exe"))
    if exe_files:
        # Copier l'exécutable (prendre le premier trouvé)
        exe_src = exe_files[0]
        exe_dst = version_folder / "Plania.exe"
        
        print(f"📦 Copie de l'exécutable : {exe_src.name} -> {exe_dst.name}")
        shutil.copy2(exe_src, exe_dst)
        
        # Vérifier que la copie a réussi
        if not exe_dst.exists():
            print("❌ Erreur : échec de la copie de l'exécutable")
            return False
        
        copied_size = exe_dst.stat().st_size
        original_size = exe_src.stat().st_size
        
        if copied_size != original_size:
            print(f"❌ Erreur : taille incohérente (original: {original_size}, copié: {copied_size})")
            return False
        
        print(f"✅ Exécutable copié avec succès")
        
        # Vérifier la taille du fichier (doit être > 10MB pour une app complète)
        exe_size_mb = exe_dst.stat().st_size / (1024 * 1024)
        print(f"📏 Taille de l'exécutable : {exe_size_mb:.1f} MB")
        if exe_size_mb < 10:
            print("⚠️ Attention : L'exécutable semble petit, vérifiez qu'il est complet")
        elif exe_size_mb > 200:
            print("⚠️ Attention : L'exécutable semble très volumineux")
        else:
            print("✅ Taille de l'exécutable normale")
        
        # Copier les données et la configuration réseau
        if (project_dir / "data").exists():
            # Copier network_config.json dans data s'il existe
            if (project_dir / "network_config.json").exists():
                shutil.copy2(project_dir / "network_config.json", project_dir / "data" / "network_config.json")
                print("✅ Configuration réseau copiée dans data/")
            shutil.copytree(project_dir / "data", version_folder / "data", dirs_exist_ok=True)
            print("✅ Données copiées")
        
        # Copier le README s'il existe dans le projet
        if (project_dir / "README.md").exists():
            shutil.copy2(project_dir / "README.md", version_folder)
            print("✅ README copié")
        
        # Créer un changelog
        changelog_content = f"""# Version {version_date}

## 📅 Date de release : {datetime.now().strftime("%d/%m/%Y à %H:%M")}

## 🆕 Nouveautés :
- [ ] Ajoutez ici vos modifications
- [ ] Corrections de bugs
- [ ] Nouvelles fonctionnalités

## 📦 Installation :
1. Décompressez le fichier ZIP
2. Double-cliquez sur Plania.exe
3. L'application se lance automatiquement

## ⚠️ Notes importantes :
- Sauvegardez vos données avant la mise à jour
- Cette version remplace la précédente
"""
        
        with open(version_folder / "CHANGELOG.md", "w", encoding="utf-8") as f:
            f.write(changelog_content)
        print("✅ Changelog créé")
        
        # Test rapide de l'exécutable (vérifier qu'il se lance sans erreur critique)
        print("🧪 Test rapide de l'exécutable...")
        try:
            # Test avec --help ou --version si disponible, sinon test de lancement rapide
            test_result = os.system(f'"{exe_dst}" --help >nul 2>&1')
            if test_result == 0:
                print("✅ L'exécutable répond correctement")
            else:
                print("⚠️ L'exécutable ne répond pas au paramètre --help (normal si non implémenté)")
        except Exception as e:
            print(f"⚠️ Impossible de tester l'exécutable : {e}")
        
        # 4. Nettoyer les artefacts après création
        clean_build_artifacts(project_dir)

        print("\n🎉 Nouvelle version créée avec succès !")
        print(f"📂 Dossier de version : {version_folder}")
        print(f"🚀 Version prête dans le dossier versions/ !")

        return version_folder
    else:
        print("❌ Erreur critique : Aucun exécutable trouvé après le build")
        print("🔍 Vérifications à effectuer :")
        print("   1. Le fichier ChatbotAnalyseData.spec est-il correct ?")
        print("   2. Toutes les dépendances sont-elles installées ?")
        print("   3. Y a-t-il des erreurs dans les logs PyInstaller ci-dessus ?")
        print("   4. L'espace disque est-il suffisant ?")
        return None

if __name__ == "__main__":
    create_new_version()
