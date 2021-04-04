# Audio downloader
Let's you download audio files (music) from youtube. It uses ```youtube-dl``` and ```ffmpeg``` to save files in ``mp3`` format.

# requirements
- ```ffmpeg``` - After installation add path to ```<..>\ffmpeg\bin``` to your system variables AND **restart** your computer
- Python modules in ```requirements.txt```

# How to use?
Install all requirements. \
Prepare txt file with ```Author - Title of a song``` lines. At this moment you have to use '-' as a separator. \
Run ```YT_Audio.py -h``` in console for more info.
Remember to use ```python <command>``` on Windows machines.

## Example:
##### 1) Use Author-Title text file
Prepare *MySongs.txt* file containing:
```text
Adventures - A Himitsu
Vexento - We are one
Buddha - Kontekst
```
and run this command in your console:
```console
YT_Audio.py -ret MySongs.txt -s MyMusicFolder
```
This will download all 3 songs and save them in 'MyMusicFolder' folder on your machine.

##### 2) Use URLs text file
TODO :)

##### 3) Use YouTube playlist's URL
TODO :)

# ToDo
1) ~~Simple interface and code clean up~~
2) Reading files with links
3) Downloading playlists
4) Customizable saved file parameters (extension, quality, etc)