#-*- coding: utf-8 -*-

import os, sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

from UDP_Process import *
from process import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.pyplot as plt

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
#        self.plt_ui.init(self)
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

class plot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(211, xlim=(0, 100), ylim=(-10, 110))
        self.axes.axis('off')
        self.axes2 = fig.add_subplot(212, xlim=(0, 100), ylim=(-10, 110))
        self.axes.axis('off')

        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def compute_initial_figure(self):
        pass


class PLT_UI(QDialog):
    def __init__(self, parent=None):
        super(PLT_UI, self).__init__(parent)
        QMainWindow.__init__(self)


        self.throttle = 0
        self.brake = 0
        vbox = QVBoxLayout()
        self.canvas = plot(self, width=10, height=8, dpi=100)
        vbox.addWidget(self.canvas)
        hbox = QHBoxLayout()
        self.setLayout(vbox)

        self.x = [[0],[0]]
        self.y = [[0],[0]]
        self.next_x = 0
        self.line, = self.canvas.axes.plot(self.x[0], self.y[0], animated=False, color='blue', lw=4)
        self.line, = self.canvas.axes.plot(self.x[1], self.y[1], animated=True, color='#00ff00',
                                           lw=4)

        self.x2 = [[0],[0]]
        self.y2 = [[0],[0]]
        self.next_x2 = 0
        self.line2, = self.canvas.axes2.plot(self.x2, self.y2, animated=True,color='red', lw=4)

        self.ani = animation.FuncAnimation(self.canvas.figure, self.updata, blit=True, interval=25)
        self.ani2 = animation.FuncAnimation(self.canvas.figure, self.updata2, blit=True, interval=25)

    def update_canvas(self, id, data):
        if data and id == 1:
            self.throttle = data
        if data and id == 2:
            self.brake = data
        if data and id == 3:
            self.next_x += 1
            if self.next_x > 1:
                self.next_x = 0

            self.x[self.next_x] = [0]
            self.y[self.next_x] = [0]

            nextNext = 0 if self.next_x == 1 else 1
            self.line, = self.canvas.axes.plot(self.x[nextNext], self.y[nextNext], animated=False, color='blue', lw=4)
            self.line, = self.canvas.axes.plot(self.x[self.next_x], self.y[self.next_x], animated=True, color='#00ff00', lw=4)

            self.next_x2 += 1
            if self.next_x2 > 1:
                self.next_x2 = 0
            self.x2[self.next_x2] = [0]
            self.y2[self.next_x2] = [0]
            nextNext = 0 if self.next_x == 1 else 1
            self.line2, = self.canvas.axes2.plot(self.x2[nextNext], self.y2[nextNext], animated=False, color='blue', lw=4)
            self.line2, = self.canvas.axes2.plot(self.x2[self.next_x2], self.y2[self.next_x2], animated=True, color='red',
                                               lw=4)


    def updata(self, i):
        self.x[self.next_x] = self.x[self.next_x] + [len(self.x[self.next_x])]
        self.y[self.next_x] = self.y[self.next_x] + [self.throttle]

        self.line.set_data(self.x[self.next_x], self.y[self.next_x])
        backX = 0#len(self.x[self.next_x])-50
        self.canvas.axes.set_xlim(0 if backX < 0 else backX, len(self.x[self.next_x]))
        return [self.line]

    def updata2(self, i):
        self.x2[self.next_x2] = self.x2[self.next_x2] + [len(self.x2[self.next_x2])]
        self.y2[self.next_x2] = self.y2[self.next_x2] + [self.brake]

        self.line2.set_data(self.x2[self.next_x2], self.y2[self.next_x2])
        backX = len(self.x[self.next_x]) - 50
        self.canvas.axes2.set_xlim(0 if backX < 0 else backX, len(self.x2[self.next_x2]))
        return [self.line2]


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