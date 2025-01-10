import logging
from psirc.server import IRCServer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

s = IRCServer("serw", "127.0.0.1", 6667)

s.start()
