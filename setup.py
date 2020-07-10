import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"include_files": [r"enemies.py", r"game_data.py", r"globals.py", r"load_sprites.py",
                                       r"main.py", r"misc_classes.py", r"player.py", "sound_manager.py",
                                       r"C:\Users\jpdodson\Box\Programming\Python\PycharmProjects\lone_warrior_1\Assets",
                                       r"C:\Users\jpdodson\Box\Programming\Python\PycharmProjects\lone_warrior_1\Utils",
                                       r"C:\Users\jpdodson\Box\Programming\Python\PycharmProjects\lone_warrior_1\Views"],
                     "packages": ["os", "pyglet", "yaml", "arcade"], "excludes": ["tkinter", "PySide2", "PyQt5"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Monster Hunter",
        version = "0.1",
        description = "My GUI application!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("main.py", base=base)])