import math
import sys

from PyQt5.QtCore import *  # QPoint
from PyQt5.QtGui import *  # QPainter
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5 import QtCore, QtWidgets


class Canvas(QtWidgets.QWidget):

    def __init__(self):
        super(Canvas, self).__init__()


# https://techoverflow.net/2017/02/23/computing-bounding-box-for-a-list-of-coordinates-in-python/
class BoundingBox(object):
    """
    A 2D bounding box
    """
    def __init__(self, points):
        if len(points) == 0:
            raise ValueError("Can't compute bounding box of empty list")
        self.minx, self.miny = float("inf"), float("inf")
        self.maxx, self.maxy = float("-inf"), float("-inf")
        for x, y in points:
            # Set min coords
            if x < self.minx:
                self.minx = x
            if y < self.miny:
                self.miny = y
            # Set max coords
            if x > self.maxx:
                self.maxx = x
            if y > self.maxy:
                self.maxy = y

    @property
    def width(self):
        return self.maxx - self.minx

    @property
    def height(self):
        return self.maxy - self.miny

    def __repr__(self):
        return "BoundingBox({}, {}, {}, {})".format(
            self.minx, self.maxx, self.miny, self.maxy)


class Recognizer(QtGui.QMainWindow):

    # press mouse button and start drawing, when mouse button released start training/recognizing
    # problem with mouse press and release - click on button also in the mix
    # instead: drawing with mouse through press and release and then button to add gesture.

    SIZE = 600  # not sure size yet; size of available space?
    N = 64  # as recommended in paper

    def __init__(self):
        super(Recognizer, self).__init__()
        self.current_points = []
        self.gestures = []  # ['1', 'triangle', 'rectangle']
        self.templates = {}
        self.drawing = False
        self.last_point = []  # QPoint()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Gesture Recognizer')
        self.setMinimumSize(1200, 700)
        central = QtGui.QWidget()
        self.setCentralWidget(central)
        self.main_layout = QtGui.QHBoxLayout()
        central.setLayout(self.main_layout)
        # init different layouts
        self.menu_layout = QtGui.QVBoxLayout()
        self.mode_layout = QtGui.QGridLayout()
        self.list_layout = QtGui.QGridLayout()
        self.canvas = QtGui.QVBoxLayout()
        # inits menu layout - train mode
        self.train_button = QtGui.QPushButton('Training')
        self.train_button.clicked.connect(self.show_training)
        self.train_button.setDefault(True)
        self.mode_layout.addWidget(self.train_button, 0, 0, 1, 2)
        self.instructions = QtGui.QLabel()
        self.instructions.setText('Press the left mouse button and draw a number or shape on '
                                  'the right side of the window.\nIf you press the "Add gesture" button the system '
                                  'adds the gesture and starts training\nYou can train the system with several shapes.')
        self.mode_layout.addWidget(self.instructions, 1, 0, 1, 4)
        self.gesture_name = QtGui.QLineEdit()
        self.mode_layout.addWidget(self.gesture_name, 6, 0, 1, 2)
        self.add_button = QtGui.QPushButton('Add')
        self.add_button.clicked.connect(self.add_gesture)
        self.mode_layout.addWidget(self.add_button, 6, 3)
        # inits menu layout - recognizer mode
        self.recognize_button = QtGui.QPushButton('Recognize')
        self.recognize_button.clicked.connect(self.show_recognition)
        self.mode_layout.addWidget(self.recognize_button, 0, 2, 1, 2)
        self.start_recognize_button = QtGui.QPushButton('Start recognizing')
        self.start_recognize_button.clicked.connect(self.start_recognizing)
        self.start_recognize_button.setVisible(False)
        self.mode_layout.addWidget(self.start_recognize_button, 6, 0)
        self.recognize_text = QtGui.QLabel()
        self.recognize_text.setVisible(False)
        self.mode_layout.addWidget(self.recognize_text, 7, 0)
        # init list layout
        self.init_list()
        # add diff layouts to right side
        self.menu_layout.addLayout(self.mode_layout)
        self.menu_layout.addLayout(self.list_layout)
        # init canvas
        self.header = QtGui.QLabel('Draw here:')
        self.header.setAlignment(QtCore.Qt.AlignTop)
        self.canvas.addWidget(self.header)
        self.image = QImage(1200, 700, QImage.Format_RGB32)
        self.image.fill(Qt.white)
        # image_label = QtGui.QLabel(" ")
        # image_label.setPixmap(QtGui.QPixmap.fromImage(self.image))  # https://stackoverflow.com/questions/12005394/initialise-a-blank-qimage-with-pyside
        # self.canvas.addWidget(image_label)
        # add layouts to main window
        self.main_layout.addLayout(self.menu_layout)
        self.main_layout.addLayout(self.canvas)

    def init_list(self):
        header = QtGui.QLabel('Gestures:')
        self.list_layout.addWidget(header, 0, 0)
        if len(self.gestures) != 0:
            for i in range(len(self.gestures)):
                self.list_layout.setRowMinimumHeight(i + 1, 50)
                gesture = QtGui.QLabel(self.gestures[i])
                self.list_layout.addWidget(gesture, i + 1, 0)
                delete_button = QtGui.QPushButton('Delete')
                delete_button.clicked.connect(lambda state, x=i: self.delete_gesture(self.gestures[x]))
                self.list_layout.addWidget(delete_button, i + 1, 1)
                retrain_button = QtGui.QPushButton('Retrain')
                retrain_button.clicked.connect(lambda state, x=i: self.retrain_gesture(self.gestures[x]))
                self.list_layout.addWidget(retrain_button, i + 1, 2)
                # optional: add button?
        else:
            blank = QtGui.QLabel('No gestures recorded')
            self.list_layout.addWidget(blank, 1, 1)

    def show_training(self):
        self.gesture_name.setVisible(True)
        self.add_button.setVisible(True)
        self.start_recognize_button.setVisible(False)
        self.recognize_text.setVisible(False)
        self.train_button.setDefault(True)
        self.recognize_button.setDefault(False)
        self.instructions.setText('Press the left mouse button and draw a number or shape on '
                                  'the right side of the window.\nIf you press the "Add gesture" button the system '
                                  'adds the gesture and starts training\nYou can train the system with several shapes.')

    def show_recognition(self):
        self.gesture_name.setVisible(False)
        self.add_button.setVisible(False)
        self.start_recognize_button.setVisible(True)
        self.recognize_text.setVisible(True)
        self.recognize_button.setDefault(True)
        self.train_button.setDefault(False)
        self.instructions.setText('Press the left mouse button and draw a number or shape on '
                                  'the right side of the window.\nIf you press "start recognizing" the programm starts '
                                  'the recognition.')

    def start_recognizing(self):
        print('start recognizing')
        if not self.current_points:
            return
        interim_points = self.resample(self.current_points, self.N)
        print('resam', len(interim_points))
        interim_points = self.rotate_to_zero(interim_points)
        print('zero', len(interim_points))
        interim_points = self.scale_to_square(interim_points, self.SIZE)
        print('square', len(interim_points))
        interim_points = self.translate_to_origin(interim_points)
        print('len', len(interim_points))
        prediction = self.recognize(interim_points, self.templates)
        self.recognize_text.setText(prediction[0])

    def add_gesture(self):
        print('add gesture: ', self.gesture_name.text())
        gesture_name = str(self.gesture_name.text())
        # add to ui
        if gesture_name == '':
            return
        if gesture_name not in self.gestures:
            self.gestures.append(gesture_name)
            self.init_list()
        # start training
        if not self.current_points:
            return
        # print(self.current_points)
        resampled_points = self.resample(self.current_points, self.N)
        print('interim', len(resampled_points))
        zero_points = self.rotate_to_zero(resampled_points)
        print('zero', len(zero_points))
        square_points = self.scale_to_square(zero_points, self.SIZE)
        interim_points = self.translate_to_origin(square_points)
        print('points', len(interim_points))
        # add to templates
        if gesture_name in self.templates:
            self.templates[gesture_name].append(interim_points)
        else:
            self.templates[gesture_name] = [interim_points]
        # delete picture
        self.current_points.clear()
        print('here')
        self.image.fill(Qt.white)
        self.update()

    def delete_gesture(self, gesture):
        print('delete gesture: ', gesture)
        # remove gesture from ui
        self.gestures.remove(gesture)
        # https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
        for i in reversed(range(self.list_layout.count())):
            self.list_layout.itemAt(i).widget().setParent(None)
        self.init_list()

    def retrain_gesture(self, gesture):
        print('retrain gesture: ', gesture)
        self.gesture_name.setText(gesture)
        self.instructions.setText('Press the left mouse button and draw a number or shape on '
                                  'the right side of the window.\nIf you press the "Add gesture" button the system '
                                  'adds the gesture and starts training\nYou can train the system with several shapes.')
        # remove already existing data
        if gesture in self.templates:
            self.templates.pop(gesture, None)

    # https://www.geeksforgeeks.org/pyqt5-create-paint-application/
    # method for checking mouse clicks
    def mousePressEvent(self, event):
        # if left mouse button is pressed
        if event.button() == Qt.LeftButton:
            # make drawing flag true
            self.drawing = True
            # make last point to the point of cursor
            self.last_point = event.pos()
            # self.current_points.append([self.last_point.x(), self.last_point.y()])

        # method for tracking mouse activity
    def mouseMoveEvent(self, event):
        # checking if left button is pressed and drawing flag is true
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            # creating painter object
            painter = QPainter(self.image)
            # set the pen of the painter
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            # draw line from the last point of cursor to the current point
            # this will draw only one step
            painter.drawLine(self.last_point, event.pos())
            # change the last point
            self.last_point = event.pos()
            self.current_points.append([self.last_point.x(), self.last_point.y()])
            # update
            self.update()

        # method for mouse left button release
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # make drawing flag false
            self.drawing = False
        # print(self.current_points)

        # paint event
    def paintEvent(self, event):
        # create a canvas
        canvasPainter = QPainter(self)
        # draw rectangle  on the canvas
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

    def resample(self, points, n):
        increment = self.path_length(points) / (n - 1)
        d = 0
        new_points = []
        for p in range(1, len(points)):
            dist = math.dist(points[p-1], points[p])
            if (d + dist) >= increment:
                q_x = points[p-1][0] + ((increment - d) / dist) * (points[p][0] - points[p-1][0])
                q_y = points[p-1][1] + ((increment - d) / dist) * (points[p][1] - points[p-1][1])
                new_points.append([q_x, q_y])
                # print(new_points)
                points.insert(p, [q_x, q_y])
                d = 0
                # print('points', points)
            else:
                d = d + dist
        return new_points

    def path_length(self, points):
        d = 0
        for i in range(len(points)):
            d = d + math.dist(points[i-1], points[i])
        return d

    # https: // stackoverflow.com / questions / 4355894 / how - to - get - center - of - set - of - points - using - python / 4355934
    def centroid(self, points):
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        centroid = (sum(x) / len(points), sum(y) / len(points))
        return centroid

    def rotate_to_zero(self, points):
        c = self.centroid(points)  #centroid = positions.mean(axis=0) (np.array)
        theta = math.atan2(c[1] - points[0][1], c[0] - points[0][0])
        new_points = self.rotate_by(points, - theta)
        return new_points

    def rotate_by(self, points, theta):
        new_points = []
        c = self.centroid(points)
        for p in points:
            q_x = (p[0] - c[0]) * math.cos(theta) - (p[1] - c[1]) * math.sin(theta) + c[0]
            q_y = (p[0] - c[0]) * math.sin(theta) - (p[1] - c[1]) * math.cos(theta) + c[1]
            new_points.append([q_x, q_y])
        return new_points

    def scale_to_square(self, points, size):
        new_points = []
        # ('poi', points)
        box = BoundingBox(points)
        print('box', box)
        for p in points:
            q_x = p[0] * (size / box.width)
            q_y = p[1] * (size / box.height)
            new_points.append([q_x, q_y])
        return new_points

    def translate_to_origin(self, points):
        new_points = []
        c = self.centroid(points)
        for p in points:
            q_x = p[0] - c[0]
            q_y = p[1] - c[1]
            new_points.append([q_x, q_y])
        return new_points

    def recognize(self, points, templates):
        b = math.inf  # np.inf, float(inf)
        theta = 45  # degrees
        theta_avg = 2  # degrees
        print('templates', templates)
        for T in templates:
            print('T', T)
            print('temp', templates[T])
            d = self.distance_at_best_angle(points, templates[T][0], - theta, theta, theta_avg)
            if d < b:
                b = d
                new_T = T
        score = 1 - b / 0.5 * math.sqrt(self.SIZE ** 2 + self.SIZE ** 2)  # size of scale_to_square
        return new_T, score

    def distance_at_best_angle(self, points, template_points, theta_a, theta_b, theta_alpha):
        print('tem_1', len(template_points))
        phi = 0.5 * (-1 + math.sqrt(5))
        x_1 = phi * theta_a + (1 - phi) * theta_b
        f_1 = self.distance_at_angle(points, template_points, x_1)
        x_2 = (1 - phi) * theta_a + phi * theta_b
        f_2 = self.distance_at_angle(points, template_points, x_2)
        while theta_b - theta_a > theta_alpha:
            if f_1 < f_2:
                theta_b = x_2
                x_2 = x_1
                f_2 = f_1
                x_1 = phi * theta_a + (1- phi) * theta_b
                f_1 = self.distance_at_angle(points, template_points, x_1)
            else:
                theta_a = x_1
                x_1 = x_2
                f_1 = f_2
                x_2 = (1 - phi) * theta_a + phi * theta_b
                f_2 = self.distance_at_angle(points, template_points, x_2)
        return min(f_1, f_2)

    def distance_at_angle(self, points, template_points, theta):
        print('tem_2', len(template_points))
        print(len(points))
        new_points = self.rotate_by(points, theta)
        d = self.path_distance(new_points, template_points)
        return d

    def path_distance(self, rec_points, template_points):
        d = 0
        print('A', len(rec_points))
        print('B', len(template_points))
        for i in range(len(rec_points)):
            d = d + math.dist(rec_points[i], template_points[i])
        return d / len(rec_points)


def main():
    app = QtGui.QApplication([])
    recognizer = Recognizer()

    recognizer.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())


if __name__ == '__main__':
    main()
