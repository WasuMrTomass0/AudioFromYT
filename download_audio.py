import argparse
import os


if __name__ == '__main__':
    # download_audio.py -in LINK_FILE -af AUDIO_FORMAT
    parser = argparse.ArgumentParser(description='gen_links.py uses text file with author - title '
                                                 'lines and generates links to youtube videos')
    parser.add_argument('-in',
                        help='Input text file containing youtube video links', required=True)
    parser.add_argument('-af', default='mp3',
                        help='Audio format used to save files. Default is mp3', required=False)
    parser.add_argument('-dir', default='downloaded_audio_files',
                        help='Save directory. Default is downloaded_audio_files', required=False)
    args = vars(parser.parse_args())

    # Read arguments
    save_directory = args["dir"]
    curr_dir = os.getcwd()
    path_to_file = os.path.join(curr_dir, args["in"])
    # create directory if needed
    if not os.path.isdir(save_directory):
        os.mkdir(save_directory)
    # Change directory
    os.chdir(save_directory)
    # Execute command
    command = f'youtube-dl -x -o %(title)s.%(ext)s --no-playlist ' \
              f'--audio-format {args["af"]} -a {path_to_file}'
    os.system(command)
    # Switch to previous directory
    os.chdir(curr_dir)
    pass
