import sys
from PyQt5 import QtCore, QtWidgets, Qt, QtGui
from PyQt5.QtMultimedia import QSound
# from PyQt5.QtCore import pyqtSlot

class Timer(QtWidgets.QWidget):

    def __init__(self):
        super(Timer, self).__init__()
        self.duration = 0               # in minutes
        self.remaining = self.duration
        self.proportion = 0.0
        #self.update_time()

        # display options
        self.nullPosition = 90             # top, 0 is left
        self.outlinePenWidth = 0.0           # width of border around bar
        self.dataPenWidth = 0.0              # width of inner border
        self.rebuildBrush = True           # rebuild brush at the beginning
        self.gradientData = [QtGui.QColor.fromRgb(255,255,255),   # white
                             QtGui.QColor.fromRgb(0  ,169  ,254)]   # blue
        self.donutThicknessRatio = 0.85    # thickness of bar, 1 means no bar

        # run control
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tic)
        self.tic_length = 100    # in ms
        self.is_running = False
        self.is_finished = False

        self.sound = QSound('sound.wav')
        # print self.sound.isAvailable()

    def mousePressEvent(self, QMouseEvent):
        if not self.is_finished:
            if self.is_running:
                self.is_running = False
                self.timer.stop()
            else:
                self.is_running = True
                self.timer.start(self.tic_length)

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.timer.stop()
        self.is_running = False
        self.hide()
        self.parent().buttons.show()

    # @pyqtSlot()
    def run_timer(self, duration):
        self.duration = duration
        self.remaining = self.duration
        self.proportion = 0.0
        self.gradientData = [QtGui.QColor.fromRgb(255, 255, 255),  # white
                             QtGui.QColor.fromRgb(0, 169, 254)]  # blue
        #self.update_time()
        self.update()
        self.show()
        # setup timer for count down
        self.is_running = True
        self.timer.start(self.tic_length)

    def tic(self):
        if self.remaining > 0:

            if self.proportion < 100.0:
                self.proportion += (100 * float(self.tic_length) / 6000.0)
            else:
                #self.timer.stop()
                self.proportion = 0.0
                self.remaining -= 1

            if (self.duration > 3 and self.remaining <= 3) or (self.duration <= 3 and self.remaining <= 1):
                self.gradientData = [QtGui.QColor.fromRgb(255, 255, 255),  # white
                                     QtGui.QColor.fromRgb(255, 50  , 0  )]

        else:
            self.proportion = 100.0
            self.is_running = False
            self.is_finished = True
            self.sound.play()
            self.timer.stop()

        self.rebuildBrush = True
        self.update()

    def paintEvent(self, event):
        outerRadius = min(self.width(), self.height())
        baseRect = QtCore.QRectF(1, 1, outerRadius-2, outerRadius-2)

        buffer = QtGui.QImage(outerRadius, outerRadius, QtGui.QImage.Format_ARGB32)
        buffer.fill(0)

        p = QtGui.QPainter(buffer)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        # data brush
        self.rebuildDataBrushIfNeeded()

        # draw background
        # p.fillRect(buffer.rect(), self.palette().background())

        # draw base circle
        p.setPen(QtGui.QPen(self.palette().shadow().color(), self.outlinePenWidth))
        p.setBrush(self.palette().base())
        p.drawEllipse(baseRect)

        # data circle
        arcStep = 360.0 / 100.0 * self.proportion
        self.drawValue(p, baseRect, arcStep)

        # draw inner background
        innerRect, innerRadius = self.calculateInnerRect(baseRect, outerRadius)
        p.setBrush(self.palette().alternateBase())
        cmod = p.compositionMode()
        p.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
        p.drawEllipse(innerRect)
        p.setCompositionMode(cmod)

        # text
        self.drawText(p, innerRect, innerRadius, self.proportion)

        # finally draw the bar
        p.end()

        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, buffer)

    def drawValue(self, p, baseRect, arcLength):
        # nothing to draw
        #if value == 0:
        #    return

        # for Pie and Donut styles
        dataPath = QtGui.QPainterPath()
        dataPath.setFillRule(Qt.Qt.WindingFill)

        # pie segment outer
        dataPath.moveTo(baseRect.center())
        dataPath.arcTo(baseRect, self.nullPosition, -arcLength)
        dataPath.lineTo(baseRect.center())

        p.setBrush(self.palette().highlight())
        p.setPen(QtGui.QPen(self.palette().shadow().color(), self.dataPenWidth))
        p.drawPath(dataPath)

    def calculateInnerRect(self, baseRect, outerRadius):
        innerRadius = outerRadius * self.donutThicknessRatio

        delta = (outerRadius - innerRadius) / 2.
        innerRect = QtCore.QRectF(delta, delta, innerRadius, innerRadius)
        return innerRect, innerRadius

    def drawText(self, p, innerRect, innerRadius, value):
        text = "  %i  " % self.remaining

        # !!! to revise
        f = self.font()
        # f.setPixelSize(innerRadius * max(0.05, (0.35 - self.decimals * 0.08)))
        f.setPixelSize(innerRadius * 1.8 / len(text))
        p.setFont(f)

        textRect = innerRect
        p.setPen(self.palette().text().color())
        p.drawText(textRect, Qt.Qt.AlignCenter, text)

    def rebuildDataBrushIfNeeded(self):
        if self.rebuildBrush:
            self.rebuildBrush = False

            dataBrush = QtGui.QConicalGradient()
            dataBrush.setCenter(0.5,0.5)
            dataBrush.setCoordinateMode(QtGui.QGradient.StretchToDeviceMode)

            # for pos, color in self.gradientData:
            dataBrush.setColorAt(1.0, self.gradientData[0])
            dataBrush.setColorAt(1.0 - self.proportion / 100.0, self.gradientData[1])

            # angle
            dataBrush.setAngle(self.nullPosition)

            p = self.palette()
            p.setBrush(QtGui.QPalette.Highlight, dataBrush)
            self.setPalette(p)

class Buttons(QtWidgets.QWidget):

    def __init__(self):
        super(Buttons, self).__init__()

        #self.button = QtWidgets.QPushButton("10sec", self)
        self.button3 = QtWidgets.QPushButton("3", self)
        self.button5 = QtWidgets.QPushButton("5", self)
        self.button6 = QtWidgets.QPushButton("6", self)
        self.button7 = QtWidgets.QPushButton("7", self)
        self.button8 = QtWidgets.QPushButton("8", self)
        self.button9 = QtWidgets.QPushButton("9", self)
        self.button10 = QtWidgets.QPushButton("10", self)
        self.button15 = QtWidgets.QPushButton("15", self)
        self.button20 = QtWidgets.QPushButton("20", self)
        self.button25 = QtWidgets.QPushButton("25", self)
        self.button30 = QtWidgets.QPushButton("30", self)
        self.button45 = QtWidgets.QPushButton("45", self)
        self.button90 = QtWidgets.QPushButton("90", self)

        self.button3.clicked.connect(self.hide)

        # self.connect(self.button3, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button5, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button6, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button7, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button8, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button9, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button10, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button15, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button20, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button25, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button30, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button45, QtCore.SIGNAL("clicked()"), self.hide)
        # self.connect(self.button90, QtCore.SIGNAL("clicked()"), self.hide)

        box = QtWidgets.QHBoxLayout()
        box.addWidget(self.button3)
        box.addWidget(self.button5)
        box.addWidget(self.button6)
        box.addWidget(self.button7)
        box.addWidget(self.button8)
        box.addWidget(self.button9)
        box.addWidget(self.button10)
        box.addWidget(self.button15)
        box.addWidget(self.button20)
        box.addWidget(self.button25)
        box.addWidget(self.button30)
        box.addWidget(self.button45)
        box.addWidget(self.button90)

        self.setLayout(box)

    def test(self):
        print "hey"


class TstWidget(QtWidgets.QWidget):
    def __init__(self):
        super(type(self), self).__init__()

        self.bar = Timer()
        size = min(self.height(), self.width()) * 0.8
        self.bar.setMinimumSize(size, size)
        self.bar.hide()

        self.buttons = Buttons()
        self.buttons.button3.clicked.connect(lambda: self.bar.run_timer(3))
        # self.connect(self.buttons.button3, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(3))
        # self.connect(self.buttons.button5, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(5))
        # self.connect(self.buttons.button6, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(6))
        # self.connect(self.buttons.button7, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(7))
        # self.connect(self.buttons.button8, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(8))
        # self.connect(self.buttons.button9, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(9))
        # self.connect(self.buttons.button10, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(10))
        # self.connect(self.buttons.button15, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(15))
        # self.connect(self.buttons.button20, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(20))
        # self.connect(self.buttons.button25, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(25))
        # self.connect(self.buttons.button30, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(30))
        # self.connect(self.buttons.button45, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(45))
        # self.connect(self.buttons.button90, QtCore.SIGNAL("clicked()"), lambda: self.bar.run_timer(90))


        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.bar)
        hbox.addStretch(1)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addWidget(self.buttons)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def resizeEvent(self, QResizeEvent):
        size = min(self.height(), self.width()) * 0.8
        try:
            self.bar.setMinimumSize(size, size)
        except:
            pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = TstWidget()
    main_window.resize(500, 500)
    main_window.move(300, 300)
    main_window.setWindowTitle('Timer')
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()