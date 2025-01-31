import configparser

# Read tool configuration stored in config.ini in a dictionary
def get_config():
    config = configparser.RawConfigParser()
    config.read('config.ini')
    return config

config = get_config()