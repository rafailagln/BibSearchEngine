import configparser
import json


class IniConfig:
    def __init__(self, ini_file):
        """
        Initializes an IniConfig object.

        Input:
        - ini_file: The path to the INI configuration file.

        Output: None
        """
        self.config = configparser.ConfigParser()
        self.config.read(ini_file)

    def get_property(self, section, key):
        """
        Retrieves a property value from the INI configuration.

        Inputs:
        - section: The section in the INI file.
        - key: The key of the property.

        Output: The value of the property.
        """
        return self.config.get(section, key)

    def get_all_properties(self, section):
        """
        Retrieves all properties within a section of the INI configuration.

        Input:
        - section: The section in the INI file.

        Output:
        - A dictionary containing all properties within the section.
        """
        return dict(self.config.items(section))


class JsonConfig:
    def __init__(self, json_file):
        """
        Initializes a JsonConfig object.

        Input:
        - json_file: The path to the JSON configuration file.

        Output: None
        """
        with open(json_file) as f:
            self.config = json.load(f)

    def get_property(self, key):
        """
        Retrieves a property value from the JSON configuration.

        Input:
        - key: The key of the property.

        Output:
        - The value of the property.
        """
        return self.config.get(key)

    def get_all_properties(self):
        """
        Retrieves all properties within the JSON configuration.

        Input: None

        Output: The JSON configuration as a dictionary.
        """
        return self.config
