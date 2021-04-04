from __future__ import unicode_literals
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
import eyed3
import os
import glob
from typing import List, Tuple
import shutil
import argparse

audio_downloader = YoutubeDL({'format': 'bestaudio'})
PRINT_INFO = True


class ShowProgress:
    """
    Class used to print out progress info while downloading/processing data.
    """
    def __init__(self, max_value: int, stages: int, msg: str = '*', end: str = ''):
        """

        :param max_value: Value interpreted as 100%
        :param stages: How many msg will be printed as 100%
        :param msg: Single msg output each stage
        :param end: End str used for build in print function
        """
        # Disable flag if maxCntValue is too small
        self.disable = max_value < 10
        self._cnt = 0
        self._step = max_value // stages
        if self._step == 0:
            self._step = 1
        self._msg = msg
        self._end = end

        if not self.disable:
            printer(f"Each '{msg}' represents {100 / stages}%  of progress")
        pass

    def step(self):
        """
        This method should be used each iteration in loop where progress is measured
        :return: None
        """
        if self.disable:
            return
        self._cnt += 1
        if self._cnt % self._step == 0:
            printer('* ', end='')
        pass
    pass


def searchForFile(sub_string: str, path: str = '') -> str:
    """
    Search for file containing substring. It is used to locate downloaded audio file.
    Each file has id substring in name.
    :param sub_string: Search substring
    :param path: Relative directory where to search
    :return: Full file name
    """
    if path:
        path += '\\'
    dirs = glob.glob(path + "*.*")
    for elem in dirs:
        if sub_string in elem:
            return elem
        pass
    return ''


def copyFile(src: str, dst: str) -> None:
    """
    :param src: Copied file
    :param dst: Destination and new filename
    :return:
    """
    if not os.path.isfile(src):
        printer(f'No such file to copy "{src}"')
        return
    while os.path.isfile(dst):
        dst = ''.join(dst.split('.')[:-1]) + '_1.' + dst.split('.')[-1]
    shutil.copy(src, dst)
    pass


def deleteFile(src: str) -> None:
    """
    :param src: Filename to be deleted
    :return:
    """
    if os.path.isfile(src):
        os.remove(src)
    pass


def downloadAudioFromURL(url: str):
    """
    Downloads audio file from given YouTube video URL
    :param url: URL to YouTube video
    :return: YT Title and saved file id (used in file name)
    """
    try:
        result = audio_downloader.extract_info(url)
        return result['title'], result['id']
    except Exception as err:
        printer(f"Error occurred while downloading audio file. Error: {err}")
        return None, None
    pass


def printer(msg: str, end: str = None, force_print: bool = False) -> None:
    """
    Function used for debug to print info in console
    :param msg: Text to be printed
    :param end: End statement for build in print function
    :param force_print: Skip global flag (PRINT_INFO)
    :return:
    """
    try:
        if PRINT_INFO or force_print:
            if end is None:
                print(msg)
            else:
                print(msg, end=end)
    except UnicodeEncodeError:
        print(msg.encode("utf-8"))
    pass


def readAndSortTxtFile(file_name: str) -> List[str]:
    """
    Reads text file and returns alphabetically sorted lines
    :param file_name: File name
    :return: List of lines from text file
    """
    if not os.path.isfile(file_name):
        printer(f'No such file!: {file_name}', force_print=True)
        return []

    with open(file_name, 'r') as token:
        lines = token.readlines()

    lines.sort()
    printer(f"Read {len(lines)} lines from {file_name} file.")
    return lines


def split_author_title(input_lines: List[str], author_title_split_char='-', titles_split_char=',') \
        -> List[Tuple[str, str]]:
    """
    Splits author and song title info from each line
    :param input_lines: List of lines from txt file
    :param author_title_split_char: Character used to split author and song titles
    :param titles_split_char: Character used to split song titles
    :return: Returns list of tuples (author, song title)
    """
    author_title = []
    for line in input_lines:
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


def singleSearchYouTube(single_author_title: Tuple[str, str]) -> Tuple[str, str]:
    """
    Performs search for pair of string data - (author, song title)
    :param single_author_title: Tuple (author, song title)
    :return: Found YouTube title and link to YouTube video
    """
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
    return '', ''


class SongObj:
    """
    Class used to store info about each song and its downloaded audio file
    """
    def __init__(self, author: str, title: str, yt_title: str, link: str, filename: str = None):
        self.author = author
        self.title = title
        self.yt_title = yt_title
        self.link = link
        self.filename = filename
        pass
    pass


def searchYoutube(all_author_title: List[Tuple[str, str]]):
    """
    Searches YouTube service fo each (author, song title) from input list
    :param all_author_title: List of tuples (author, song title)
    :return: List of SongObj
    """
    printer("Searching YouTube in progress")
    songsObjects = []
    sp = ShowProgress(len(all_author_title), 10)
    for author_title in all_author_title:
        sp.step()
        ret = singleSearchYouTube(author_title)
        if any([not r for r in ret]):
            printer('"' + ' '.join(author_title) + '" Not found in YouTube search')
            continue
        songsObjects.append(
            SongObj(author_title[0], author_title[1], ret[0], ret[1])
        )
        pass
    printer(f"\nGot {len(songsObjects)} songs from YouTube")
    return songsObjects


def changeDir(directory: str) -> None:
    """
    Change current directory
    :param directory: Directory path
    :return:
    """
    if not os.path.isdir(directory):
        os.mkdir(directory)
    os.chdir(directory)
    pass


def downloadFiles(songs_objects: List[SongObj]) -> None:
    """
    Downloads audio file from YouTube video and updates stored filename for each song object
    :param songs_objects: List of songObjects
    :return:
    """
    printer(f"Downloading {len(songs_objects)} items from YouTube")
    sp = ShowProgress(len(songs_objects), 10)
    for elem in songs_objects:
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


def convertAudioFile(file_name: str, to_ext: str = 'mp3') -> str:
    """
    Converts audio file using ffmpeg
    :param file_name: Audio file to convert
    :param to_ext: New file extension
    :return: New file full name
    """
    # fileExt = filePath.split('.')[-1]
    fileName = file_name.split('.')[0]
    outName = fileName + '.' + to_ext
    # Convert file
    os.system(f'ffmpeg -i "{file_name}" -acodec libmp3lame -loglevel quiet -hide_banner -y "{outName}"')
    return outName


def is_mp3_valid(file_name: str) -> bool:
    """
    Checks if audio file is mp3 valid
    :param file_name: Audio file name with path
    :return: Verification result
    """
    return eyed3.load(file_name) is not None


def changeExtensions(songs_objects: List[SongObj]) -> None:
    """
    Converts all audio files from given list and updates filename properties
    :param songs_objects: List of songObjects
    :return:
    """
    printer(f"Changing extensions in progress")
    sp = ShowProgress(len(songs_objects), 10)
    for elem in songs_objects:
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


def changeFilename(old_name: str, new_file_name: str) -> None:
    """
    Changes filenames of downloaded files using author and song title
    :param old_name: Audio file name to change
    :param new_file_name: New file name
    :return:
    """
    # Copy file
    copyFile(old_name, new_file_name)
    # Delete old file
    deleteFile(old_name)
    pass


def changeNames(songs_objects: List[SongObj]) -> None:
    """
    Changes and updates names for all songObjects
    :param songs_objects: List of songObjects
    :return:
    """
    printer(f"Changing names in progress")
    sp = ShowProgress(len(songs_objects), 10)
    for elem in songs_objects:
        sp.step()
        if not elem.filename:
            continue
        ext = elem.filename.split('.')[-1]
        newFilename = elem.author + ' - ' + elem.title + '.' + ext
        changeFilename(elem.filename, newFilename)
        pass
    printer(f"Changing names done")
    pass


def main_1(input_file_name: str, save_dir: str = None) -> None:
    """
    Serial procedure for ALL songs. If anything goes wrong processed data is useless.
    :param input_file_name: Text file containing author, song title data
    :param save_dir: Directory where audio files should be saved
    :return:
    """
    # Save current directory
    currDir = os.getcwd()
    if save_dir is not None:
        # Check directory change
        changeDir(save_dir)
        os.chdir(currDir)
        pass
    # Read file
    lines = readAndSortTxtFile(input_file_name)
    # Split author and song name
    author_titles = split_author_title(lines)
    # Search for YouTube links
    songsObjects = searchYoutube(author_titles)
    if save_dir is not None:
        # Change dir
        changeDir(save_dir)
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


def main_2(input_file_name: str, save_dir: str = None) -> None:
    """
    Serial download for each song. If anything goes wrong downloaded songs are ready to use.
    :param input_file_name: Text file containing author, song title data
    :param save_dir: Directory where audio files should be saved
    :return:
    """
    global PRINT_INFO
    PRINT_INFO = False
    # Save current directory
    currDir = os.getcwd()
    if save_dir is not None:
        # Check directory change
        changeDir(save_dir)
        os.chdir(currDir)
        pass
    # Read file
    lines = readAndSortTxtFile(input_file_name)
    # Split author and song name
    author_titles = split_author_title(lines)
    if save_dir is not None:
        # Change dir
        changeDir(save_dir)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YT_Audio allows you to download audio from YouTube videos.'
                                                 'Only educational purpose. '
                                                 'Remember to download copyrighted music from dedicated services.')
    parser.add_argument('-rat', '--reqAuthTitle',
                        help='Text file name containing author and song title info', required=True)

    parser.add_argument('-s', '--savDir',
                        help='Audio file saving relative directory', required=True)
    args = vars(parser.parse_args())

    # Read arguments
    save_directory = args['savDir']
    text_file_name = args['reqAuthTitle']

    # Start script
    main_2(text_file_name, save_directory)
    pass