import os
import subprocess


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

    import winreg

    key_path = "Directory\\Background\\shell\\" + name
    key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)

    # set the icon to display for the menu item
    icon = f'"{file_path}"'
    winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)

    command_key = winreg.CreateKey(key, "command")
    winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, f"\"{file_path}\"")
    # close the registry key
    winreg.CloseKey(key)

    return 0


def check_pyintsaller_to_install():
    if os.name == 'nt':
        cmd = 'where'
    else:
        cmd = 'which'
    try:
        subprocess.check_call([cmd, 'pyinstaller'])
    except subprocess.CalledProcessError:
        print("PyInstaller is not installed, installing now...")
        subprocess.check_call(['pip', 'install', 'pyinstaller'])

    return 0
