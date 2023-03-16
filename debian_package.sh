#!/bin/bash

package_name="eczephyr"
prj_package_dir_name="zephyr_debian_package"
prj_path="$(dirname $(readlink -f "$0"))"
deb_pkg_file="${prj_package_dir_name}.deb"
deb_pkg="${prj_path}/${deb_pkg_file}"
commands=('create' 'install' 'uninstall')

function debian_pacakge_cmd_process {
	function create {
		dpkg -b "${prj_path}/${prj_package_dir_name}" "$deb_pkg"
		return
	}

	function install {
		deb_pkg_tmp_file="/tmp/$deb_pkg_file"
		if [ ! -f "$deb_pkg" ]; then
			echo -e "\033[1;31m error\033[0m: debian package is not found!" >&2
			exit 1
		fi
		cp "$deb_pkg" "$deb_pkg_tmp_file"
		# sudo dpkg -i "${prj_path}/${prj_package_dir_name}.deb"
		sudo apt install "$deb_pkg_tmp_file"
		return
	}

	function uninstall {
		# sudo dpkg -P "${package_name}"
		sudo apt remove "${package_name}"
		return
	}

	if [ $# -ge 1 ]; then
		case "$1" in
			'create')
				create
				;;
			'install')
				install
				;;
			'uninstall')
				uninstall
				;;
			*)
				echo -e "\033[1;31m error\033[0m:'$1' selected command is unrecognized" >&2
				exit 1
				;;
		esac
		return
	fi

	while [[ true ]]; do
		echo -e "\033[1;32mSelect a command to execute:\033[0m:" >&1
		select cmd_sel in "${commands[@]}" "quit"; do
			case "${cmd_sel}" in
				'create')
					create
					;;
				'install')
					install
					;;
				'uninstall')
					uninstall
					;;
				'quit')
					exit 0
					;;
				*)
					echo -e "\033[1;31m error\033[0m:'$1' selected command is unrecognized" >&2
					exit 1
					;;
			esac
			break
		done
	done

	return
}

debian_pacakge_cmd_process "$@"
sleep 0.5

exit 0
