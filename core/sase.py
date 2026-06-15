from typing import Optional
from core.dao import SEAsDAO
from core.types import SEA, SEAStatus, SEATipo


class SASE:
    def __init__(self, dao: SEAsDAO) -> None:
        self.__dao = dao

    def chamar_senha(self) -> Optional[SEA]:
        sea = self.__proxima_senha()

        if sea is not None:
            sea.status = SEAStatus.CHAMADA
            self.__dao.salvar_sea(sea)

        return sea

    def gerar_sea(self, tipo: str) -> SEA:
        sea_tipo = self.__validar_tipo(tipo)

        sea = SEA(sea_tipo, self.__nova_senha(sea_tipo))
        self.__dao.salvar_sea(sea)

        return sea

    def __proxima_senha(self):
        if self.__proxima_e_prioridade():
            sea = self.__dao.proxima_sea(SEATipo.PRIORITARIA)

            if sea is not None:
                return sea

        return self.__dao.proxima_sea(SEATipo.NORMAL)

    def __proxima_e_prioridade(self) -> bool:
        ultimas_seas = self.__dao.ultimas_chamadas()

        if len(ultimas_seas) < 2:
            return False

        return all(sea.tipo == SEATipo.NORMAL for sea in ultimas_seas[-2:])

    def __validar_tipo(self, tipo: str) -> SEATipo:
        try:
            return SEATipo(tipo)
        except ValueError:
            raise Exception("Tipo Inválido")

    def __nova_senha(self, tipo: SEATipo) -> str:
        prox_num = 1

        for sea in reversed(self.__dao.get_seas(tipo)):
            prox_num = int(sea.senha[1:]) + 1
            break

        return f"{tipo.value[0].upper()}{prox_num}"
