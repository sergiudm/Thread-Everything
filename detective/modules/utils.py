import json
import os


class Config:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config_data = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file '{self.config_path}' not found.")
        with open(self.config_path, "r") as file:
            return json.load(file)

    def get_param(self, key, default=None):
        return self.config_data.get(key, default)

    def print_info(self):
        for key, value in self.config_data.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    config = Config(config_path=os.path.join(os.path.dirname(__file__), "test.json"))
    config.print_info()
