import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from message_parser import MessageParser


class ConnectionManager:
    def __init__(
            self,
            host: str, port: int,
            max_workers: Optional[int] = 10
            ) -> None:
        self._host = host
        self._port = port
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._connections = []
        self._running = False

    def start(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._host, self._port))
            s.listen()
            self._running = True

            while self._running:
                logging.info("Waiting for connection...")
                client_socket, client_address = s.accept()
                logging.info(f"Connected with {client_address}")

                self._executor.submit(
                    self.handle_client,
                    client_socket, client_address)

    def handle_client(
            self,
            client_socket: socket.socket, client_address: socket._RetAddress
            ) -> None:
        while self._running:
            try:
                data = client_socket.recv(4096).decode()
                message = MessageParser.parse_message(data)
                if not message:
                    logging.warning(
                        f"Invalid message from client {client_address}")
                    continue

            except OSError as e:
                logging.info(
                    f"Client {client_address} connection OSError: {e}")
                break
