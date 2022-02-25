import random
import sys
import os
import typing
import numpy as np
import shutil
from joblib import Parallel, delayed, parallel_backend
from scipy import signal
import time
import math


import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtTest as qtt
from qtwidgets import Toggle


# pool = mp.Pool()

AgeColor = {
    0: "White",
    1: "#2b9348",
    2: "#55a630",
    3: "#80b918",
    4: "#bfd200",
    5: "#ffff3f",
    6: "#ffda3d",
    7: "#fdc43f",
    8: "#ff8c00",
    9: "#ff8000",
    10: "#dc2f02",
    11: "#d00000",
    12: "#9d0208",
}


def toList(data):
    List = np.zeros([len(data), len(data[0])])
    for i in range(len(data)):
        listTemp = list(data[i])
        if i != len(data)-1:
            listTemp = listTemp[:-1]
        for j in range(len(listTemp)):
            List[i][j] = 0 if listTemp[j] == '.' else 1
    return List


class SimpleColor(qtw.QWidget):
    def __init__(self, a, d):
        super(SimpleColor, self).__init__()

        self.setAutoFillBackground(True)
        self.status = "DEAD"
        self.age = a
        self.setFixedHeight(int(100 / d))
        self.setFixedWidth(int(100 / d))

    def updateStatus(self):
        self.status = "ALIVE" if self.age > 0 else "DEAD"

    def updateColor(self):
        palette = self.palette()
        palette.setColor(qtg.QPalette.Window, qtg.QColor("Black" if self.status == "ALIVE" else "DarkGrey"))
        self.setPalette(palette)

    def getAge(self):
        return self.age


class Color(qtw.QGraphicsWidget):

    def __init__(self, a, button, color):
        super(Color, self).__init__()

        self.setAutoFillBackground(True)
        self.controlButton = button
        self.color = color
        self.setGeometry(0, 0, 10, 10)
        self.status = "DEAD"
        self.age = a

    def grow(self):
        self.age += 1
        # self.setStatus("ALIVE")

    def grow_or_die(self, n):
        if not n:
            self.age = 0
        else:
            self.age += 0 if (n == 2 and not self.age) else 1

    def die(self):
        self.age = 0
        # self.setStatus("DEAD")

    def setAge(self, a):
        self.age = a

    def getAge(self):
        return self.age

    def mousePressEvent(self, e):
        if e.button() == qtc.Qt.LeftButton:
            if not self.controlButton.isChecked():
                self.setAge(1 if self.getAge() == 0 else 0)
                self.updateStatus()
                self.updateColor()

    def updateStatus(self):
        self.status = "ALIVE" if self.age > 0 else "DEAD"

    def updateColor(self):
        palette = self.palette()
        palette.setColor(qtg.QPalette.Window, qtg.QColor(
            (AgeColor[self.age if self.age < 12 else 12] if self.color.isChecked() else "Black")
            if self.age else AgeColor[0]))
        self.setPalette(palette)

    def getStatus(self):
        return self.status

    def setStatus(self, s):
        self.status = s


class GameView(qtw.QGraphicsView):

    def __init__(self, parent: typing.Optional[qtw.QWidget] = ...):
        super().__init__(parent)
        self._panStartY = 0
        self._panStartX = 0
        self.rightMousePressed = False

    def mousePressEvent(self, e):
        print("mousePressEvent RIGHT")
        self._panStartY = e.y()
        self._panStartX = e.x()
        self.rightMousePressed = True
        print([self._panStartX, self._panStartY])

    def mouseMoveEvent(self, e):
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (e.x() - self._panStartX))
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (e.y() - self._panStartY))
        self._panStartX = e.x()
        self._panStartY = e.y()


class MapWindow(qtw.QMainWindow):
    def __init__(self, mainWindow):
        super().__init__()

        self.scroll = qtw.QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = qtw.QWidget()  # Widget that contains the collection of Vertical Box
        self.vbox = qtw.QVBoxLayout()  # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.hboxes = []
        self.main = mainWindow

        self.DIR = './Maps'
        # mapsNum = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

        k = 0
        for name in os.listdir(self.DIR):
            if os.path.isfile(os.path.join(self.DIR, name)):
                self.addMap(name, k)
                k = k + 1

        self.widget.setLayout(self.vbox)

        # Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setWindowTitle('Maps')

    def useMap(self):
        self.main.empty()
        index = int(self.sender().objectName())
        f = self.hboxes[index].itemAt(1).layout()

        r_start = int(self.main.gridDim / 2 - f.rowCount() / 2)
        c_start = int(self.main.gridDimY / 2 - f.columnCount() / 2)
        for i in range(f.rowCount()):
            for j in range(f.columnCount()):
                self.main.layout4.itemAt(i + r_start, j + c_start).graphicsItem().setAge(
                    1 if f.itemAtPosition(i, j).widget().getAge() else 0)
                self.main.layout4.itemAt(i + r_start, j + c_start).graphicsItem().updateStatus()
                self.main.layout4.itemAt(i + r_start, j + c_start).graphicsItem().updateColor()

        self.close()

    def addMap(self, name, k):
        self.hboxes.append(qtw.QHBoxLayout())
        labelButton = qtw.QPushButton(str(name[:-4]))
        labelButton.setFixedWidth(200)
        labelButton.setObjectName(str(k))
        labelButton.clicked.connect(self.useMap)
        self.hboxes[k].addWidget(labelButton)
        grid = qtw.QGridLayout()

        self.vbox.addLayout(self.hboxes[k])

        with open(os.path.join(self.DIR, name)) as f:
            # d = json.load(f)
            d = f.readlines()
            data = np.array(toList(d))

            for i in range(data.shape[0]):
                for j in range(data.shape[1]-1):
                    grid.addWidget(SimpleColor(1 if data[i][j] else 0, data.shape[0]), i, j)
                    grid.itemAtPosition(i, j).widget().updateStatus()
                    grid.itemAtPosition(i, j).widget().updateColor()

        grid.setAlignment(qtc.Qt.AlignCenter)
        grid.setSpacing(2)
        self.hboxes[k].addLayout(grid)


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.births = 0
        self.deaths = 0
        self.wDim = 800
        self.cDim = 20
        self.dialFactor = 1
        self.frame_rate = 1
        self.bg_color = "DarkGrey"
        self.mapWindow = MapWindow(self)
        self.generation = 0

        self.setFixedSize(qtc.QSize(self.wDim - 3, self.wDim + 50))
        self.gridDim = 50
        self.gridDimY = 64
        self.layout = qtw.QVBoxLayout()
        self.layout2 = qtw.QHBoxLayout()
        self.layout3 = qtw.QGridLayout()
        self.layout4 = qtw.QGraphicsGridLayout()
        self.buttonLayout = qtw.QVBoxLayout()
        self.zoomLayout = qtw.QVBoxLayout()
        self.frameRateLayout = qtw.QVBoxLayout()
        self.optionsLayout = qtw.QVBoxLayout()
        self.infoLayout = qtw.QHBoxLayout()
        self.mapLayout = qtw.QHBoxLayout()

        self.button_is_checked = True
        self.setWindowTitle("Game of life")

        self.infoBLabel = qtw.QLabel()
        self.infoBLabel.setVisible(False)
        self.infoBLabel.setFixedHeight(10)

        self.infoDLabel = qtw.QLabel()
        self.infoDLabel.setVisible(False)
        self.infoDLabel.setFixedHeight(10)

        self.infoGLabel = qtw.QLabel()
        self.infoGLabel.setVisible(False)

        self.mode = qtw.QPushButton()
        self.mode.setFixedWidth(120)
        self.mode.setFixedHeight(30)
        self.modeMenu = qtw.QMenu()
        self.modeMenu.addAction("Normal", self.setMode)
        self.modeMenu.addAction("HighLife", self.setMode)
        self.modeMenu.addAction("Day-Night", self.setMode)
        self.modeMenu.addAction("Bosco", self.setMode)
        self.mode.setText("Normal")
        self.mode.setMenu(self.modeMenu)

        self.infoLayout.addWidget(self.infoBLabel)
        self.infoLayout.addWidget(self.infoDLabel)
        self.infoLayout.addWidget(self.infoGLabel)
        self.infoLayout.addWidget(self.mode)

        self.button = qtw.QPushButton("Start!")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.start)

        self.refreshButton = qtw.QPushButton("Refresh")
        self.refreshButton.clicked.connect(self.refresh)

        self.loadButton = qtw.QPushButton(qtg.QIcon("load-icon.png"), "")
        self.loadButton.setFixedWidth(40)
        self.loadButton.clicked.connect(self.loadMap)
        # self.loadButton.setFixedHeight(40)

        self.searchButton = qtw.QPushButton(qtg.QIcon("lent.png"), "")
        self.searchButton.setFixedWidth(40)
        self.searchButton.clicked.connect(self.searchMap)

        self.mapLayout.addWidget(self.refreshButton)
        self.mapLayout.addWidget(self.loadButton)
        self.mapLayout.addWidget(self.searchButton)
        self.mapLayout.setAlignment(qtc.Qt.AlignCenter)
        self.mapLayout.setSpacing(10)

        self.emptyButton = qtw.QPushButton("Empty")
        self.emptyButton.clicked.connect(self.empty)

        self.dial = qtw.QDial()
        self.dial.setFixedHeight(int(self.wDim / 4) - 50)
        self.dial.valueChanged.connect(self.zoom)

        self.dialLabel = qtw.QLabel("ZOOM")
        self.dialLabel.setFixedHeight(20)
        self.dialLabel.setAlignment(qtc.Qt.AlignCenter)

        self.zoomLayout.addWidget(self.dial)
        self.zoomLayout.addWidget(self.dialLabel)
        self.zoomLayout.setAlignment(qtc.Qt.AlignVCenter)

        self.slider = qtw.QSlider()
        self.slider.setFixedHeight(int(self.wDim / 4) - 100)
        self.slider.setFixedWidth(50)
        self.slider.valueChanged.connect(self.speed)

        self.frLabel = qtw.QLabel("FR")
        self.frLabel.setFixedWidth(50)
        self.frLabel.setFixedHeight(20)
        self.frLabel.setAlignment(qtc.Qt.AlignCenter)

        self.frTopLabel = qtw.QLabel("1 fps")
        self.frTopLabel.setFixedWidth(50)
        self.frTopLabel.setFixedHeight(20)
        self.frTopLabel.setAlignment(qtc.Qt.AlignCenter)

        self.frameRateLayout.addWidget(self.frTopLabel)
        self.frameRateLayout.addWidget(self.slider)
        self.frameRateLayout.addWidget(self.frLabel)

        self.version = Toggle()
        self.version.setFixedWidth(70)
        self.version.setFixedHeight(30)
        self.version.clicked.connect(self.changeVersion)
        self.vLabel = qtw.QLabel("LIGHT")
        self.vLabel.setFixedWidth(70)
        self.vLayout = qtw.QHBoxLayout()
        self.vLayout.addWidget(self.version)
        self.vLayout.addWidget(self.vLabel)

        self.layout.setSpacing(7)

        self.option1 = qtw.QCheckBox("Oldness")
        self.option2 = qtw.QCheckBox("PacMan Effect")
        self.option3 = qtw.QCheckBox("Info")
        self.optionC = qtw.QCheckBox("Colors")
        self.optionsLayout.addWidget(self.optionC)
        self.optionsLayout.addWidget(self.option1)
        self.optionsLayout.addWidget(self.option2)
        self.optionsLayout.addWidget(self.option3)
        self.optionsLayout.addLayout(self.vLayout)
        self.optionsLayout.setAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)
        self.optionsLayout.setSpacing(20)

        self.option3.clicked.connect(self.showInfo)
        self.optionC.clicked.connect(self.updateColors)

        self.scene = qtw.QGraphicsScene()

        for i in range(self.gridDim):
            for j in range(self.gridDimY):
                self.layout4.addItem(Color(1 if random.randint(0, 100) < 20 else 0, self.button, self.optionC), i, j)
                self.layout4.itemAt(i, j).graphicsItem().updateStatus()
                self.layout4.itemAt(i, j).graphicsItem().updateColor()

        self.gameLifeTab = qtw.QGraphicsWidget()
        self.gameLifeTab.setLayout(self.layout4)
        self.scene.addItem(self.gameLifeTab)
        # self.scene.setSceneRect(750, 500, 500, 500)

        self.graphicsView = GameView(self.scene)
        self.graphicsView.setAlignment(qtc.Qt.AlignTop | qtc.Qt.AlignLeft)
        self.graphicsView.setBackgroundBrush(qtg.QColor(self.bg_color))
        self.graphicsView.setObjectName("graphicsView")

        self.graphicsView.scale(0.2, 0.2)

        self.buttonLayout.addWidget(self.button)
        self.buttonLayout.addLayout(self.mapLayout)
        self.buttonLayout.addWidget(self.emptyButton)
        self.buttonLayout.setAlignment(qtc.Qt.AlignVCenter | qtc.Qt.AlignRight)
        self.buttonLayout.setSpacing(30)

        self.layout2.addLayout(self.buttonLayout)
        self.layout2.addLayout(self.zoomLayout)
        self.layout2.addLayout(self.frameRateLayout)
        self.layout2.addLayout(self.optionsLayout)

        self.layout.addLayout(self.infoLayout)
        self.layout.addWidget(self.graphicsView)
        self.layout.addLayout(self.layout2)

        container = qtw.QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

    def setMode(self):
        self.mode.setText(self.sender().text())

    def updateColors(self):
        for i in range(self.gridDim):
            for j in range(self.gridDimY):
                self.layout4.itemAt(i, j).graphicsItem().updateColor()

    def changeVersion(self):
        self.bg_color = "White" if self.version.isChecked() else "DarkGrey"
        self.graphicsView.setBackgroundBrush(qtg.QColor(self.bg_color))
        AgeColor[0] = "DarkGrey" if self.version.isChecked() else "White"
        self.updateColors()
        self.vLabel.setText("DARK" if self.version.isChecked() else "LIGHT")

    def searchMap(self):
        self.mapWindow.show()

    def loadMap(self):

        fileName, _ = qtw.QFileDialog.getOpenFileName(self, 'Single File', qtc.QDir.rootPath(), '*.txt')
        try:
            try:
                shutil.copy2(fileName, "Maps/")
            except shutil.SameFileError:
                pass
            with open(fileName) as f:
                # d = json.load(f)
                d = f.readlines()
                data = np.array(toList(d))
                print(data)
        except FileNotFoundError:
            return

        self.empty()

        r_start = int(self.gridDim / 2 - data.shape[0] / 2)
        c_start = int(self.gridDimY / 2 - data.shape[1] / 2)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                self.layout4.itemAt(i + r_start, j + c_start).graphicsItem().setAge(1 if data[i][j] else 0)
                self.layout4.itemAt(i + r_start, j + c_start).graphicsItem().updateStatus()
                self.layout4.itemAt(i + r_start, j + c_start).graphicsItem().updateColor()

        mapsNum = len(
            [name for name in os.listdir(self.mapWindow.DIR) if os.path.isfile(os.path.join(self.mapWindow.DIR, name))])
        self.mapWindow.addMap(fileName, mapsNum - 1)

    def showInfo(self):
        if self.option3.isChecked():
            self.infoBLabel.setText("Births: " + str(self.births))
            self.infoBLabel.setVisible(True)
            self.infoDLabel.setText("Deaths: " + str(self.deaths))
            self.infoDLabel.setVisible(True)
            self.infoGLabel.setText("Generations: " + str(self.generation))
            self.infoGLabel.setVisible(True)
            # self.dial.setFixedHeight(self.dial.height() - 18)
            # self.slider.setFixedHeight(self.slider.height() - 18)
        else:
            self.infoBLabel.setVisible(False)
            self.infoDLabel.setVisible(False)
            self.infoGLabel.setVisible(False)
            # self.dial.setFixedHeight(self.dial.height() + 18)
            # self.slider.setFixedHeight(self.slider.height() + 18)

    def refresh(self):
        if not self.button.isChecked():
            for i in range(self.gridDim):
                for j in range(self.gridDimY):
                    self.layout4.itemAt(i, j).graphicsItem().setAge(
                        1 if random.randint(0, 100) < 30 else 0)
                    self.layout4.itemAt(i, j).graphicsItem().updateStatus()
                    self.layout4.itemAt(i, j).graphicsItem().updateColor()

            self.births = 0
            self.deaths = 0
            self.generation = 0
            self.infoBLabel.setText("Births: " + str(self.births))
            self.infoDLabel.setText("Deaths: " + str(self.deaths))
            self.infoGLabel.setText("Generations: " + str(self.generation))

    def playGame(self):

        matrix = [[1 if self.layout4.itemAt(i, j).graphicsItem().getAge() > 0 else 0 for j in range(self.gridDimY)] for i in
                  range(self.gridDim)]

        if self.mode.text() != "Bosco":
            if not self.option2.isChecked():
                s = signal.convolve2d(matrix, [[1, 1, 1], [1, 0, 1], [1, 1, 1]], mode='same', boundary='fill', fillvalue=0)
            else:
                s = signal.convolve2d(matrix, [[1, 1, 1], [1, 0, 1], [1, 1, 1]], mode='same', boundary='wrap')

            if self.mode.text() == "Normal":
                s[s > 3] = 0
                r = s+matrix
                r[r < 3] = 0

            elif self.mode.text() == "HighLife":
                s[s > 6] = 0
                s[s == 4] = 0
                s[s == 5] = 0
                r = s + matrix
                r[r < 3] = 0
                r[r > 6] = 0

            elif self.mode.text() == "Day-Night":
                s[s == 5] = 0
                s[s == 3] = 7
                r = s + matrix
                r[r < 5] = 0

            for i in range(self.gridDim):
                for j in range(self.gridDimY):
                    if r[i][j]:
                        if not matrix[i][j]:
                            self.births += 1
                        self.layout4.itemAt(i, j).graphicsItem().grow()
                        self.layout4.itemAt(i, j).graphicsItem().updateColor()
                    else:
                        if matrix[i][j]:
                            self.deaths += 1
                            self.layout4.itemAt(i, j).graphicsItem().die()
                            self.layout4.itemAt(i, j).graphicsItem().updateColor()

        else:
            convM = np.ones((11, 11))
            convM[6][6] = 0
            if not self.option2.isChecked():
                s = signal.convolve2d(matrix, convM, mode='same', boundary='fill', fillvalue=0)
            else:
                s = signal.convolve2d(matrix, convM, mode='same', boundary='wrap')

            s[s < 33] = 0
            s[s > 57] = 0
            r = s+matrix

            for i in range(self.gridDim):
                for j in range(self.gridDimY):
                    if r[i][j] in range(34, 47):
                        if not matrix[i][j]:
                            self.births += 1
                        self.layout4.itemAt(i, j).graphicsItem().grow()
                        self.layout4.itemAt(i, j).graphicsItem().updateColor()
                    elif r[i][j] in range(47, 59):
                        if matrix[i][j]:
                            self.layout4.itemAt(i, j).graphicsItem().grow()
                            self.layout4.itemAt(i, j).graphicsItem().updateColor()
                    else:
                        if matrix[i][j]:
                            self.deaths += 1
                            self.layout4.itemAt(i, j).graphicsItem().die()
                            self.layout4.itemAt(i, j).graphicsItem().updateColor()

    def empty(self):
        if not self.button.isChecked():
            for i in range(self.gridDim):
                for j in range(self.gridDimY):
                    self.layout4.itemAt(i, j).graphicsItem().setAge(0)
                    self.layout4.itemAt(i, j).graphicsItem().updateStatus()
                    self.layout4.itemAt(i, j).graphicsItem().updateColor()

            self.births = 0
            self.deaths = 0
            self.generation = 0
            self.infoBLabel.setText("Births: " + str(self.births))
            self.infoDLabel.setText("Deaths: " + str(self.deaths))
            self.infoGLabel.setText("Generations: " + str(self.generation))

    def start(self, checked):
        self.button.setText("Pause!" if checked else "Start!")
        while self.button.isChecked():
            self.generation += 1
            start = time.time()
            self.playGame()
            self.infoBLabel.setText("Births: " + str(self.births))
            self.infoDLabel.setText("Deaths: " + str(self.deaths))
            self.infoGLabel.setText("Generations: " + str(self.generation))
            end = time.time()
            qtt.QTest.qWait(int(1000 / self.frame_rate)-math.ceil((end - start)*1000))
            end = time.time()
            print(end-start)

    def zoom(self):
        self.graphicsView.resetTransform()
        self.graphicsView.scale(0.2 + (self.dial.value()) * 0.04,
                                0.2 + (self.dial.value()) * 0.04)

    def speed(self):
        print(self.slider.value())
        if self.slider.value() < 99:
            self.frame_rate = divmod(self.slider.value(), 1)[0] if divmod(self.slider.value(), 1)[0] != 0 else 1
            self.frTopLabel.setText(str(self.frame_rate) + " fps")
        else:
            self.frame_rate = 100
            self.frTopLabel.setText("100" + " fps")


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
