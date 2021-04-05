import argparse
import os


if __name__ == '__main__':
    # download_audio.py -in LINK_FILE -af AUDIO_FORMAT
    parser = argparse.ArgumentParser(description='gen_links.py uses text file with author - title '
                                                 'lines and generates links to youtube videos')
    parser.add_argument('-in',
                        help='Input text file containing youtube video links', required=True)
    parser.add_argument('-af',
                        help='Audio format used to save files', required=True)
    args = vars(parser.parse_args())

    command = f'youtube-dl -x -o %(title)s.%(ext)s --no-playlist ' \
              f'--audio-format {args["in"]} -a {args["af"]}'
    os.system(command)
    pass
