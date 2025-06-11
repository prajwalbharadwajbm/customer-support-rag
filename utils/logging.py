import logging
import logging.config
import json
import os


def setup_logging(
    default_path: str = 'config/logging.json',
    default_level: int = logging.INFO,
) -> None:
    """
    Set up logging for application.
    
    This function tries to load logging settings from a JSON file.
    If the file doesn't exist, it uses basic logging instead.
    
    Args:
        default_path: Path to the logging config file (default: 'config/logging.json')
        default_level: Logging level to use if no config file (default: INFO)
    """
    path = default_path
    
    # Check if the config file exists
    if os.path.exists(path):
        # File exists, so try to load it
        with open(path, 'rt') as f:
            config = json.load(f)  # Load JSON data
        
        # Apply the loaded configuration
        logging.config.dictConfig(config)
    else:
        # No config file found, use simple logging setup
        logging.basicConfig(level=default_level)