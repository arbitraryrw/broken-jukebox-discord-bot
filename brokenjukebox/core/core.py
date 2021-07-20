from brokenjukebox.config.config import Config

class Core:

    def __init__(self):
        # Initialise an instance of the Config class to run initialisation functions
        Config()

    def start(self):
        print("Starting..")
