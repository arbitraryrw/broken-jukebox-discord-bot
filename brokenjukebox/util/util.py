import json
import os

class Util:

    def __init__(self):
        pass

    @staticmethod
    def deserialise_json_file(json_file_path: str) -> dict:
        # Weak file check, simply check file extension is json..
        if json_file_path[-5:] != ".json":
            return None

        if not os.path.isfile(json_file_path):
            return None

        with open(json_file_path) as file:
            data = json.load(file)
        
        return data

    @staticmethod
    def get_audio_files_in_dir(directory_path: str) -> list:
        file_matches = list()

        for (dir_path, dir_name, file_names) in os.walk(directory_path):
            file_matches = [os.path.join(dir_path, f) for f in file_names if f[-4:] == ".mp3"]
        
        return file_matches

    @staticmethod
    def pretty_format_json(json_string: str) -> str:
        return json.dumps(json_string, indent=4, sort_keys=True)
    
    @staticmethod
    def write_json_to_file(file_path: str, data: str) -> None: 
        # Attempt to remove the file
        try:
            os.remove(file_path)
        except OSError as e:
            pass

        with open(file_path, 'w') as file:
            file.write(json.dumps(data))

    @staticmethod
    def read_json_from_file(file_path: str) -> dict: 
        if not os.path.isfile(file_path):
            return None

        json_data = None

        with open(file_path, 'r') as file:
            try:
                json_data = json.loads(file.read())
            except json.decoder.JSONDecodeError:
                print(f"[WARNING] Failed to decode json from {file_path}")
        
        return json_data
