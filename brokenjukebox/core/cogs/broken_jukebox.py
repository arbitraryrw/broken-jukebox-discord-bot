import discord
import random
import asyncio
from brokenjukebox.core.youtube_download_source import YTDLSource
import datetime


class BrokenJukebox(discord.ext.commands.Cog, name='Broken Jukebox'):
    def __init__(self, bot):
        self.bot = bot
        self._TASKS = dict()
        self._IDLE_MEMBERS = dict()
        self._youtube_clips = {
            "idle": list(),
            "regular": list(),
            "welcome": list()
        }


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

        if len(self._youtube_clips.get('regular')) < 1:
            await ctx.send(f'No clips added to `regular` category, try running `!add` or use `!help` for support')
            return
        
        await ctx.send(f'Clip coming right up for you')

        await self.play_audio_from_youtube_in_channel(
            channel=channel_match[0],
            clip_catalogue=self._youtube_clips.get('regular')
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

        if len(self._youtube_clips.get('regular')) < 1:
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
        await ctx.send(
            f'I will stop bothering you in `{channel}` for now. I will start again when someone joins though!'
        )

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
    async def remove_youtube_clip(self, ctx, clip_category:str, remove_index: int):
        """
        Remove a clip from a category catalogue
        """
        if not self.is_valid_clip_category(clip_category):
            valid_categories = ", ".join(f"`{category}`" for category in self._youtube_clips.keys())
            await ctx.send(f'Clip category proivded does not match and of {valid_categories}')
            return 
        
        clip_category = clip_category.lower()

        if len(self._youtube_clips.get(clip_category)) < 1:
            await ctx.send(f'There are no clips currently, add one using !add see !help')
            return

        if remove_index > len(self._youtube_clips.get(clip_category)) or remove_index < 0:
            await ctx.send(f'Cannot remove index see !list for a valid index')

        removed_item = self._youtube_clips[clip_category].pop(remove_index-1)
        await ctx.send(f'Removed {removed_item}, there are now {len(self._youtube_clips.get(clip_category))}'
            f' item(s) in the catalogue')


    @discord.ext.commands.command(name="list")
    async def list_youtube_clips(self, ctx, clip_category:str):
        """
        List the youtube clips that have been added to the bot for a given category
        """
        if not self.is_valid_clip_category(clip_category):
            valid_categories = ", ".join(f"`{category}`" for category in self._youtube_clips.keys())
            await ctx.send(f'Clip category proivded does not match and of {valid_categories}')
            return 
        
        clip_category = clip_category.lower()

        if len(self._youtube_clips.get(clip_category)) < 1:
            await ctx.send(f'There are no clips currently, add one using !add see !help')
            return
        
        embed = discord.Embed(
            title="Jukebox Catalogue", 
            description="The clips that have been added to the bot through !add, to remove a clip run `!remove <clip category> <number>`", 
            color=0x800080
        )

        for index, clip in enumerate(self._youtube_clips.get(clip_category)):
            embed.add_field(
                name=f'{index+1} out of {len(self._youtube_clips.get(clip_category))}, to remove this clip run `!remove {clip_category} {index+1}`',
                value=clip,
                inline=False
            )
        
        await ctx.send(embed=embed)

    @discord.ext.commands.has_role('Jukebox Admin')
    @discord.ext.commands.command(name="add")
    async def queue_youtube_clip(self, ctx, url:str, clip_category:str):
        """
        Add a youtube clip to the catalogue of clips
        
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if not self.is_valid_clip_category(clip_category):
            valid_categories = ", ".join(f"`{category}`" for category in self._youtube_clips.keys())
            await ctx.send(f'Clip category proivded does not match and of {valid_categories}')
            return 

        async with ctx.typing():
            if any(youtube_clip == url for youtube_clip in self._youtube_clips.get(clip_category.lower())):
                await ctx.send(f'This is already in the catalogue, see `!list` and `!help`')
                return

            self._youtube_clips[clip_category.lower()].append(url)

            await ctx.send(f'Added clip to {clip_category} catalog, there are a total of '
                f'{len(self._youtube_clips.get(clip_category))} clip(s) in this category now'
            )
    
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
            if after.self_mute:
                print(f"{member} went on mute")
                self._IDLE_MEMBERS[member.name] = datetime.datetime.now()

            if not after.self_mute:
                print(f"{member} unmuted!")

                if not self._IDLE_MEMBERS.get(member.name):
                    print(f"Member {member.name} was not in the idle members object, ignoring..")
                    return

                time_delta = datetime.datetime.now() - self._IDLE_MEMBERS[member.name]
                del self._IDLE_MEMBERS[member.name]

                if time_delta.total_seconds() < 5:
                    return

                print(f"{member} was on mute for {time_delta.total_seconds()} seconds, playing an audio clip")
                await self.play_audio_from_youtube_in_channel(
                    channel=after.channel,
                    clip_catalogue=self._youtube_clips.get('idle')
                )
            return

        await self.play_audio_from_youtube_in_channel(
            channel=after.channel, 
            clip_catalogue=self._youtube_clips.get('welcome')
        )

        if len(self._youtube_clips.get('regular')) < 1:
            print("No youtube clips queued, not starting redundant background task")
            return

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
    
    async def play_audio_from_youtube_in_channel(self, channel: discord.channel.VoiceChannel, clip_catalogue: list) -> None:
        if len(clip_catalogue) < 1:
            print("No clips to play, skipping")
            return

        voice_client = self.get_channel_voice_client(channel.name)

        if voice_client and voice_client.is_playing():
            print("Clip already playing ignoring!")
            return
        
        url = random.choice(clip_catalogue)
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

            await self.play_audio_from_youtube_in_channel(
                channel=channel, 
                clip_catalogue=self._youtube_clips.get('regular')
            )

    async def remove_task(self, task_name: str) -> None:
        if self._TASKS.get(task_name) is None:
            return

        self._TASKS.get(task_name).cancel()
        del self._TASKS[task_name]
    
    async def queue_task(self, task_name: str, task, *args) -> None:
        if self._TASKS.get(task_name) is not None:
            return

        self._TASKS[task_name] = asyncio.ensure_future(task(*args))
