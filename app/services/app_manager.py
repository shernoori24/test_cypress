import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import webbrowser
from typing import Optional, Set
import websockets

class ApplicationManager:
    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.shutdown_timer: Optional[asyncio.Task] = None
        self.is_shutting_down = False
        self.last_client_timestamp = datetime.now()
        
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Enregistre un nouveau client WebSocket"""
        self.clients.add(websocket)
        self.last_client_timestamp = datetime.now()
        if self.shutdown_timer:
            self.shutdown_timer.cancel()
            self.shutdown_timer = None
            self.is_shutting_down = False
            
    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Désenregistre un client WebSocket"""
        self.clients.remove(websocket)
        if not self.clients and not self.shutdown_timer:
            self.shutdown_timer = asyncio.create_task(self.schedule_shutdown())
            
    async def schedule_shutdown(self):
        """Programme l'arrêt de l'application après 5 minutes"""
        self.is_shutting_down = True
        await self.broadcast_message({
            "type": "warning",
            "message": "L'application s'arrêtera dans 5 minutes si aucun utilisateur ne se reconnecte"
        })
        
        await asyncio.sleep(300)  # 5 minutes
        if not self.clients:
            # Arrêt propre de l'application
            await self.broadcast_message({
                "type": "shutdown",
                "message": "Arrêt de l'application..."
            })
            asyncio.get_event_loop().stop()
            
    async def broadcast_message(self, message: dict):
        """Envoie un message à tous les clients connectés"""
        if self.clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) for client in self.clients]
            )
            
    async def loading_handler(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Gère la connexion WebSocket pour l'écran de chargement"""
        await self.register_client(websocket)
        try:
            # Simuler les étapes de chargement
            steps = [
                ("Configuration réseau", 20),
                ("Chargement des données", 40),
                ("Initialisation des services", 60),
                ("Préparation de l'interface", 80),
                ("Finalisation", 100)
            ]
            
            for status, progress in steps:
                await websocket.send(json.dumps({
                    "progress": progress,
                    "status": status
                }))
                await asyncio.sleep(1)  # Délai artificiel entre les étapes
                
            await asyncio.sleep(1)  # Pause finale
            # Redirection vers la page principale
            await websocket.close()
            
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)

app_manager = ApplicationManager()
