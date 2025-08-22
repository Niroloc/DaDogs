import json
from typing import Union

from constants import CONFIG_FILE


class Config:
    def __init__(self):
        with open(CONFIG_FILE) as f:
            self.config = json.load(f)

    def get_config(self) -> Union[dict, list]:
        return self.config
