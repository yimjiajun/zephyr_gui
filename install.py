import os
import subprocess
import shutil
import src.lib


def install_debian_package():
    if src.lib.check_distro() != 'debian':
        return 0

    print('Installing Debian package...')
    script_path = src.lib.get_script_path(__file__)
    package_name = src.lib.get_package_name()
    pkg = package_name + '.deb'
    pkg_path = src.lib.search_file(pkg, script_path)
    if pkg_path == ' ':
        print('Error: Package not found !')
        return -1

    shutil.copy(pkg_path, '/tmp')
    pkg = os.path.join('/tmp', pkg)
    print(pkg)
    cmd = 'sudo apt install -y ' + pkg
    os.system(cmd)

    return 0


def install_execute_file(os_type):
    def install_win_exe():
        if os.name != 'nt':
            print('Error: Windows system not found !')
            return -1

        program = program_name + '.exe'
        program_path = src.lib.search_file(program, script_path)

        if program_path == ' ':
            return -1

        if src.lib.add_to_window_context_menu(program_path, program_name):
            print(f"Error: {os.path.basename(program_path)} not added to context menu.")
            return -1

        print(f"{os.path.basename(program_path)} added to context menu.")

        return 0

    def install_posix_exe():
        if os.name != 'posix':
            print('Error: Linux system not found !')
            return -1

        program = program_name
        program_path = src.lib.search_file(program, script_path)

        if program_path == ' ':
            return -1

        return 0

    script_path = src.lib.get_script_path(__file__)
    program_name = src.lib.get_package_name()

    if os.name == 'nt':
        return install_win_exe()

    return install_posix_exe()


def main():
    if src.lib.check_distro() == 'debian':
        install_debian_package()
    else:
        install_execute_file(os.name)


if __name__ == "__main__":
    main()
