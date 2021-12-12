#-*- coding: utf-8 -*-

import os, sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic



from UDP_Process import *
from process import *
from PLOT import *


GUI_class = uic.loadUiType('ui.ui')[0]

class mainWindow(QMainWindow, GUI_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        self.plt_ui = PLT_UI(self)
        self.plt_ui.show()


        
        self.udp_pack = UDP_pack(self)
        self.data_process = Process(self)
        self.data_process.Set_Text.connect(self.Set_Text)
        self.data_process.Set_Pixmap.connect(self.Set_Pixmap)
        self.data_process.Set_StyleSheet.connect(self.Set_StyleSheet)

        self.data_process.img_init()

        self.udp_pack.start()
        self.data_process.start()

    @pyqtSlot(str, str)
    def Set_Text(self, object, data):
        getattr(self, object).setText(data)

    @pyqtSlot(str, QPixmap)
    def Set_Pixmap(self, object, data):
        getattr(self,object).setPixmap(data)

    @pyqtSlot(str, str)
    def Set_StyleSheet(self, object, data):
        getattr(self, object).setStyleSheet(data)
        getattr(self, object).repaint()

    def closeEvent(self, evant):
        self.udp_pack.Working = False
        self.data_process.Working = False



def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)

    sys._excepthook(exctype, value, traceback)

if __name__ == "__main__":
    sys._excepthook = sys.excepthook
    sys.excepthook = my_exception_hook

    app  =QApplication(sys.argv)
    app.aboutToQuit.connect(mainWindow)
    MainWindow = mainWindow()
    app.exec()
