import json
import selectors
import socket as _socket
from typing import Any, Callable, Dict, Optional, Tuple


# Conexao TCP cliente (bloqueante, com buffer JSON).
class TCPSocket:
    def __init__(self, sock: Optional[_socket.socket] = None) -> None:
        self._sock = sock or _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        self._buffer = ""

    def connect(self, address: str) -> None:
        host, port_str = address.rsplit(":", 1)
        port = int(port_str)
        self._sock.connect((host, port))

    def send(self, data: Dict[str, Any]) -> None:
        message = json.dumps(data) + "\n"
        self._sock.sendall(message.encode("utf-8"))

    def read(self) -> Optional[Dict[str, Any]]:
        # Le a proxima mensagem JSON delimitada por \\n.
        # Bloqueia ate uma mensagem chegar.
        # Retorna None se a conexao foi fechada.
        while True:
            if "\n" in self._buffer:
                line, self._buffer = self._buffer.split("\n", 1)
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue

            try:
                chunk = self._sock.recv(4096)
            except BlockingIOError:
                continue

            if not chunk:
                return None

            self._buffer += chunk.decode("utf-8")

    def close(self) -> None:
        self._sock.close()

    def recv(self, bufsize: int = 4096) -> bytes:
        return self._sock.recv(bufsize)

    def setblocking(self, blocking: bool) -> None:
        self._sock.setblocking(blocking)

    def fileno(self) -> int:
        return self._sock.fileno()


# Socket TCP servidor que aceita conexões.
class TCPServerSocket:
    def __init__(self) -> None:
        self._sock = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)

    def bind(self, address: str) -> None:
        host, port_str = address.rsplit(":", 1)
        port = int(port_str)
        self._sock.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
        self._sock.bind((host, port))
        self._sock.listen(5)

    def accept(self) -> Tuple["TCPSocket", str]:
        client_sock, addr = self._sock.accept()
        return TCPSocket(client_sock), f"{addr[0]}:{addr[1]}"

    def close(self) -> None:
        self._sock.close()

    def setblocking(self, blocking: bool) -> None:
        self._sock.setblocking(blocking)

    def fileno(self) -> int:
        return self._sock.fileno()

    def getsockname(self) -> Tuple[str, int]:
        return self._sock.getsockname()


# Cliente conectado (uso interno do TCPServer).
class _Client:
    __slots__ = ("sock", "addr", "buffer", "tag")

    def __init__(self, sock: TCPSocket, addr: str) -> None:
        self.sock = sock
        self.addr = addr
        self.buffer = ""
        self.tag: Optional[str] = None


# Servidor TCP nao-bloqueante com mensagens JSON delimitadas por \\n.
class TCPServer:
    def __init__(self, address: str) -> None:
        self._server_sock = TCPServerSocket()
        self._addr = address
        self._sel = selectors.DefaultSelector()
        self._clients: Dict[int, _Client] = {}
        self._running = False

        self.on_connect: Optional[Callable[[int, str], None]] = None
        self.on_message: Optional[Callable[[int, Dict[str, Any]], None]] = None
        self.on_disconnect: Optional[Callable[[int], None]] = None

    def run(self) -> None:
        self._server_sock.setblocking(False)
        self._server_sock.bind(self._addr)

        self._sel.register(
            self._server_sock, selectors.EVENT_READ, self._accept
        )
        self._running = True

        while self._running:
            events = self._sel.select(timeout=0.5)
            for key, _mask in events:
                callback = key.data
                print(callback)
                try:
                    callback(key.fileobj)
                except Exception as e:
                    print(f"[TCPServer] Error in handler: {e}")

        self._server_sock.close()

    def stop(self) -> None:
        self._running = False

    def send(self, client_id: int, data: Dict[str, Any]) -> bool:
        client = self._clients.get(client_id)
        if client is None:
            return False
        try:
            client.sock.send(data)
            return True
        except (ConnectionResetError, BrokenPipeError, OSError):
            self._remove(client_id)
            return False

    # Envia mensagem para todos os clientes (ou apenas os com a tag).
    def broadcast(self, data: Dict[str, Any], tag: Optional[str] = None) -> None:
        for client_id, client in list(self._clients.items()):
            if tag is None or client.tag == tag:
                self.send(client_id, data)

    # Associa uma tag opaca a um cliente (ex: 'ts', 'ta', 'tv').
    def tag_client(self, client_id: int, tag: str) -> None:
        client = self._clients.get(client_id)
        if client is not None:
            client.tag = tag

    def disconnect(self, client_id: int) -> None:
        self._remove(client_id)

    def _accept(self, server_sock: TCPServerSocket) -> None:
        client_sock, addr = server_sock.accept()
        client_sock.setblocking(False)
        fd = client_sock.fileno()
        self._clients[fd] = _Client(client_sock, addr)
        self._sel.register(client_sock, selectors.EVENT_READ, self._read)
        if self.on_connect:
            self.on_connect(fd, addr)

    def _read(self, sock: TCPSocket) -> None:
        fd = sock.fileno()
        client = self._clients.get(fd)
        if client is None:
            return

        try:
            chunk = sock.recv(4096)
        except BlockingIOError:
            return
        except (ConnectionResetError, OSError):
            self._remove(fd)
            return

        if not chunk:
            self._remove(fd)
            return

        client.buffer += chunk.decode("utf-8")

        # Processa todas as mensagens completas no buffer
        while "\n" in client.buffer:
            line, client.buffer = client.buffer.split("\n", 1)
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if self.on_message:
                self.on_message(fd, msg)

    def _remove(self, client_id: int) -> None:
        client = self._clients.pop(client_id, None)
        if client is None:
            return
        try:
            self._sel.unregister(client.sock)
        except KeyError:
            pass
        try:
            client.sock.close()
        except OSError:
            pass
        if self.on_disconnect:
            self.on_disconnect(client_id)
