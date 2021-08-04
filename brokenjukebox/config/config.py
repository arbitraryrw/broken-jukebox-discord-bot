import os
from brokenjukebox.util.util import Util


class Config:
    ROOT_DIR=None
    CONFIG_FILE = None
    CATALOGUE_FILE=None

    VERBOSE_MODE=None

    ASSET_DIR=None
    AUDIO_ASSET_DIR=None

    TOKEN=None

    VERSION = "0.1"
    BANNER = f"""
broken-jukebox v{VERSION}
    """

    def __init__(self):
        if self.read_token_environment_variable() is not None:
            print("[INFO] Getting discord token from DISCORD_TOKEN env variable")
            Config.TOKEN = self.read_token_environment_variable()
        else:
            print("[INFO] Getting discord token from config file")
            Config.TOKEN = self.read_json_config()

        if Config.TOKEN is None:
            exit("ERROR - unable to get TOKEN from config")
        
    def __del__(self):
        pass

    def read_token_environment_variable(self):
        env_token = os.environ.get('DISCORD_TOKEN', None)

        if env_token is not None and len(env_token) > 10:
            return env_token

        return None

    def read_json_config(self):
        Config.CONFIG_FILE = os.path.join(
            self.ROOT_DIR,
            "brokenjukebox/config/broken_jukebox_config.json"
        )

        deserialised_json_config = Util.deserialise_json_file(Config.CONFIG_FILE)

        return deserialised_json_config.get('Token', None)
