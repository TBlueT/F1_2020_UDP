#-*- coding:utf-8 -*-

import os, sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

from UDP_Process import *
from process import *

GUI_class = uic.loadUiType('ui.ui')[0]

class mainWindow(QMainWindow, GUI_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.udp_pack = UDP_pack(self)
        self.data_process = Process(self)
        self.udp_pack.start()
        self.data_process.start()

    def lapData_ui(self, object, data):
        getattr(self, object).setText(data)

    def carTelemetryData_ui(self, object, data):
        getattr(self,object).setText(data)

    def carStatusData_ui(self, ID, object, data):
        if ID == "setStyleSheet":
            getattr(self, object).setStyleSheet(data)
        elif ID == "setText":
            getattr(self, object).setText(data)



def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)

    sys._excepthook(exctype, value, traceback)

if __name__ == "__main__":
    sys._excepthook = sys.excepthook
    sys.excepthook = my_exception_hook

    app = QApplication(sys.argv)
    MainWindow = mainWindow()
    MainWindow.show()
    app.exec()