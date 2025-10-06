# version_manager.py
# Gestionnaire de versions avec numérotation sémantique

import json
import os
from pathlib import Path
from datetime import datetime

class VersionManager:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.version_file = self.project_dir / "version.json"
        self.load_version()
    
    def load_version(self):
        """Charge la version actuelle depuis le fichier"""
        if self.version_file.exists():
            with open(self.version_file, 'r', encoding='utf-8') as f:
                self.version_data = json.load(f)
        else:
            # Version initiale
            self.version_data = {
                "major": 1,
                "minor": 0,
                "patch": 0,
                "build": 0,
                "release_date": None,
                "changelog": []
            }
            self.save_version()
    
    def save_version(self):
        """Sauvegarde la version dans le fichier"""
        with open(self.version_file, 'w', encoding='utf-8') as f:
            json.dump(self.version_data, f, indent=2, ensure_ascii=False)
    
    def get_version_string(self):
        """Retourne la version sous forme de string"""
        v = self.version_data
        return f"{v['major']}.{v['minor']}.{v['patch']}.{v['build']}"
    
    def increment_version(self, level="patch", changelog_entry=""):
        """Incrémente la version selon le niveau spécifié"""
        if level == "major":
            self.version_data["major"] += 1
            self.version_data["minor"] = 0
            self.version_data["patch"] = 0
        elif level == "minor":
            self.version_data["minor"] += 1
            self.version_data["patch"] = 0
        elif level == "patch":
            self.version_data["patch"] += 1
        
        self.version_data["build"] += 1
        self.version_data["release_date"] = datetime.now().isoformat()
        
        if changelog_entry:
            self.version_data["changelog"].append({
                "version": self.get_version_string(),
                "date": self.version_data["release_date"],
                "changes": changelog_entry
            })
        
        self.save_version()
        return self.get_version_string()
    
    def create_release(self, level="patch", changelog="Mise à jour"):
        """Crée une nouvelle release avec incrémentation de version"""
        old_version = self.get_version_string()
        new_version = self.increment_version(level, changelog)
        
        print(f"🔄 Mise à jour de version : {old_version} → {new_version}")
        print(f"📝 Changelog : {changelog}")
        
        # Créer l'exécutable avec la nouvelle version
        self.build_executable()
        
        return new_version
    
    def build_executable(self):
        """Construit l'exécutable avec PyInstaller"""
        print("🔨 Construction de l'exécutable...")
        
        # Mettre à jour le fichier de version dans l'application
        version_py_content = f'''# Version générée automatiquement
VERSION = "{self.get_version_string()}"
BUILD_DATE = "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
'''
        
        # Créer/mettre à jour app/version.py
        app_version_file = self.project_dir / "app" / "version.py"
        with open(app_version_file, 'w', encoding='utf-8') as f:
            f.write(version_py_content)
        
        # Construire avec PyInstaller
        os.system(f'"{self.project_dir}/venv/Scripts/pyinstaller.exe" --clean ChatbotAnalyseData.spec')
        
        print(f"✅ Exécutable créé avec version {self.get_version_string()}")

def main():
    """Interface en ligne de commande pour la gestion des versions"""
    vm = VersionManager()
    
    print("=" * 50)
    print("🏷️  GESTIONNAIRE DE VERSIONS")
    print("=" * 50)
    print(f"Version actuelle : {vm.get_version_string()}")
    
    print("\nTypes de mise à jour :")
    print("1. Patch (1.0.0 → 1.0.1) - Corrections de bugs")
    print("2. Minor (1.0.1 → 1.1.0) - Nouvelles fonctionnalités")
    print("3. Major (1.1.0 → 2.0.0) - Changements majeurs")
    
    try:
        choice = input("\nChoisissez le type (1-3) : ").strip()
        
        level_map = {"1": "patch", "2": "minor", "3": "major"}
        level = level_map.get(choice, "patch")
        
        changelog = input("Décrivez les changements : ").strip()
        if not changelog:
            changelog = f"Mise à jour {level}"
        
        new_version = vm.create_release(level, changelog)
        print(f"\n🎉 Nouvelle version créée : {new_version}")
        
    except KeyboardInterrupt:
        print("\n❌ Opération annulée")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    main()
