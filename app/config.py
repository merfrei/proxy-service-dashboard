"""
Read the config file
- config.toml

Plase be sure this is the only config

Even for scrapers/spiders

That means, it should always be imported this way

from config import get_config
"""

import os
import toml


HERE = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILENAME = 'config.toml'


class ConfigError(Exception):
    '''Used when an error happens'''


def get_config():
    '''Read the config file and return a dict'''
    config = None
    config_path = os.path.join(HERE, CONFIG_FILENAME)
    if not os.path.exists(config_path):
        raise ConfigError('File does not exist: {}'.format(config_path))
    with open(config_path) as c_f:
        config = toml.load(c_f)
    return config
