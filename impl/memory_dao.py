from typing import List, Optional

from core.dao import SEAsDAO
from core.types import SEA, SEAStatus, SEATipo


class InMemoryDAO(SEAsDAO):
    def __init__(self) -> None:
        self._seas: List[SEA] = []

    def salvar_sea(self, sea: SEA) -> None:
        for i, s in enumerate(self._seas):
            if s.senha == sea.senha:
                self._seas[i] = sea
                return

        self._seas.append(sea)

    def get_seas(self, tipo: Optional[SEATipo] = None) -> List[SEA]:
        if tipo is None:
            return list(self._seas)

        return [sea for sea in self._seas if sea.tipo == tipo]

    def proxima_sea(self, tipo: SEATipo) -> Optional[SEA]:
        for sea in self._seas:
            if sea.tipo == tipo and sea.status == SEAStatus.CRIADA:
                return sea

        return None

    def ultimas_chamadas(self) -> List[SEA]:
        return [sea for sea in self._seas if sea.status == SEAStatus.CHAMADA]
