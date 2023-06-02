import configparser
import json


class IniConfig:
    def __init__(self, ini_file):
        self.config = configparser.ConfigParser()
        self.config.read(ini_file)

    def get_property(self, section, key):
        return self.config.get(section, key)

    def get_all_properties(self, section):
        return dict(self.config.items(section))


class JsonConfig:
    def __init__(self, json_file):
        with open(json_file) as f:
            self.config = json.load(f)

    def get_property(self, key):
        return self.config.get(key)

    def get_all_properties(self):
        return self.config
