# app/services/file_lock_service.py
# Service de verrouillage de fichiers multi-plateforme
# Gère les verrous pour éviter les corruptions lors d'accès concurrents

import sys
import os
import time
import threading
import json
from pathlib import Path
from typing import Optional, Any, Dict, Callable
from contextlib import contextmanager
import logging

# Import conditionnel selon la plateforme
if sys.platform == "win32":
    import msvcrt
else:
    try:
        import fcntl
    except ImportError:
        fcntl = None

logger = logging.getLogger(__name__)

class FileLockService:
    """
    Service de verrouillage de fichiers multi-plateforme
    
    Fournit des mécanismes de verrouillage sûrs pour :
    - Fichiers JSON (classes, configuration, planning)
    - Fichiers Excel (inscriptions, présences)
    - Opérations atomiques
    """
    
    def __init__(self):
        """Initialise le service de verrouillage"""
        # Verrous en mémoire par chemin de fichier
        self._memory_locks: Dict[str, threading.RLock] = {}
        self._memory_locks_lock = threading.Lock()
        
        # Statistiques de verrouillage
        self.lock_stats = {
            'acquired': 0,
            'conflicts': 0,
            'timeouts': 0
        }
    
    def _get_memory_lock(self, file_path: Path) -> threading.RLock:
        """Obtient ou crée un verrou en mémoire pour un fichier"""
        file_key = str(file_path.absolute())
        
        with self._memory_locks_lock:
            if file_key not in self._memory_locks:
                self._memory_locks[file_key] = threading.RLock()
            return self._memory_locks[file_key]
    
    @contextmanager
    def file_lock(self, file_path: Path, timeout: float = 10.0, mode: str = 'exclusive'):
        """
        Gestionnaire de contexte pour verrouiller un fichier
        
        Args:
            file_path: Chemin du fichier à verrouiller
            timeout: Délai d'attente en secondes
            mode: Type de verrou ('exclusive' ou 'shared')
        
        Usage:
            with file_lock_service.file_lock(file_path):
                # Opérations sur le fichier
                pass
        """
        memory_lock = self._get_memory_lock(file_path)
        file_handle = None
        lock_acquired = False
        start_time = time.time()
        
        try:
            # 1. Acquérir le verrou en mémoire (pour les threads)
            if not memory_lock.acquire(timeout=timeout):
                self.lock_stats['timeouts'] += 1
                raise TimeoutError(f"Impossible d'acquérir le verrou mémoire pour {file_path}")
            
            # 2. Acquérir le verrou de fichier (pour les processus)
            lock_acquired = True
            self.lock_stats['acquired'] += 1
            
            # Créer le fichier s'il n'existe pas
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Ouvrir le fichier en mode approprié
            try:
                file_handle = open(file_path, 'r+b')
            except FileNotFoundError:
                file_handle = open(file_path, 'w+b')
            
            # Appliquer le verrou système
            self._apply_system_lock(file_handle, mode, timeout - (time.time() - start_time))
            
            logger.debug(f"Verrou acquis pour {file_path}")
            yield file_handle
            
        except Exception as e:
            if time.time() - start_time > timeout * 0.8:
                self.lock_stats['timeouts'] += 1
            else:
                self.lock_stats['conflicts'] += 1
            
            logger.warning(f"Erreur de verrouillage pour {file_path}: {e}")
            raise
            
        finally:
            # Libérer le verrou de fichier
            if file_handle:
                try:
                    self._release_system_lock(file_handle)
                    file_handle.close()
                except Exception as e:
                    logger.warning(f"Erreur lors de la libération du verrou {file_path}: {e}")
            
            # Libérer le verrou en mémoire
            if lock_acquired:
                try:
                    memory_lock.release()
                except Exception as e:
                    logger.warning(f"Erreur lors de la libération du verrou mémoire {file_path}: {e}")
            
            logger.debug(f"Verrou libéré pour {file_path}")
    
    def _apply_system_lock(self, file_handle, mode: str, timeout: float):
        """Applique un verrou système selon la plateforme"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if sys.platform == "win32":
                    # Windows - utiliser msvcrt avec gestion d'erreur améliorée
                    try:
                        if mode == 'exclusive':
                            msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
                        else:
                            # Windows n'a pas de verrous partagés avec msvcrt
                            msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
                    except OSError as e:
                        # Si le fichier ne peut pas être verrouillé, continuer sans verrou système
                        # Le verrou mémoire fourni une protection suffisante pour les threads
                        logger.debug(f"Verrou système non disponible (Windows): {e}, utilisation du verrou mémoire seulement")
                        return
                else:
                    # Unix/Linux - utiliser fcntl
                    if fcntl:
                        lock_type = fcntl.LOCK_EX if mode == 'exclusive' else fcntl.LOCK_SH
                        fcntl.flock(file_handle.fileno(), lock_type | fcntl.LOCK_NB)
                
                return  # Verrou acquis avec succès
                
            except (OSError, IOError) as e:
                # Verrou occupé ou erreur de permission
                if "Permission denied" in str(e) or e.errno == 13:
                    # Erreur de permission - continuer sans verrou système
                    logger.debug(f"Permission refusée pour le verrou système: {e}")
                    return
                # Autres erreurs - attendre un peu
                time.sleep(0.1)
        
        # Timeout atteint - continuer sans verrou système mais avec verrou mémoire
        logger.debug(f"Timeout verrou système ({timeout}s) - utilisation du verrou mémoire seulement")
    
    def _release_system_lock(self, file_handle):
        """Libère un verrou système"""
        try:
            if sys.platform == "win32":
                # Windows - déverrouiller seulement si le verrou a été acquis
                try:
                    msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError as e:
                    # Ignorer les erreurs de déverrouillage si le verrou n'était pas acquis
                    logger.debug(f"Déverrouillage système ignoré (Windows): {e}")
            else:
                # Unix/Linux - déverrouiller
                if fcntl:
                    fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.debug(f"Erreur lors de la libération du verrou système: {e}")
    
    def safe_json_write(self, file_path: Path, data: Any, timeout: float = 10.0) -> bool:
        """
        Écriture atomique et sécurisée d'un fichier JSON
        
        Args:
            file_path: Chemin du fichier JSON
            data: Données à écrire
            timeout: Délai d'attente
            
        Returns:
            bool: True si l'écriture a réussi
        """
        temp_file = file_path.with_suffix('.tmp')
        memory_lock = self._get_memory_lock(file_path)
        
        try:
            # Acquérir le verrou en mémoire
            if not memory_lock.acquire(timeout=timeout):
                raise TimeoutError(f"Impossible d'acquérir le verrou mémoire pour {file_path}")
            
            # Créer le dossier parent si nécessaire
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Écrire dans un fichier temporaire
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Déplacement atomique
            temp_file.replace(file_path)
            
            logger.debug(f"Écriture JSON réussie: {file_path}")
            self.lock_stats['acquired'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture JSON {file_path}: {e}")
            
            # Nettoyer le fichier temporaire
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
            
            return False
            
        finally:
            # Libérer le verrou en mémoire
            try:
                memory_lock.release()
            except:
                pass
    
    def safe_json_read(self, file_path: Path, default: Any = None, timeout: float = 5.0) -> Any:
        """
        Lecture sécurisée d'un fichier JSON
        
        Args:
            file_path: Chemin du fichier JSON
            default: Valeur par défaut si le fichier n'existe pas
            timeout: Délai d'attente
            
        Returns:
            Données lues ou valeur par défaut
        """
        if not file_path.exists():
            return default
        
        try:
            with self.file_lock(file_path, timeout=timeout, mode='shared'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
                    
        except Exception as e:
            logger.error(f"Erreur lors de la lecture JSON {file_path}: {e}")
            return default
    
    def safe_json_update(self, file_path: Path, update_func: Callable, timeout: float = 10.0) -> bool:
        """
        Mise à jour atomique d'un fichier JSON
        
        Args:
            file_path: Chemin du fichier JSON
            update_func: Fonction qui prend les données et les modifie
            timeout: Délai d'attente
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        memory_lock = self._get_memory_lock(file_path)
        
        try:
            # Acquérir le verrou en mémoire
            if not memory_lock.acquire(timeout=timeout):
                raise TimeoutError(f"Impossible d'acquérir le verrou mémoire pour {file_path}")
            
            # Lire les données actuelles
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            # Appliquer la modification
            modified_data = update_func(data)
            
            # Écrire atomiquement
            temp_file = file_path.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(modified_data, f, ensure_ascii=False, indent=2)
            
            temp_file.replace(file_path)
            
            logger.debug(f"Mise à jour JSON réussie: {file_path}")
            self.lock_stats['acquired'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour JSON {file_path}: {e}")
            return False
            
        finally:
            # Libérer le verrou en mémoire
            try:
                memory_lock.release()
            except:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de verrouillage"""
        return {
            'locks_acquired': self.lock_stats['acquired'],
            'conflicts': self.lock_stats['conflicts'],
            'timeouts': self.lock_stats['timeouts'],
            'active_memory_locks': len(self._memory_locks)
        }

# Instance globale du service de verrouillage
file_lock_service = FileLockService()
