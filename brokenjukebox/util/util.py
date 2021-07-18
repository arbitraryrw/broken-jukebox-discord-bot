import os
import json


class Util:

    def __init__(self):
        pass

    @staticmethod
    def deserialise_json_file(file_path: str) -> dict:
        data = dict()

        if not os.path.isfile(file_path):
            return data

        with open(file_path) as f:
                data = json.load(f)

        return data
