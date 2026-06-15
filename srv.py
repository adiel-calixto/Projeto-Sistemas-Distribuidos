from datetime import datetime
from typing import Any, Dict

from core.sase import SASE
from core.types import SEA
from impl.memory_dao import InMemoryDAO
from impl.tcp import TCPServer


def _now() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def _serializar_sea(sea: SEA) -> Dict[str, str]:
    return {
        "senha": sea.senha,
        "tipo": sea.tipo.value,
        "status": sea.status.value,
        "datahora": sea.datahora.isoformat(),
    }


class SRV:
    def __init__(self, address: str = "localhost:5000") -> None:
        self._server = TCPServer(address)
        self._sase = SASE(InMemoryDAO())
        self._client_types: Dict[int, str] = {}

    def run(self) -> None:
        self._server.on_connect = self._ao_conectar
        self._server.on_message = self._ao_receber_mensagem
        self._server.on_disconnect = self._ao_desconectar
        self._server.run()

    def stop(self) -> None:
        self._server.stop()

    def _ao_conectar(self, client_id: int, addr: str) -> None:
        # Nova conexao recebida
        print(f"[SRV] Nova conexao de {addr}")

    def _ao_receber_mensagem(self, client_id: int, msg: Dict[str, Any]) -> None:
        # Identifica o tipo de cliente e roteia a mensagem
        client_type = self._client_types.get(client_id)

        if client_type is None:
            self._identificar_cliente(client_id, msg)
            return

        if client_type == "ts":
            self._processar_mensagem_ts(client_id, msg)
        elif client_type == "ta":
            self._processar_mensagem_ta(client_id, msg)

    def _ao_desconectar(self, client_id: int) -> None:
        # Remove o cliente e informa
        role = self._client_types.pop(client_id, None)
        print(f"[SRV] Conexao encerrada ({role or 'unknown'})")

    def _identificar_cliente(self, client_id: int, msg: Dict[str, Any]) -> None:
        # Registra o cliente com base no tipo informado
        msg_type = msg.get("type", "")
        role = msg_type.replace("register_", "")
        if role in ("ts", "ta", "tv"):
            self._client_types[client_id] = role
            self._server.tag_client(client_id, role)
            print(f"[SRV] {role.upper()} registrado")
            self._server.send(client_id, {"type": "registered", "role": role})
        else:
            print(f"[SRV] Registro desconhecido: {msg}")

    def _processar_mensagem_ts(self, client_id: int, msg: Dict[str, Any]) -> None:
        # Processa requisicao de geracao de SEA vinda do TS
        if msg.get("type") != "generate_sea":
            return

        tipo = msg.get("tipo", "normal")
        if tipo not in ("normal", "prioritaria"):
            self._server.send(client_id, {"type": "error", "message": "Tipo invalido"})
            return

        try:
            sea = self._sase.gerar_sea(tipo)
            timestamp = _now()
            print(f"[SRV] {timestamp} - SEA recebida do TS: {sea.senha} ({sea.tipo.value})")
            self._server.send(client_id, {
                "type": "sea_generated",
                "sea": _serializar_sea(sea),
                "timestamp": timestamp,
            })
        except Exception as e:
            self._server.send(client_id, {"type": "error", "message": str(e)})

    def _processar_mensagem_ta(self, client_id: int, msg: Dict[str, Any]) -> None:
        # Processa requisicao de chamada de SEA vinda do TA
        if msg.get("type") != "request_sea":
            return

        try:
            sea = self._sase.chamar_senha()

            if sea is None:
                self._server.send(client_id, {
                    "type": "no_sea",
                    "message": "Nenhuma SEA disponivel no momento",
                })
                return

            timestamp = _now()
            print(f"[SRV] {timestamp} - SEA enviada para TA: {sea.senha} ({sea.tipo.value})")

            sea_data = _serializar_sea(sea)

            self._server.send(client_id, {
                "type": "sea_received",
                "sea": sea_data,
                "timestamp": timestamp,
            })

            self._server.broadcast(
                {"type": "sea_display", "sea": sea_data, "timestamp": timestamp},
                tag="tv",
            )
        except Exception as e:
            self._server.send(client_id, {"type": "error", "message": str(e)})


def run_srv(address: str = "localhost:5000") -> None:
    server = SRV(address)
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n[SRV] Encerrando...")
        server.stop()
