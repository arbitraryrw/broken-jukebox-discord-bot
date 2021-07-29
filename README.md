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

