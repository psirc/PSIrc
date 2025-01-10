import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty


class ConnectionManager:
    """
    Class managing connections to the server.
    attributes:
        host - string, server ip address,
        port - string, server port,
        executor - ThreadPoolExecutor, thread pool executor for class
    fields:
        _running - bool, set True after start method,
        _socket - server's socket,
        _queue - Queue - queue of messages received from connected sockets,
        _connection - set - set of connected sockets
    """

    def __init__(self, host: str, port: int, thread_pool: ThreadPoolExecutor) -> None:
        self.host = host
        self.port = port
        self.executor = thread_pool
        self._running = False
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.host, self.port))
        self._queue: Queue[tuple[socket.socket, str]] = Queue()
        self._connections: set[socket.socket] = set()

    def start(self) -> None:
        """Start thread accepting connections.

        Connected clients start new threads.
        Data received from clients gets added into message queue.
        Retrieve messages using the ``get_message`` method.
        """
        self._socket.listen()
        self._running = True

        self.executor.submit(self._accept_connections)

    def disconnect_client(self, client_socket: socket.socket) -> None:
        if client_socket in self._connections:
            self._connections.remove(client_socket)
        client_socket.close()

    def _accept_connections(self) -> None:
        while self._running:
            try:
                logging.info("ConnectionManager: waiting for connection...")
                client_socket, client_address = self._socket.accept()
                logging.info(f"ConnectionManager: Connected with {client_address}")
                self._connections.add(client_socket)

                self.executor.submit(self._handle_connection, client_socket, client_address)
            except socket.error as e:
                if not self._running:
                    break
                logging.warning(f"ConnectionManager: server socket error: {e}")
            except Exception as e:
                print(f"exception: {e}")

    def _handle_connection(self, client_socket: socket.socket, client_address: str) -> None:
        while self._running:
            try:
                data = client_socket.recv(4096)
                data_list = data.decode().split("\r\n")
                print(f"data: {data_list}")
                for data in data_list:
                    if data:
                        self._queue.put((client_socket, data))
                        continue
                    # TODO: handle disconnecting (send info downstream)
                #break

            except UnicodeError:
                logging.warning("ConnectionManager: " + f"Message from {client_address} was not valid unicode")

            except OSError as e:
                if not self._running and client_socket in self._connections:
                    logging.warning("ConnectionManager: " + f"{client_address} socket error: {e}")
                break
            except Exception as e:
                print(f"exception in handle connection {e}")

        self.disconnect_client(client_socket)

    def get_message(self, blocking: bool = True, timeout: float | None = None) -> tuple[socket.socket, str]:
        """Get received message from a connected socket.

        :param blocking: block until new message is available
        :type blocking: ``bool``
        :return: Socket and data received from said socket
        :rtype: ``Tuple[socket.socket, str]``
        """
        try:
            return self._queue.get(blocking, timeout=timeout)
        except Empty:
            return None

    def stop(self) -> None:
        """Close server socket and connected sockets.

        Should terminate related threads
        """
        self._running = False
        self._socket.close()
        while self._connections:
            self._connections.pop().close()
