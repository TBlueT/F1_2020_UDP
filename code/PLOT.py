from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class plot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(311, xlim=(0, 100), ylim=(-10, 110))
        self.axes.axis('off')
        self.axes2 = fig.add_subplot(312, xlim=(0, 100), ylim=(-10, 110))
        self.axes2.axis('off')
        self.axes3 = fig.add_subplot(337, xlim=(-10, 10), ylim=(-10, 10))
        self.axes3.grid()
        #self.axes3.axis('off')

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

        self.x = [0,]
        self.y = [0,]
        self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, color='#00ff00', lw=4)

        self.x2 = [0,]
        self.y2 = [0,]
        self.line2, = self.canvas.axes2.plot(self.x2, self.y2, animated=True,color='red', lw=4)

        self.x3 = 0
        self.y3 = 0
        self.line3, = self.canvas.axes3.plot(self.x3, self.y3, 'ro', animated=True,  lw=5)

        self.ani = animation.FuncAnimation(self.canvas.figure, self.updata, blit=True, interval=25)
        self.ani2 = animation.FuncAnimation(self.canvas.figure, self.updata2, blit=True, interval=25)
        self.ani3 = animation.FuncAnimation(self.canvas.figure, self.updata3, blit=True, interval=25)

    def update_canvas(self, id, data):
        if id == 1:
            self.throttle = data
        elif id == 2:
            self.brake = data
        elif id == 3:
            self.x = [0,]
            self.y = [0,]

            self.x2 = [0,]
            self.y2 = [0,]
            self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, color='#00ff00', lw=4)
            self.line2, = self.canvas.axes2.plot(self.x2, self.y2, animated=True, color='red', lw=4)

        elif id == 5:
            self.y3 = -(self.y3+data)/2
        elif id == 6:
            self.x3 = (self.x3+data)/2

    def updata(self, i):
        self.x = self.x + [len(self.x)]
        self.y = self.y + [self.throttle]

        self.line.set_data(self.x, self.y)
        backX = len(self.x)-50
        self.canvas.axes.set_xlim(0 if backX < 0 else backX, len(self.x))
        return [self.line]

    def updata2(self, i):
        self.x2 = self.x2 + [len(self.x2)]
        self.y2 = self.y2 + [self.brake]

        self.line2.set_data(self.x2, self.y2)
        backX = len(self.x)-50
        self.canvas.axes2.set_xlim(0 if backX < 0 else backX, len(self.x2))
        return [self.line2]

    def updata3(self, i):
        self.line3.set_data(self.x3, self.y3)
        return [self.line3]
