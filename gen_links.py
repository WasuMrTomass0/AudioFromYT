from __future__ import unicode_literals
from youtubesearchpython import VideosSearch
from youtube_dl import YoutubeDL
from typing import List, Tuple
import argparse
import os

# Global variables
audio_downloader = YoutubeDL({'format': 'bestaudio'})
PRINT_INFO = True

# Defaults
DEF_AUTHOR_SONG_SPLIT_CHAR = '-'
DEF_SONG_TITLES_SPLIT_CHAR = ';'
DEF_COMMENT_CHAR = '#'
DEF_OUT_FILE_NAME = 'generated_links.txt'


def printer(msg: str, end: str = '\n', force_print: bool = False) -> None:
    """
    Function used for debug to print info in console
    :param msg: Text to be printed
    :param end: End statement for build in print function
    :param force_print: Skip global flag (PRINT_INFO)
    :return:
    """
    try:
        if PRINT_INFO or force_print:
            print(msg, end=end)
    except UnicodeEncodeError:
        print(msg.encode("utf-8"))
    pass


def read_sort_text_file(file_name: str) -> List[str]:
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


def split_author_title(input_lines: List[str],
                       author_title_split_char=DEF_AUTHOR_SONG_SPLIT_CHAR,
                       titles_split_char=DEF_SONG_TITLES_SPLIT_CHAR) -> List[Tuple[str, str]]:
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
        if author_title_split_char not in line:
            # No split character in line
            printer(f"Dropped line due to no split character: '{line}'")
            continue
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
        pass
    printer(f"Read {len(author_title)} author-title pairs.")
    return author_title


def single_search_youtube(single_author_title: Tuple[str, str]) -> Tuple[str, str]:
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


def search_youtube(author_title: List[Tuple[str, str]]):
    """
    Searches YouTube service fo each (author, song title) from input list
    :param author_title: List of tuples (author, song title)
    :return: List of SongObj
    """
    printer("Searching YouTube in progress")
    ret_list = []
    cnt = 0
    for author_title in author_title:
        ret = single_search_youtube(author_title)
        if any([not r for r in ret]):
            print('"' + ' '.join(author_title) + '" Not found in YouTube search')
            continue
        # Add link
        ret_list.append('# ' + ' - '.join(author_title))
        ret_list.append(ret[1])
        # Show progress
        cnt += 1
        printer(f'Done: {cnt}', end='\r')
        pass
    printer(f"\nGot {len(ret_list)} songs from YouTube")
    return ret_list


def save_to_file(txt_lines: List[str]) -> None:
    with open(DEF_OUT_FILE_NAME, 'w') as token:
        token.write('\n'.join(txt_lines))
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gen_links.py uses text file with author - title '
                                                 'lines and generates links to youtube videos')
    parser.add_argument('-in', '--input_txt_file',
                        help='Input text file containing author - title data', required=True)
    parser.add_argument('-out', '--output_txt_file',
                        help=f'Output text file containing links. Default is "{DEF_OUT_FILE_NAME}"', required=False)

    parser.add_argument('-atc', '--at_char',
                        help=f'Author-Title split character. Default is "{DEF_AUTHOR_SONG_SPLIT_CHAR}"', required=False)
    parser.add_argument('-stc', '--st_char',
                        help=f'Songs titles split character. Default is "{DEF_SONG_TITLES_SPLIT_CHAR}"', required=False)
    parser.add_argument('-quiet', action='store_false',
                        help='Do not show info in console excepts for errors.', required=False)
    args = vars(parser.parse_args())
    # Read arguments
    input_name = args['input_txt_file']
    PRINT_INFO = args['quiet']
    if args['at_char']:
        DEF_AUTHOR_SONG_SPLIT_CHAR = args['at_char']
    if args['st_char']:
        DEF_SONG_TITLES_SPLIT_CHAR = args['st_char']
    if args['output_txt_file']:
        DEF_OUT_FILE_NAME = args['output_txt_file']

    # Do stuff
    _lines = read_sort_text_file(input_name)
    _pairs = split_author_title(_lines)
    _lines = search_youtube(_pairs)
    save_to_file(_lines)
    pass
