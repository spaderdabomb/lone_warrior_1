import subprocess
import ctypes
import sys

def get_capslock_state():
    capslock = None
    if sys.platform == "win32":
        hllDll = ctypes.WinDLL ("User32.dll")
        VK_CAPITAL = 0x14
        capslock = hllDll.GetKeyState(VK_CAPITAL)
    elif sys.platform == "darwin":
        if subprocess.check_output('xset q | grep LED', shell=True)[65] == 50:
            capslock = False
        if subprocess.check_output('xset q | grep LED', shell=True)[65] == 51:
            capslock = True

    return capslock


# def resize_image(file_name: str, pixels_x, pixels_y, overwrite=False):
#     from PIL import Image
#
#     fname, ext = file_name.split(".")
#     size = pixels_x, pixels_y
#
#     im = Image.open(file_name)
#
#     if overwrite:
#         size = pixels_x, pixels_y
#         im_resized = im.resize(size, Image.ANTIALIAS)
#         im_resized.save(file_name, dpi=(pixels_x, pixels_y))
#     else:
#         full_path = fname + "_" + str(pixels_x) + "x" + str(pixels_y) + "." + ext
#         im_resized = im.resize(size, Image.ANTIALIAS)
#         im_resized.save(full_path, "PNG")
#
#     return size

class CounterClass():
    def __init__(self):
        self.counter = 0

    def increase_counter(self):
        self.counter += 1
        return self.counter

