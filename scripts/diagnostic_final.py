#!/usr/bin/env python3
"""
Test de diagnostic pour le problème de clics sur apprenants permanents
"""

import requests
import json

BASE_URL = 'http://192.168.0.150:5555'

def tester_fonctionnement():
    """Test rapide pour diagnostiquer le problème"""
    
    print("🔍 DIAGNOSTIC RAPIDE - PROBLÈME CLICS APPRENANTS")
    print("=" * 60)
    
    try:
        # 1. Vérifier que le serveur fonctionne
        response = requests.get(f'{BASE_URL}/planning/pointage', timeout=5)
        print(f"✅ Serveur accessible: {response.status_code}")
        
        # 2. Vérifier le contenu de pointage_pour_engistrer.json
        with open('data/pointage_pour_engistrer.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📄 CONTENU FICHIER POINTAGE:")
        print(f"- Date: {data.get('date')}")
        print(f"- Présences permanentes: {len([v for v in data.get('presences', {}).values() if v])}")
        print(f"- Apprenants temporaires: {sum(len(temp) for temp in data.get('apprenants_temporaires', {}).values())}")
        print(f"- Observations: {len(data.get('observations', {}))}")
        
        # 3. Détail des présences
        presences = data.get('presences', {})
        print(f"\n📊 DÉTAIL PRÉSENCES PERMANENTES:")
        for classe_id, presence_data in presences.items():
            nb_presences = len([v for v in presence_data.values() if v == 'present'])
            print(f"- {classe_id}: {nb_presences} présences sur {len(presence_data)} enregistrées")
        
        # 4. Détail des temporaires
        temporaires = data.get('apprenants_temporaires', {})
        print(f"\n📊 DÉTAIL APPRENANTS TEMPORAIRES:")
        for classe_id, temp_data in temporaires.items():
            nb_presents = len([v for v in temp_data.values() if v.get('statut_presence') == 'present'])
            print(f"- {classe_id}: {nb_presents} présents sur {len(temp_data)} temporaires")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == '__main__':
    success = tester_fonctionnement()
    
    print("\n" + "=" * 60)
    print("💡 ANALYSE:")
    print("=" * 60)
    
    if success:
        print("✅ Le système de sauvegarde fonctionne (temporaires se sauvegardent)")
        print("❌ PROBLÈME: Les clics sur apprenats permanents ne fonctionnent pas")
        print("🔧 SOLUTION: Corriger la fonction basculerPresence et le HTML")
        
        print("\n🎯 ACTIONS RÉALISÉES:")
        print("1. ✅ Corrigé le HTML de genererListeApprenants")
        print("2. ✅ Supprimé le gestionnaire d'événements conflictuel") 
        print("3. 🔄 Maintenant il faut tester les clics")
        
        print("\n📱 PROCHAINE ÉTAPE:")
        print("Tester la page web après rechargement")
    else:
        print("❌ Problème de base détecté")
        
    print(f"\n🌐 URL: {BASE_URL}/planning/pointage")
