import os
import subprocess
import src.lib

package_name = src.lib.get_package_name()


def create_deb_package():
    deb_pkg = package_name + '.deb'
    deb_pkg_dir = src.lib.search_directory('DEBIAN', os.getcwd())

    try:
        print(f"Building debian package: {deb_pkg} ...")
        subprocess.check_call(["dpkg", "-b", str(deb_pkg_dir), deb_pkg])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing debian package: {e}")
        return -1

    return 0


def create_execute_file(os_type):
    wsl_system = False

    if os_type == 'nt' and src.lib.check_distro() != 'windows':
        if os.path.exists(os.path.join(os.sep, 'run', 'WSL')):
            wsl_system = True

    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(script_dir, 'src')
    src_file = os.path.join(src_dir, 'main.py')

    tool = "pyinstaller"
    args = "--onefile --windowed --log-level=ERROR"
    exe_name = "--name" + ' ' + package_name
    cmd = str(tool + ' ' + args + ' ' + exe_name + ' ' + src_file)

    if wsl_system:
        cmd = f"powershell.exe -c \"{cmd}\""

    try:
        msg = f"Building execute file: {src_file} ..."
        if wsl_system:
            msg += ' in WSL build Win executable file (.exe) ...'

        print(msg)
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing execute file: {e}")
        return -1

    return 0


def main():
    def unix_system_build_execute_file():
        create_execute_file(os.name)

        if src.lib.check_distro() == 'debian':
            create_deb_package()

        return 0

    def dos_system_build_exe():
        if src.lib.check_distro() != 'windows':
            if not os.path.exists(
                    os.path.join(os.sep, 'run', 'WSL')):
                return 0

            print(f"{os.name}: WSL is detected !")

        return create_execute_file('nt')

    if os.name != 'nt':
        unix_system_build_execute_file()

    dos_system_build_exe()


if __name__ == "__main__":
    main()
