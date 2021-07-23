import os
from brokenjukebox.util.util import Util


class Config:
    ROOT_DIR=None
    CONFIG_FILE = None
    VERBOSE_MODE=None

    ASSET_DIR=None
    AUDIO_ASSET_DIR=None

    TOKEN=None

    VERSION = "0.1"
    BANNER = f"""
broken-jukebox v{VERSION}
    """

    def __init__(self):
        self.read_json_config()

    def __del__(self):
        pass

    def read_json_config(self):
        Config.CONFIG_FILE = os.path.join(
            self.ROOT_DIR,
            "brokenjukebox/config/broken_jukebox_config.json"
        )

        deserialised_json_config = Util.deserialise_json_file(Config.CONFIG_FILE)

        Config.TOKEN = deserialised_json_config.get('Token', None)

        if Config.TOKEN is None:
            exit("ERROR - unable to get TOKEN from config")
