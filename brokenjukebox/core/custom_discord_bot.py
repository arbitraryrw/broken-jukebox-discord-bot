from discord.ext import commands

class CustomDiscordBot(commands.Bot):

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')
    