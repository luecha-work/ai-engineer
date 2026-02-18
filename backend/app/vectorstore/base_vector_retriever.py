from abc import ABC, abstractmethod
from typing import List, Dict


class BaseVectorRetriever(ABC):
    def __init__(self, k: int = 3):
        self.k = k
        self._initialize()

    @abstractmethod
    def _initialize(self):
        pass

    @abstractmethod
    def search(self, tenant_id: str, query: str) -> List[Dict]:
        pass
