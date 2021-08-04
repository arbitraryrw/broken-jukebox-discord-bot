import discord
from brokenjukebox.config.config import Config
from brokenjukebox.core.custom_discord_bot import CustomDiscordBot
from brokenjukebox.core.cogs.command_error_handler import CommandErrorHandler
from brokenjukebox.core.cogs.broken_jukebox import BrokenJukebox



class Core:
    def __init__(self):
        # Initialise an instance of the Config class to run initialisation functions
        Config()

    def start(self):
        print("[INFO] Starting discord bot..")

        bot = CustomDiscordBot(command_prefix='!')

        bot.add_cog(BrokenJukebox(bot))
        bot.add_cog(CommandErrorHandler(bot))

        bot.run(Config.TOKEN)
