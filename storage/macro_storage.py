import json
import os

MACROS_DIR = "macros"


class MacroStorage:

    def save(self, groups: list, name: str) -> str:
        os.makedirs(MACROS_DIR, exist_ok=True)
        path = os.path.join(MACROS_DIR, f"{name}.json")
        with open(path, 'w') as f:
            json.dump(groups, f)
        return path

    def load(self, path: str) -> list:
        with open(path, 'r') as f:
            return json.load(f)

    @property
    def default_dir(self) -> str:
        return MACROS_DIR
