import tkinter as tk
import subprocess
import os
import re
import glob
import shutil

color_bg = "black"
color_fg = "white"
font_size = 8
font_select = "Times New Roman"
script_dir = os.path.dirname(os.path.abspath(__file__))
width = 600
height = 500
default_board_option_menu_msg = "Select Board"

if os.name == 'nt':
    home_dir = os.path.expanduser('~')
else:
    home_dir = os.environ['HOME']

prj_conf_dir = ".eczephyr"
board_file = os.path.join(home_dir, prj_conf_dir, 'board.txt')
download_file = os.path.join(home_dir, prj_conf_dir, 'download.txt')

def display_msg(msg, type):
    display = msg
    output_text.delete(1.0, tk.END)
    # Insert new text
    output_text.insert(tk.END, display, type)
    output_text.see("end")  # scroll the widget to show the latest text


def display_building_msg():
    output_text.insert(tk.END, "Building ...\n")
    # scroll the widget to show the latest text
    output_text.see("end")
    # schedule the next update after 1 second
    output_text.after(1000, display_building_msg)


def run_command(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
        # read the output of the command line-by-line
        line = proc.stdout.readline().decode()
        if not line:
            break
        # insert each line of output into the Text widget
        output_text.insert(tk.END, line)
        # update the display of the text widget
        output_text.see(tk.END)
        output_text.update()

    return proc.returncode


def chmod_recursive(path, mode):
    if os.name == 'nt':  # Windows OS
        return 0  # No need to change the permission

    os.chmod(path, mode)
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), mode)
        for file in files:
            os.chmod(os.path.join(root, file), mode)

    return 0


def pre_build_setup(topdir, board):
    def zepyr_env_setup():
        toolchain_env = 'ZEPHYR_TOOLCHAIN_VARIANT'
        toolcain_val = 'zephyr'
        os.environ[toolchain_env] = toolcain_val

        if os.name != 'nt':
            os.system(f'export {toolchain_env}={toolcain_val}')

        output_text.insert("end", f"Success: Exported {toolchain_env}={toolcain_val}\n", 'notify')
        output_text.see("end")

        return 0

    def mchp_family_config(topdir, board):
        def export_spi_gen_path(env, path):
            os.environ[env] = path

            if os.name != 'nt':
                os.system(f'export {env}={path}')

            output_text.insert("end", f"Success: Exported {env}={path}\n", 'notify')
            output_text.see("end")
            return 0

        def mec172x_family(board):
            if os.name == 'nt':
                spi_gen = 'mec172x_spi_gen_win.exe'
            else:
                spi_gen = 'mec172x_spi_gen_lin_x86_64'

            path = os.path.join(mchp_spi_gen_path,
                                'MEC172x',
                                'SPI_image_gen',
                                spi_gen)
            export_spi_gen_path('MEC172X_SPI_GEN', path)
            return 0, board

        def mec170x_family(board):
            return -1, board

        def mec152x_family(board):
            def board_wrapper(board):
                if board.startswith('mec1523'):
                    board = 'mec1501' + board[7:]
                return board

            if os.name == 'nt':
                spi_gen = 'everglades_spi_gen_RomE.exe'
            else:
                spi_gen = 'everglades_spi_gen_RomE'

            path = os.path.join(mchp_spi_gen_path,
                                'MEC152x',
                                'SPI_image_gen',
                                spi_gen)
            export_spi_gen_path('EVERGLADES_SPI_GEN', path)

            return 0, board_wrapper(board)

        def mec150x_family(board):
            if os.name == 'nt':
                spi_gen = 'everglades_spi_gen.exe'
            else:
                spi_gen = 'everglades_spi_gen_lin64'

            path = os.path.join(mchp_spi_gen_path,
                                'MEC1501',
                                'SPI_image_gen',
                                spi_gen)
            export_spi_gen_path('EVERGLADES_SPI_GEN', path)
            return 0, board

        mchp_spi_gen_dir = 'CPGZephyrDocs'
        mchp_spi_gen_path = os.path.join(topdir, mchp_spi_gen_dir)
        mchp_spi_gen_url = 'https://github.com/MicrochipTech/CPGZephyrDocs.git'
        mchp_series = ["mec172", "mec150", "mec152", "mec170"]

        if not os.path.exists(mchp_spi_gen_path):
            output_text.insert("end", "Download Microchip SPI generator ...\n", 'info')
            output_text.see("end")
            cmd = "git clone " + mchp_spi_gen_url + ' --depth=1 ' + mchp_spi_gen_path
            run_command(cmd)
            # if run_command(cmd) != 0:
            #     output_text.insert("end", "Failed: Downloaded Microchip SPI generator\n", 'error')
            #     output_text.see("end")
            #     return -1
            # Search for the directory named "SPI_image_gen"
            output_text.insert("end", "Success: Downloaded Microchip SPI generator\n", 'notify')
            output_text.see("end")

            output_text.insert("end", "Change to execute mode\n", 'info')
            output_text.see("end")
            chmod_recursive(mchp_spi_gen_path, 0o755)
            # for root, dirs, files in os.walk(mchp_spi_gen_path):
            #     if "SPI_image_gen" in dirs:
            #         spi_dir = os.path.join(root, "SPI_image_gen")
            #         # Search for files whose names contain "spi_gen" and set execute permission on them
            #         for file in spi_dir:
            #             print(f'file = {file}')
            #             if "spi_gen" in file:
            #                 filepath = os.path.join(root, file)
            #                 print(filepath)
            #                 os.chmod(filepath, 0o755)
        # Search for matches with any of the patterns
        matches = [pattern for pattern in
                   mchp_series
                   if pattern in board]
        # Perform independent actions for each match found
        for match in matches:
            if match == "mec172":
                err, board = mec172x_family(board)
                if err:
                    return -1
                break
            elif match == "mec150":
                err, board = mec150x_family(board)
                if err:
                    return -1
                break
            elif match == "mec152":
                err, board = mec152x_family(board)
                if err:
                    return -1
                break
            elif match == "mec170":
                err, board = mec170x_family(board)
                if err:
                    return -1
                break
            else:
                output_text.insert("end", "Fatal Error: Board Not Found in match !\n", 'error')
                output_text.see("end")
                return -1

        cmd = "west config --local" + " build.board " + board
        run_command(cmd)

        return 0

    if zepyr_env_setup():
        return -1

    if re.compile('[mec]').match(board):
        output_text.insert("end", "Board is MEC family!\n", 'info')
        output_text.see("end")
        return mchp_family_config(topdir, board)
    else:
        output_text.insert("end", "Error: Board is not MEC family!\n", 'error')
        output_text.see("end")

    return -1

def setup_workspace_variables():
    workspace_topdir = subprocess.check_output('west topdir', shell=True, stderr=subprocess.STDOUT)
    workspace_topdir = workspace_topdir.decode().strip()
    manifest_path = subprocess.check_output('west config --local manifest.path', shell=True, stderr=subprocess.STDOUT)
    manifest_path = manifest_path.decode().strip()
    ec_app_path = os.path.join(workspace_topdir, manifest_path)
    build_path = os.path.join(ec_app_path, 'build')
    build_board = selected_option.get()

    if not bool(build_board):
        output_text.insert("end", "Fatal Error: Empty Option Menu!\n", 'error')
        output_text.see("end")
        return -1

    if build_board == default_board_option_menu_msg:
        output_text.insert("end", "Error: Please select a board first !\n", 'error')
        output_text.see("end")
        return -1

    if pre_build_setup(workspace_topdir, build_board) != 0:
        output_text.insert("end", "Error: Board not supported !\n", 'error')
        output_text.see("end")
        return -1

    return 0, workspace_topdir, ec_app_path, build_path, build_board


def get_default_board():
    try:
        default_board = subprocess.check_output('west config --local build.board', shell=True, stderr=subprocess.STDOUT)
        default_board = default_board.decode().strip()
    except subprocess.CalledProcessError:
        default_board = "unknow"

    return default_board


def run_command_build():

    if selected_option.get() != get_default_board():
        pristine = "--pristine"
    else:
        pristine = ""

    err, workspace_topdir, ec_app_path, build_path, build_board = setup_workspace_variables()

    if err:
        return -1

    cmd = "west build" + ' ' + pristine + ' ' + "--cmake" + ' ' + \
        "--build-dir" + ' ' + build_path + ' ' + \
        ec_app_path

    run_command(cmd)


def west_workspace_init():
    west_config_cmd = "west config --local"
    zephyr_rtos_path = os.path.join('ecfwwork', 'zephyr_fork')
    conf_zephyr_base = "zephyr.base" + ' ' + zephyr_rtos_path
    conf_zephyr_base_prefer = "zephyr.base-prefer 'configfile'"
    conf_val = [conf_zephyr_base, conf_zephyr_base_prefer]

    try:
        output_text.insert("end", "west workspace Start Initialization!\n", 'normal')
        return_code = subprocess.check_call(['west', 'init', '-l'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        return_code = e.returncode
        msg = "Error: west workspace has been initializtion !"
        output_text.insert("end", msg, 'error')
        output_text.see("end")

    for conf in conf_val:
        cmd = west_config_cmd + ' ' + conf
        subprocess.call(cmd, shell=True, stderr=subprocess.STDOUT)

    output = subprocess.check_output('west config -l', shell=True, stderr=subprocess.STDOUT)
    output_text.insert("end", "Success: west workspace setup done !\n", 'notify')
    output_text.insert("end", "\nwest workspace configuration details:\n", 'normal')
    output_text.insert("end", output.decode() + "\n", 'normal')
    output_text.see("end")


def west_workspace_update():
    def update_intel_ec_zephyr_patch(patch_path, target_path):
        patterns = [r'v2_(\d+)', r'v(\d+)']
        # Find all patch files in the current directory
        patch_path = os.path.join(patch_path, '*.patch')
        patches = glob.glob(patch_path)
        # Initialize variables for the maximum version number and the corresponding filename
        max_version = 0
        newest_patch_file = ''
        max_patch = 0
        # Loop through each patch file
        for file in patches:
            # Search for the version pattern in the filename
            for pattern in patterns:
                match = re.search(pattern, file)
                if match:
                    break

            # If the pattern is found in the filename
            if match:
                # Get the version number from the match object
                version_num = match.group(1) if match.lastindex else 0
                version_num = int(version_num)

                # Search for the patch number in the filename
                match = re.search(r'(\d+)\.patch$', file)

                # If the pattern is found in the filename
                if match:
                    # Get the patch number from the match object
                    patch_num = int(match.group(1))

                    # If the version number is greater than the current maximum
                    if version_num > max_version:
                        # Update the maximum version and filename
                        max_version = version_num
                        max_patch = patch_num
                        newest_patch_file = file
                    elif version_num == max_version and patch_num > max_patch:
                        # Update the maximum patch number and filename
                        max_patch = patch_num
                        newest_patch_file = file

        if not newest_patch_file:
            return -1

        patch_path = os.path.join(patch_path, newest_patch_file)

        # try:
        output_text.insert("end",
                           "start apply intel zephyr patch: " + patch_path + "...\n",
                           'normal')
        output_text.see("end")
        cmd = 'git -C ' + target_path + ' am ' + patch_path
        # cmd = ["git", "-C", target_path, "am", patch_path]
        # subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if run_command(cmd) != 0:
            cmd = 'git -C ' + target_path + ' am --abort'

            if run_command(cmd) != 0:
                cmd = 'git -C ' + target_path + ' reset --hard'
                run_command(cmd)
        else:
            output_text.insert("end", "Success: applied intel zephyr patch !\n", 'notify')
            output_text.see("end")
        # except subprocess.CalledProcessError as e:
        #     output_text.insert(tk.END, e.stderr, 'error')
        #     output_text.see("end")
        #     cmd = ["git", "-C", target_path, "reset", "--hard"]
        #     subprocess.run(cmd, capture_output=True, text=True)
        #     return -1

        return 0

    # try:
    workspace_path = subprocess.check_output('west topdir',
                                             shell=True, stderr=subprocess.STDOUT)
    manifest_path = subprocess.check_output('west config --local manifest.path',
                                            shell=True, stderr=subprocess.STDOUT)

    workspace_path = workspace_path.decode().strip()
    manifest_path = manifest_path.decode().strip()
    target_path = os.path.join(workspace_path, manifest_path)
    output_text.insert("end", "Start West Update\n", 'normal')
    output_text.see("end")

    cmd = 'west update -n'
    run_command(cmd)
        # subprocess.check_call(['west', 'update', '-n'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # except subprocess.CalledProcessError as e:
    #     return_code = e.returncode
    #     msg = "Error: west workspace update failed !\n"
    #     output_text.insert(tk.END, msg, 'error')
    #     output_text.see("end")
    #     return -1

    output_text.insert("end", "West Update Completed!\n", 'normal')
    output_text.see("end")

    intel_zephyr_patches_path = "zephyr_patches"
    target_path = os.path.join(target_path, intel_zephyr_patches_path)

    if (os.path.exists(target_path)):
        output_text.insert("end", "Found Zephyr Patches to apply !\n", 'normal')
        output_text.see("end")
        zephyr_rtos_path = subprocess.check_output('west config --local zephyr.base',
                                                   shell=True, stderr=subprocess.STDOUT)
        zephyr_rtos_path = zephyr_rtos_path.decode().strip()
        zephyr_rtos_path = os.path.join(workspace_path, zephyr_rtos_path)

        if update_intel_ec_zephyr_patch(target_path, zephyr_rtos_path) != 0:
            output_text.insert("end", "Failed: west workspace update !\n", 'error')
            output_text.see("end")
            return -1

    check_west_workspace()

    output_text.insert("end", "Success: west workspace update !\n", 'notify')
    output_text.see("end")

    return 0


def run_command_download():

    def setup_window_download():
        new_window_download.title("Download")
        new_win_dl_width = 400
        new_win_dl_height = 400
        new_window_download.geometry('{}x{}'.format(new_win_dl_width, new_win_dl_height))
        screen_width = new_window_download.winfo_screenwidth()
        screen_height = new_window_download.winfo_screenheight()
        x = screen_width - new_win_dl_width - 100 - width
        y = screen_height - new_win_dl_height - 200
        new_window_download.geometry('+{}+{}'.format(x, y))
        new_window_download.grid_rowconfigure(0, weight=1)
        new_window_download.grid_columnconfigure(0, weight=1)
        new_window_download.configure(background=color_bg)

    def setup_window_download_label():
        new_win_dl_frame_label = tk.Frame(new_window_download, bd=1, relief=tk.SOLID, background=color_bg)
        new_win_dl_frame_label.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky='nsew')
        new_win_dl_frame_label.grid_rowconfigure(0, weight=1)
        new_win_dl_frame_label.grid_columnconfigure(0, weight=1)
        new_win_dl_label = tk.Label(new_win_dl_frame_label, text="Embedded Controller Firmware Application", font=(font_select, 12))
        new_win_dl_label.grid(row=0, column=0, columnspan=2, padx=0, pady=0)
        new_win_dl_label.configure(foreground=color_fg, background=color_bg)
        new_win_dl_label_2 = tk.Label(new_win_dl_frame_label, text="Choose a projectt to download", font=(font_select, font_size))
        new_win_dl_label_2.grid(row=1, column=0, columnspan=1, padx=0, pady=0)
        new_win_dl_label_2.configure(foreground=color_fg, background=color_bg)

    def setup_window_download_optional_menu():
        new_win_dl_frame_optional = tk.Frame(new_window_download, bd=1, relief=tk.SOLID, background=color_bg)
        new_win_dl_frame_optional.grid(row=1, column=0, padx=0, pady=0, sticky='nsew')
        new_win_dl_frame_optional.grid_rowconfigure(0, weight=1)
        new_win_dl_frame_optional.grid_columnconfigure(0, weight=1)
        new_win_dl_sel_option = tk.StringVar(new_win_dl_frame_optional)
        option_menu = tk.OptionMenu(new_win_dl_frame_optional, new_win_dl_sel_option, *prj_name)
        option_menu.pack()
        option_menu.configure(width=25, foreground="yellow", background="grey")

        return new_win_dl_sel_option

    def download_source_code():
        try:
            cmd = ['west', 'topdir']
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        except subprocess.CalledProcessError:
            prj_name_sel = prj_name_selected_opt_menu.get()

            if not prj_name_sel in prj_name:
                return -1
            else:
                repo_url = prj_url[prj_name.index(prj_name_sel)]
                workspace_name = prj_name_sel.lower().replace(" ", "_")

                target_dir = os.path.join(os.getcwd(), 'sandbox_' + workspace_name)

                for i in range(0, 99):
                    if not os.path.exists(target_dir + '_' + str(i)):
                        target_dir += '_' + str(i)
                        break

                target_dir = os.path.join(target_dir, 'ecfw-zephyr')
                cmd = "git clone" + ' ' + repo_url + ' ' + target_dir
                new_window_download.destroy()
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

                while True:
                    line = proc.stdout.readline().decode()
                    if not line:
                        break
                    output_text.insert(tk.END, line)
                    output_text.see("end")
                    output_text.update()

                msg = prj_name_sel + ' ' + "cloned into " + target_dir
                output_text.insert("end", msg + "\n\n", 'normal')
                output_text.see("end")
                os.chdir(target_dir)
                current_path.configure(text=os.getcwd())
                west_workspace_init()

        west_workspace_update()

        return 0

    def setup_window_download_button():
        f_btn = tk.Frame(new_window_download, bd=1, relief=tk.SOLID, background=color_bg)
        f_btn.grid(row=1, column=1, padx=0, pady=0)
        btn = tk.Button(f_btn, text="Download", command=download_source_code)
        btn.grid(row=0, column=0)
        btn.configure(foreground="yellow", background="grey")

    try:
        cmd = ['west', 'topdir']
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return west_workspace_update()
    except subprocess.CalledProcessError:
        new_window_download = tk.Toplevel()

        prj_name = []
        prj_url = []

        if not os.path.exists(download_file):
            prj_name.append("Intel Open Source EC-Firmware")
            prj_url.append("https://github.com/intel/ecfw-zephyr")
        else:
            with open(download_file, 'r') as f:
                lines = f.readlines()
                # Loop through each line in the file, starting from the second row
                for line in lines[2:]:
                    # Split the line based on the pipe symbol surrounded by spaces and strip any whitespace
                    values = [v.strip() for v in line.split('|') if v.strip()]
                    # Add the values to the respective columns
                    prj_name.append(values[0])
                    prj_url.append(values[1])
                f.close()

        setup_window_download()
        setup_window_download_label()
        setup_window_download_button()
        prj_name_selected_opt_menu = setup_window_download_optional_menu()


def run_command_menu():
    err, workspace_topdir, ec_app_path, build_path, build_board = setup_workspace_variables()

    if err:
        return -1

    cmd = "west build " + "--cmake " + \
        "--target guiconfig " + ' ' + \
        "--build-dir " + build_path + ' ' + \
        ec_app_path

    err = run_command(cmd)

    if err:
        output_text.insert("end", 'Error: west kconfig menu failed !', 'error')
        output_text.see("end")
        return -1

    cmd = "west build " + "--cmake " + \
        "--build-dir " + build_path + ' ' + \
        ec_app_path

    run_command(cmd)


def find_bin_files(directory, bin_files):
    bin = ' '

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename in bin_files:
                bin = os.path.join(root, filename)
                break
    return bin

def merge_bin(src1_bin, src2_bin, target_path):
    if not os.path.exists(src1_bin) or not os.path.exists(src2_bin):
        return -1, ' '

    target_bin = os.path.join(target_path, 'combined.bin')

    if os.path.exists(target_bin):
        os.remove(target_bin)

    with open(src1_bin, 'rb') as file1, open(src2_bin, 'rb') as file2:
        contents1 = file1.read()
        contents2 = file2.read()

    with open(target_bin, 'wb') as file1:
        file1.write(contents1 + contents2)

    return 0, target_bin

def run_command_flash():
    def get_rom_addr(board):
        def mec172x_family(board):
            flash_bin = ['kcs.bin', 'spi_gen.bin']
            if 'evb' in board:
                addr = 0
            else:
                addr = 0x1000

            return addr, flash_bin

        def mec170x_family(board):
            flash_bin = ['kcs.bin', 'spi_gen.bin']
            if 'evb' in board:
                addr = 0
            else:
                addr = 0x1000

            return addr, flash_bin

        def mec152x_family(board):
            flash_bin = ['kcs.bin', 'spi_gen.bin']
            if 'evb' in board:
                addr = 0
            else:
                addr = 0x1000

            return addr, flash_bin

        def mec150x_family(board):
            flash_bin = ['kcs.bin', 'spi_gen.bin']
            if 'evb' in board:
                addr = 0
            else:
                addr = 0x1000

            return addr, flash_bin


        chip_series = ["mec172", "mec150", "mec152", "mec170"]
        addr = -1
        flash_bin = 'zephyr.bin'

        matches = [pattern for pattern in
                   chip_series
                   if pattern in board]
        # Perform independent actions for each match found
        for match in matches:
            if match == "mec172":
                addr, flash_bin = mec172x_family(board)
                break
            elif match == "mec150":
                addr, flash_bin = mec150x_family(board)
                break
            elif match == "mec152":
                addr, flash_bin = mec152x_family(board)
                break
            elif match == "mec170":
                addr, flash_bin = mec170x_family(board)
                break
            else:
                output_text.insert("end", "Fatal Error: Board Not Found in match !\n", 'error')
                output_text.see("end")
                return -1, ' '

        return addr, flash_bin

    def flash_rom(tool, addr, build_path, flash_bin):
        def read_flash(tool, size, build_path):
            bin = selected_option.get() + '.bin'
            read_bin = os.path.join(build_path, bin)
            err = -1

            if os.path.exists(read_bin):
                os.remove(read_bin)

            if tool == 'dediprog':
                if os.name == 'nt':
                    tool = 'dpcmd.exe'
                else:
                    tool = 'dpcmd'

                cmd = tool + " -r " + read_bin + " -s " + str(size)
                err = run_command(cmd)
            else:
                read_bin = ' '

            if err:
                output_text.insert("end", 'Error: Flash Read Failed !', 'error')
                output_text.see("end")

            return err, read_bin

        def write_flash(tool, bin, build_path):
            if not os.path.exists(bin):
                return -1

            cmd = 'west flash' +  ' --skip-rebuild ' + \
                ' --build-dir ' + build_path + \
                ' --runner ' + tool

            err = run_command(cmd)

            if err:
                return -1

        start_addr = 0
        read_size = 0
        read_bin = ' '

        if addr != start_addr:
            read_size = addr - start_addr

        if read_size > 0:
            err, read_bin = read_flash(tool, read_size, build_path)
            if err or not os.path.exists(read_bin):
                return -1

        bin = find_bin_files(build_path, flash_bin)

        if bin == ' ':
            output_text.insert("end", 'Error: No Binary File Found !', 'error')
            output_text.see("end")
            return -1

        bk_bin = bin + '~'

        if os.path.exists(bk_bin):
            os.remove(bk_bin)

        shutil.copy(bin, bk_bin)

        if read_size > 0:
            if not os.path.exists(read_bin):
                return -1

            err, bin = merge_bin(read_bin, bin, build_path)

            if err:
                return -1

        output_text.insert("end", f'Write flash bin : {bin}\n', 'notify')
        output_text.see("end")

        err = write_flash(tool, bin, build_path)

        if os.path.exists(bk_bin) and os.path.exists(bin):
            os.remove(bin)
            shutil.copy(bk_bin, bin)
        if err:
            return -1

        output_text.insert("end", f'Success: Flash to ROM address : {addr}', 'notify')
        output_text.see("end")

        return 0

    err, workspace_topdir, ec_app_path, build_path, build_board = setup_workspace_variables()

    if err:
        return -1

    output_text.insert("end", 'Processing flash ....\n', 'info')
    output_text.see("end")

    rom_addr, flash_bin = get_rom_addr(build_board)

    output_text.insert("end", f'Board = {build_board}\n', 'info')
    output_text.insert("end", f'Flash Address = {rom_addr}\n', 'info')
    output_text.insert("end", f'Flash Supported bin = {flash_bin}\n', 'info')
    output_text.see("end")

    if rom_addr < 0 or not flash_bin:
        output_text.insert("end", f'Error: Exit flash processing ... !\n', 'error')
        output_text.see("end")
        return -1

    output_text.insert("end", '> start flash ....\n', 'info')
    output_text.see("end")

    err = flash_rom('dediprog', rom_addr, build_path, flash_bin)

    output_text.insert("end", '< end flash ....\n', 'info')
    output_text.see("end")

    if err:
        output_text.insert("end", 'Error: Flash to ROM Failed !', 'error')
        output_text.see("end")
        return -1

    output_text.insert("end", 'Finish Flash !\n', 'notify')
    output_text.see("end")

    return 0


def get_manifest_path():
    workspace_topdir = subprocess.check_output('west topdir', shell=True, stderr=subprocess.STDOUT)
    workspace_topdir = workspace_topdir.decode().strip()
    manifest_path = subprocess.check_output('west config --local manifest.path', shell=True, stderr=subprocess.STDOUT)
    manifest_path = manifest_path.decode().strip()
    ec_app_path = os.path.join(workspace_topdir, manifest_path)

    return ec_app_path

def get_support_board_to_optionmenu():
    board_options = []

    try:
        return_code = subprocess.check_call(['west', 'topdir'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        return_code = e.returncode
        msg = "Error: west workspace not found in current path !"
        output_text.insert(tk.END, msg, 'error')
        output_text.see("end")

    if return_code == 0:
        cmd = "west boards"
        output = subprocess.check_output(
                    cmd, shell=True, stderr=subprocess.STDOUT)
        output = output.decode('utf-8')
        lines = output.split('\n')
        for line in lines:
            if 'mec' in line.lower():
                board_options.append(line.strip())

        if os.path.exists(board_file):
            with open(board_file, 'r') as file:
                for line in file:
                    if 'mec' in line.lower():
                        board_options.append(line.strip())
                file.close()

        ec_app_path = get_manifest_path()
        ec_app_path = os.path.join(ec_app_path, 'out_of_tree_boards', 'boards')

        for root, dirs, files in os.walk(ec_app_path):
            for dir in dirs:
                if 'mec' in dir:
                    board_options.append(dir)

        try:
            cmd = "west config build.board"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            output = output.strip()
            display = output.decode()
        except subprocess.CalledProcessError as e:
            output = e.output.decode('utf-8')
            display = default_board_option_menu_msg

        if len(selected_option.get()) == 0:
            selected_option.set(display)
            option_menu = tk.OptionMenu(frame_optional, selected_option, *board_options)
            option_menu.pack()
            option_menu.configure(width=25, foreground="yellow", background="grey")


def check_west_workspace():
    try:
        return_code = subprocess.check_call(['west', 'topdir'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        return_code = e.returncode

    if return_code == 0:
        get_support_board_to_optionmenu()
        button1.config(state="active")
        button2.config(text="Update", state="active")
        button3.config(state="active")
        button4.config(state="active")
    else:
        button1.config(state="disabled")
        button3.config(state="disabled")
        button4.config(state="disabled")

    return 0


window = tk.Tk()
window.geometry('{}x{}'.format(width, height))
# get the dimensions of the screen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
# set the window position to the lower-right corner of the screen
x = screen_width - width - 50
y = screen_height - height - 100
window.geometry('+{}+{}'.format(x, y))
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
window.configure(background=color_bg)
# window.geometry("400x400")
# window.maxsize(400,400)
# window.minsize(400,400)
window.title("eczephyr")

frame_label = tk.Frame(window,
                       # width=200, height=200,
                       bd=1, relief=tk.SOLID,
                       background=color_bg)
frame_label.grid(row=0, column=0, padx=0, pady=0, sticky='nsew')
frame_label.grid_rowconfigure(0, weight=1)
frame_label.grid_columnconfigure(0, weight=1)
frame_button = tk.Frame(window,
                        # width=200, height=200,
                        bd=1, relief=tk.SOLID,
                        background=color_bg)
frame_button.grid(row=2, column=0, padx=0, pady=0)
frame_optional = tk.Frame(window,
                          # width=200, height=200,
                          bd=1, relief=tk.SOLID,
                          background=color_bg)
frame_optional.grid(row=3, column=0, padx=0, pady=0, sticky='nsew')
frame_optional.grid_rowconfigure(0, weight=1)
frame_optional.grid_columnconfigure(0, weight=1)
frame_display = tk.Frame(window,
                         # width=200, height=200,
                         # bd=1, relief=tk.SOLID,
                         background=color_bg)
frame_display.grid(row=4, column=0, padx=0, pady=0, sticky='nsew')
frame_display.grid_rowconfigure(0, weight=1)
frame_display.grid_columnconfigure(0, weight=1)

label = tk.Label(frame_label,
                 text="Zephyr Project RTOS", font=(font_select, 24))
label.grid(row=0, column=0, padx=0, pady=0)
label.configure(foreground=color_fg, background=color_bg)

current_path = tk.Label(frame_label,
                        text=os.getcwd(), font=(font_select, font_size))
current_path.grid(row=1, column=0, padx=0, pady=0)
current_path.configure(foreground="green", background=color_bg)

button1 = tk.Button(frame_button, text="Build", command=run_command_build)
button1.grid(row=0, column=0)
button1.configure(foreground="yellow", background="grey")

button2 = tk.Button(frame_button, text="Download", command=run_command_download)
button2.grid(row=0, column=1)
button2.configure(foreground="yellow", background="grey")

button3 = tk.Button(frame_button, text="Menu", command=run_command_menu)
button3.grid(row=0, column=2)
button3.configure(foreground="yellow", background="grey")

button4 = tk.Button(frame_button, text="Flash", command=run_command_flash)
button4.grid(row=0, column=3)
button4.configure(foreground="yellow", background="grey")

output_text = tk.Text(frame_display)
output_text.grid(row=0, column=0, padx=0, pady=0)
output_text.config(
    foreground="white", background="black", font=(font_select, font_size))
output_text.tag_configure(
    "notify", foreground="green", font=(font_select, font_size))
output_text.tag_configure(
    "warning", foreground="yellow", font=(font_select, font_size))
output_text.tag_configure(
    "error", foreground="red", font=(font_select, font_size))
output_text.tag_configure(
    "info", foreground="white", font=(font_select, font_size))

selected_option = tk.StringVar(frame_optional)

check_west_workspace()

window.mainloop()
