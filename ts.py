from typing import Any, Dict

from impl.tcp import TCPSocket


class TS:
    def __init__(self, address: str = "localhost:5000") -> None:
        self._address = address
        self._sock = TCPSocket()

    def run(self) -> None:
        try:
            self._sock.connect(self._address)
            print(f"[TS] Conectado ao SRV em {self._address}")

            # Registra como TS
            self._sock.send({"type": "register_ts"})
            resp = self._sock.read()
            if resp and resp.get("type") == "registered":
                print("[TS] Registrado como TS no servidor")
            else:
                print(f"[TS] Erro no registro: {resp}")
                return

            print("\n=== SISTEMA DE SENHAS (TS) ===")
            print("Comandos: 'normal' | 'prioritaria' | 'sair'")
            print()

            while True:
                cmd = input("Tipo de SEA a gerar: ").strip().lower()

                if cmd == "sair":
                    break

                if cmd not in ("normal", "prioritaria"):
                    print("Comando invalido. Use: normal, prioritaria, ou sair")
                    continue

                self._sock.send({
                    "type": "generate_sea",
                    "tipo": cmd,
                })

                resp = self._sock.read()
                if resp is None:
                    print("[TS] Conexao perdida com o servidor")
                    break

                self._processar_resposta(resp)

        except ConnectionRefusedError:
            print(f"[TS] Erro: Nao foi possivel conectar ao SRV em {self._address}")
        except KeyboardInterrupt:
            print("\n[TS] Encerrando...")
        finally:
            self._sock.close()

    def _processar_resposta(self, resp: Dict[str, Any]) -> None:
        # Processa a resposta recebida do servidor
        if resp.get("type") == "sea_generated":
            sea = resp["sea"]
            print(f"[TS] SEA gerada: {sea['senha']} ({sea['tipo']}) - {resp.get('timestamp', '')}")
        elif resp.get("type") == "error":
            print(f"[TS] Erro: {resp.get('message', '')}")
        else:
            print(f"[TS] Resposta inesperada: {resp}")


def run_ts(address: str = "localhost:5000") -> None:
    ts = TS(address)
    ts.run()
