import os
import subprocess
import winreg


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
                return os.path.abspath(os.path.join(dirpath, filename))
    return ' '


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


def get_script_path(file):
    file_path = os.path.realpath(file)
    return os.path.dirname(file_path)


def check_shell_command_available(cmd):
    try:
        subprocess.check_output(["which", cmd])
    except subprocess.CalledProcessError:
        return -1

    return 0


def add_to_window_context_menu(file_path, name):
    if os.name != 'nt':
        return -1

    # key_path = r"Directory\\Background\\shell\\MyApp"
    # key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
    # winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Open with MyApp")
    # command_key = winreg.CreateKey(key, "command")
    # winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, f"\"{file_path}\"")
    # get the file extension and create a key for it
    file_ext = os.path.splitext(file_path)[1]
    key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, file_ext)

    # create a subkey for the file type
    sub_key = winreg.CreateKey(key, "shell")

    # create a subkey for the menu item
    menu_key = winreg.CreateKey(sub_key, name)

    # set the command to run when the menu item is clicked
    winreg.SetValueEx(menu_key, "", 0, winreg.REG_SZ, f'"{file_path}"')

    # set the icon to display for the menu item
    winreg.SetValueEx(menu_key, "Icon", 0, winreg.REG_SZ, f'"{file_path}"')

    # close the registry keys
    winreg.CloseKey(menu_key)
    winreg.CloseKey(sub_key)
    winreg.CloseKey(key)

    return 0
