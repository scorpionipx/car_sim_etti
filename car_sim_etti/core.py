import logging
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow


from car_sim_etti import settings, APP_SLUG


LOGGER = logging.getLogger(APP_SLUG)


class CarSimETTI(QMainWindow):
    """

    """
    def __init__(self):
        super(CarSimETTI, self).__init__()

        self.init_gui()

    def button_clicked(self):
        LOGGER.info('Clicked!')

    def init_gui(self):
        self.setGeometry(100, 200, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setWindowTitle(settings.WINDOW_TITLE)

        self.label = QtWidgets.QLabel(self)
        self.label.setText("my first label!")
        self.label.move(50, 50)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("click me!")
        self.b1.clicked.connect(self.button_clicked)


def run_application():
    app = QApplication(sys.argv)
    win = CarSimETTI()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_application()
