# Zephyr RTOS GUI

<img src="https://raw.githubusercontent.com/wiki/yimjiajun/zephyr_gui/image/eczephyr_sample.jpg" alt="eczephyr sample image" width="600"/>

## Installation

Zephyr RTOS project requirement tools should been installed

[Getting Started of Zephyr Project](https://docs.zephyrproject.org/latest/develop/getting_started/index.html)

- _west tool chain recommendation install globally rather than python environment._

1. Build source becomes debian package or executable file:

    - unix/window(or mouse click):

        ```bash
        python3 build.py
        ```

    `eczpehyr.deb`, `dist/eczephyr`, `dist/eczephyr.exe` been generated after success build.

      * _`eczephyr.deb` and `dist/eczephyr`: not generated in MS-DOS._

      * _`dist/eczephyr.exe`: will generated in **WSL**_

2. Install debian package (Linux) or executable file (Window):

    - unix/window(or mouse click):

        ```bash
        python3 install.py
        ```

3. Process zephyr GUI:

    - unix:

        ```bash
        eczephyr gui
        ```

    - window:

      1. right-click mouse button

      2. select `eczephyr`

          <img src="https://raw.githubusercontent.com/wiki/yimjiajun/zephyr_gui/image/eczephyr_cortext_menu.jpg" alt="eczephyr context menu display image" width="200"/>

## Usage

1. Download Intel Open EC firmware

- Click **Download**:

    <img src="https://raw.githubusercontent.com/wiki/yimjiajun/zephyr_gui/image/eczephyr_download.jpg" alt="eczephyr download" width="400"/>

  - Select Project to Download:

      <img src="https://raw.githubusercontent.com/wiki/yimjiajun/zephyr_gui/image/eczephyr_select_to_download.jpg" alt="eczephyr download selection" width="400"/>
