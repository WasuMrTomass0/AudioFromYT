# Link generator
Let's you generate youtube video links which can be used to download audio by ```youtube-dl```.

**Requirements:**
- ```youtube-search-python```

**How to use it?**
- Create ```input.txt``` text file with ```author - song title``` pairs in each line. 
Example ```input.txt``` file:
```
Adventures - A Himitsu
Vexento - We are one
Buddha - Kontekst
```
- Install requirements with ```pip install -r requirements.txt```.
- Run ```gen_links.py -in input.txt -out my_links.txt```.
- Results in ```my_links.txt```:
```
# Adventures - A Himitsu
https://www.youtube.com/watch?v=6E0zgBxObkk
# Buddha - Kontekst
https://www.youtube.com/watch?v=3oZ8vwNfC2s
# Vexento - We Are One
https://www.youtube.com/watch?v=2N4t_kChuiU
```
- Run ```gen_links.py -h``` for more options.

# Downloading audio
**Requirements:**
- ```ffmpeg``` - Add path to ```<..>\ffmpeg\bin``` to your system variables and **restart** your computer
- ```youtube_dl```

**How to download songs from generated file?**
- Run script ```download_audio.py -h``` and follow instructions
- Run command
```console
youtube-dl -x -o %(title)s.%(ext)s --no-playlist --audio-format AUDIO_FORMAT -a LINK_FILE
```
where: \
```AUDIO_FORMAT``` is your preferred audio format - for example mp3 \
```LINK_FILE``` is the name of generated file with links

