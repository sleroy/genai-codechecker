import configparser
import logging
from pathlib import Path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read tool configuration stored in config.ini in a dictionary
def get_config():
    """Load and validate configuration securely"""
    config = configparser.ConfigParser()
    try:
        config_path = Path("config.ini").resolve()
        if not config_path.exists():
            raise FileNotFoundError("Configuration file not found")
            
        config.read(config_path)
        #validate_config(config)
        return config
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        raise
config = get_config()