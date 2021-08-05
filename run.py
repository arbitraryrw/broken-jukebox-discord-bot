import os 
from brokenjukebox.config.config import Config

Config.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
Config.ASSET_DIR = os.path.join(Config.ROOT_DIR, 'brokenjukebox/assets')
Config.AUDIO_ASSET_DIR = os.path.join(Config.ASSET_DIR, 'audio')
Config.CATALOGUE_FILE = os.path.join(Config.AUDIO_ASSET_DIR,"broken_jukebox_catalogue.json")

# Core logic must be imported after Config variables are set for paths etc
from brokenjukebox.core.core import Core

def run() -> None:
    c = Core()
    c.start()

if __name__ == '__main__':
    run()