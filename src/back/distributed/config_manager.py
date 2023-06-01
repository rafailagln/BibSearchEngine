import json


class ConfigManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_config(self):
        with open(self.file_path, 'r') as file:
            config_data = json.load(file)
        return config_data

    def save_config(self, config_data):
        data_to_save = {"nodes": config_data}
        with open(self.file_path, 'w') as file:
            json.dump(data_to_save, file, indent=4)
