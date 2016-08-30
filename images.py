import inspect
import os
import sys
import Tkinter as tk

class Images(object):
    """ A class to load and cache the images displayed in the application. """
    
    __images = {}

    @staticmethod
    def Get(name):
        """ Get the image with the specifed name. """
        if not name in Images.__images:
            imageDirectory = Images.__getImageDir()
            imagePath = os.path.join(imageDirectory, name)
            Images.__images[name] = tk.PhotoImage(file=imagePath)
        return Images.__images[name]

   
    @staticmethod
    def __getImageDir():
        """ Get the directory to load the images from. """
        scriptDir = Images.get_script_dir()
        return os.path.join(scriptDir, "images")

    @staticmethod
    def get_script_dir(follow_symlinks=True):
        """ Get the directory the the script is located in. """
        if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
            path = os.path.abspath(sys.executable)
        else:
            path = inspect.getabsfile(Images.get_script_dir)
        if follow_symlinks:
            path = os.path.realpath(path)
        return os.path.dirname(path)
