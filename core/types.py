from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SEATipo(str, Enum):
    NORMAL = "normal"
    PRIORITARIA = "prioritaria"


class SEAStatus(str, Enum):
    CRIADA = "criada"
    CHAMADA = "chamada"


@dataclass
class SEA:
    tipo: SEATipo
    senha: str
    status: SEAStatus = SEAStatus.CRIADA
    datahora: datetime = field(default_factory=datetime.now)
