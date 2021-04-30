from shutil import copy2, move as shmove, unpack_archive
from time import sleep
from os import listdir, remove, mkdir
import getpass
from json import loads

dir_path = str(__file__).replace('downloads_manager.py', '')
username = getpass.getuser()
user_dir = None

DOWNLOADS_PATH = f'{user_dir}Downloads'

PICTURES_PATH = f'{user_dir}OneDrive\\Изображения\\Downloaded'
PICTURES_EXTENSIONS = ('jpg', 'jpeg', 'png', 'bmp', 'ico')

DOCUMENTS_PATH = f'{user_dir}OneDrive\\Documents\\Downloaded'
DOCUMENTS_EXTENSIONS = ('pdf', 'csv', 'txt', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
                        'accdb', 'db', 'html')

VIDEOS_PATH = f'{user_dir}Videos\\Downloaded'
VIDEOS_EXTENSIONS = ('mp4', 'avi', 'mkv', 'm4a')

MUSIC_PATH = f'{user_dir}Music\\Downloaded'
MUSIC_EXTENSIONS = ('mp3', 'ogg', 'wav')

ARCHIVES_PATH = f'{user_dir}Downloads\\Archives'
ARCHIVES_EXTENSIONS = ('zip', 'rar', '7z')

EXE_PATH = f'{user_dir}Downloads\\Exe-files'
EXE_EXTENSIONS = ('exe', 'msi', 'jar')

TEMP_PATH = f'{user_dir}Downloads\\Temp'
TEMP_EXTENSIONS = ('torrent', 'TEMP', 'osz', 'osk')

PROGRAMMING_PATH = f'{user_dir}Downloads\\Programming-files'
PROGRAMMING_EXTENSIONS = ('cpp', 'c', 'h', 'hpp', 'java', 'py', 'dll', 'dart', 'rb')

MISC_PATH = f'{user_dir}Downloads\\Misc'
MISC_EXTENSIONS = ('ini', 'ics', 'vsix', 'ttf', 'tur')

# List of files that have already been checked
ignored_files = []

# Restore from cache
with open(dir_path+'ignored_files.txt', encoding='UTF-8') as ign_f:
    for line in ign_f:
        ignored_files.append(line.strip())

PATHS_AND_EXTENSIONS = ((PICTURES_PATH, PICTURES_EXTENSIONS), (DOCUMENTS_PATH, DOCUMENTS_EXTENSIONS),
                        (VIDEOS_PATH, VIDEOS_EXTENSIONS), (MUSIC_PATH, MUSIC_EXTENSIONS),
                        (ARCHIVES_PATH, ARCHIVES_EXTENSIONS), (EXE_PATH, EXE_EXTENSIONS), (TEMP_PATH, TEMP_EXTENSIONS),
                        (PROGRAMMING_PATH, PROGRAMMING_EXTENSIONS), (MISC_PATH, MISC_EXTENSIONS))


# Keep ignoring file by its name (optimization)
def ignore(filename):
    ignored_files.append(filename)
    with open(dir_path+'ignored_files.txt', 'a', encoding='UTF-8') as ign_f:
        ign_f.write(filename + '\n')


# Creates directory from zip archive src in dst folder, then removes .zip file.
# If something goes wrong, just moves an archive to dst folder
def unzip(src, dst):
    print(f'Unarchived {src}')
    try:
        unpack_archive(f'{DOWNLOADS_PATH}\\{src}', extract_dir=f'{dst}\\{src.replace(src.split(".")[-1], "")}', format='zip')
        remove(src)
    except Exception as e:
        move(src, dst)
        print(f'{src} caused {str(e)}')


# Moves src file to dst folder
def move(src, dst):
    print(f'Moved {src}')
    # ignore(src)
    try:
        shmove(f'{DOWNLOADS_PATH}\\{src}', dst)
    except Exception as e:
        print(f'{src} caused {e.__class__}')


# Main method that checks for any available for moving files
def check():
    files = listdir(DOWNLOADS_PATH)
    for file in files:
        is_archive = False
        if file in ignored_files:
            continue
        extension = file.split('.')[-1]
        path_to_copy = None
        for path, extensions in PATHS_AND_EXTENSIONS:
            if extension in extensions:
                is_archive = extension == 'zip'
                path_to_copy = path
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

    raw_json = loads(raw)
    raw = raw.replace('%user_dir%', raw_json['USER_DIR_PATH'])
    print(raw)
    raw_json = loads(raw)
    raw = raw.replace('%downloads_dir%', raw_json['DOWNLOADS_PATH'])


    return loads(raw)


def prepare_paths_and_extensions():
    config = load_json_as_dict('downloads_manager_config.json')
    print(config)


if __name__ == '__main__':
    prepare_paths_and_extensions()
    # Create directories that may be missing
    for path, ext in PATHS_AND_EXTENSIONS:
        try:
            mkdir(path)
            print(f"Created directory: {path}")
        except FileExistsError as e:
            pass
        except Exception as e:
            print(f'Warning! Unknown error: {str(e)}')

    # Check if script is already running
    remove(dir_path + 'run.txt')
    recreate = open(dir_path + 'run.txt', 'w')
    recreate.write('0x01110')

    while True:
        check()
        sleep(2)
