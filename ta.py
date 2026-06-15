from typing import Any, Dict

from impl.tcp import TCPSocket


class TA:
    def __init__(self, address: str = "localhost:5000") -> None:
        self._address = address
        self._sock = TCPSocket()

    def run(self) -> None:
        try:
            self._sock.connect(self._address)
            print(f"[TA] Conectado ao SRV em {self._address}")

            # Registra como TA
            self._sock.send({"type": "register_ta"})
            resp = self._sock.read()
            if resp and resp.get("type") == "registered":
                print("[TA] Registrado como TA no servidor")
            else:
                print(f"[TA] Erro no registro: {resp}")
                return

            print("\n=== SISTEMA DE ATENDIMENTO (TA) ===")
            print("Comandos: 'proxima' | 'sair'")
            print()

            while True:
                cmd = input("ACAO: ").strip().lower()

                if cmd == "sair":
                    break

                if cmd != "proxima":
                    print("Comando invalido. Use: proxima, ou sair")
                    continue

                self._sock.send({
                    "type": "request_sea",
                })

                resp = self._sock.read()
                if resp is None:
                    print("[TA] Conexao perdida com o servidor")
                    break

                self._processar_resposta(resp)

        except ConnectionRefusedError:
            print(f"[TA] Erro: Nao foi possivel conectar ao SRV em {self._address}")
        except KeyboardInterrupt:
            print("\n[TA] Encerrando...")
        finally:
            self._sock.close()

    def _processar_resposta(self, resp: Dict[str, Any]) -> None:
        # Processa a resposta recebida do servidor
        if resp.get("type") == "sea_received":
            sea = resp["sea"]
            print(f"[TA] SEA recebida: {sea['senha']} ({sea['tipo']}) - {resp.get('timestamp', '')}")
        elif resp.get("type") == "no_sea":
            print(f"[TA] {resp.get('message', 'Nenhuma SEA disponivel')}")
        elif resp.get("type") == "error":
            print(f"[TA] Erro: {resp.get('message', '')}")
        else:
            print(f"[TA] Resposta inesperada: {resp}")


def run_ta(address: str = "localhost:5000") -> None:
    ta = TA(address)
    ta.run()
