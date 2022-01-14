from shutil import copy2, move as shmove, unpack_archive
from time import sleep
from os import listdir, remove, mkdir
import getpass
from json import loads

SCRIPT_NAME = "Downloads Manager"


def print_with_script_name(message, end='\n'):
    print(f'[{SCRIPT_NAME}]: {message}', end=end)


dir_path = str(__file__).replace('downloads_manager.py', '')
username = getpass.getuser()
user_dir = None

DOWNLOADS_PATH = dict()

# List of files that have already been checked
ignored_files = []

# Restore from cache
with open(dir_path+'ignored_files.txt', encoding='UTF-8') as ign_f:
    for line in ign_f:
        ignored_files.append(line.strip())


PATHS_AND_EXTENSIONS = None


# Keep ignoring file by its name (optimization)
def ignore(filename):
    ignored_files.append(filename)
    with open(dir_path+'ignored_files.txt', 'a', encoding='UTF-8') as ign_f:
        ign_f.write(filename + '\n')


# Creates directory from zip archive src in dst folder, then removes .zip file.
# If something goes wrong, just moves an archive to dst folder
def unzip(src, dst):
    print_with_script_name(f'Unarchived {src}')
    try:
        unpack_archive(f'{DOWNLOADS_PATH}/{src}', extract_dir=f'{dst}/{src.replace(src.split(".")[-1], "")}', format='zip')
        remove(src)
    except Exception as e:
        move(src, dst)
        print_with_script_name(f'{src} caused {str(e)}')


# Moves src file to dst folder
def move(src, dst):
    print_with_script_name(f'Moved {src}')
    # ignore(src)
    try:
        shmove(f'{DOWNLOADS_PATH}/{src}', dst)
    except Exception as e:
        print_with_script_name(f'{src} caused {e.__class__}')


# Main method that checks for any available for moving files
def check():
    files = listdir(DOWNLOADS_PATH)
    for file in files:
        is_archive = False
        if file in ignored_files:
            continue
        extension = file.split('.')[-1]
        path_to_copy = None
        for item in PATHS_AND_EXTENSIONS:
            if extension in item['extensions']:
                is_archive = extension == 'zip'
                path_to_copy = item['path']
        if path_to_copy:
            if not is_archive:
                move(file, path_to_copy)
            else:
                unzip(file, path_to_copy)
        ignore(file)


def load_json_as_dict(path_to_json) -> dict:
    raw = ''
    with open(path_to_json, encoding='utf-8') as f:
        raw = str(f.read(8192))
    raw = raw.replace('%username%', username)

    # TODO optimize
    raw_json = loads(raw)
    raw = raw.replace('%user_dir%', raw_json['USER_DIR_PATH'])
    raw_json = loads(raw)
    raw = raw.replace('%downloads_dir%', raw_json['DOWNLOADS_PATH'])
    print_with_script_name('Config loaded')
    return loads(raw)


def prepare_paths_and_extensions():
    global DOWNLOADS_PATH, PATHS_AND_EXTENSIONS
    config = load_json_as_dict(f'{dir_path}downloads_manager_config.json')

    DOWNLOADS_PATH = config['DOWNLOADS_PATH']
    PATHS_AND_EXTENSIONS = config['paths']

import sys
if __name__ == '__main__':
    print_with_script_name("Welcome to Downloads Manager!")
    print_with_script_name(f'Username:{username}')
    prepare_paths_and_extensions()

    assert PATHS_AND_EXTENSIONS

    # Create directories that may be missing
    for item in PATHS_AND_EXTENSIONS:
        try:
            mkdir(item['path'])
            print_with_script_name(f"Created directory: {item['path']}")
        except FileExistsError as e:
            pass
        except Exception as e:
            print_with_script_name(f'Warning! Unknown error: {str(e)}')

    # Check if script is already running
    try:
        remove(dir_path + 'run.txt')
        recreate = open(dir_path + 'run.txt', 'w')
        recreate.write('0x01110')
    except PermissionError:
        print_with_script_name("Error: script is already running. Shutting down")
        exit()
    i = 0
    while True:
        check()
        sleep(2)
