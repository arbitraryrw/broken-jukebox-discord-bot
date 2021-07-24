import discord
import random
import asyncio
from brokenjukebox.core.youtube_download_source import YTDLSource


class BrokenJukebox(discord.ext.commands.Cog, name='Broken Jukebox'):
    def __init__(self, bot):
        self.bot = bot
        self._youtube_clips = list()
        self._TASKS = dict()


    @discord.ext.commands.command(name="play")
    async def adhoc_play(self, ctx, channel: str):
        """
        Plays a clip from the catalogue in a specific voice channel, to add clips use `!add`, to see what clips are currently there use `!list`
        """
        channel_match = [vc for vc in ctx.guild.voice_channels if vc.name == channel]

        if len(channel_match) < 1:
            known_channels = ", ".join(f"`{channel.name}`" for channel in ctx.guild.voice_channels)
            await ctx.send(f'Channel provided did not match the following known channels {known_channels}')
            return

        if len(channel_match[0].members) < 1:
            await ctx.send(f'No one is in that channel, stop being weird')
            return

        if len(self._youtube_clips) < 1:
            await ctx.send(f'No clips added, try running `!add` or use `!help` for support')
            return
        
        await self.play_audio_from_youtube_in_channel(
            channel=channel_match[0]
        )

    @discord.ext.commands.command(name="enable")
    async def enable_task(self, ctx, channel: str):
        """
        Enables the bot on a channel assuming clips have been added through `!add`, to see what clips are currently there use `!list`
        """
        channel_match = [vc for vc in ctx.guild.voice_channels if vc.name == channel]

        if len(channel_match) < 1:
            known_channels = ", ".join(f"`{channel.name}`" for channel in ctx.guild.voice_channels)
            await ctx.send(f'Channel provided did not match the following known channels {known_channels}')
            return

        if len(channel_match[0].members) < 1:
            await ctx.send(f'No one is in that channel, stop being weird')
            return

        if self._TASKS.get(channel_match[0].name) is not None:
            await ctx.send(f'Already active in that channel, calm down')
            return

        if len(self._youtube_clips) < 1:
            await ctx.send(f'No clips added, try running `!add` or use `!help` for support')
            return
        
        await self.queue_task(
            channel_match[0].name, 
            self.monitor_channel_task, 
            channel_match[0]
        )

        active_channels = ", ".join(f"`{channel}`" for channel in self._TASKS)
        await ctx.send(f'Added the channel, now engaging with {active_channels}')

    @discord.ext.commands.command(name="disable")
    async def disable_task(self, ctx, channel: str):
        """
        Disables the bot from playing clips in a channel, a user joining would re-enable the bot on that channel
        """
        channel_match = [vc for vc in ctx.guild.voice_channels if vc.name == channel]

        if len(channel_match) < 1:
            known_channels = ", ".join(f"`{channel.name}`" for channel in ctx.guild.voice_channels)
            await ctx.send(f'Channel provided did not match the following known channels {known_channels}')
            return

        if self._TASKS.get(channel) is None:
            active_channels = ", ".join(f"`{channel}`" for channel in self._TASKS)
            await ctx.send(f'Not active in that channel, currently engaging with {active_channels}')
            return
        
        voice_client = self.get_channel_voice_client(channel)

        await self.remove_task(channel)
        await ctx.send(f'uWWu I will stop bothering you in that channel until someone joins reeee')

        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()  


    @discord.ext.commands.command(name="stop")
    async def stop_voice_client_playing(self, ctx, channel: str):
        """
        Stop a clip from playing, this stops the current clip it does not remove it from the catalogue
        """
        channel_match = [vc for vc in ctx.guild.voice_channels if vc.name == channel]

        if len(channel_match) < 1:
            known_channels = ", ".join(f"`{channel.name}`" for channel in ctx.guild.voice_channels)
            await ctx.send(f'Channel provided did not match the following known channels {known_channels}')

            return

        voice_client = self.get_channel_voice_client(channel)

        if not voice_client or not voice_client.is_playing():
            await ctx.send(f'Not currently playing in that channel')
            return

        voice_client.stop()
        await ctx.send(f'Stopped that one for you bud')

        if voice_client.is_connected():
            await voice_client.disconnect()  

    @discord.ext.commands.has_role('Jukebox Admin')
    @discord.ext.commands.command(name="remove")
    async def remove_youtube_clip(self, ctx, remove_index: int):
        """
        Remove a clip from the catalogue
        """

        if len(self._youtube_clips) < 1:
            await ctx.send(f'There are no clips currently, add one using !add see !help')
            return

        if remove_index > len(self._youtube_clips) or remove_index < 0:
            await ctx.send(f'Cannot remove index see !list for a valid index')

        removed_item = self._youtube_clips.pop(remove_index-1)
        await ctx.send(f'Removed item {removed_item} - {removed_item}, there are now {len(self._youtube_clips)}'
            f' item(s) in the catalogue')


    @discord.ext.commands.command(name="list")
    async def list_youtube_clips(self, ctx):
        """
        List the youtube clips that have been added to the bot
        """
        if len(self._youtube_clips) < 1:
            await ctx.send(f'There are no clips currently, add one using !add see !help')
            return

        
        embed = discord.Embed(
            title="Jukebox Catalogue", 
            description="The clips that have been added to the bot through !add, to remove a clip run `!remove <number>`", 
            color=0x00ff00
        )

        for index, clip in enumerate(self._youtube_clips):

            embed.add_field(
                name=f'{index+1} out of {len(self._youtube_clips)}, to remove this clip run `!remove {index+1}`',
                value=clip,
                inline=True
            )
        
        await ctx.send(embed=embed)

    @discord.ext.commands.has_role('Jukebox Admin')
    @discord.ext.commands.command(name="add")
    async def queue_youtube_clip(self, ctx, url:str):
        """
        Add a youtube clip to the catalogue of clips
        
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        async with ctx.typing():
            if any(youtube_clip == url for youtube_clip in self._youtube_clips):
                await ctx.send(f'{url} is already in the catalog')
                return

            self._youtube_clips.append(url)
            await ctx.send(f'{url} added to catalog')
    
    @discord.ext.commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after): 
        if after.channel is None:
            print("User left")
            if len(before.channel.members) < 1 :
                print("Channel is now empty")
                await self.remove_task(before.channel.name)
            return

        if member.bot:
            print(f"Bot {member.name} voice update, ignoring..")
            return

        # Check if there is a channel state change, muting / unmuting shoudn't trigger the bot
        if before.channel == after.channel:
            if before.self_mute and not after.self_mute:
                print("Unmuted!")
            return

        if len(self._youtube_clips) < 1:
            print("No youtube clips queued, ignoring")
            return

        await self.play_audio_from_youtube_in_channel(channel=after.channel)

        await self.queue_task(
            after.channel.name, 
            self.monitor_channel_task, 
            after.channel
        )

    def get_channel_voice_client(self, channel_name: str) :
        bot_voice_client = [vc for vc in self.bot.voice_clients if vc.channel.name == channel_name]

        if len(bot_voice_client) > 0:
            return bot_voice_client[0]

        return None
    
    async def play_audio_from_youtube_in_channel(self, channel: discord.channel.VoiceChannel):
        voice_client = self.get_channel_voice_client(channel.name)

        if voice_client and voice_client.is_playing():
            print("Clip already playing ignoring!")
            return
        
        url = random.choice(self._youtube_clips)
        clip = await YTDLSource.from_url(url, loop=self.bot.loop)
            
        print(f'Playing {clip.title} - {url}')

        if not voice_client:
            voice_client = await channel.connect()

        voice_client.play(
            clip, 
            after=lambda e: print(f'Player error: {e}') if e else None
        )  

        # After callback does not work above, desperate times
        while voice_client.is_playing():
            await asyncio.sleep(0.5)

        voice_client.stop()
        await voice_client.disconnect()  


    async def monitor_channel_task(self, channel: discord.channel.VoiceChannel):
        while True:
            sleep_interval = random.randint(30,300)
            print(f"Sleeping {sleep_interval}")
            print(f"Tasks {len(self._TASKS)}")
            await asyncio.sleep(sleep_interval)

            await self.play_audio_from_youtube_in_channel(channel=channel)

    async def remove_task(self, task_name: str) -> None:
        if self._TASKS.get(task_name) is None:
            return

        self._TASKS.get(task_name).cancel()
        del self._TASKS[task_name]
    
    async def queue_task(self, task_name: str, task, *args) -> None:
        if self._TASKS.get(task_name) is not None:
            return

        self._TASKS[task_name] = asyncio.ensure_future(task(*args))
