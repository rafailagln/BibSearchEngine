import json


class JsonConfig:
    def __init__(self, json_file):
        with open(json_file) as f:
            self.config = json.load(f)

    def get_property(self, key):
        return self.config.get(key)

    def get_all_properties(self):
        return self.config
