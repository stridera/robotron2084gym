""" Configuration file for Robotron. """
from os import path
import yaml


class Config:
    """ Load and manage the configuration file. """

    def __init__(self):
        dirname = path.dirname(__file__)
        with open(path.join(dirname, 'config.yaml'), 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def get(self, key):
        return self.config[key] if key in self.config else None
