from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

from PyQt5.QtWidgets import *


import threading
import numpy as np

from Cdll import *

class plot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_facecolor('black')
        self.axes = fig.add_subplot(311, xlim=(0, 100), ylim=(-10, 110))

        self.axes.axis('off')
        self.axes2 = fig.add_subplot(312, xlim=(0, 100), ylim=(-10, 110))
        self.axes2.axis('off')
        self.axes3 = fig.add_subplot(337, xlim=(-10, 10), ylim=(-10, 10))
        self.axes3.grid()
        self.axes4 = fig.add_subplot(338, xlim=(-10, 10), ylim=(-10, 10))
        self.axes4.grid()
        self.axes5 = fig.add_subplot(339, xlim=(-1000, 1000), ylim=(-1000, 1000))
        self.axes5.axis('off')

        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def compute_initial_figure(self):
        pass


class PLT_UI(QDialog):
    def __init__(self, parent=None):
        super(PLT_UI, self).__init__(parent)
        QMainWindow.__init__(self)

        self.MathsDll = DLL()
        self.sum = self.MathsDll.Function("Sum", [c_double, c_double], c_double)
        self.sub = self.MathsDll.Function("Sub", [c_double, c_double], c_double)
        self.mul = self.MathsDll.Function("Mul", [c_double, c_double], c_double)
        self.div = self.MathsDll.Function("Div", [c_double, c_double], c_double)
        self.rot_x = self.MathsDll.Function("Rot_x", [c_double, c_double, c_double], c_double)
        self.rot_y = self.MathsDll.Function("Rot_y", [c_double, c_double, c_double], c_double)
        self.Cangle = self.MathsDll.Function("CAngle", [c_double, c_double], c_double)

        self.throttle = 0
        self.brake = 0
        vbox = QVBoxLayout()
        self.canvas = plot(self, width=8, height=8, dpi=100)
        vbox.addWidget(self.canvas)
        hbox = QHBoxLayout()
        self.setLayout(vbox)

        self.x = [0, ]
        self.y = [0, ]
        self.x_old = [0, ]
        self.y_old = [0, ]
        self.line_old, = self.canvas.axes.plot(self.x_old, self.y_old, animated=True, color='#0000ff', lw=2)
        self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, color='#00ff00', lw=4)


        self.x2 = [0, ]
        self.y2 = [0, ]
        self.x2_old = [0, ]
        self.y2_old = [0, ]
        self.line2_old, = self.canvas.axes2.plot(self.x2_old, self.y2_old, animated=True, color='#0000ff', lw=2)
        self.line2, = self.canvas.axes2.plot(self.x2, self.y2, animated=True,color='red', lw=4)

        self.xG = 0
        self.yG = 0
        self.xG_data = 0
        self.yG_data = 0
        self.line3, = self.canvas.axes3.plot(self.xG, self.yG, 'ro', animated=True,  lw=5)

        self.steer_data = 0
        self.xSteer = np.cos(np.radians(np.arange(360)))*8
        self.ySteer = np.sin(np.radians(np.arange(360)))*8
        self.xSteer2 = np.cos(np.radians(-1*np.arange(5)))*8
        self.ySteer2 = np.sin(np.radians(-1*np.arange(5)))*8
        self.xSteer2 = np.append(self.xSteer2, [self.xSteer2[len(self.xSteer2)-1], -self.xSteer2[len(self.xSteer2)-1]])
        self.ySteer2 = np.append(self.ySteer2, [self.ySteer2[len(self.ySteer2)-1], self.ySteer2[len(self.ySteer2)-1]])
        self.xSteer2 = np.append(self.xSteer2, [0, 0])
        self.ySteer2 = np.append(self.ySteer2, [self.ySteer2[len(self.ySteer2)-1], self.ySteer[270]])
        self.line4, = self.canvas.axes4.plot(self.xSteer, self.ySteer, 'g', animated=True,  lw=8)
        self.line4_2, = self.canvas.axes4.plot(self.xSteer2, self.ySteer2, 'g', animated=True, lw=8)

        self.xPintData = []
        self.yPintData = []
        self.xPintMap = []
        self.yPintMap = []
        self.xPintMap_old = []
        self.yPintMap_old = []
        self.line5_old, = self.canvas.axes5.plot(self.xPintMap_old, self.yPintMap_old, '#0000ff', animated=True, lw=1)
        self.line5, = self.canvas.axes5.plot(self.xPintMap, self.yPintMap, '#00ff00', animated=True, lw=0.5)

        self.ani = animation.FuncAnimation(self.canvas.figure, self.updata, blit=True, interval=25)
        self.ani2 = animation.FuncAnimation(self.canvas.figure, self.updata2, blit=True, interval=25)
        self.ani3 = animation.FuncAnimation(self.canvas.figure, self.updata3, blit=True, interval=25)
        self.ani4 = animation.FuncAnimation(self.canvas.figure, self.updata4, blit=True, interval=25)
        self.ani5 = animation.FuncAnimation(self.canvas.figure, self.updata5, blit=True, interval=25)

        self.q = 0.0
        self.xMap = []
        self.yMap = []
        self.speed = []
        self.gamePaused = False

    def update_canvas(self, id, data):

        if id == 0:
            self.gamePaused = data
        elif id == 1:
            self.throttle = data
        elif id == 2:
            self.brake = data
        elif id == 3:

            self.x_old = self.x
            self.y_old = self.y
            self.x = [0,]
            self.y = [0,]

            self.x2_old = self.x2
            self.y2_old = self.y2
            self.x2 = [0,]
            self.y2 = [0,]

            self.xPintMap_old = self.xPintMap
            self.yPintMap_old = self.yPintMap
            self.xPintMap = []
            self.yPintMap = []

        elif id == 5:
            self.yG_data = -data
        elif id == 6:
            self.xG_data = data

        elif id == 7:
            self.steer_data = -data

        elif id == 8:
            self.xPintData = -data
        elif id == 9:
            self.yPintData = data

        elif id == 10:
            self.speed = data

    def updata(self, i):
        if self.gamePaused and self.speed != 0.0:
            self.x = self.x + [len(self.x)]
            self.y = self.y + [self.throttle]

            if len(self.x_old) > 5:
                self.line_old.set_data(self.x_old, self.y_old)
            self.line.set_data(self.x, self.y)
            backX = self.sub(len(self.x), 50)
            self.canvas.axes.set_xlim(0 if backX < 0 else backX, len(self.x))


        return [self.line_old, self.line]

    def updata2(self, i):
        if self.gamePaused and self.speed != 0.0:
            self.x2 = self.x2 + [len(self.x2)]
            self.y2 = self.y2 + [self.brake]

            self.line2.set_data(self.x2, self.y2)
            self.line2_old.set_data(self.x2_old, self.y2_old)

            backX = self.sub(len(self.x), 50)
            self.canvas.axes2.set_xlim(0 if backX < 0 else backX, len(self.x2))
        return [self.line2_old, self.line2]

    def updata3(self, i):
        if self.gamePaused:
            x = self.sum(self.xG, self.xG_data)
            self.xG = self.div(x, 2)
            y = self.sum(self.yG, self.yG_data)
            self.yG = self.div(y, 2)
            self.line3.set_data(self.xG, self.yG)
        return [self.line3]

    def updata4(self, i):
        if self.gamePaused:
            r = np.radians(self.steer_data)
            s = np.sin(r)
            c = np.cos(r)

            xMap = (self.xSteer2 * c) - (self.ySteer2 * s)
            yMap = (self.xSteer2 * s) + (self.ySteer2 * c)

            self.line4_2.set_data(xMap, yMap)
        return [self.line4, self.line4_2]

    def updata5(self, i):
        if self.gamePaused:
            if self.xPintData:
                self.xPintMap = np.append(self.xPintMap, self.xPintData)
            if self.yPintData:
                self.yPintMap = np.append(self.yPintMap, self.yPintData)
            xMap = []
            yMap = []
            xMap_old = []
            yMap_old = []
            if len(self.xPintMap) >= 2 and self.speed != 0.0:
                xmaplen = self.xPintMap.size
                ymaplen = self.yPintMap.size
                if self.xPintMap[xmaplen - 1] != self.xPintMap[xmaplen - 2]:
                    x = self.xPintMap[xmaplen-1] - self.xPintMap[xmaplen - 2]
                    y = self.yPintMap[ymaplen-1] - self.yPintMap[ymaplen - 2]
                    d = self.Cangle(x,y)

                    r = np.radians(d)
                    s = np.sin(r)
                    c = np.cos(r)
                    xMap = (self.xPintMap * c) - (self.yPintMap * s)
                    yMap = (self.xPintMap * s) + (self.yPintMap * c)

                    xMap = xMap.tolist()
                    yMap = yMap.tolist()
                    if len(self.xPintMap_old):
                        xMap_old = (self.xPintMap_old * c) - (self.yPintMap_old * s)
                        yMap_old = (self.xPintMap_old * s) + (self.yPintMap_old * c)

                        xMap_old = xMap_old.tolist()
                        yMap_old = yMap_old.tolist()
            if xMap:
                self.line5_old.set_data(xMap_old, yMap_old)
                self.line5.set_data(xMap, yMap)
                self.canvas.axes5.set_xlim(xMap[len(xMap)-1] - 280, xMap[len(xMap)-1] + 280)
            if yMap:
                self.canvas.axes5.set_ylim(yMap[len(yMap)-1] - 280, yMap[len(yMap)-1] + 280)
        return [self.line5_old, self.line5]

    def drowmap(self, d):
        for x, x_data in enumerate(self.xPintMap):
            self.xMap = np.append(self.xMap, self.rot_x(d, x_data, self.yPintMap[x]))
        for y, y_data in enumerate(self.yPintMap):
            self.yMap = np.append(self.yMap, self.rot_y(d, self.xPintMap[y], y_data))
