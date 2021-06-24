import math
import sys
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
            elif y > self.maxy:
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

    SIZE = 50  # not sure size yet

    def __init__(self):
        super(Recognizer, self).__init__()
        self.setWindowTitle('Gesture Recognizer')
        self.setMinimumSize(1200, 700)
        central = QtGui.QWidget()
        self.setCentralWidget(central)
        self.main_layout = QtGui.QHBoxLayout()
        central.setLayout(self.main_layout)
        # init different layouts
        self.menu_layout = QtGui.QVBoxLayout()
        self.menu = QtGui.QGridLayout()
        self.list = QtGui.QGridLayout()
        self.canvas = QtGui.QVBoxLayout()
        # inits menu layout
        self.train_button = QtGui.QPushButton('Training')
        self.train_button.clicked.connect(self.show_training)
        self.train_button.setDefault(True)
        self.menu.addWidget(self.train_button, 0, 0, 1, 2)
        self.recognize_button = QtGui.QPushButton('Recognize')
        self.recognize_button.clicked.connect(self.show_recognition)
        self.menu.addWidget(self.recognize_button, 0, 2, 1, 2)
        self.instructions = QtGui.QLabel()
        self.instructions.setText('Press the left mouse button and draw a number or shape on '
                                  'the right side of the window.\nIf you release the mouse button the programm starts '
                                  'training the system.\nYou can train the system with several shapes.')
        self.menu.addWidget(self.instructions, 1, 0, 1, 4)
        # init list layout !!TODO

        # add diff layouts to right side
        self.menu_layout.addLayout(self.menu)
        self.menu_layout.addLayout(self.list)
        # init canvas
        self.header = QtGui.QLabel('Draw here:')
        self.header.setAlignment(QtCore.Qt.AlignTop)
        self.canvas.addWidget(self.header)
        # add layouts to main window
        self.main_layout.addLayout(self.menu_layout)
        self.main_layout.addLayout(self.canvas)

    def show_training(self):
        self.train_button.setDefault(True)
        self.recognize_button.setDefault(False)
        self.instructions.setText('Press the left mouse button and draw a number or shape on '
                                  'the right side of the window.\nIf you release the mouse button the programm starts '
                                  'training the system.\nYou can train the system with several shapes.')

    def show_recognition(self):
        self.recognize_button.setDefault(True)
        self.train_button.setDefault(False)
        self.instructions.setText('Press the left mouse button and draw a number or shape on '
                                  'the right side of the window.\nIf you release the mouse button the programm starts '
                                  'the recognition.')

    def resample(self, points, n):
        I = self.path_length(points) / (n - 1)
        D = 0
        new_points = []
        for p in points:
            d = math.dist(points[p-1], points[p])
            if (D + d) >= I:
                q_x = points[p-1][0] + ((I - D) / d) * (points[p][0] - points[p][0])
                q_y = points[p-1][1] + ((I - D) / d) * (points[p][1] - points[p][1])
                new_points.append([q_x, q_y])
                points.insert(p, [q_x, q_y])
            else:
                D = D + d
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
        B = BoundingBox(points)
        for p in points:
            q_x = p[0] * (size / B.width())
            q_y = p[1] * (size / B.height())
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
        for T in templates:
            d = self.distance_at_best_angle(points, T, - theta, theta, theta_avg)
            if d < b:
                b = d
                new_T = T
        score = 1 - b / 0.5 * math.sqrt(self.SIZE ** 2 + self.SIZE ** 2)  # size of scale_to_square
        return new_T, score

    def distance_at_best_angle(self, points, T, theta_a, theta_b, theta_alpha):
        phi = 0.5 * (-1 + math.sqrt(5))
        x_1 = phi * theta_a + (1 - phi) * theta_b
        f_1 = self.distance_at_angle(points, T, x_1)
        x_2 = (1 - phi) * theta_a + phi * theta_b
        f_2 = self.distance_at_angle(points, T, x_2)
        while theta_b - theta_a > theta_alpha:
            if f_1 < f_2:
                theta_b = x_2
                x_2 = x_1
                f_2 = f_1
                x_1 = phi * theta_a + (1- phi) * theta_b
                f_1 = self.distance_at_angle(points, T, x_1)
            else:
                theta_a = x_1
                x_1 = x_2
                f_1 = f_2
                x_2 = (1 - phi) * theta_a + phi * theta_b
                f_2 = self.distance_at_angle(points, T, x_2)
        return min(f_1, f_2)

    def distance_at_angle(self, points, T, theta):
        new_points = self.rotate_by(points, theta)
        d = self.path_distance(new_points, T)
        return d

    def path_distance(self, A, B):
        d = 0
        for i in range(len(A)):
            d = d + math.dist(A[i], B[i])
        return d / len(A)


def main():
    app = QtGui.QApplication([])
    recognizer = Recognizer()

    recognizer.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())


if __name__ == '__main__':
    main()
