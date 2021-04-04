from __future__ import unicode_literals
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
import eyed3
import os
import glob
from typing import List
import shutil

audio_downloader = YoutubeDL({'format': 'bestaudio'})
PRINT_INFO = True


class ShowProgress:
    def __init__(self, maxValue: int, stages: int, msg: str = '*', end: str = ''):
        self.disable = maxValue < 10
        self._cnt = 0
        self._step = maxValue // stages
        if self._step == 0:
            self._step = 1
        self._msg = msg
        self._end = end

        if not self.disable:
            printer(f"Each '{msg}' represents {100 / stages}%  of progress")
        pass

    def step(self):
        if self.disable:
            return
        self._cnt += 1
        if self._cnt % self._step == 0:
            printer('* ', end='')
        pass
    pass


def searchForFile(name: str, path: str = '') -> str:
    if path:
        path += '\\'
    dirs = glob.glob(path + "*.*")
    for elem in dirs:
        if name in elem:
            return elem
        pass
    return ''


def copyFile(src: str, dst: str):
    if not os.path.isfile(src):
        printer(f'No such file to copy "{src}"')
        return
    while os.path.isfile(dst):
        dst = ''.join(dst.split('.')[:-1]) + '_1.' + dst.split('.')[-1]
    shutil.copy(src, dst)
    pass


def deleteFile(src: str):
    if os.path.isfile(src):
        os.remove(src)
    pass


def downloadAudioFromURL(url: str):
    try:
        result = audio_downloader.extract_info(url)
        return result['title'], result['id']
    except Exception as err:
        printer(f"Error occurred while downloading audio file. Error: {err}")
        return None, None
    pass


def printer(txt, end: str = None):
    try:
        if PRINT_INFO:
            if end is None:
                print(txt)
            else:
                print(txt, end=end)
    except UnicodeEncodeError:
        print(txt.encode("utf-8"))
    pass


def readAndSortTxtFile(txtName: str) -> List[str]:
    if not os.path.isfile(txtName):
        printer(f'No such file!: {txtName}')
        return []

    with open(txtName, 'r') as token:
        lines = token.readlines()

    lines.sort()
    printer(f"Read {len(lines)} lines from {txtName} file.")
    return lines


def split_author_title(txt_lines, author_title_split_char='-', titles_split_char=','):
    author_title = []
    for line in txt_lines:
        line = line.replace('\n', '')
        line = line.replace('\t', '')
        line = line.replace('.', '')
        line = line.strip()
        if line == '':
            continue
        if author_title_split_char in line:
            author = line.split(author_title_split_char)[0].strip().title()
            titles = line.split(author_title_split_char)[-1].strip().title()
            if titles_split_char in titles:
                # There are more song titles in this line
                for song_title in titles.split(titles_split_char):
                    author_title.append((author, song_title))
                pass  # if titles_split_char
            else:
                # there is only one song title in this line
                author_title.append((author, titles))
                pass
        else:
            # No split character in line
            # TODO What should be done here?
            printer(f"Dropped line due to no split character: '{line}'")
            pass
        pass
    printer(f"Read {len(author_title)} author-title pairs.")
    return author_title


def singleSearchYouTube(single_author_title: tuple):
    # Use lower case for banned words
    bannedWords = ['live', 'karaoke', 'instrumental']  # 'official video'
    limit = 3

    for i in range(2):
        # Search for "author title". Then try with "lyrics"
        searchPhrase = ' '.join(single_author_title) + ('lyric' if i == 0 else '')
        videosSearch = VideosSearch(searchPhrase, limit=limit).result()['result']
        for elem in videosSearch:
            elem = dict(elem)
            # Read data
            title = elem['title']
            title_low = title.lower()
            link = elem['link']
            # Check banned phrases
            if any([word in title_low for word in bannedWords]):
                continue
            # Return found title and link
            return title, link
    # Nothing was found
    return None


class SongObj:
    def __init__(self, author: str, title: str, yt_title: str, link: str, filename: str = None):
        self.author = author
        self.title = title
        self.yt_title = yt_title
        self.link = link
        self.filename = filename
        pass
    pass


def searchYoutube(all_author_title):
    printer("Searching YouTube in progress")
    songsObjects = []
    sp = ShowProgress(len(all_author_title), 10)
    for author_title in all_author_title:
        sp.step()
        ret = singleSearchYouTube(author_title)
        if ret is None:
            printer('"' + ' '.join(author_title) + '" Not found in YouTube search')
            continue
        songsObjects.append(
            SongObj(author_title[0], author_title[1], ret[0], ret[1])
        )
        pass
    printer(f"\nGot {len(songsObjects)} songs from YouTube")
    return songsObjects


def changeDir(directory: str):
    if not os.path.isdir(directory):
        os.mkdir(directory)
    os.chdir(directory)
    pass


def downloadFiles(songsObjects: List[SongObj]):
    printer(f"Downloading {len(songsObjects)} items from YouTube")
    sp = ShowProgress(len(songsObjects), 10)
    for elem in songsObjects:
        sp.step()
        title, _id = downloadAudioFromURL(elem.link)
        if title is None or _id is None:
            printer(f'{elem.author} {elem.title} - Failed to download. '
                    f'yt_title "{elem.yt_title}", link "{elem.link}"')
            continue
        filename = searchForFile(_id)
        if not filename:
            printer(f'{elem.author} {elem.title} - Failed to find file in directory. '
                    f'yt_title "{elem.yt_title}", link "{elem.link}"')
            elem.filename = None
        else:
            elem.filename = filename
        pass
    printer(f"Downloading done")
    pass


def convertAudioFile(filePath: str, toExt: str = 'mp3'):
    # fileExt = filePath.split('.')[-1]
    fileName = filePath.split('.')[0]
    outName = fileName + '.' + toExt
    # Convert file
    os.system(f'ffmpeg -i "{filePath}" -acodec libmp3lame -loglevel quiet -hide_banner -y "{outName}"')
    return outName


def is_mp3_valid(filePath: str):
    return eyed3.load(filePath) is not None


def changeExtensions(songsObjects: List[SongObj]):
    printer(f"Changing extensions in progress")
    sp = ShowProgress(len(songsObjects), 10)
    for elem in songsObjects:
        sp.step()
        if elem.filename is None:
            continue
        # Convert
        newFilename = convertAudioFile(elem.filename)
        # Check if mp3 file is valid
        if is_mp3_valid(newFilename):
            # Delete old file
            deleteFile(elem.filename)
            # Save new path
            elem.filename = newFilename
        else:
            # Delete new file
            deleteFile(newFilename)
            printer(f'[ERROR] {newFilename} is invalid')
            pass
        pass
    printer(f"Changing extensions done")
    pass


def changeFilename(oldName: str, newFilename: str):
    # Copy file
    copyFile(oldName, newFilename)
    # Delete old file
    deleteFile(oldName)
    pass


def changeNames(songsObjects: List[SongObj]):
    printer(f"Changing names in progress")
    sp = ShowProgress(len(songsObjects), 10)
    for elem in songsObjects:
        sp.step()
        if not elem.filename:
            continue
        ext = elem.filename.split('.')[-1]
        newFilename = elem.author + ' - ' + elem.title + '.' + ext
        changeFilename(elem.filename, newFilename)
        pass
    printer(f"Changing names done")
    pass


def main(filePath: str, saveDir: str = None):
    # Save current directory
    currDir = os.getcwd()
    if saveDir is not None:
        # Check directory change
        changeDir(saveDir)
        os.chdir(currDir)
        pass
    # Read file
    lines = readAndSortTxtFile(filePath)
    # Split author and song name
    author_titles = split_author_title(lines)
    # Search for YouTube links
    songsObjects = searchYoutube(author_titles)
    if saveDir is not None:
        # Change dir
        changeDir(saveDir)
        pass
    # Download files
    downloadFiles(songsObjects)
    # Change extensions
    changeExtensions(songsObjects)
    # Change names
    changeNames(songsObjects)
    # Go back to first directory
    os.chdir(currDir)
    pass


def main2(filePath: str, saveDir: str = None):
    global PRINT_INFO
    PRINT_INFO = False
    # Save current directory
    currDir = os.getcwd()
    if saveDir is not None:
        # Check directory change
        changeDir(saveDir)
        os.chdir(currDir)
        pass
    # Read file
    lines = readAndSortTxtFile(filePath)
    # Split author and song name
    author_titles = split_author_title(lines)
    if saveDir is not None:
        # Change dir
        changeDir(saveDir)
        pass
    for at_pair in author_titles:
        # Search for YouTube links
        songsObjects = searchYoutube([at_pair])
        # Download files
        downloadFiles(songsObjects)
        # Change extensions
        changeExtensions(songsObjects)
        # Change names
        changeNames(songsObjects)
    # Go back to first directory
    os.chdir(currDir)
    pass


# main('piosenki.txt', 'muzyka')
# main('yt_links.txt', 'muzyka_Lyrics')
main2('piosenki.txt', 'muzyka_Lyrics232323')
