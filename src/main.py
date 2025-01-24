import argparse
import logging
import os
from psirc.server import IRCServer


def main() -> None:
    parser = argparse.ArgumentParser(prog="psirc", description="PSI IRC Server")
    
    parser.add_argument("-a", "--address", dest="server_addr", default="127.0.0.1")
    parser.add_argument("-p", "--port", dest="port", default="6667")
    parser.add_argument("-n", "--name", dest="name", default="PSIrc Server")

    args = parser.parse_args()

    address = args.server_addr
    port = args.port
    name = args.name

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "psirc.conf")

    s = IRCServer(name, address, int(port), config_file=conf_file)

    s.start()


if __name__ == "__main__":
    main()
