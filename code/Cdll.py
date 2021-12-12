from ctypes import *

import os

class DLL:
    def __init__(self):
        self.lodDll = windll.LoadLibrary(os.path.dirname(os.path.realpath(__file__)) + "\\Maths.dll")

    def Function(self, name, input, output):
        temporary = self.lodDll[name]
        temporary.argtypes = input
        temporary.restype = output

        return temporary