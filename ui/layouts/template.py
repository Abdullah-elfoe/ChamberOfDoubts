""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

from config.general import WINDOW_WIDTH, WINDOW_HEIGHT


class Basic:
    def __init__(self):
        self.visible = False
        self.widthOfScreen = WINDOW_WIDTH
        self.heigthOfScreen = WINDOW_HEIGHT


    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False