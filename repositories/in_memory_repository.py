from typing import Dict, Generic, TypeVar, Optional, List
from threading import RLock

T = TypeVar('T')

class InMemoryRepository(Generic[T]):
    """
    Thread-safe generic repository using a Dictionary and RLock.
    """
    def __init__(self):
        self._store: Dict[str, T] = {}
        self._lock = RLock()

    def save(self, id: str, entity: T):
        with self._lock:
            self._store[id] = entity

    def get(self, id: str) -> Optional[T]:
        with self._lock:
            return self._store.get(id)

    def delete(self, id: str):
        with self._lock:
            if id in self._store:
                del self._store[id]
    
    def all(self) -> List[T]:
        with self._lock:
            return list(self._store.values())

    def update(self, id: str, entity: T):
        self.save(id, entity)
