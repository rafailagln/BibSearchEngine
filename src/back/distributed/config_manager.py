import json


class ConfigManager:

    def __init__(self, file_path):
        """
        Initialize a ConfigManager object.

        Args:
            file_path (str): The path to the config file.
        """
        self.file_path = file_path

    def load_config(self):
        """
        Loads the configuration data from the config file.

        Inputs:
            None

        Outputs:
            config_data (dict): A dictionary containing the loaded configuration data.
        """
        with open(self.file_path, 'r') as file:
            config_data = json.load(file)
        return config_data

    def save_config(self, config_data):
        """
        Saves-rewrites the provided configuration data to the file.

        Inputs:
            config_data (dict): A dictionary containing the configuration data to be saved.

        Outputs:
            None
        """
        data_to_save = {"nodes": config_data}
        with open(self.file_path, 'w') as file:
            json.dump(data_to_save, file, indent=4)
