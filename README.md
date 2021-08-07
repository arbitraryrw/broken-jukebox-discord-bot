# Broken Jukebox Discord Bot
An intentionally bad jukebox style Discord bot designed to join voice channels and play sound clips randomly.

## Dependencies
### Python3 Dependencies

All the python3 dependencies are documented in the requirements.txt file, to install the dependencies run:

```
python3 -m pip install -r requirements.txt
```

The project depends on the following python packages:

1. [discord.py](https://pypi.org/project/discord.py/)
1. [youtube-dl](https://pypi.org/project/youtube_dl/)
1. [PyNaCl](https://pypi.org/project/PyNaCl/)

### System Dependencies
The discord bot handles audio files, this depends on [FFmpeg](http://ffmpeg.org/) as this is required by [discord.py](https://pypi.org/project/discord.py/).

## Developer Usage

Replace the token stored in [broken_jukebox_config.json](https://github.com/arbitraryrw/broken-jukebox-discord-bot/blob/master/brokenjukebox/config/broken_jukebox_config.json) with your discord bot token. For more details on this see [realpython's guide](https://realpython.com/how-to-make-a-discord-bot-python/). Then simply run the `run.py` file:

```
python3 run.py
```

## Discord User Usage
The box exposes commands for interfacing with the bot, see `!help` for instructions on each of the commands. Note that the `!add` and `!remove` commands require you to have the `JukeBox Admin` role, this can be seen in the source [here](https://github.com/arbitraryrw/broken-jukebox-discord-bot/blob/master/brokenjukebox/core/cogs/broken_jukebox.py).

```
Broken Jukebox:
  add     Add a song to the memealogue of memes
  disable Disables the bot from playing clips in a channel, a user joining wo...
  enable  Enables the bot on a channel assuming clips have been added through...
  list    List the youtube clips that have been added to the bot
  remove  Remove a clip from the memealogue
  stop    Stop a clip from playing, this stops the current clip it does not r...
CommandErrorHandler:
  repeat  A simple command which repeats your input!
​No Category:
  help    Shows this message

Type !help command for more info on a command.
You can also type !help category for more info on a category.
```