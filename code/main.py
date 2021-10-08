#-*- coding: utf-8 -*-

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
        self.show()

        self.udp_pack = UDP_pack(self)
        self.data_process = Process(self)
        self.udp_pack.start()
        self.data_process.start()

        self.data_process.Set_Text.connect(self.Set_Text)
        self.data_process.Set_Pixmap.connect(self.Set_Pixmap)
        self.data_process.Set_StyleSheet.connect(self.Set_StyleSheet)

    @pyqtSlot(str, str)
    def Set_Text(self, object, data):
        getattr(self, object).setText(data)

    @pyqtSlot(str, QImage)
    def Set_Pixmap(self, object, data):
        getattr(self,object).setPixmap(QtGui.QPixmap.fromImage(data))
        #time.sleep(0.001)

    @pyqtSlot(str, str)
    def Set_StyleSheet(self, object, data):
        getattr(self, object).setStyleSheet(data)

    def carStatusData_ui(self, ID, object, data):
        if ID == "setStyleSheet":
            getattr(self, object).setStyleSheet(data)
            #time.sleep(0.001)
        elif ID == "setText":
            getattr(self, object).setText(data)

        elif ID == "setPixmap":
            getattr(self, object).setPixmap(data)
            #time.sleep(0.001)
            #getattr(self, object).repaint()

    def closeEvent(self, evant):
        self.udp_pack.Working = False
        self.data_process.Working = False



def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)

    sys._excepthook(exctype, value, traceback)

if __name__ == "__main__":
    sys._excepthook = sys.excepthook
    sys.excepthook = my_exception_hook

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(mainWindow)
    MainWindow = mainWindow()
    app.exec()