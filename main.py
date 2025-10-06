# main.py
# Fichier principal optimisé pour la création d'exécutable avec PyInstaller
import sys
import os
import webbrowser
import threading
import time
import socket
from pathlib import Path

# Ajouter le dossier de l'application au path Python
if getattr(sys, 'frozen', False):
    # Si l'application est "gelée" par PyInstaller
    application_path = Path(sys.executable).parent
    bundle_dir = sys._MEIPASS
else:
    # Si l'application est lancée normalement
    application_path = Path(__file__).parent
    bundle_dir = application_path

# Ajouter le dossier de l'application au Python path
sys.path.insert(0, str(application_path))

from app import create_app

# Configuration réseau 
HOST = "0.0.0.0" 
PORT = 5555

def get_local_ip():
    """Obtient l'adresse IP locale de la machine"""
    try:
        # Créer une socket pour découvrir l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Se connecter à un serveur externe (Google DNS) pour déterminer l'IP locale
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Impossible d'obtenir l'IP locale"

def display_network_access_info():
    """Affiche les informations d'accès réseau dans la console"""
    local_ip = get_local_ip()
    
    print("\n ACCÈS RÉSEAU À L'APPLICATION :")
    print("=" * 50)
    print(f" Accès local :      http://localhost:{PORT}")
    print(f" Accès local :      http://127.0.0.1:{PORT}")
    if local_ip != "Impossible d'obtenir l'IP locale":
        print(f" Accès réseau :     http://{local_ip}:{PORT}")
        print(f"   (Accessible depuis d'autres appareils du réseau)")
    else:
        print(f" Accès réseau :     Non disponible")
    print("=" * 50)
    print()



def open_browser(base_url):
    time.sleep(1.5)  # Attendre que le serveur soit prêt
    try:
        webbrowser.open(base_url)
        print(f" Navigateur ouvert sur {base_url}")
    except Exception as e:
        print(f" Impossible d'ouvrir le navigateur automatiquement: {e}")
        print(f" Ouvrez manuellement : {base_url}")

def main():
    """Fonction principale qui lance l'application"""
    print("Démarrage de l'application Plania...")
    print("=" * 50)
    
    try:
        # Créer l'application Flask
        app = create_app()

        # Afficher les informations d'accès réseau
        display_network_access_info()

        # Ouverture automatique du navigateur
        browser_thread = threading.Thread(target=open_browser, args=(f"http://localhost:{PORT}",))
        browser_thread.daemon = True
        browser_thread.start()

        # Lancer le serveur Flask
        app.run(
            host=HOST,
            port=PORT,
            debug=False,
            use_reloader=False,
            threaded=True
        )

        
    except Exception as e:
        print(f" Erreur lors du démarrage : {e}")
        if getattr(sys, 'frozen', False):
            input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)

if __name__ == "__main__":
    main()
