import logging
from src.utils.config import SETTINGS

def setup_logger():
    """Sets up a centralized logger."""
    log_config = SETTINGS['logging']
    logging.basicConfig(
        level=log_config['level'],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_config['file']),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()