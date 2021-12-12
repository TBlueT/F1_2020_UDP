from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

from PyQt5.QtWidgets import *

from Cdll import *

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

        self.MathsDll = DLL()
        self.sum = self.MathsDll.Function("Sum", [c_double, c_double], c_double)
        self.sub = self.MathsDll.Function("Sub", [c_double, c_double], c_double)
        self.mul = self.MathsDll.Function("Mul", [c_double, c_double], c_double)
        self.div = self.MathsDll.Function("Div", [c_double, c_double], c_double)

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

        self.xG = 0
        self.yG = 0
        self.xG_data = 0
        self.yG_data = 0
        self.line3, = self.canvas.axes3.plot(self.xG, self.yG, 'ro', animated=True,  lw=5)

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
            self.yG_data = -data
        elif id == 6:
            self.xG_data = data

    def updata(self, i):
        self.x = self.x + [len(self.x)]
        self.y = self.y + [self.throttle]

        self.line.set_data(self.x, self.y)
        backX = self.sub(len(self.x), 50)
        self.canvas.axes.set_xlim(0 if backX < 0 else backX, len(self.x))
        return [self.line]

    def updata2(self, i):
        self.x2 = self.x2 + [len(self.x2)]
        self.y2 = self.y2 + [self.brake]

        self.line2.set_data(self.x2, self.y2)
        backX = self.sub(len(self.x), 50)
        self.canvas.axes2.set_xlim(0 if backX < 0 else backX, len(self.x2))
        return [self.line2]

    def updata3(self, i):
        x = self.sum(self.xG, self.xG_data)
        self.xG = self.div(x, 2)
        y = self.sum(self.yG, self.yG_data)
        self.yG = self.div(y, 2)
        self.line3.set_data(self.xG, self.yG)
        return [self.line3]
