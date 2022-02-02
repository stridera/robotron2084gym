""" Configuration file for Robotron. """
from os import path
import yaml


class Config:
    """ Load and manage the configuration file. """

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = path.join(path.dirname(__file__), "config.yaml")

        with open(config_path, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def get(self, key):
        return self.config[key] if key in self.config else None
