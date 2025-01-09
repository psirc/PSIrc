from connection_manager import ConnectionManager
from concurrent.futures import ThreadPoolExecutor
from message_parser import MessageParser


class IRCServer:
    def __init__(self, host: str, port: int, max_workers: int = 10) -> None:
        self.running = False
        self._thread_executor = ThreadPoolExecutor(max_workers)
        self._connection = ConnectionManager(host, port, self._thread_executor)

    def start(self) -> None:
        self.running = True
        self._connection.start()
        while self.running:
            socket, data = self._connection.get_message()
            message = MessageParser.parse_message(data)
            message.command
