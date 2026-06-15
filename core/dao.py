from abc import ABC, abstractmethod
from typing import List, Optional

from core.types import SEA, SEATipo


class SEAsDAO(ABC):
    @abstractmethod
    def salvar_sea(self, sea: SEA) -> None:
        pass

    @abstractmethod
    def get_seas(self, tipo: Optional[SEATipo] = None) -> List[SEA]:
        pass

    @abstractmethod
    def proxima_sea(self, tipo: SEATipo) -> Optional[SEA]:
        pass

    @abstractmethod
    def ultimas_chamadas(self) -> List[SEA]:
        pass
