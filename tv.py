from typing import Any, Dict

from impl.tcp import TCPSocket


class TV:
    def __init__(self, address: str = "localhost:5000") -> None:
        self._address = address
        self._sock = TCPSocket()

    def run(self) -> None:
        try:
            self._sock.connect(self._address)
            print(f"[TV] Conectado ao SRV em {self._address}")

            # Registra como TV
            self._sock.send({"type": "register_tv"})
            resp = self._sock.read()
            if resp and resp.get("type") == "registered":
                print("[TV] Registrado como TV no servidor")
            else:
                print(f"[TV] Erro no registro: {resp}")
                return

            print("\n=== PAINEL DE SENHAS (TV) ===")
            print("Aguardando senhas do servidor...")
            print()

            while True:
                resp = self._sock.read()
                if resp is None:
                    print("[TV] Conexao perdida com o servidor")
                    break

                self._processar_resposta(resp)

        except ConnectionRefusedError:
            print(f"[TV] Erro: Nao foi possivel conectar ao SRV em {self._address}")
        except KeyboardInterrupt:
            print("\n[TV] Encerrando...")
        finally:
            self._sock.close()

    def _processar_resposta(self, resp: Dict[str, Any]) -> None:
        # Processa a mensagem recebida do servidor
        if resp.get("type") == "sea_display":
            sea = resp["sea"]
            print(f"[TV] *** SENHA: {sea['senha']} ({sea['tipo']}) *** - {resp.get('timestamp', '')}")
        else:
            print(f"[TV] Mensagem inesperada: {resp}")


def run_tv(address: str = "localhost:5000") -> None:
    tv = TV(address)
    tv.run()
