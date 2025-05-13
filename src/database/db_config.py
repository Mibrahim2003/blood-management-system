from configparser import ConfigParser
import os

def config(section: str = 'postgresql', filename: str = None) -> dict:
    """Read database configuration file and return a dict of parameters."""
    if filename is None:
        # Default path for the config file relative to this script
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        filename = os.path.join(base_path, 'database.ini')
    
    parser = ConfigParser()
    parser.read(filename)

    if not parser.has_section(section):
        raise Exception(f"Section {section} not found in {filename}")

    params = {param[0]: param[1] for param in parser.items(section)}
    return params