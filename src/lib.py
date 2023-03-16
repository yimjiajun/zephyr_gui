import os


def get_package_name():
    package_name = 'eczephyr'
    return package_name


def search_directory(target_dir, search_dir):
    for dirpath, dirnames, filenames in os.walk(search_dir):
        for dir in dirnames:
            if dir == target_dir:
                return os.path.abspath(dirpath)
    return ' '


def search_file(target_file, search_dir):
    for dirpath, dirnames, filenames in os.walk(search_dir):
        for filename in filenames:
            if filename == target_file:
                return os.path.abspath(dirpath)
    return None


def check_distro():
    if os.name == 'nt':
        return 'windows'

    with open('/etc/os-release') as f:
        for line in f:
            if line.startswith('ID_LIKE='):
                distro_id = line.split('=')[1].strip()
                return distro_id

    return 'unknown'


def get_home_path():
    if os.name == 'nt':
        home_dir = os.path.expanduser('~')
    else:
        home_dir = os.environ['HOME']

    return home_dir
