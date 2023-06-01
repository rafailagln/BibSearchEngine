import configparser


class IniConfig:
    def __init__(self, ini_file):
        self.config = configparser.ConfigParser()
        self.config.read(ini_file)

    def get_property(self, section, key):
        return self.config.get(section, key)

    def get_all_properties(self, section):
        return dict(self.config.items(section))
