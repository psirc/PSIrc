import logging
import os
from psirc.server import IRCServer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "psirc.conf")

s = IRCServer("CSSetti", "127.0.0.1", 6667, config_file=conf_file)

s.start()
